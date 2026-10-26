## Context

`plan.py` loads `nutrition_rules.json` through `_check_rules_shape` and `load_rules`. A food has exactly the keys in `FOOD_KEYS` (`food, categories, seasons, placeholder`), and any other key stops the run (Review 8). `food_label` adds `[placeholder]` when the flag is true. One `DISCLAIMER` constant heads both outputs. The tests keep decided values as literals in `tests/test_plan.py`, with a date comment pointing to PLANNING_LOG.md, so they never take them from `plan.py`.

Decisions for this change are in PLANNING_LOG.md (2026-10-26). Motivation is in proposal.md, and the required behavior is in the two delta specs.

## Goals / Non-Goals

**Goals:**
- Real data lives in `nutrition_rules.json` only, and the loader checks it as strictly as everything else in the file.
- One label function feeds both outputs, so the terminal and `nutrients.md` cannot drift apart.
- The demo in README Section 1 can be run word for word on a fresh copy and gives what it says.

**Non-Goals:**
- No fetch script or FDC client. Values are copied by hand and checked by tests.
- No change to ranking, rotation or `history.json` format.
- Seasons and categories of real foods stay hand-written. FDC has no season data.

## Decisions

### 1. The 15 entries

All 15 entries are SR Legacy and described as eaten. FDC reports the unit as `MG`; it is stored as `mg`. Order, categories and seasons stay as they are today, so ranking and exclusion behavior do not change.

| Slot | Food name | FDC ID | FDC description | per_100g | % NRV |
|---|---|---|---|---|---|
| Iron | lentils, cooked | 172421 | Lentils, mature seeds, cooked, boiled, without salt | 3.33 | 24 |
| Iron | spinach, cooked | 168463 | Spinach, cooked, boiled, drained, without salt | 3.57 | 26 |
| Iron | ground beef, cooked | 172161 | Beef, ground, unspecified fat content, cooked | 2.67 | 19 |
| Iron | sardines (canned in oil) | 175139 | Fish, sardine, Atlantic, canned in oil, drained solids with bone | 2.92 | 21 |
| Iron | firm tofu (calcium-set) | 172475 | Tofu, raw, firm, prepared with calcium sulfate | 2.66 | 19 |
| Vitamin C | oranges | 169097 | Oranges, raw, all commercial varieties | 53.2 | 67 |
| Vitamin C | red bell peppers | 170108 | Peppers, sweet, red, raw | 128 | 160 |
| Vitamin C | strawberries | 167762 | Strawberries, raw | 58.8 | 74 |
| Vitamin C | broccoli, cooked | 169967 | Broccoli, cooked, boiled, drained, without salt | 64.9 | 81 |
| Vitamin C | green kiwi | 168153 | Kiwifruit, green, raw | 92.7 | 116 |
| Magnesium | pumpkin seeds (dried) | 170556 | Seeds, pumpkin and squash seed kernels, dried | 592 | 158 |
| Magnesium | almonds (raw) | 170567 | Nuts, almonds | 270 | 72 |
| Magnesium | black beans, cooked | 173735 | Beans, black, mature seeds, cooked, boiled, without salt | 70 | 19 |
| Magnesium | cashews (raw) | 170162 | Nuts, cashew nuts, raw | 292 | 78 |
| Magnesium | whole-wheat bread | 172688 | Bread, whole-wheat, commercially prepared | 75 | 20 |

Where the values came from:
- **Iron and Vitamin C:** taken from the FDC API (SR Legacy search) on 2026-10-26. The user checked 5 of them by hand on fdc.nal.usda.gov.
- **Magnesium:** given by the user from fdc.nal.usda.gov. Black beans 173735 also appeared in the API search. The almonds entry has no "raw" in its description, but its FDC footnote says unroasted; the cashews entry is heat-treated to remove the shell, not roasted (both confirmed by the user).

Names decided by the user: tofu, beef, spinach, broccoli, bell peppers, kiwi, pumpkin seeds, almonds, cashews, black beans. The other five names (lentils, sardines, oranges, strawberries, whole-wheat bread) were chosen by Claude to the same rule.

Rejected alternatives:
- **Tofu set with nigari** (174290: 2.04 mg, 14.6%; 172448: 1.61 mg, 11.5%) fails the threshold. The calcium-set entry is the one that passes.
- **Raw spinach** (2.71 mg) and **raw broccoli** (89.2 mg) also pass. Cooked was chosen because these are normally cooked.

### 2. Shape: `"fdc"` replaces `"placeholder"` on real foods

`FOOD_KEYS` becomes `food, categories, seasons, placeholder, fdc`. Each food must have exactly one of `"placeholder": true` or `"fdc"`. `"placeholder": false` becomes an error, because with `"fdc"` present it would be a second, contradictory signal (PLANNING_LOG 2026-10-26, decision 5). The `"fdc"` keys are checked as strictly as food keys: an unknown key stops the run.

`id` must be an `int` and not a `bool`, because `isinstance(True, int)` is true in Python. `per_100g` must be an `int` or `float`, again not a `bool`.

- *Alternative:* keep `"placeholder": false` next to `"fdc"`. Rejected because two flags can disagree.
- *Alternative:* derive the placeholder status silently from whether `"fdc"` is missing, with no flag at all. Rejected because a food that loses its `"fdc"` by mistake would quietly become a placeholder instead of stopping the run.

### 3. Threshold check in `load_rules`, with exact arithmetic

`plan.py` gets an NRV table, `{"Iron": (14, "mg"), "Vitamin C": (80, "mg"), "Magnesium": (375, "mg")}`, with the regulation named in a comment. A real food passes when `per_100g * 100 >= 15 * nrv`.

The values are converted with `Decimal(str(value))`. Float multiplication can put an amount that is exactly on the line just below it: 56.25 mg is exactly 15% of 375.

The % NRV shown is the same exact value rounded half up. Plain `round()` on floats gives 66% for oranges (53.2 / 80 = 66.5%); exact half-up gives 67%.

Keying the table by nutrient name means a real food in a slot without an entry (Fiber, Omega-3, …) stops the run with "no 'source of' threshold". That keeps fibre (g, or per 100 kcal) and omega-3 (ALA or EPA+DHA, per 100 g and per 100 kcal) as future work that cannot slip in half-checked.

- *Alternative:* store the threshold or % in the JSON. Rejected: a stored % could disagree with the stored amount, and the NRVs are law, not data.

### 4. One label for both outputs

`food_label` returns `"<food> [<per_100g> <unit>/100 g, <pct>% NRV, FDC <id>]"` for a real food. `per_100g` is printed as stored: 3.33 stays 3.33, and 128 stays 128, not 128.0. Both `render_terminal` and `render_markdown` already call `food_label`, so the `nutrients.md` table keeps its four columns (Nutrient | Evidence | Food | Notes). Existing tests that check `| <food> | <notes> |` adjacency still hold. The FDC description is not shown, because it is long. It stays in the data and is reachable from the FDC ID.

- *Alternative:* add "Amount" and "Source" columns. Rejected: it changes the table for placeholder rows too, for no gain in a 5-minute demo.

### 5. Disclaimer text

The full sentence is "Not nutrition advice. Foods marked [placeholder] come from a stub database that has not been evidence-reviewed." The user decided the opening of the second sentence and that "not nutrition advice" is always shown. The ending is reused from the current text, which is Claude's completion. It is shown on every run, including a Menstrual run with no placeholder.

### 6. README Section 1

Section 1 becomes the 5-step demo from the proposal. It uses placeholder dates such as `<a date 2 days ago>` (Menstrual) and `<a date 14 days ago>` (Ovulatory) with `--cycle-length 28`, so no real dates are committed. It names `python3`, starts by copying the project to a separate folder, and says rotation in one sentence: a food is kept for the whole cycle and not repeated within the next 2 cycles.

Step 3 uses `--exclude fish` on the Ovulatory day. On a scratch copy (2026-10-26), salmon became walnuts, while on a Menstrual day no category changed any pick, because the top-ranked Menstrual foods have no categories. The expected output in the README is pasted from a real run on a scratch copy after implementation, with its dates replaced.

## Risks / Trade-offs

- **[Food renames orphan Menstrual history]** Old names like "lentils" no longer match. On the next run the same-cycle pick is recomputed and older entries no longer block repeats, so the Menstrual rotation starts over once. No crash, because `plan_slot` already handles a saved food that is no longer a candidate. → Documented here and in the PLANNING_LOG line, like the Review 8 nutrient-rename limitation. No migration code.
- **[Real foods carry hand-written seasons and categories]** "Real" means only the nutrient amount. → The `notice` in `nutrition_rules.json` and README Section 4 say so.
- **[FDC content ≠ phase evidence]** A real amount could read as support for the phase pairing. → The evidence tier stays on every line, and the README evidence note is unchanged.
- **[DEMO_KEY rate limit]** The key is shared and allows only a few calls an hour from one IP. → Nothing at runtime uses the network, and verification is done in the FDC web UI.

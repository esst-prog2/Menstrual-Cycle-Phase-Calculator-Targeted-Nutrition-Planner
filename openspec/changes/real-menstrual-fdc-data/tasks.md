## 1. Confirm the data

- [x] 1.1 Copy the exact FDC descriptions for almonds (FDC 170567) and cashews (FDC 170162) from fdc.nal.usda.gov (SR Legacy) into the design.md table, and confirm their magnesium values (270 mg, 292 mg); verify both rows in design.md have no "to be copied" placeholder left
- [x] 1.2 Append any confirmed description or value correction to PLANNING_LOG.md as a new line; verify no earlier line was changed (`git diff PLANNING_LOG.md` shows only added lines)

## 2. Tests first (they fail until section 3 is done)

- [ ] 2.1 In `tests/test_plan.py`, change the `DISCLAIMER` literal to "Not nutrition advice. Foods marked [placeholder] come from a stub database that has not been evidence-reviewed." (dated 2026-10-26); verify `test_disclaimer_and_placeholder_labels_in_both` now fails on the old output
- [ ] 2.2 Add a literal snapshot of the 15 Menstrual entries (food name, FDC ID, description, per_100g, unit) from design.md, plus the NRV literals (Iron 14 mg, Vitamin C 80 mg, Magnesium 375 mg) and 15%, each dated 2026-10-26; add a test that the shipped Menstrual foods match the snapshot exactly and each passes the threshold computed from those literals; verify it fails against today's data
- [ ] 2.3 Replace `test_every_entry_is_placeholder_with_no_evidence_label` with: Menstrual entries have `"fdc"` and no `"placeholder"`; Follicular, Ovulatory and Luteal entries have `"placeholder": true` and no `"fdc"`; no entry has an evidence label; verify it fails against today's data
- [ ] 2.4 Add loader tests, one subTest each, for every stop in the nutrient-selection delta: fdc missing a key, unknown fdc key, `id` not a positive int (including `true`), empty description, `per_100g` negative or not a number (including `true`), both `fdc` and `placeholder`, neither (including `"placeholder": false`), below threshold (calcium+nigari tofu, 1.61 mg, error names food, 1.61 mg, 2.1 mg, Iron), wrong unit, real food in Ovulatory Omega-3; plus a pass at exactly 56.25 mg Magnesium; verify each asserts the error text and that no files are written
- [ ] 2.5 Update `test_placeholder_must_be_true_or_false` and `test_unknown_key_on_food_or_claim` to the new rule and key list (`food, categories, seasons, placeholder, fdc`); replace `test_placeholder_label_follows_the_flag` (which uses `placeholder=False`) with a test using a `real_food()` fixture helper; verify they fail on the current code
- [ ] 2.6 Add output tests: a Menstrual run with the shipped data shows `lentils, cooked [3.33 mg/100 g, 24% NRV, FDC 172421]` in both the terminal and `nutrients.md`, with no `[placeholder]` in either and the disclaimer exactly once in each; oranges render as 67% NRV (half-up, not float `round()`); `per_100g` 128 renders as `128`, not `128.0`; an Ovulatory run still shows 3 `[placeholder]` labels; a test that two real foods with equal rank keep list order whatever their amounts; verify all fail before section 3

## 3. Code and data

- [ ] 3.1 In `plan.py`: add the NRV table (with a comment naming Regulation (EU) 1169/2011 Annex XIII and Regulation (EC) 1924/2006), add `fdc` to `FOOD_KEYS`, and check in `_check_rules_shape`/`load_rules` the exactly-one-of rule, the `fdc` shape and the threshold using `Decimal(str(value))`; verify the section 2.4 and 2.5 loader tests pass
- [ ] 3.2 In `plan.py`: change `DISCLAIMER` and make `food_label` produce the real-food label (exact half-up % NRV, amount printed as stored); verify the section 2.1 and 2.6 output tests pass
- [ ] 3.3 Rewrite the 15 Menstrual entries in `nutrition_rules.json` from the design.md table (names, `fdc`, no `placeholder`; categories, seasons and order unchanged), and update `notice` to say that the Menstrual foods' amounts are real FDC SR Legacy data, while all other foods and every food's seasons and categories are hand-written stubs; verify tests 2.2 and 2.3 pass and the full suite is green (`python3 -m unittest discover -s tests`)

## 4. README

- [ ] 4.1 Update README Section 4's description of `nutrition_rules.json` (no longer "all hand-written placeholder pairings"), and say that "real" covers the nutrient amount only and that the evidence tier still describes the phase pairing; verify by reading the section that it matches the new `notice`
- [ ] 4.2 Rewrite README Section 1 as the 5-step demo from proposal.md: copy the project to a separate folder first; use `python3`; use placeholder dates (`<a date 2 days ago>`, `<a date 14 days ago>`) with `--cycle-length 28`; step 3 is `--exclude fish` on the Ovulatory day; give rotation one sentence; no real dates, usernames or local paths; verify with `grep` that Section 1 has no `python ` without the 3 and no YYYY-MM-DD date
- [ ] 4.3 Rehearse the demo word for word on a fresh scratch copy (no `history.json`): run all 5 steps and check each shows what Section 1 says (real FDC labels on Menstrual; `[placeholder]` on Ovulatory; salmon → walnuts with `--exclude fish`; swap note with `--prefer-alternative`; FDC IDs in `nutrients.md`). Paste any expected output into the README with its dates replaced; verify the repo's own `history.json` and `nutrients.md` are unchanged (modification time and `git status`)

## 5. Close

- [ ] 5.1 Append a PLANNING_LOG.md line for the known limitation (renamed Menstrual foods orphan existing Menstrual history, so that rotation starts over once) and for any implementation detail decided along the way; verify only added lines in `git diff PLANNING_LOG.md`
- [ ] 5.2 Run `openspec validate real-menstrual-fdc-data --strict` and the full test suite; verify both pass

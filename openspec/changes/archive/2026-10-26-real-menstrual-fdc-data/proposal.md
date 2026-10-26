## Why

Every food in `nutrition_rules.json` is a hand-written stub, so the tool cannot yet show a single sourced fact about what a food contains. For the next two weeks the Menstrual phase (Iron, Vitamin C, Magnesium) moves to real values from USDA FoodData Central, so the demo can show real, sourced foods next to the placeholder ones in the other phases.

README Section 1 (The Demo) also no longer works and has to be rewritten in the same change:
- its command starts with `python`, which does not run on the author's machine (`python3` does);
- its `--exclude dairy` changes nothing in the Ovulatory phase it lands in, because none of the picked foods is dairy;
- the rotation it promises is not visible in one run, because a pick is kept for the whole cycle;
- it describes the old grocery-list idea, not the move to real FDC data.

## What Changes

- **Real Menstrual data.** All 15 Menstrual foods (5 per nutrient) get an `"fdc"` object: the SR Legacy FDC ID, the exact FDC description, the amount per 100 g and the unit. Each food is taken as eaten: cooked where it is normally cooked, while pumpkin seeds are dried and almonds and cashews raw. Values are copied into the file by hand. There are no API calls at runtime and no API key in the repository.
- **Food names follow their FDC entry**, for example "firm tofu (calcium-set)", "ground beef, cooked", "spinach, cooked", "red bell peppers", "green kiwi", "pumpkin seeds (dried)".
- **Real vs placeholder.** A food is real when it has `"fdc"`, and real foods carry no `"placeholder"` key. Every other food keeps `"placeholder": true`. A food with both, or with neither, stops the run. **BREAKING** for the rules file: `"placeholder": false` is no longer accepted.
- **EU "source of" threshold enforced at load.** A real food must provide at least 15% of the EU nutrient reference value (NRV) per 100 g (Regulation (EU) 1169/2011, Annex XIII). Otherwise the run stops with an error naming the food, its amount and the threshold. The NRVs are Iron 14 mg, Vitamin C 80 mg and Magnesium 375 mg.
- **Output shows the source.** A real food is shown with its amount per 100 g, its % of NRV and its FDC ID, in both the terminal and `nutrients.md`. Placeholder foods keep `[placeholder]`.
- **New disclaimer.** "PLACEHOLDER DATA - … Every food below comes from a stub database …" would now be false on a Menstrual day. It becomes "Not nutrition advice. Foods marked [placeholder] come from a stub database that has not been evidence-reviewed." "Not nutrition advice" stays on every run.
- **README Section 1 rewritten** as a 5-minute demo with slides. It runs in a separate copy of the project, so the presenter's real `history.json` is never touched:
  1. `python3 plan.py` on a Menstrual day shows real, sourced foods with FDC amounts and evidence tiers.
  2. The same on an Ovulatory day shows placeholder foods.
  3. `--exclude fish` on the Ovulatory day turns salmon into walnuts, showing the hard rule. No exclusion changes a pick on a Menstrual day.
  4. `--prefer-alternative` swaps a food.
  5. `nutrients.md` is opened to show the table with sources.
  Rotation is explained in one sentence rather than shown.
- The `notice` in `nutrition_rules.json` and README Section 4 are updated so they no longer say every pairing is a stub.

Not in scope: real data for the other three phases, recipes (future work), ranking foods by nutrient amount, and real seasonal or category data.

## Capabilities

### New Capabilities
None.

### Modified Capabilities
- `nutrient-selection`: placeholder labeling now follows the presence of `"fdc"`; the rules-file check accepts and validates `"fdc"` and enforces the "source of" threshold; ranking explicitly ignores the stored amount; new requirement for real food data from FDC.
- `cli-output`: the disclaimer text changes; real foods show amount, % NRV and FDC ID in both the terminal and `nutrients.md`.

## Impact

- `nutrition_rules.json`: 15 Menstrual entries rewritten (new names, `"fdc"`, no `"placeholder"`), plus the `notice`.
- `plan.py`: `FOOD_KEYS` and `_check_rules_shape`/`load_rules` (the `"fdc"` shape and threshold), an NRV table, `food_label`, and `DISCLAIMER`.
- `tests/test_plan.py`: the disclaimer literal, the real-data tests, new loader-error tests, and real-food label tests. The `placeholder: false` fixture test is replaced.
- `README.md`: Section 1 is rewritten and Section 4's description of the data is updated.
- `history.json` (user's local, uncommitted): Menstrual food names change, so existing Menstrual history no longer matches any food, and that rotation starts over once. Nothing crashes.
- No new dependencies. FDC data is public domain.

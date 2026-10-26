## ADDED Requirements

### Requirement: Real food data from FoodData Central
Every Menstrual-phase food (Iron, Vitamin C, Magnesium; 5 foods each) SHALL be a real food: its entry carries an `"fdc"` object with exactly the keys `"id"` (the USDA FoodData Central ID of an SR Legacy entry, a positive whole number), `"description"` (that entry's exact FDC description, a non-empty string), `"per_100g"` (the amount of the slot's nutrient per 100 g, a number of at least 0) and `"unit"` (the unit of that amount). Each entry SHALL describe the food as eaten: cooked where it is normally cooked, while pumpkin seeds are dried and almonds and cashews raw. Each food's name SHALL say which form it is, matching its FDC entry (for example "spinach, cooked", "firm tofu (calcium-set)"). The values SHALL be stored in `nutrition_rules.json`. The tool SHALL make no network request at runtime, and no API key SHALL appear in the repository. Foods in the Follicular, Ovulatory and Luteal phases SHALL stay placeholders.

#### Scenario: Menstrual foods are all real
- **WHEN** the shipped `nutrition_rules.json` is checked
- **THEN** all 15 Menstrual foods have an `"fdc"` object and no `"placeholder"` key, and every food in the other three phases has `"placeholder": true` and no `"fdc"` object

#### Scenario: Stored values match the recorded FDC entries
- **WHEN** the Menstrual foods are compared with the 15 FDC IDs and amounts recorded for this change
- **THEN** every food has the recorded FDC ID, description, amount per 100 g and unit

#### Scenario: No network at runtime
- **WHEN** the tool runs with no network connection
- **THEN** it completes normally and shows the stored FDC values

#### Scenario: Malformed fdc object
- **WHEN** a food's `"fdc"` object is missing a key, has an unknown key, has a non-positive or non-whole `"id"`, an empty `"description"`, or a `"per_100g"` that is not a number of at least 0
- **THEN** the system stops with an error naming the food and the problem, and writes no files

### Requirement: EU "source of" threshold for real foods
A real food SHALL provide at least 15% of the EU nutrient reference value (NRV) for its slot's nutrient per 100 g. This is the "source of" condition of Regulation (EC) 1924/2006, with the significant amount defined in Regulation (EU) 1169/2011 Annex XIII Part A. The NRVs are Iron 14 mg, Vitamin C 80 mg and Magnesium 375 mg, so the thresholds are 2.1 mg, 12 mg and 56.25 mg. An amount exactly at the threshold passes. When `nutrition_rules.json` loads, the system SHALL stop with an error and write no files if:
- a real food is below the threshold (the error names the food, its amount, the threshold and the nutrient);
- a real food's unit is not the unit of its nutrient's NRV;
- a real food sits in a nutrient slot that has no NRV.

#### Scenario: Food below the threshold
- **WHEN** a real Iron food has `"per_100g": 1.61` and `"unit": "mg"`
- **THEN** the system stops with an error naming that food, 1.61 mg, the 2.1 mg threshold and Iron, and writes no files

#### Scenario: Food exactly at the threshold
- **WHEN** a real Magnesium food has `"per_100g": 56.25` and `"unit": "mg"`
- **THEN** it loads and can be suggested

#### Scenario: Wrong unit
- **WHEN** a real Vitamin C food has `"unit": "g"`
- **THEN** the system stops with an error naming the food, the unit given and the expected unit mg

#### Scenario: Real food in a slot with no NRV
- **WHEN** a food in the Ovulatory Omega-3 slot has an `"fdc"` object
- **THEN** the system stops with an error saying Omega-3 has no "source of" threshold, and writes no files

## MODIFIED Requirements

### Requirement: Placeholder labeling
A food suggestion SHALL carry a placeholder label exactly when its entry in `nutrition_rules.json` has `"placeholder": true`. Every food SHALL be either a placeholder (`"placeholder": true` and no `"fdc"` object) or a real food (an `"fdc"` object and no `"placeholder"` key), never both and never neither. A real food SHALL carry no placeholder label. No food entry SHALL carry an evidence-strength label; evidence strength belongs to the phase-nutrient claim (see "Evidence tier per nutrient").

#### Scenario: Placeholder label present
- **WHEN** the system suggests a food whose entry has `"placeholder": true`
- **THEN** that suggestion carries a placeholder label

#### Scenario: Food not marked as a placeholder
- **WHEN** the system suggests a food whose entry does not have `"placeholder": true`
- **THEN** that suggestion carries no placeholder label

#### Scenario: Real food carries no placeholder label
- **WHEN** the system suggests a food whose entry has an `"fdc"` object
- **THEN** that suggestion carries no placeholder label

#### Scenario: Food marked both real and placeholder
- **WHEN** a food entry has both an `"fdc"` object and a `"placeholder"` key
- **THEN** the system stops with an error naming the food, and writes no files

#### Scenario: Food marked neither real nor placeholder
- **WHEN** a food entry has no `"fdc"` object and no `"placeholder": true` (including `"placeholder": false`)
- **THEN** the system stops with an error naming the food, and writes no files

### Requirement: Rules file checked against the code's lists
When `nutrition_rules.json` loads, the system SHALL check it before writing any file. It SHALL stop with an error naming the problem if:
- `phases` or `evidence` does not have exactly the four phases (Menstrual, Follicular, Ovulatory, Luteal);
- a nutrient has an evidence tier but no foods in `phases` (a nutrient with foods but no tier is covered by "Evidence tier per nutrient");
- a food is not an object with a string `"food"`, a list `"categories"`, a list `"seasons"`, and either `"placeholder": true` or a valid `"fdc"` object (see "Placeholder labeling", "Real food data from FoodData Central" and "EU 'source of' threshold for real foods");
- a food has any other key, so no food can carry an evidence label;
- a food carries a category outside the fixed set of 11, or a season outside winter, spring, summer, autumn.

A typo in the data SHALL never silently change which foods `--exclude` removes or which foods count as in season.

#### Scenario: Phase missing from the rules file
- **WHEN** `phases` has no Follicular entry
- **THEN** the system stops with an error naming the missing phase, and writes no files

#### Scenario: Category typo in the rules file
- **WHEN** a food is tagged `diary` instead of `dairy`
- **THEN** the system stops with an error naming the food and the unknown category, instead of running with an `--exclude dairy` that misses that food

#### Scenario: Season typo in the rules file
- **WHEN** a food has the season `Autumn` instead of `autumn`
- **THEN** the system stops with an error naming the food and the unknown season

### Requirement: Constraint priority order
Candidates for a nutrient slot SHALL be filtered and ranked in this order:
1. exclusions — hard, never violated;
2. no-repeat-within-2-cycles — soft;
3. seasonality — soft, lowest priority.

Candidates that rank equally keep their order in `nutrition_rules.json`. Foods SHALL NOT be ranked by evidence or by nutrient content: a real food's amount per 100 g SHALL NOT affect ranking, and real foods SHALL NOT rank above or below placeholder foods for being real.

#### Scenario: Excluded food never shown
- **WHEN** a food matches an active `--exclude` value
- **THEN** it is never shown for any nutrient slot, regardless of how well it would otherwise rank

#### Scenario: A food-level evidence label does not affect ranking
- **WHEN** a candidate carries an `evidence` field
- **THEN** it is ranked the same as if the field were absent

#### Scenario: Amount per 100 g does not affect ranking
- **WHEN** two real foods in a slot rank equally on every constraint, and the second has the larger amount per 100 g
- **THEN** the first in list order is chosen

#### Scenario: No-repeat outranks seasonality
- **WHEN** one candidate is in-season but repeats a recent pick, and another is out-of-season but new
- **THEN** the out-of-season-but-new candidate is chosen, and the in-season-but-repeating candidate is shown as the alternative

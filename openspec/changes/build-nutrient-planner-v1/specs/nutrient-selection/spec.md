## Purpose

Selects, for each of a phase's tracked nutrients, a single food from the stub placeholder database, applying a fixed constraint priority so exclusions are never violated and the data's unevidenced status stays visible.

## ADDED Requirements

### Requirement: Nutrients tracked per phase
Each of the four phases SHALL track exactly 3 nutrients, the same number in every phase.

#### Scenario: Phase output always shows 3 nutrients
- **WHEN** the system generates suggestions for any phase
- **THEN** exactly 3 nutrients are shown for that phase

### Requirement: Category tags for exclusion matching
Every stub food entry SHALL carry one or more category tags drawn from the fixed set: `dairy`, `eggs`, `gluten`, `nuts`, `peanuts`, `soy`, `fish`, `shellfish`, `sesame`, `meat`, `pork` — covering common allergens and foods avoided for diet or religious reasons. A food MAY carry several tags; a pork food SHALL carry both `meat` and `pork`. Excluding a single food by name is not supported in v1 — category is the only exclusion mechanism.

#### Scenario: Food carries a category tag
- **WHEN** a stub food entry is added to `nutrition_rules.json`
- **THEN** it has at least one category tag from the fixed set

#### Scenario: Pork food carries both tags
- **WHEN** a stub food entry is pork
- **THEN** it carries both the `meat` and `pork` tags, so excluding either one matches it correctly

### Requirement: Constraint priority order
Candidates for a nutrient slot SHALL be filtered and ranked in this order: (1) exclusions — hard, never violated; (2) nutrient coverage — highest-priority soft constraint; (3) no-repeat-within-2-cycles — soft; (4) seasonality — soft, lowest priority.

#### Scenario: Excluded food never shown
- **WHEN** a food matches an active `--exclude` value
- **THEN** it is never shown for any nutrient slot, regardless of how well it would otherwise rank

#### Scenario: No-repeat outranks seasonality
- **WHEN** one candidate is in-season but repeats a recent pick, and another is out-of-season but new
- **THEN** the out-of-season-but-new candidate is chosen, and the in-season-but-repeating candidate is shown as the alternative

### Requirement: Single-candidate slot has no alternative note
If exactly one valid candidate remains for a nutrient slot after filtering, it SHALL be used directly with no alternative note.

#### Scenario: One valid candidate
- **WHEN** exactly one candidate remains for a nutrient slot after exclusions and other constraints are applied
- **THEN** that candidate is shown with no alternative note

### Requirement: Multi-candidate slot shows the real deciding reason
If two or more valid candidates remain and rank differently, the system SHALL show the top-ranked candidate plus a note naming the next-best alternative and the specific constraint that decided against it — not a fixed phrase used regardless of the actual reason.

#### Scenario: Alternative note states the real reason
- **WHEN** two valid candidates for a nutrient slot are ranked differently by a soft constraint (e.g. seasonality or no-repeat)
- **THEN** the shown alternative note names that specific constraint as the reason, matching whichever one actually broke the tie

### Requirement: --prefer-alternative swaps and persists for the cycle
`--prefer-alternative <nutrient>` SHALL swap the named nutrient's shown food to its available alternative for the remainder of the current cycle. If the named nutrient has no alternative available, the system SHALL error clearly rather than swap silently or guess.

#### Scenario: Swap applied
- **WHEN** `--prefer-alternative zinc` is passed and the Zinc slot has an available alternative
- **THEN** the alternative is shown instead of the original top-ranked candidate

#### Scenario: No alternative available for named nutrient
- **WHEN** `--prefer-alternative` names a nutrient with no alternative available this cycle
- **THEN** the system prints a clear error and does not swap or guess

### Requirement: Empty candidate pool after exclusions
If exclusions remove every candidate for a nutrient slot, the system SHALL NOT fail; it SHALL continue processing the other nutrients and mark that slot as having no suitable food.

#### Scenario: All candidates excluded for one nutrient
- **WHEN** every candidate for a nutrient slot is removed by active `--exclude` values
- **THEN** the system completes the run, shows the other nutrients normally, and marks the emptied slot as having no suitable food

### Requirement: Placeholder labeling
Every food suggestion SHALL carry a placeholder label, since `nutrition_rules.json` is not evidence-reviewed. No stub rule SHALL carry an evidence-strength label (Strong/Moderate/Weak/Speculative).

#### Scenario: Placeholder label present
- **WHEN** the system suggests any food from the stub database
- **THEN** that suggestion carries a placeholder label and no evidence-strength label

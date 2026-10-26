## ADDED Requirements

### Requirement: Real foods show their FDC amount and source
A suggested real food SHALL be shown, in both the terminal output and `nutrients.md`, with its name followed by a bracketed label giving:
- its amount per 100 g and unit, as stored;
- that amount as a whole-number percentage of the NRV (rounded half up);
- its FDC ID.

The format is `<food> [<per_100g> <unit>/100 g, <percent>% NRV, FDC <id>]`, for example `lentils, cooked [3.33 mg/100 g, 24% NRV, FDC 172421]`. A placeholder food SHALL keep the `[placeholder]` label and show no amount.

#### Scenario: Real food in the terminal and nutrients.md
- **WHEN** the system suggests a real Iron food with FDC ID 172421 and 3.33 mg per 100 g
- **THEN** both the terminal output and `nutrients.md` show it as `<food> [3.33 mg/100 g, 24% NRV, FDC 172421]`, with the evidence tier as before

#### Scenario: Menstrual run shows no placeholder label
- **WHEN** the system runs on a Menstrual day with the shipped data
- **THEN** no suggestion in the terminal output or `nutrients.md` carries `[placeholder]` (the disclaimer still names the label), and each of the three suggestions shows an FDC ID

#### Scenario: Ovulatory run keeps placeholder labels
- **WHEN** the system runs on an Ovulatory day with the shipped data
- **THEN** each of the three suggestions carries `[placeholder]` and no amount or FDC ID

## MODIFIED Requirements

### Requirement: Placeholder disclaimer in both terminal and nutrients.md
Both the terminal output and `nutrients.md` SHALL start with this disclaimer, exactly once, on every run whatever the phase: "Not nutrition advice. Foods marked [placeholder] come from a stub database that has not been evidence-reviewed."

#### Scenario: Disclaimer shown once in each output
- **WHEN** the system completes a run
- **THEN** the terminal output and `nutrients.md` each contain the disclaimer exactly once

#### Scenario: Disclaimer shown when no food is a placeholder
- **WHEN** the system runs on a Menstrual day and every suggestion is a real food
- **THEN** the disclaimer, including "Not nutrition advice", still appears exactly once in each output

### Requirement: Item-level notes appear in both terminal and nutrients.md
These labels and notes SHALL each appear in both the terminal output and `nutrients.md`, since each is a standing fact about a specific suggestion:
- placeholder labels;
- real-food amount-and-source labels;
- repeat-fallback notes;
- alternative notes;
- swap notes ("swapped in with --prefer-alternative", without naming the food it replaced);
- "no suitable food" notes;
- "no foods for this nutrient in the data" notes.

#### Scenario: Each note type appears in both places
- **WHEN** any of a placeholder label, a real-food amount-and-source label, a repeat-fallback note, an alternative note, a swap note, a no-suitable-food note, or a no-foods-in-the-data note applies to a nutrient this run
- **THEN** that label or note appears in both the terminal output and `nutrients.md`

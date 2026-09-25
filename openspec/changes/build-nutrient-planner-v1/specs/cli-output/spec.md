## Purpose

Defines the terminal and `nutrients.md` output surfaces, ensuring every caveat about a suggestion (placeholder status, a forced repeat, an available alternative, an exclusion emptying a slot) is visible wherever a person might read the result, and defines the CLI flags that shape that output.

## ADDED Requirements

### Requirement: nutrients.md output file
The system SHALL write a `nutrients.md` file each run, listing the current phase's nutrient-food pairs for the current phase.

#### Scenario: File written each run
- **WHEN** the system completes a run
- **THEN** `nutrients.md` is written with the current phase's nutrient-food pairs

### Requirement: Item-level notes appear in both terminal and nutrients.md
Placeholder labels, repeat-fallback notes, alternative notes, and "no suitable food" notes SHALL each appear in both the terminal output and `nutrients.md`, since each is a standing fact about a specific suggestion.

#### Scenario: Each note type appears in both places
- **WHEN** any of a placeholder label, a repeat-fallback note, an alternative note, or a no-suitable-food note applies to a nutrient this run
- **THEN** that note appears in both the terminal output and `nutrients.md`

### Requirement: history.json warnings are terminal-only
A warning about an unreadable or corrupt `history.json` SHALL appear only in the terminal output, never in `nutrients.md`, since it is a one-time fact about the run rather than a property of any suggestion.

#### Scenario: Corrupt-history warning absent from the file
- **WHEN** `history.json` could not be parsed this run
- **THEN** a warning appears in the terminal output, and `nutrients.md` contains no mention of it

### Requirement: --exclude flag matches by category
`--exclude <category>` SHALL remove every food carrying that category tag from consideration for every nutrient slot this run, and SHALL be repeatable to exclude multiple categories.

#### Scenario: Excluded category never appears
- **WHEN** `--exclude dairy` is passed
- **THEN** no food tagged `dairy` appears anywhere in the output, for any nutrient slot

### Requirement: Unknown category rejected
If `--exclude` is given a value that does not match any known category, the system SHALL stop with an error listing the valid categories, and SHALL NOT silently proceed as if nothing were excluded.

#### Scenario: Typo in exclude value
- **WHEN** `--exclude diary` is passed (not a valid category)
- **THEN** the system stops with an error listing the valid categories, and produces no output

### Requirement: --prefer-alternative flag takes a nutrient name
`--prefer-alternative <nutrient>` SHALL take the target nutrient's name as its argument.

#### Scenario: Named nutrient is swapped
- **WHEN** `--prefer-alternative zinc` is passed and Zinc has an available alternative
- **THEN** only the Zinc slot's shown food is swapped to its alternative; other nutrients are unaffected

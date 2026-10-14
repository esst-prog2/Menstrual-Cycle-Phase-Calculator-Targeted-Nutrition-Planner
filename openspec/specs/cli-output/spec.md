# cli-output Specification

## Purpose

Defines the terminal and `nutrients.md` output surfaces, ensuring every caveat about a suggestion (placeholder status, a forced repeat, an available alternative, an exclusion emptying a slot) is visible wherever a person might read the result, and defines the CLI flags that shape that output.

## Requirements

### Requirement: nutrients.md output file
The system SHALL write a `nutrients.md` file each run, listing the current phase's nutrient-food pairs for the current phase.

#### Scenario: File written each run
- **WHEN** the system completes a run
- **THEN** `nutrients.md` is written with the current phase's nutrient-food pairs

### Requirement: Placeholder disclaimer in both terminal and nutrients.md
Both the terminal output and `nutrients.md` SHALL start with this disclaimer, exactly once: "PLACEHOLDER DATA - not nutrition advice. Every food below comes from a stub database that has not been evidence-reviewed."

#### Scenario: Disclaimer shown once in each output
- **WHEN** the system completes a run
- **THEN** the terminal output and `nutrients.md` each contain the disclaimer exactly once

### Requirement: Files live next to the script
`nutrition_rules.json` SHALL be read from, and `history.json`, its backups and `nutrients.md` SHALL be written to, the folder that contains `plan.py`, whatever folder the tool is run from.

#### Scenario: Run from another folder
- **WHEN** the tool is run as `python path/to/plan.py ...` from a different working folder
- **THEN** `history.json` and `nutrients.md` are written next to `plan.py`, and nothing is written to the working folder

### Requirement: Data file problems are clear errors
Every problem reading `nutrition_rules.json`, opening `history.json`, or writing `nutrients.md` or `history.json` SHALL stop the run with one clear error message naming the file and the problem, never a Python traceback. (A `history.json` that opens but is corrupt is backed up instead; see rotation-history.) All files SHALL be read and written as UTF-8, whatever the system's locale. `nutrients.md` SHALL be written before `history.json`, so a run whose output could not be written does not advance the rotation.

#### Scenario: Rules file missing or not JSON
- **WHEN** `nutrition_rules.json` is missing, is not valid UTF-8, or is not valid JSON
- **THEN** the system stops with an error naming the file and the problem (for invalid JSON, the line and column), and writes no files

#### Scenario: history.json cannot be opened
- **WHEN** `history.json` exists but cannot be opened (for example, it is a folder or not readable)
- **THEN** the system stops with an error saying so, leaves the file unchanged, makes no backup, and writes no files

#### Scenario: Output cannot be written
- **WHEN** `nutrients.md` cannot be written
- **THEN** the system stops with an error naming the file, and `history.json` is not updated

#### Scenario: Non-UTF-8 locale
- **WHEN** the tool runs under a non-UTF-8 locale and a food name contains accented letters
- **THEN** the name is read, shown and saved correctly

### Requirement: Item-level notes appear in both terminal and nutrients.md
Placeholder labels, repeat-fallback notes, alternative notes, swap notes ("swapped in with --prefer-alternative", without naming the food it replaced), "no suitable food" notes, and "no foods for this nutrient in the data" notes SHALL each appear in both the terminal output and `nutrients.md`, since each is a standing fact about a specific suggestion.

#### Scenario: Each note type appears in both places
- **WHEN** any of a placeholder label, a repeat-fallback note, an alternative note, a swap note, a no-suitable-food note, or a no-foods-in-the-data note applies to a nutrient this run
- **THEN** that note appears in both the terminal output and `nutrients.md`

### Requirement: Late-period note appears in both terminal and nutrients.md
When the run falls in the late-period grace window, a "period may be late" note SHALL appear in both the terminal output and `nutrients.md`, since it qualifies every suggestion shown for that run.

#### Scenario: Grace-window run
- **WHEN** `--last-period` is between `cycle_length` and `cycle_length + 6` days ago
- **THEN** both the terminal output and `nutrients.md` show a "period may be late" note

### Requirement: Personal output files are not committed
`history.json`, its backups (`history.json.bak` and the dated `history.json.<YYYY-MM-DD>[-N].bak`), and `nutrients.md` SHALL be listed in `.gitignore`, since each reveals the user's period timing and the repository is public.

#### Scenario: Files ignored after a run
- **WHEN** the tool has been run in the repository
- **THEN** `git status` shows none of `history.json`, any `history.json` backup, or `nutrients.md`

### Requirement: history.json warnings are terminal-only
A warning about a corrupt `history.json` (one that can be opened but is not valid UTF-8 JSON in the expected shape, see rotation-history) SHALL appear only in the terminal output, never in `nutrients.md`, since it is a one-time fact about the run rather than a property of any suggestion.

#### Scenario: Corrupt-history warning absent from the file
- **WHEN** `history.json` could not be parsed this run
- **THEN** a warning appears in the terminal output, and `nutrients.md` contains no mention of it

### Requirement: --exclude flag matches by category
`--exclude <category>` SHALL remove every food carrying that category tag from consideration for every nutrient slot this run, and SHALL be repeatable to exclude multiple categories. The category is matched case-insensitively (`FISH` and `fish` are the same).

#### Scenario: Excluded category never appears
- **WHEN** `--exclude dairy` is passed
- **THEN** no food tagged `dairy` appears anywhere in the output, for any nutrient slot

### Requirement: Unknown category rejected
If `--exclude` is given a value that does not match any known category, the system SHALL stop with an error listing the valid categories, and SHALL NOT silently proceed as if nothing were excluded.

#### Scenario: Typo in exclude value
- **WHEN** `--exclude diary` is passed (not a valid category)
- **THEN** the system stops with an error listing the valid categories, and produces no output

### Requirement: --prefer-alternative flag takes a nutrient name
`--prefer-alternative <nutrient>` SHALL take the target nutrient's name as its argument, matched case-insensitively. If that nutrient is not tracked in the current phase, the system SHALL stop with an error that names the phase and lists its tracked nutrients, and SHALL write no files.

#### Scenario: Named nutrient is swapped
- **WHEN** `--prefer-alternative zinc` is passed and Zinc has an available alternative
- **THEN** only the Zinc slot's shown food is swapped to its alternative; other nutrients are unaffected

#### Scenario: Nutrient not tracked in this phase
- **WHEN** `--prefer-alternative iron` is passed during the Ovulatory phase
- **THEN** the system stops with an error saying `iron` is not tracked in the Ovulatory phase, listing Fiber, Zinc, Omega-3, and writes no files

## Purpose

Tracks, per phase and nutrient, which foods were suggested in recent cycles so the same food isn't suggested again too soon, without losing data silently or letting repeated runs within one cycle corrupt the record.

## ADDED Requirements

### Requirement: Candidate pool minimum
Each phase/nutrient slot's stub candidate pool SHALL contain at least 5 foods — enough to support the 2-cycle no-repeat window even after some candidates are filtered out (3 distinct candidates are the minimum the window itself requires).

#### Scenario: Slot has enough candidates to rotate
- **WHEN** a nutrient slot has 5 stub candidates and 1 is removed by an exclusion
- **THEN** 4 remain, still enough to avoid repeating either of the last 2 cycles' picks

### Requirement: No-repeat window
A food SHALL NOT be suggested for the same nutrient in either of the previous 2 cycles, unless that nutrient's candidate pool does not have enough distinct valid options, in which case the system falls back to repeating.

#### Scenario: Repeat avoided
- **WHEN** a nutrient slot has at least 3 valid candidates not used in the last 2 cycles
- **THEN** the shown food is not one used in either of the last 2 cycles

#### Scenario: Forced repeat when pool too small
- **WHEN** a nutrient slot's valid candidates (after exclusions) are fewer than the last-2-cycles history requires to avoid repeating
- **THEN** the system falls back to repeating a previously-used food rather than failing

### Requirement: Repeat fallback note
When a repeat cannot be avoided, the system SHALL show a note next to that item stating it repeated because no other candidate was available within the last 2 cycles.

#### Scenario: Fallback note shown
- **WHEN** a nutrient's shown food repeats one from the last 2 cycles because no alternative was available
- **THEN** a note to that effect is shown for that item

### Requirement: history.json structure
History SHALL be recorded per phase and nutrient, with each entry tagged by the `--last-period` value of the cycle it belongs to. Only the most recent 2 distinct cycles SHALL be retained per slot.

#### Scenario: Oldest cycle evicted
- **WHEN** a third distinct cycle produces a new pick for a phase/nutrient slot
- **THEN** the oldest of the previously-recorded 2 cycles' entries is dropped and the new one is kept

### Requirement: Same-cycle re-run reuses the cached pick
A run whose `--last-period` matches the most recently recorded cycle for a phase/nutrient slot SHALL reuse that cycle's cached pick without advancing the rotation window, unless `--exclude` or `--prefer-alternative` invalidates the cached pick — in which case that cycle's entry SHALL be recomputed and updated in place, not treated as a new rotation event.

#### Scenario: Identical re-run
- **WHEN** the tool is run twice with the same `--last-period`, `--cycle-length`, and `--exclude` values, within the same phase
- **THEN** both runs show the same food for each nutrient, and the rotation window does not advance

#### Scenario: Re-run with a new exclusion invalidates the cached pick
- **WHEN** a same-cycle re-run adds an `--exclude` value that matches the cached pick for a nutrient
- **THEN** the system recomputes that nutrient's pick under the new exclusion, updates that cycle's history entry in place, and does not violate the exclusion

#### Scenario: Re-run with --prefer-alternative updates and persists
- **WHEN** a same-cycle re-run passes `--prefer-alternative` for a nutrient
- **THEN** that cycle's history entry is updated to the alternative, and a later re-run in the same cycle without the flag still shows the alternative

### Requirement: Missing history.json
A missing `history.json` SHALL be treated as normal on first run: the system proceeds with empty history and creates the file on its first write. This SHALL NOT be treated as an error.

#### Scenario: First run, no history file
- **WHEN** `history.json` does not exist
- **THEN** the system runs normally with empty history and writes a new `history.json`

### Requirement: Corrupt history.json
A `history.json` that exists but cannot be parsed SHALL be backed up to `history.json.bak`, then treated as empty. The system SHALL print a warning in the terminal only (not in `nutrients.md`) and SHALL NOT crash.

#### Scenario: Unparseable history file
- **WHEN** `history.json` exists but is not valid JSON in the expected shape
- **THEN** the system copies it to `history.json.bak`, proceeds with empty history, prints a terminal warning, and completes the run

### Requirement: 21-day cycle does not break rotation
The system SHALL run to completion for a 21-day cycle, including its zero-day Follicular phase, without error.

#### Scenario: 21-day cycle end to end
- **WHEN** `--cycle-length` is 21
- **THEN** the system produces valid output for whichever phase the current cycle day falls in, including correctly handling the Follicular phase having no days

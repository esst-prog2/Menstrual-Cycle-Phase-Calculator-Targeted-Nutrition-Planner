## Purpose

Validates the user's cycle inputs and determines the current cycle day and active phase (Menstrual, Follicular, Ovulatory, or Luteal), including for cycle lengths at the edges of the supported range.

## ADDED Requirements

### Requirement: Last period date format
`--last-period` SHALL be required and SHALL be validated as strict ISO 8601 (`YYYY-MM-DD`). A value that does not parse in that format SHALL be rejected with an "invalid date format" error, distinct from the future-date error.

#### Scenario: Malformed date rejected
- **WHEN** `--last-period` is given as `08/25/2026` or another non-ISO format
- **THEN** the system stops and prints an invalid-date-format error, and does not proceed

#### Scenario: Valid ISO date accepted
- **WHEN** `--last-period` is given as `2026-08-25`
- **THEN** the system parses it and proceeds

### Requirement: Future date rejected
The system SHALL reject a `--last-period` date that is in the future, printing an error that the date is invalid.

#### Scenario: Future last-period date
- **WHEN** `--last-period` is a date after today
- **THEN** the system stops and prints an error saying the date is invalid

### Requirement: Cycle length required with validated range
`--cycle-length` SHALL be required with no default value. It SHALL be validated as an integer from 21 to 38 days inclusive; a value outside that range SHALL be rejected with an error stating the supported range (21–38).

#### Scenario: Cycle length omitted
- **WHEN** `--cycle-length` is not provided
- **THEN** the system stops and prints an error that `--cycle-length` is required

#### Scenario: Cycle length below supported range
- **WHEN** `--cycle-length` is 20 or fewer days
- **THEN** the system rejects the input with an error stating the supported range is 21–38 days

#### Scenario: Cycle length above supported range
- **WHEN** `--cycle-length` is 39 or more days
- **THEN** the system rejects the input with an error stating the supported range is 21–38 days

#### Scenario: Boundary values accepted
- **WHEN** `--cycle-length` is 21 or 38
- **THEN** the system accepts the input and proceeds

### Requirement: Cycle day calculation
Given a valid `--last-period` and `--cycle-length`, the system SHALL calculate the current cycle day as `elapsed + 1`, where `elapsed = (today − last_period).days`, with no modulo — every accepted `--last-period` lies within the current cycle or its late-period grace window, so the day never wraps into a new cycle.

#### Scenario: Last period is today
- **WHEN** `--last-period` equals today's date
- **THEN** the system reports cycle day 1

#### Scenario: Day past the cycle length is not wrapped
- **WHEN** cycle length is 28 and `--last-period` was 31 days ago
- **THEN** the system reports cycle day 32, not day 4

### Requirement: Late-period grace window
If `cycle_length ≤ elapsed < cycle_length + 7`, the system SHALL treat the day as a late-period grace day: the phase SHALL be Luteal (forced, not recomputed from the boundaries) and the run SHALL be flagged as possibly late. If `elapsed ≥ cycle_length + 7`, the system SHALL reject the input with an error naming the 7-day grace limit, since more than 7 days of variation is an irregular cycle, which is out of scope.

#### Scenario: Inside the grace window
- **WHEN** cycle length is 28 and `--last-period` was 30 days ago
- **THEN** the system reports cycle day 31, the Luteal phase, and flags that the period may be late

#### Scenario: Past the grace window
- **WHEN** cycle length is 28 and `--last-period` was 35 days ago
- **THEN** the system stops with an error naming the 7-day grace limit, and produces no output

### Requirement: Phase boundaries
The system SHALL determine the active phase from the cycle day using fixed boundaries: Menstrual is days 1–5; the Ovulatory window is `ovulation_day − 1` to `ovulation_day + 1` where `ovulation_day = cycle_length − 14`; Follicular is day 6 through `ovulation_day − 2`; Luteal is `ovulation_day + 2` through the last day of the cycle.

#### Scenario: 28-day cycle, day 15
- **WHEN** cycle length is 28 and the current cycle day is 15
- **THEN** the system reports the Ovulatory phase (ovulation_day = 14, window = 13–15)

#### Scenario: 21-day cycle has no Follicular days
- **WHEN** cycle length is 21
- **THEN** Menstrual is days 1–5, Ovulatory is days 6–8, Luteal is days 9–21, and Follicular has zero days — the system does not error and every day 1–21 is assigned to exactly one phase

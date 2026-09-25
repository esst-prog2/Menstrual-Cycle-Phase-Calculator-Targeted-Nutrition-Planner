## 1. Setup

- [ ] 1.1 Create `plan.py` entry point with argument parsing for `--last-period`, `--cycle-length`, `--exclude` (repeatable), `--prefer-alternative`; verify `python plan.py --help` lists all four
- [ ] 1.2 Create empty `nutrition_rules.json` scaffold (phase → nutrient → candidate list shape) and verify it parses as valid JSON

## 2. Input validation and phase calculation (cycle-phase-calculation)

- [ ] 2.1 Implement strict `YYYY-MM-DD` parsing for `--last-period`, rejecting malformed input with a distinct error; verify with a test passing a non-ISO date
- [ ] 2.2 Implement future-date rejection for `--last-period`; verify with a test passing tomorrow's date
- [ ] 2.3 Make `--cycle-length` required with no default, validated to the 21–38 integer range, rejecting out-of-range values with an error stating the supported range; verify with tests for missing, 20, 39, and boundary values 21 and 38
- [ ] 2.4 Implement cycle-day calculation as `elapsed + 1` where `elapsed = (today − last_period).days` — no modulo; every accepted `--last-period` is always within the current cycle plus grace (see 2.7), never wrapping to a new one; verify with a test where `--last-period` is today (expect Day 1)
- [ ] 2.5 Implement phase-boundary calculation (Menstrual 1–5, Ovulatory `ovulation_day−1..+1` where `ovulation_day = cycle_length−14`, Follicular/Luteal filling the remainder); verify with a test for a 28-day cycle, day 15 → Ovulatory
- [ ] 2.6 Verify the 21-day cycle case specifically: Menstrual 1–5, Ovulatory 6–8, Luteal 9–21, zero Follicular days, no error and no day double-assigned (follow-up decided in PLANNING_LOG.md)
- [ ] 2.7 Implement the late-period grace window: for `cycle_length ≤ elapsed < cycle_length + 7`, force the phase to Luteal (not recomputed) and flag it as a grace-period day; for `elapsed ≥ cycle_length + 7`, reject with an error naming the 7-day grace limit; verify with tests for a day inside the grace window and a day just past it

## 3. Stub nutrition data

- [ ] 3.1 Author `nutrition_rules.json` with exactly 3 nutrients per phase (same 3 across all four phases) and at least 5 placeholder candidate foods per phase/nutrient slot; verify with a script/test asserting every slot meets both counts
- [ ] 3.2 Mark every stub entry as a placeholder (no evidence-strength field); verify no entry contains a Strong/Moderate/Weak/Speculative label
- [ ] 3.3 Add a minimal seasonal tag (Northern Hemisphere, also marked placeholder) to each stub ingredient; verify every entry has a season field
- [ ] 3.4 Tag every stub food entry with one or more categories from the fixed set (dairy, eggs, gluten, nuts, peanuts, soy, fish, shellfish, sesame, meat, pork — covering allergies and diet/religious exclusions); pork foods get both "meat" and "pork"; verify every entry has at least one tag from the set and every pork entry also carries "meat"

## 4. Nutrient selection (nutrient-selection)

- [ ] 4.1 Implement `resolve_candidates(candidates, exclusions, history, prefer_alternative)` as a pure function (no file I/O inside it); verify with unit tests that construct synthetic candidate lists directly, including a constraint tie-break case
- [ ] 4.2 Implement the constraint priority order (exclusions hard-filter first, then coverage, then no-repeat, then seasonality); verify with a test where an excluded food is never returned even when otherwise top-ranked
- [ ] 4.3 Implement single-candidate vs. multi-candidate output (no alternative note vs. alternative note with the real deciding reason); verify with tests for both cases, checking the alternative note's reason text matches the constraint that actually decided it
- [ ] 4.4 Implement `--prefer-alternative <nutrient>` swap, erroring clearly when the named nutrient has no alternative available; verify with a successful-swap test and a no-alternative-available test
- [ ] 4.5 Implement the empty-candidate-pool case (all candidates excluded for a nutrient): continue with other nutrients, mark the slot as having no suitable food; verify with a test excluding every candidate for one nutrient
- [ ] 4.6 Implement a load-time check on `nutrition_rules.json`: warn in the terminal for any phase/nutrient slot with fewer than 5 candidates, but keep running; verify with a test using a deliberately thin slot (fewer than 5) and confirming the tool still produces output (resolves the open question in design.md)

## 5. Rotation and history (rotation-history)

- [ ] 5.1 Implement `history.json` read/write with the `{phase: {nutrient: [{cycle_start, food}, ...]}}` shape, capped at 2 entries per slot; verify with a round-trip read/write test
- [ ] 5.2 Implement same-cycle detection (compare most recent entry's `cycle_start` to this run's `--last-period`) and cached-pick reuse; verify with a test running twice with identical arguments and asserting identical output with no history change
- [ ] 5.3 Implement same-cycle recompute-and-update-in-place when `--exclude` or `--prefer-alternative` invalidates the cached pick; verify with a test that re-runs mid-cycle with a new exclusion removing the cached food, asserting the exclusion is honored and only one entry exists for that cycle
- [ ] 5.4 Implement the 2-distinct-cycles no-repeat check and the forced-repeat fallback when the pool is too small; verify with tests for both the avoided-repeat and forced-repeat cases
- [ ] 5.5 Implement missing-`history.json` handling (treat as empty, create on first write, no error); verify with a test run against a directory with no history file
- [ ] 5.6 Implement corrupt-`history.json` handling (back up to `history.json.bak`, reset to empty, terminal-only warning, no crash); verify with a test using a deliberately malformed history file
- [ ] 5.7 Verify `--prefer-alternative` persistence across runs: run once with `--prefer-alternative <nutrient>`, then run again in the same cycle without the flag, and confirm the swapped food is still shown (follow-up decided in PLANNING_LOG.md)

## 6. Output (cli-output)

- [ ] 6.1 Implement `nutrients.md` generation listing the current phase's nutrient-food pairs; verify the file is written and contains all 3 nutrients for the phase
- [ ] 6.2 Implement placeholder labeling and the one-time stub-data disclaimer in both terminal and `nutrients.md`; verify both surfaces show it
- [ ] 6.3 Implement the repeat-fallback note in both terminal and `nutrients.md`; verify with the forced-repeat test from 5.4
- [ ] 6.4 Implement the alternative note (with dynamic reason) in both terminal and `nutrients.md`; verify with the multi-candidate test from 4.3
- [ ] 6.5 Implement the "no suitable food" note in both terminal and `nutrients.md`; verify with the empty-pool test from 4.5
- [ ] 6.6 Implement the `history.json`-unreadable warning as terminal-only; verify `nutrients.md` contains no mention of it in the corrupt-history test from 5.6
- [ ] 6.7 Implement the late-period grace-window note ("period may be late") in both terminal and `nutrients.md`; verify with the grace-window test from 2.7
- [ ] 6.8 Implement `--exclude` category matching (against the set defined in 3.4) and reject an unknown category with an error listing the valid categories; verify with a test passing an unknown value like "diary" and a test confirming a valid category excludes correctly

## 7. Repo hygiene

- [ ] 7.1 Confirm `.gitignore` covers `history.json` and `history.json.bak` (already added) and verify neither is tracked by `git status` after a test run

## 8. End-to-end verification

- [ ] 8.1 Run the full README Section 1 demo command and manually verify the terminal output and `nutrients.md` match the documented behavior
- [ ] 8.2 Run the full test suite and verify all tests from sections 2–6 pass together, not just in isolation

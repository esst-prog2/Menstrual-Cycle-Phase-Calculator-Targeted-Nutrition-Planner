# Code reviews (Homework 6)

The whole repo is reviewed one topic at a time, with each review in its own commit.
Each entry records what we looked for, what we found and what we did.

## Review 1: tests

**Date:** 2026-10-14
**Scope:** `tests/test_plan.py` (65 tests)

### What we looked for

1. For each test: could a person work out the expected value by hand from the spec,
   `EVIDENCE.md` or the data? Or does it look copied from running the code?
2. Which tests are unit tests with invented data, and which run the whole program with
   the real `nutrition_rules.json`?

### What we found

**Kinds of test.** Only `test_help_lists_all_flags` starts `plan.py` as a separate
process. Every other "whole program" test calls `plan.main()` in-process, in a temp folder
holding a copy of the real rules file. The same code path runs either way.

| Kind | Count | Where |
|---|---|---|
| Unit, invented data | 23 | `TestCycleMath`, `TestResolveCandidates`, `TestHistory.test_round_trip` |
| End-to-end, real `nutrition_rules.json` | 24 | `TestInputValidation` (except the missing-length case), `TestCycleEndToEnd`, most of `TestSelectionEndToEnd`, `TestHistory` and `TestOutput`, plus the `--help` subprocess test |
| End-to-end, stops before the rules are read | 1 | `test_cycle_length_required` |
| End-to-end, invented rules (`use_rules`) | 8 | thin slot, all excluded, same-cycle recompute, forced repeat, missing tier, sourced tier without source, tier when excluded, alternative note |
| Data checks, no program run | 9 | `TestSetup` rules shape, `TestStubData`, `TestEvidenceTiers`, `TestGitignore` |

**Where the expected values come from.** In every test, a person could work out by hand
which food, phase, day or error is expected. We found no test whose expected result could
only have come from running the code. The strongest tests are:

- the cycle-math tests (leap year, month boundary and grace window, each worked out in
  the test);
- `TestEvidenceTiers`, which we checked line by line against `EVIDENCE.md`, lines 18–39.

There were four problems:

1. **One test covers a code path the real data never reaches.**
   `test_strong_evidence_outranks_new_and_in_season` ranks foods by a per-food `evidence`
   label. Stub foods never carry one (spec, and the comment at `plan.py:29`). So with the
   real data, the "nutrient coverage" constraint never changes the ranking. This was
   deliberate when it was decided (PLANNING_LOG, 2026-09-24: "tested via synthetic in-code
   fixtures"). Since then, evidence tiers have moved to per-claim, so the per-food path
   may now be spec drift or dead code.
2. **Circular expected phase.** `test_every_suggestion_states_its_evidence_tier_in_both`
   worked out its expected phase with `plan.phase_for_day()`, the code under test.
3. **Expected values taken from the code's own constants.** The tests used
   `plan.NUTRIENTS_PER_PHASE`, `plan.MIN_CANDIDATES`, `plan.CATEGORIES` and
   `plan.DISCLAIMER` as expected values. If one of those constants were changed, the
   tests would still pass.
4. **Exact output wording the spec doesn't define.** About 8 assertions check exact
   output text that the spec does not spell out. Examples are the reason strings
   (`"in season, but repeats a recent pick"`, `"out of season"`), `(none)`, the full
   `chosen over … ; swap with --prefer-alternative …` note and the table format.

Smaller notes, not acted on:

- `test_rerun_with_new_exclusion_updates_in_place` expects `salmon` only because it is
  first in the JSON list. Reordering the data would break the test.
- `test_cycle_length_out_of_range` checks for `21-38` with a hyphen; the spec writes
  `21–38` with an en dash.
- `test_valid_exclude_removes_category_everywhere` checks that `FISH` in capitals is
  accepted, which the spec doesn't mention.
- `TestGitignore` inherits `Workspace` and makes a temp folder it never uses.

### What we did

- **Finding 2, fixed.** The expected phases are now written in the test:
  elapsed 0/8/14/20 → Menstrual/Follicular/Ovulatory/Luteal (days 1/9/15/21 of a
  28-day cycle).
- **Finding 3, fixed.** The tests now use the literal values the user decided: 3 nutrients
  per phase and at least 5 candidates per slot (PLANNING_LOG, 2026-09-24), and the
  11 categories (PLANNING_LOG, 2026-09-25). They are defined at the top of the test file
  as `CATEGORIES` and `DISCLAIMER`.
  The disclaimer sentence is copied from the current output. It appears in the logged
  real runs, but PLANNING_LOG has no line recording a decision on its exact wording.
- **Finding 4, kept as is.** The note wording is the user's decision in `design.md`
  ("Note wording is templated, with one dynamic field"). So these assertions check
  decided wording, not text copied from running the code.
- **Finding 1, deferred.** No change now. To check in the spec-drift and dead-code
  reviews.

**Check after the fixes.** All 65 tests pass. In a throwaway copy, we changed each
constant in `plan.py`:

| Constant changed | Result |
|---|---|
| `DISCLAIMER` | 1 test failed |
| `NUTRIENTS_PER_PHASE` | all passed |
| `MIN_CANDIDATES` | all passed |
| `CATEGORIES` (an extra category added) | all passed |

The tests now check the data against the decided values, but they still don't check the
code's own constants. To pick up in later reviews:

- `NUTRIENTS_PER_PHASE` is defined but never used in `plan.py` (dead-code review).
- No test checks that `MIN_CANDIDATES` triggers the thin-slot warning at exactly 5.
- No test checks that `--exclude` rejects a category outside the 11.

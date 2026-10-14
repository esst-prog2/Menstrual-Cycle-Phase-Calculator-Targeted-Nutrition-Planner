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

## Review 2: spec drift

**Date:** 2026-10-14
**Scope:** `plan.py` compared with the four specs in `openspec/specs/`, plus the two items
deferred from Review 1 (the per-food evidence ranking and `NUTRIENTS_PER_PHASE`).

### What we looked for

- **(a)** Things the code does that no spec requirement describes.
- **(b)** Spec requirements the code doesn't implement, or implements differently.

Each "differs from spec" item was confirmed by running it in a throwaway folder.

### What we found

**(a) In the code, not in any spec**

| # | Finding |
|---|---|
| a1 | Foods were ranked first by a per-food `evidence` label. The spec forbids that label on stub foods, so the step never did anything with the real data. If someone added the label, it changed the ranking silently (confirmed: flaxseeds beat salmon). It also produced a confusing `weaker evidence (unlabelled)` note. |
| a2 | `NUTRIENTS_PER_PHASE` was defined but never used. |
| a3 | The season is the Northern Hemisphere meteorological season from today's month. The rule existed only in PLANNING_LOG. |
| a4 | The disclaimer banner in both outputs. The spec only asked for a `[placeholder]` label on each food. |
| a5 | A fifth note type, "swapped in with --prefer-alternative, instead of X". The spec listed four. |
| a6 | A swapped food that is later excluded is worked out again, and the swap is dropped. |
| a7 | An error when `--prefer-alternative` names a nutrient not tracked in this phase. |
| a8 | `--exclude` matches categories regardless of capital letters. |
| a9 | Two wordings of the repeat reason. Already covered by design.md; no action needed. |

**(b) In the spec, missing or different in the code**

| # | Finding |
|---|---|
| b1 | Constraint 2, "nutrient coverage", did nothing with the real data (the same problem as a1). |
| b2 | "Exactly 3 nutrients per phase" wasn't checked by the code. A rules file with 2 nutrients ran silently. |
| b3 | A same-cycle re-run worked out the pick again instead of reusing the saved one. Confirmed: on Nov 30 Fiber was pears; on Dec 1 (winter) it became oats, and the history entry was overwritten. |
| b4 | After a swap, a forced repeat got no repeat note. |
| b5 | The spec said a slot "SHALL contain at least 5" candidates. The code warns, as decided on 2026-09-25, so the spec was out of date. |
| b6 | A second corrupt history file overwrote the first `history.json.bak`. |
| b7 | design.md wrote the alternative note with an em dash; the code and tests use a hyphen. |

### What we did

All of these decisions are the user's unless marked otherwise. Every decision is logged
in PLANNING_LOG.md under 2026-10-14.

**Fixed in code, each with a new test.** Every new test fails against the old `plan.py`.

| Finding | Change | New test |
|---|---|---|
| b3 | `plan_slot` now reuses this cycle's saved pick, swapped or not, while the food is still allowed. | `test_same_cycle_rerun_keeps_pick_when_season_changes` |
| b4 | `resolve_candidates` sets `forced_repeat` on the swap path, and a kept swap carries the flag too. | `test_forced_repeat_flagged_after_swap` and `test_forced_repeat_note_after_swap_in_both_outputs` |
| b6 | Backups are named `history.json.YYYY-MM-DD.bak`, and never overwrite an earlier one (`-2`, `-3`, … on the same day). `.gitignore` now uses `history.json*.bak`. | `test_second_corruption_keeps_earlier_backups` |

The backup name format is Claude's decision.

When a reused saved pick would no longer rank first, it is shown with no "chosen over"
note. That is Claude's decision.

**a1/b1, evidence ranking removed.** We removed the per-food evidence ranking, its test and
the `weaker evidence` note. Within a slot, the ranking is now no repeat, then season. The
nutrient-selection spec is updated to match. Logged as future work, the user's idea: once
real per-food data exists, rank foods by evidence or by how rich they are in the nutrient.
In place of the removed test, `test_food_evidence_label_does_not_change_ranking` guards the
removal (Claude's decision).

**a2/b2, nutrient-count warning.** `load_rules` now warns in the terminal if a phase
doesn't have exactly `NUTRIENTS_PER_PHASE` (3) nutrients, and keeps running. New test:
`test_wrong_nutrient_count_warns_but_runs`.

**b5.** The rotation-history spec now says fewer than 5 candidates gives a warning, not a
failure.

**b7.** design.md now uses the plain hyphen.

**a3–a8, added to the specs.** The code is unchanged; the specs now describe it.

| Spec | Added |
|---|---|
| nutrient-selection | How the season is decided; what happens when a swapped food is later excluded |
| cli-output | The disclaimer, with its exact wording; the swap note; case-insensitive matching; the error for a nutrient not tracked this phase |
| rotation-history | The repeat note after a swap; the season-change re-run; dated backups |
| cli-output (`.gitignore` requirement) | Dated backup names |

`openspec validate --specs` passes, 4 of 4.

**Planning log.** Besides the Review 2 decisions, a line from just before this review
records the disclaimer wording as the user's decision. Review 1 had found it was never
logged.

**Result.** All 70 tests pass (65 before; 1 removed, 6 added).

**Left open:**

- ~~README.md §7 "Constraint priorities" still lists nutrient coverage, with Strong evidence
  protected over Weak. It now disagrees with the spec and the code.~~ **Resolved** in a
  separate commit, "Review 2 follow-up: README §7": within a slot, no repeat, then season;
  evidence-based food ranking is future work.
- `EVIDENCE_RANK` is now used only for its tier names; its numeric ranks are unused. For
  the dead-code review.

## Review 3: names not in the spec

**Date:** 2026-10-14
**Scope:** every function, parameter, constant and concept in `plan.py`.

### What we looked for

Names that don't come from the specs, design.md or PLANNING_LOG.md. For each one: what it
does, where it came from, and whether other code depends on it.

A name counted as traceable when its idea is named in those documents, even if the
identifier itself is new (for example `HISTORY_ENTRIES` for "at most 3 entries", or
`item_notes` for "item-level notes"). About 35 names passed on that basis.

### What we found

All of the names below were invented while writing the code, with no decision recorded.
Most come from the v1 build (`de73012`); `NO_SOURCE` comes from `66d10a3`.

| # | Name | What it does | Who depends on it |
|---|---|---|---|
| 1 | `EVIDENCE_RANK` | Tier names mapped to the numbers 3/2/1/0. Since Review 2 the numbers are unused. | `load_rules`; 3 tests |
| 2 | `NO_SOURCE` | The text "no supporting source found". The spec only says "none was found". | `evidence_detail`; 1 test used it as its expected value (circular) |
| 3 | `InputError` | The exception for any user or data problem; `main` turns it into an error exit. | 7 places that raise it; 1 test |
| 4 | `NoAlternativeError` | Raised when `--prefer-alternative` has nothing to swap to. Its two messages reach the user. | `resolve_candidates` → `main`; 1 test |
| 5 | `Suggestion` | Bundles a nutrient, its `Resolution` and its evidence claim. | Renderers and label functions |
| 6 | `plan_slot` | Works out one slot against its history (Review 2's b3 fix). | `main` only |
| 7 | `new_entries`, `phase_history` | Locals. `None` means "leave history unchanged", which isn't written down. | `main` ↔ `plan_slot` |
| 8 | `_rank_key` | The sort key. `_deciding_reason` read it by position (`[0]`, `[1]`). | `resolve_candidates`, `_deciding_reason` |
| 9 | `runner_up`, `top` | Locals. The spec says "top-ranked" and "next-best alternative". | Local only |
| 10 | `season_for` | Month to season. The behaviour is in the spec since Review 2; the name isn't. | `main` |
| 11 | `food_label`, `evidence_label`, `evidence_detail` | Formatting helpers, including the `(none)` text. | Both renderers |
| 12 | `render_terminal`, `render_markdown` | Build the two outputs, with headers no document defines. | `main` |
| 13 | `build_parser` | Sets up the argument parser. | `main` |
| 14 | `warn` | A callback that `load_rules` and `load_history` print warnings with. | `main`; 2 tests |
| 15 | `main(today, workdir, out, err)` | Test hooks. | All end-to-end tests |
| 16 | `main(rules_path=…)` | Overrides where the rules file is read from. Nothing passes it. | None |
| 17 | `HERE` | The default `workdir`. It means the output files are always written next to `plan.py`, which no spec stated. | `main`'s default |
| 18 | Empty Follicular stored as first day > last day | How a zero-day phase is represented. | `phase_for_day`; 1 test |

### What we did

All of these decisions are the user's unless marked otherwise. Every decision is logged
in PLANNING_LOG.md under 2026-10-14.

- **#17, file location added to the spec.** The cli-output spec has a new requirement,
  "Files live next to the script". It matches the README demo ("Next to the script").
  Confirmed by running a copy of `plan.py` from another folder: both output files were
  written next to the script, and nothing was written to the working folder.
  `openspec validate --specs` passes, 4 of 4.
- **#2, #4, #12, wording accepted and logged.** The user accepted the current wording as
  their decision: `NO_SOURCE`, the two `NoAlternativeError` messages and the output
  headers. The test that used `plan.NO_SOURCE` now uses the literal text. Confirmed by
  changing the wording in a throwaway copy: that test fails.
- **#8, rank key fields named.** `_rank_key` now returns a `RankKey(repeats,
  out_of_season)` NamedTuple, and `_deciding_reason` compares the parts by name. A
  NamedTuple sorts like a plain tuple, so the ranking is unchanged (Claude's choice of
  NamedTuple). No test changed.
- **#1 and #16, deferred.** Left for the dead-code review.
- **#3, #5–#7, #9–#11, #13–#15 and #18, no change.** Accepted as normal implementation
  names.

**Result.** All 70 tests pass.

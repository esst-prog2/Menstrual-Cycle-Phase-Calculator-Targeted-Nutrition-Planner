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

## Review 4: patched where it broke, not where it's wrong

**Date:** 2026-10-14
**Scope:** git history on `main`, `hw4-spike`, `hw5-usable` and `hw6-review`, plus `plan.py`.

### What we looked for

- **Chains of commits that fix the same area again and again.** For each chain: what was
  the original assumption, what did each fix patch, and can the actual rule now be stated
  in one sentence that matches the spec?
- **Special cases stacked on top of each other in the code.**

### What we found

There are 19 commits. Only 4 touch `plan.py`, and there are no "fix:" commits: each round
of patching was folded into one large commit (`5a077d0`, `de73012`). Git alone can't show
the chains, so **PLANNING_LOG is the real trail.** It has 9 lines that say "replaces",
"revised", "corrected" or "retired".

Side note: local `main` was at `de73012`, behind `origin/main` (`dc81853`). Pull it
before merging.

#### Chain 1: Rotation and the no-repeat rule

- **Original assumption** (README, 2026-09-12): a whole grocery list of K items is drawn
  from one shared pool per phase, and two lists may share at most N items, with N worked
  out from P and K.
- **What each fix patched:**
  1. N formula decided, plus a "validate P ≥ K" follow-up.
  2. The formula replaced by a per-slot version (K=1).
  3. ≥5 candidates per slot; window "2–3", then 2; the P ≥ K follow-up retired.
  4. History cap raised from 2 to 3 in the build, so recomputing within a cycle still sees
     both earlier cycles.
  5. Review 2 (b4): repeat note missing after a swap.
- **One sentence:** "For each nutrient, never show a food used for that nutrient in either
  of the previous 2 cycles, unless every allowed candidate was. Then repeat one and say so."
- **Matches the spec?** Yes: "No-repeat window" plus "Repeat fallback note".

#### Chain 2: Re-runs within the same cycle and `--prefer-alternative`

- **Original assumption** (`tasks.md` 5.2 and the spec): a same-cycle re-run reuses the
  saved pick unless `--exclude` or `--prefer-alternative` makes it invalid.
- **What each fix patched:**
  1. The build implemented reuse only for swaps, by adding the `swapped` field.
  2. Review 2 (b3): the gap showed up when the season changed.
  3. Review 2 (b4): the forced-repeat flag had to be passed into each hand-built result.
- **One sentence:** "Within a cycle, keep the saved pick while its food is still allowed.
  Otherwise pick again and replace that cycle's entry."
- **Matches the spec?** Yes. The code was the most stacked part of the repo (special case A).

#### Chain 3: Cycle day and late periods

- **Original assumption** (early `tasks.md` 2.4): the cycle day was worked out with a
  modulo, so a late date silently wrapped into a new cycle.
- **What each fix patched:**
  1. 2026-09-25: day = elapsed + 1, a 7-day grace window, rejection after that.
  2. Specs, design and proposal revised with `/opsx:update` to match the build.
- **One sentence:** "Cycle day = days since the last period + 1. Days past the cycle
  length, up to 6 more, are Luteal and flagged as possibly late; anything later is
  rejected."
- **Matches the spec?** Yes. The code split the rule across two functions (special case C).

#### Chain 4: Evidence

- **Original assumption** (README §4 and §7): each rule or food carries an evidence
  strength, and Strong is protected over Weak when ranking.
- **What each fix patched:**
  1. 2026-09-24: no labels on stub foods; Strong-over-Weak tested only with made-up data.
  2. The build still added per-food ranking code.
  3. 2026-10-08: per-claim tiers, which "replace" two earlier decisions, but only for the
     claim.
  4. Review 2 removed the per-food ranking; the README §7 follow-up updated the docs.
- **One sentence:** "Evidence belongs to the phase-nutrient claim: it is checked when the
  rules file loads and shown with every nutrient, and it never affects which food is
  chosen."
- **Matches the spec?** Yes. What's left: `EVIDENCE_RANK`'s unused numbers (dead-code
  review) and the open Ovulatory Fiber gap.

#### Smaller chains

Each one is now one clear rule that matches the spec:

- **Gitignored files:** `history.json` and `.bak` → `nutrients.md` → dated backups.
- **Category tags:** "one or more" → "may be empty".
- **Nutrients per phase:** "same 3" → "each phase its own 3" → load-time warning.
- **Scope:** groceries → nutrients. This also started Chain 1.

#### Special cases stacked in the code

- **A. `plan_slot` had five ways out for one rule.**
  - The forced-repeat flag was copied into hand-built results in 3 places.
  - The exclusion filter was a second copy of `resolve_candidates`'s.
  - Two branches existed only because `_deciding_reason` assumes the winner ranks at
    least as well as the loser.
- **B. Two edge cases in the swap note.**
  - "Instead of X" named whatever ranked first now, which might not be the food swapped
    away from.
  - If the ranking later agreed with the swap, no swap note was shown, although history
    said `swapped: true`.
- **C. The grace rule was split across two functions.** `cycle_day` used
  `elapsed >= cycle_length`; `phase_for_day` used `day > cycle_length`.
- **Not a stack:** `resolve_candidates`'s exits each match one spec requirement.

### What we did

All of these decisions are the user's unless marked otherwise. Every decision is logged
in PLANNING_LOG.md under 2026-10-14.

- **A, `plan_slot` rewritten to the one-sentence rule from Chain 2.** It now has one call
  to `resolve_candidates`, with this cycle's saved pick passed as the new optional `keep`
  argument, then two plain exits: keep the saved pick, or record the new one.
  `resolve_candidates` builds a single `Resolution`. The forced-repeat flag is worked out
  once ("every allowed candidate was used recently"), and the exclusion filter exists only
  there. The `keep` argument is Claude's design; design.md's signature is updated to match.
- **C, grace rule in one place.** `is_late(day, cycle_length)` is used by both
  `cycle_day` and `phase_for_day`. `cycle_day`'s rejection check is now written in terms
  of the same `day`.
- **B, swap note simplified.** The note is now "swapped in with --prefer-alternative",
  with no food named, and it is always shown when history says `swapped: true`. The
  cli-output and nutrient-selection specs are updated to match. There is a new test for
  each edge case: `test_swap_note_kept_when_ranking_later_agrees` and
  `test_swap_note_does_not_name_another_food`. Both fail against the old `plan.py`.
- **No other behaviour change.** All 70 existing tests pass unchanged, both before and
  after the rewrite. Old and new `plan.py` were also compared on 7,485 random runs, with
  random rules, exclusions, swaps and dates. With the swap-note text removed, the terminal
  output, `nutrients.md` and `history.json` were identical in every run (Claude's check).

**Result.** All 72 tests pass. `openspec validate --specs` passes, 4 of 4.

## Review 5: a copy instead of a change

**Date:** 2026-10-14
**Scope:** `plan.py`, `tests/test_plan.py`, `nutrition_rules.json`, README.md,
EVIDENCE.md and `openspec/`.

### What we looked for

Units that do almost the same job under different names, and the same fact kept in two
places where the copies could drift apart. For each: where the copies are, how different
they are now, and which one should stay.

### What we found

**Group 1: the same fact in code, data and docs**

| # | Fact | Copies | State before this review |
|---|---|---|---|
| 1 | Phases | `PHASES`, `phase_ranges()` keys, JSON keys, spec | `plan.py` never used `PHASES`. A rules file without a phase crashed with a `KeyError`. |
| 2 | Season names | `season_for()`, JSON, spec, tests | Never checked. A food tagged `"Autumn"` was silently always out of season. |
| 3 | Categories | `CATEGORIES`, JSON, spec, log, tests | The data was never checked against the list. A food tagged `"diary"` would silently escape `--exclude dairy`. |
| 4 | Nutrients per phase | JSON `phases` and `evidence` | Checked in one direction only; an extra nutrient in `evidence` was ignored. |
| 5 | Tiers and sources | EVIDENCE.md (two tables), README count table, JSON, tests, spec, log | All 12 rows matched. README's table was an unchecked third copy. |
| 6 | "This data is a placeholder" | 60 × `placeholder` and `seasons_placeholder` flags, JSON `notice`, `DISCLAIMER`, the `[placeholder]` label | The code ignored the flags and labelled every food. |
| 7 | Foods in several slots | 10 foods, each with its own copy of tags and seasons | Consistent, but not checked. |
| 8 | "2 cycles" | `NO_REPEAT_CYCLES` and the literal in `REPEAT_NOTE` | Same, written twice. |
| 9 | Decided wording | Spec, code and test literals | Deliberate (Reviews 2–4). |
| 10 | Archived change vs main specs | `openspec/changes/archive/…` and `openspec/specs/` | The archive is a snapshot, but its design.md was edited in Reviews 2 and 4. |
| 11 | Tier definitions | README §4 and EVIDENCE.md | Same meaning, different words. |

**Group 2: near-duplicates in `plan.py`**

- **#12:** `render_terminal` and `render_markdown`.
- **#13:** `evidence_label` and `evidence_detail`.
- **#14:** the "is this food a repeat?" check, done both in the rank key and in the
  forced-repeat line.

**Group 3: test helpers**

- **#15:** `OVULATORY` defined twice.
- **#16:** the slot-A rules pattern written out 6 times, plus `use_season_rules`.
- **#17:** the real rules file read in 5 places.
- **#18:** three ways of finding a nutrient's line in the output.
- **#19:** data-flattening one-liners.
- **#20:** a test that rebuilt the workspace inline.

**Group 4: deliberate copies.** The tests' literal decided values and `SPIKE_TIERS`
(Reviews 1 and 3).

### What we did

All of these decisions are the user's unless marked otherwise. Every decision is logged
in PLANNING_LOG.md under 2026-10-14.

- **#1–#4, load-time checks.** `load_rules` now stops, before any file is written, with
  an error naming the problem when:
  - `phases` or `evidence` doesn't have exactly the four phases;
  - a nutrient has a tier but no foods (the other direction was already checked);
  - a food has a category or season outside the code's lists.

  `PHASES` is now used by `plan.py`. A new `SEASONS` constant feeds both `season_for()`
  and the check (Claude's design; the month mapping was checked for all 12 months).
  There is a new test for each check: missing phase, unknown phase, evidence nutrient
  without foods, unknown season, and a category typo used together with `--exclude dairy`.
  The new nutrient-selection requirement is "Rules file checked against the code's lists".
- **#6, placeholder label from the flag.** `[placeholder]` is shown only when a food has
  `"placeholder": true`. New test: `test_placeholder_label_follows_the_flag`. The spec
  is updated.
- **#7, consistency test.** `test_food_in_several_slots_has_same_tags_everywhere` is a
  data test, so it passes on the old code too.
- **#8 and #14.** `REPEAT_NOTE` is built from `NO_REPEAT_CYCLES`, with the same text as
  before. The forced-repeat flag now reads the top candidate's rank key: repeats rank
  last, so the top repeats only when every allowed candidate does.
- **#5 and #11, README links.** README's copied count table and tier definitions are
  replaced by links to EVIDENCE.md, at `#summary` and `#how-claims-were-graded`.
- **#10, archive frozen.** From now on, `openspec/changes/archive/` is frozen. **Record:**
  the archived `design.md` was edited twice before this decision:
  - Review 2: the alternative-note template switched from an em dash to a hyphen;
  - Review 4: the `resolve_candidates` signature gained `keep=None`.

  No other archived file was changed.
- **#15–#18 and #20, test helpers tidied.** One module-level `OVULATORY`, `real_rules()`,
  `nutrient_lines()` and `markdown_row()`, `Workspace.use_slot_a()` (replacing 5 inline
  copies and `use_season_rules`) and `Workspace.reset()`.

  **Check:** the old and tidied test files were run against the same 12 deliberately
  broken copies of `plan.py`. Each copy was caught by exactly the same tests (Claude's
  check).
- **Kept as they are:** #9, #12, #13, #19 and group 4.

**New tests fail on the old code.** 6 of the 7 new tests fail against the old `plan.py`;
the seventh is the #7 data test.

**Result.** All 79 tests pass. `openspec validate --specs` passes, 4 of 4.

**Left open, then closed in "Review 5 follow-up":**

- `PHASES` and the keys of `phase_ranges()` were two lists in the code. **Closed:** `PHASES`
  is now derived from `phase_ranges()`, which is the phase rule.
- Tests compared against `plan.REPEAT_NOTE`, `NO_FOOD_NOTE` and `LATE_NOTE` instead of
  literal text, the circular pattern from Review 1. **Closed:** the tests now check the
  literal text, and the late-note tests check the full sentence instead of only "period may
  be late". Changing any of the three wordings in a throwaway copy makes a test fail.

  **Wording origin:** design.md contains no note text. Only `NO_FOOD_NOTE`'s wording is
  recorded as decided (PLANNING_LOG, 2026-09-25). The full repeat-note and late-note
  sentences are copied from the code and still need the user's confirmation.

## Review 6: errors that disappear

**Date:** 2026-10-14
**Scope:** `plan.py` and `tests/test_plan.py`.

### What we looked for

`except Exception`, bare `except:`, `except: pass`, `return None` or empty values after an
error, and errors caught and turned into a default. For each: what is caught, whether the
catch is narrower or broader than needed, and whether the user finds out. The deliberate
corrupt-history handling was checked to make sure it catches only what it should.

### What we found

There is no `except Exception`, no bare `except:` and no `except: pass` in `plan.py` or the
tests. All 5 `except` clauses are narrow:

| # | Where | What is caught | Notes |
|---|---|---|---|
| 1 | `parse_iso_date` | `ValueError` | Fine. |
| 2 | `parse_cycle_length` | `ValueError` | `int()` accepted `2_8` and `" 28 "` silently. |
| 3 | `load_history` | `JSONDecodeError`, `UnicodeDecodeError`, plus the shape check | Catches only parse failures, as intended. A history file that couldn't be opened crashed with a traceback. The cli-output spec said "unreadable or corrupt". |
| 4 | `main` | `NoAlternativeError` → `InputError` | Fine. |
| 5 | `main` | `InputError` → `parser.error` | Fine. |

The errors that really disappeared did so through **missing checks**, where bad data
quietly became a default. Each was confirmed by running it in a throwaway folder.

**Bad data turned into a default:**

| # | What happened |
|---|---|
| A1 | A `"placeholder"` value that wasn't exactly `true` silently dropped the `[placeholder]` label. |
| A2 | An empty slot in the data was blamed on the user's exclusions, in the note and in the `--prefer-alternative` error. |
| A3 | A non-boolean `"swapped"` in history counted as true. |
| A4 | A history food no longer in the data was kept silently. |
| A5 | `categories` written as a string gave the error "unknown categories d, a, i, r, y". |

**Loud but unhelpful (a traceback instead of a message):**

| # | What happened |
|---|---|
| B1 | A missing rules file crashed with `FileNotFoundError`. |
| B2 | A rules file that wasn't JSON crashed with `JSONDecodeError`. |
| B3 | Missing fields crashed with `KeyError`. |
| B4 | A history file that couldn't be opened crashed with `IsADirectoryError`. |

**Also found:** files were read and written in the system's default encoding, which is
not UTF-8 on every system.

### What we did

All of these decisions are the user's unless marked otherwise. Every decision is logged
in PLANNING_LOG.md under 2026-10-14. Each fix has a test. All 11 new tests fail against
the old `plan.py`.

| Finding | Change | Test |
|---|---|---|
| A1, A5, B3 | A shape and type check runs when the rules file loads: the file, `phases` and `evidence` must be objects; each food must be an object with a string `food`, list `categories`, list `seasons`, and a `placeholder` that is `true` or `false`. A missing `placeholder` also fails (Claude's reading). | `test_placeholder_must_be_true_or_false`, `test_categories_and_seasons_must_be_lists`, `test_missing_fields_are_named` |
| A2 | An empty slot shows "no foods for this nutrient in the data". `--prefer-alternative` fails with "there are no foods for this nutrient in the data". The exclusions note appears only when exclusions removed everything. | `test_empty_slot_in_data_is_not_blamed_on_exclusions` |
| A3 | `_valid_history` requires `swapped`, when present, to be `true` or `false`. Otherwise the file is backed up as corrupt. | `test_swapped_not_true_or_false_treated_as_corrupt` |
| B1, B2 | A new `read_json()` turns a missing file, an unreadable file, non-UTF-8 text or invalid JSON (with line and column) into one `InputError`. | `test_missing_rules_file`, `test_rules_file_not_json_or_not_utf8` |
| B4 | A `history.json` that can't be opened stops the run with a clear error. It is left unchanged and gets no backup, since a backup would fail too (Claude's choice). Parse errors are still backed up as before, with the same warning text. | `test_unopenable_history_stops_and_is_left_alone` |
| Write errors | Failing to write `nutrients.md` or `history.json` is one clear error. `nutrients.md` is now written **first**, so a run whose output fails doesn't advance the rotation (Claude's choice). | `test_unwritable_output_is_a_clear_error_and_rotation_does_not_advance` |
| `--cycle-length` | Digits 0–9 only. This rejects `2_8`, `" 28 "`, `+28`, and non-ASCII digits (the last one is Claude's addition). | `test_cycle_length_digits_only` |
| UTF-8 | Every file read and write in `plan.py` and the tests passes `encoding="utf-8"`. | `test_files_read_and_written_as_utf8` runs `plan.py` under a Latin-1 locale with an accented food name. It is skipped where no such locale exists. |
| Spec wording | cli-output's "unreadable or corrupt" now says "corrupt", with a definition. The new requirement "Data file problems are clear errors" covers opening and writing failures. | — |

Specs updated:

- **cli-output:** the new "Data file problems are clear errors" requirement, plus the
  no-foods-in-the-data note in the item-level notes.
- **rotation-history:** a precise definition of a corrupt file, including `swapped`, plus
  the case of a file that can't be opened.
- **nutrient-selection:** the empty slot in the data, and the type checks.
- **cycle-phase-calculation:** digits only for `--cycle-length`.

**Known limitation (A4, kept as is).** A history entry naming a food that is no longer in
`nutrition_rules.json` is kept and still counts as "recent", but matches nothing. Renaming
a food in the data therefore resets that food's rotation silently.

*Extended in Review 8:* the same applies one level up. History kept under a **nutrient**
name that is no longer in the data stays in `history.json` forever and is never read
again. Renaming a nutrient therefore resets the rotation for all of its foods silently.

**Result.** All 90 tests pass. `openspec validate --specs` passes, 4 of 4.

## Review 7: things nobody chose

**Date:** 2026-10-14
**Scope:** every import in `plan.py` and the tests, the tools the project relies on, and
dead code. This includes two items deferred from Review 3: `EVIDENCE_RANK`'s numbers and
the `rules_path` parameter.

### What we looked for

- **Dependencies:** for each one, does it exist, is it used, and is its version pinned
  anywhere?
- **Dead code:** functions, parameters, constants, branches or test helpers that nothing
  uses.

### What we found

**Imports.** All are standard library, and all are used. There are no third-party
packages and no requirements file, as decided on 2026-09-25.

**Tools:**

| Tool | Finding |
|---|---|
| Python | "3.10 or newer" was stated in README, but not pinned, checked or tested anywhere; only 3.14 had ever been run. macOS's `/usr/bin/python3` is 3.9.6, and there `plan.py` crashed with `TypeError: unsupported operand type(s) for \|`. |
| git | `TestGitignore` needs a git checkout. In a copy without `.git` (for example a zip download), it failed instead of skipping. |
| OpenSpec | 1.13.0, installed globally with npm; it needs Node. Not pinned anywhere: the version appeared only as `generatedBy` in the files under `.claude/`. README and AGENTS.md didn't mention it. |
| Node | v24.21.0 here, only as OpenSpec's runtime. Not pinned. |
| uv | Installed on this machine but not used by the project. |

**Dead code:**

| # | What | Finding |
|---|---|---|
| D1 | `EVIDENCE_RANK` | Its numbers 3/2/1/0 were unused; only its keys were. |
| D2 | `main(rules_path=…)` | Never passed by anything. |
| D3 | `plan_slot(nutrient)` | Never read inside the function. |
| D4 | `Resolution.alternative` on a swap | Set, but never read by the program since Review 4's swap note; only one test read it. |
| D5 | The last `raise` in `phase_for_day` | Can't happen through `main`. |
| D6 | The `{}` default in `evidence.get(phase, {})` | Unreachable since Review 5's phase check. |
| D7 | `"seasons_placeholder"` on all 60 foods | Never read by any code; only a test checked it. |
| D8 | Two `.gitkeep` files | Their folders have real content now. |
| D9 | `openspec/config.yaml` | Only `schema` was set; the rest was the untouched template, which nobody chose. |
| D10 | `TestGitignore` inherits `Workspace` | Made a temporary folder it never used (also noted in Review 1). |

### What we did

All of these decisions are the user's unless marked otherwise. Every decision is logged
in PLANNING_LOG.md under 2026-10-14.

- **Python version check.** `plan.py` checks `sys.version_info` right after `import sys`,
  before the other imports and the `dict | None` annotations. On anything older than
  3.10 it stops with "plan.py needs Python 3.10 or newer; this is Python 3.9." and exit
  code 1.
  - Checked for real with macOS's `/usr/bin/python3` 3.9.6.
  - New test: `test_python_older_than_3_10_stops_with_clear_message`. It fakes 3.9 in a
    subprocess (Claude's method).
- **`TestGitignore`.** It is skipped when the folder isn't a git checkout or git isn't
  installed, and it is now a plain `unittest.TestCase` (D10). Checked in a copy without
  `.git`: 1 skipped, 90 passed.
- **README.** It now says the specs were written with OpenSpec 1.13.0, which needs
  Node.js 20.19 or newer (OpenSpec's own requirement), and that OpenSpec is only needed
  for the spec workflow, not to run `plan.py` or its tests. The Requirements section also
  describes the startup check, names the test command, and drops a stale line link into
  `plan.py` (Claude's additions).
- **Dead code removed:**
  - **D1:** `EVIDENCE_RANK` is now `EVIDENCE_TIERS`, the tier names only (the rename is
    Claude's).
  - **D2:** `main(rules_path=…)` removed.
  - **D3:** `plan_slot(nutrient)` removed.
  - **D4:** a swap no longer stores an alternative. `test_prefer_alternative_swaps` now
    checks that `alternative` is `None`.
  - **D6:** the unreachable default is gone; the code now reads `evidence[phase]`
    directly.
  - **D8:** both `.gitkeep` files deleted.
- **D5, kept as a guard.** It would only fire if the phase boundaries were broken.
- **D7, `seasons_placeholder` removed.** It is gone from all 60 foods in
  `nutrition_rules.json`; a script checked that nothing else in the data changed. It is
  also gone from the test helper `food()` and from `TestStubData`, where the test is
  renamed `test_every_entry_has_a_season`.

  This **replaces the 2026-09-24 decision** that every seasonal tag is also marked
  placeholder. Reason: each food's `placeholder` flag and its `[placeholder]` label
  already cover that food's seasons, and no code ever read the separate flag.
- **D9.** `openspec/config.yaml` now holds only `schema: spec-driven`.

**Result.** All 91 tests pass. `openspec validate --specs` passes, 4 of 4.

## Review 8: the quiet default

**Date:** 2026-10-14
**Scope:** every place in `plan.py` where a missing or empty value becomes a default:
`.get(key, default)`, `or` fallbacks, default parameter values and similar.

### What we looked for

For each default: what is it, what does it change downstream, and is a missing value
really normal there, or is it a bug that should be an error? Defaults already handled in
Reviews 5–7 were listed only briefly.

### What we found

26 places. Each new finding was confirmed by running it in a throwaway folder.

**New findings:**

| # | Finding |
|---|---|
| Q1 | A **missing** `"source"` passed the load check for a Speculative claim (`.get("source") is None`). The renderer then crashed with `KeyError: 'source'`, a traceback. |
| Q2 | An **empty** source (`""`) passed as "named", and was then shown as "Weak - no supporting source found": a line that contradicts itself. |
| Q3 | The source's **type** wasn't checked: `123` was shown as "Weak - 123". |
| Q4 | **Unknown keys** on foods and claims were ignored. That includes a per-food `"evidence"` label, which the spec forbids. |
| Q5 | `phase_history.get(nutrient, [])`: history kept under a **renamed nutrient** is never read again, and the nutrient's rotation starts over. This is A4 from Review 6, one level up. |
| Q6 | `main(out=sys.stdout, err=sys.stderr)` bound the streams when the module was loaded, so `contextlib.redirect_stdout` didn't capture the output. |

**Normal, no action.** These defaults all mean "nothing recorded yet" or "nothing
requested":

- a missing `history.json` → `{}`;
- `history.get(phase, {})`;
- `bool(entries)`;
- an optional `swapped` flag;
- `--exclude` defaulting to `[]`;
- no `--prefer-alternative`;
- `argv=None`;
- `today or date.today()`;
- `workdir=HERE`;
- `keep=None`;
- the `Resolution` field defaults;
- `_deciding_reason` returning `None` on a full tie;
- `or 'none'` in an error message.

**Already covered by Reviews 5–7:**

- The tier lookup and `claim.get("tier")`.
- The structure checks (`data.get(...)`, `c.get(...)`).
- The history entry checks.
- The `None` returned for an unparseable `history.json`.
- `names.get(...)` for `--prefer-alternative`.
- The removed `evidence.get(phase, {})` and `rules_path or …`.
- `res.chosen.get("placeholder") is True`: since Review 6 the flag is always a boolean,
  so the `.get` default could never be used.

### What we did

All of these decisions are the user's unless marked otherwise. Every decision is logged
in PLANNING_LOG.md under 2026-10-14.

- **Q1–Q3, one rule for the source, checked once at load.** `"source"` is required on
  every claim. It must be `null` for Speculative, and a non-empty string for Weak,
  Moderate and Strong; a whitespace-only source also counts as empty (Claude's choice).
  The renderer now uses the checked value directly: `None` means "no supporting source
  found", with no `or` fallback.

  New test: `test_source_rule`, with 5 cases: missing (Weak and Speculative), empty,
  blank, and not a string.
- **Q4, unknown keys are an error.** A food may only have `food`, `categories`, `seasons`
  and `placeholder` (`FOOD_KEYS`). A claim may only have `tier` and `source`
  (`CLAIM_KEYS`). Any other key stops the run with an error naming it, which enforces the
  spec rule "no evidence label on foods".

  New test: `test_unknown_key_on_food_or_claim`.
- **Q5, known limitation extended.** Review 6's A4 limitation now also covers renamed
  nutrients.
- **Q6.** `main(out=None, err=None)` resolves the streams when it is called. New test:
  `test_main_honours_redirected_stdout_and_stderr`.
- **Placeholder flag.** It is now read directly (`res.chosen["placeholder"]`).

The nutrient-selection spec is updated: "Evidence tier per nutrient" now states the
source rule and the allowed claim keys, and "Rules file checked against the code's
lists" covers unknown food keys.

**New tests fail on the old code.** All 3 new tests fail against the old `plan.py`.
`test_source_rule` fails in all 5 cases, one of them with the old `KeyError` crash.

**Result.** All 94 tests pass. `openspec validate --specs` passes, 4 of 4.

## Review 9: what should not be in git

**Date:** 2026-10-14
**Scope:** the whole git history on all branches, local and remote (`main`, `hw4-spike`,
`hw5-usable`, `hw6-review`), not only the current files.

### What we looked for

- **Files that should never have been committed:** `history.json`, any `.bak` backup,
  `nutrients.md`, `.env`, keys or tokens, large data files.
- **Personal data inside committed text:** real `--last-period` dates or cycle details
  from the user's own runs, in the log, the reviews, the tests, sample outputs or commit
  messages.
- **Anything else personal** beyond normal git author information.

This entry describes the personal data without repeating it.

### What we found

**Files: clean.**

- No personal file, `.env`, key, token or credential file was ever committed, in any
  commit on any branch.
- The largest blob ever stored is 45 KB.
- A search of every commit for secret-like strings found nothing.
- The user's real `history.json` and `nutrients.md` exist only locally, covered by
  `.gitignore`.

**Personal data in committed text:**

| # | What | Where | Since | In current files? |
|---|---|---|---|---|
| P1 | The user's real run: a written prediction stating the user's current cycle state, the real command with the real last-period date and cycle length, and the full terminal and `nutrients.md` output (cycle day and phase, run date). The date matched the user's local, ignored `history.json`. | PLANNING_LOG.md, the 2026-10-08 entries | Commit `fde555e`, merged into public `origin/main` by PR #4 | Yes, until this review |
| P2 | The commit message of `fde555e` names the phase of that real run. Together with its timestamp, it reveals the timing even without the file. | Commit message | `fde555e` | Only in history |
| P3 | A local folder path containing the user's macOS username, inside pasted test output | PLANNING_LOG.md, the 2026-10-08 mutation-check output | Commit `fb9b034`, also on `origin/main` | Yes, until this review |

The repository is public on GitHub (checked through the GitHub API, which needs no login:
`visibility: public`, 0 forks).

**Other personal data: clean.**

- Author information is normal: the user's name and email as the git author, plus
  GitHub-web commits.
- No email addresses or other names appear in any file, in any commit.
- Every other `--last-period` date in the repo is invented.

### What we did

All of these decisions are the user's. Every decision is logged in PLANNING_LOG.md under
2026-10-14.

- **P1 and P3 removed from the current PLANNING_LOG.md.**
  - The real-run entries (the prediction, the real command, the output and the
    "matched the prediction" line) are replaced by one note. It says a real run with a
    prediction was logged and matched, and that its details were removed on 2026-10-14
    for privacy.
  - The two "open gap" lines from the same day are kept; they hold no personal data.
  - The folder path in the mutation-check output is replaced by
    `[project folder, removed for privacy]`.
  - This is the one exception to the log's "never rewrite an earlier line" rule.
    Privacy overrides it here, and a new log line says so and why.
- **New rule at the top of AGENTS.md:** never write real personal data (real dates,
  cycle details, usernames, folder paths) into any committed file; use invented dates in
  examples.
- **History is not rewritten** (the user's decision). The removed details remain in
  earlier commits on every branch that contains `fde555e` or `fb9b034`, including public
  `origin/main` and PR #4's diff, and in `fde555e`'s commit message (P2). The user knows
  this and accepts it: removing the data from the current files is enough.

**Check.** After the change, a search of every file in the working tree finds none of the
removed data.

**Result.** No code changed. All 94 tests pass.

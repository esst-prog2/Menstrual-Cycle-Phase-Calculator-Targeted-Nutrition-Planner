## Context

Greenfield Python CLI — see `proposal.md` for motivation. The four capability specs (`cycle-phase-calculation`, `nutrient-selection`, `rotation-history`, `cli-output`) define required behavior; this covers the technical shape behind them where it isn't obvious from the specs alone.

## Goals / Non-Goals

**Goals:** a concrete, testable shape for phase math, candidate resolution, `history.json`'s structure, and note rendering.

**Non-Goals:** populating `nutrition_rules.json` with real, evidence-graded data; anything from the deferred Evidence Basis pipeline (`EVIDENCE.md`, citation sourcing/grading).

## Decisions

**`resolve_candidates()` is a pure function.** Signature `resolve_candidates(candidates, exclusions, recent_foods, prefer_alternative, season) -> Resolution` (chosen, alternative, deciding reason, forced-repeat and swapped flags). It never reads `nutrition_rules.json` or `history.json` itself — the caller loads data and passes it in. This lets tests construct small synthetic candidate lists directly (e.g. to exercise a constraint tie-break) without touching real data files, and keeps a test failure attributable to either the ranking logic or the data loading, never an ambiguous mix of both. Alternative considered: resolving candidates inline during data loading — rejected because it would force tests to fake entire data files to exercise one ranking branch, and it's incompatible with keeping the placeholder data honest (no fabricated evidence labels just to make a test pass).

**Ovulation day is `cycle_length − 14`, not proportional scaling or a fixed day 14.** Grounded in ACOG/NHS: the luteal phase (ovulation to next period) stays close to 14 days regardless of cycle length; the follicular phase absorbs the variation. Scaling day 14 proportionally to cycle length (e.g. `14/28 × cycle_length`) would be physiologically wrong — it assumes the wrong phase is the variable one.

**`history.json` shape:**
```json
{
  "<Phase>": {
    "<Nutrient>": [
      {"cycle_start": "YYYY-MM-DD", "food": "...", "swapped": true},
      {"cycle_start": "YYYY-MM-DD", "food": "..."},
      {"cycle_start": "YYYY-MM-DD", "food": "..."}
    ]
  }
}
```
At most 3 entries per phase/nutrient, most recent first: the current cycle plus the 2 before it. Keeping only 2 would mean that once the current cycle is recorded, a same-cycle recompute could check just 1 earlier cycle, silently weakening the 2-cycle no-repeat rule. `swapped` is optional and present only on an entry chosen with `--prefer-alternative`. `cycle_start` is the `--last-period` value active when that entry was written — this is what lets a same-cycle re-run be detected (compare today's `--last-period` to the most recent entry's `cycle_start`) without adding any new input or a separate cycle counter.

**Same-cycle re-run logic:** if the most recent entry's `cycle_start` matches this run's `--last-period`, this is the same cycle. The no-repeat set is the foods of the 2 entries after it. If the entry is `swapped` and its food is still allowed, keep it (the swap persists for the cycle) unless `--prefer-alternative` names this nutrient again. Otherwise call `resolve_candidates()` with this run's inputs: if the result matches the cached food nothing changes; if not (e.g. a new `--exclude` removed it), overwrite that entry in place (still one entry for that cycle, not a second one). If `cycle_start` doesn't match, it's a new cycle: call `resolve_candidates()` against the 2 most recent entries' foods as the no-repeat set, then prepend the new entry and trim to 3.

**Corrupt `history.json` → backup, then reset, never crash.** Matches the project's general convention (established for the nutrient-selection fallback) of never silently refusing to produce output. Copy the unreadable file to `history.json.bak` before treating history as empty, so the original bytes aren't lost if the corruption is manually recoverable.

**`nutrition_rules.json` gets a load-time candidate-count check, as a warning, not a gate.** When the file loads, the tool checks every phase/nutrient slot against the ≥5-candidate minimum (`rotation-history`'s "Candidate pool minimum" requirement) and prints a terminal warning for any slot below it — but still runs. This catches an under-populated stub slot early, without blocking the tool over the rest of the phases if only one slot is thin. Alternative considered: hard-reject at load time — rejected as disproportionate for a slot count problem that only degrades rotation quality for that one nutrient, not correctness elsewhere.

**Note wording is templated, with one dynamic field.** Placeholder and repeat notes are fixed strings. The alternative note is `chosen over <alt> — <reason>; swap with --prefer-alternative <nutrient>`, where `<reason>` is generated from whichever constraint actually decided the pair (e.g. "in season, but repeats a recent pick" vs. "out of season") — never a hardcoded phrase, since the deciding constraint varies per case.

## Risks / Trade-offs

- **Ovulation estimate is a population average, not a measurement** (no temperature/hormone input exists) → Mitigated by the 3-day window instead of a single day; residual imprecision is inherent to the input the tool has, not something design can remove.
- **Fixed 5-day Menstrual length won't match everyone's actual bleeding duration** → Accepted for v1; there's no bleeding-duration input to do better with, and it's a documented simplification rather than a silent assumption.
- **A mistyped `--last-period` on an intended same-cycle re-run would be read as a new cycle**, consuming a rotation slot prematurely → Input validation (strict format, future-date and range rejection) narrows the chance of a stray typo slipping through; residual risk accepted for v1 given the CLI is stateless and non-interactive by design.

## Migration Plan

None — greenfield project, no prior deployment or data.

## Open Questions

- Exact file/module layout (single `plan.py` vs. split into a few modules) — an implementation detail that doesn't change any spec or the approach above; left to `tasks.md`.

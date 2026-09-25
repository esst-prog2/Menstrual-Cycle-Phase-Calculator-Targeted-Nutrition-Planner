## Why

The project currently has no code — `README.md` is a fully-specified pitch doc (Shape Up style) after extensive clarification of scope, phase math, and rotation behavior. This change builds the v1 CLI tool the README now describes: given a last period date and cycle length, tell the user which nutrients matter in the current phase and, for each one, a food that contains it — using a stub, placeholder-only food database (the evidence-graded database is explicitly separate, later work).

## What Changes

- **New CLI tool** (`plan.py`) that takes `--last-period` (required, strict `YYYY-MM-DD`), `--cycle-length` (required, no default, valid range 21–38 days), `--exclude` (optional, repeatable), and `--prefer-alternative <nutrient>` (optional).
- **Phase calculation**: cycle day is `elapsed + 1` (no wrap-around); up to 7 days past the cycle length is a late-period grace window (Luteal, with a "period may be late" note), and beyond that the input is rejected; phase boundaries are Menstrual (fixed days 1–5), Ovulatory (a 3-day window centered on `cycle_length − 14`), with Follicular and Luteal filling the remaining days. A 21-day cycle is valid and has zero Follicular days by design — handled, not rejected.
- **Nutrient suggestions**: each phase tracks exactly 3 nutrients (fixed across phases); each nutrient slot draws from a stub `nutrition_rules.json` pool of at least 5 placeholder candidates, all explicitly unevidenced. Selection follows a fixed constraint order — exclusions (hard, never violated) > nutrient coverage > no-repeat-within-2-cycles > seasonality (soft, in that priority order) — via a pure `resolve_candidates()` function that takes candidates as input and never reads the data file itself.
- **Rotation via `history.json`**: entries are keyed by phase/nutrient and tagged with the cycle's `--last-period` value, so a same-cycle re-run reuses the cached pick unless `--exclude` or `--prefer-alternative` invalidates it (in which case that cycle's entry is recomputed and updated in place, never treated as a new rotation event). A missing file is normal on first run; an unparseable one is backed up to `history.json.bak`, then treated as empty, with a terminal-only warning.
- **Output**: a terminal summary and `nutrients.md`, both carrying the same per-item notes — placeholder labeling (with the one-time stub-data disclaimer), repeat-fallback notes, alternative notes (stating the real deciding constraint, not a fixed phrase), and "no suitable food" notes when exclusions empty a slot entirely. `history.json` read/parse issues are terminal-only, since they're a fact about the run, not about any suggestion.
- **`.gitignore`** covers `history.json`, `history.json.bak`, and `nutrients.md` (all reveal period timing; public repo).
- Explicitly **not** in this change: recipes, meal composition, supplement suggestions, the evidence-review pipeline (`EVIDENCE.md`, citation sourcing/grading), symptom/mood logging, irregular-cycle prediction, or any non-CLI interface.

## Capabilities

### New Capabilities
- `cycle-phase-calculation`: input validation (date format, required cycle-length, 21–38 day range) and phase-boundary/cycle-day math (Menstrual/Follicular/Ovulatory/Luteal), including the 21-day empty-Follicular edge case.
- `nutrient-selection`: the stub food database, the fixed 3-nutrients-per-phase list, and the constraint-priority resolution logic (exclusions/coverage/no-repeat/seasonality) that picks a food per nutrient slot, including the empty-candidate-after-exclusion case.
- `rotation-history`: `history.json`'s structure and lifecycle — cycle-aware entries, the 2-cycle no-repeat window, same-cycle re-run behavior (including `--prefer-alternative` persistence), and missing/corrupt-file handling.
- `cli-output`: terminal and `nutrients.md` output, including placeholder/repeat/alternative/no-suitable-food note wording and placement, and the `--exclude`/`--prefer-alternative` flags.

### Modified Capabilities
None — this is a greenfield project (`openspec list --specs` shows no existing capabilities).

## Impact

- New files: `plan.py`, `nutrition_rules.json` (stub data), `.gitignore` entries for `history.json`/`history.json.bak`/`nutrients.md`.
- No existing code affected (none exists yet).
- Out of scope for this change: populating `nutrition_rules.json` with evidence-reviewed data and the accompanying `EVIDENCE.md` — tracked as separate future work per README Section 4.

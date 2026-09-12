Menstrual Cycle Phase Calculater and Targeted Nutrition Planner

## 1. The Demo
I open my terminal and run `python plan.py --last-period 2026-08-25 --cycle-length 28`. The script calculates that today is Day 15 of my cycle and tells me I am in the Ovulatory phase. It prints a short summary of the key nutrients I should focus on right now (like fiber and zinc) and suggests a few simple meals. Next to the script, it creates a clean file called `groceries.md` with a categorized shopping list for the week. Since it checks my previous logs in `history.json`, it rotates meal suggestions so I don't get the exact same grocery list every single month. If I pass `--exclude dairy`, it automatically removes all dairy items from that list.

## 2. The Shape
**in:** The start date of my last period, my average cycle length, any food exclusions (optional), a local `nutrition_rules.json` rulebook, and a lightweight `history.json` tracking recent recommendations.  
**out:** A short terminal summary + a freshly rotated `groceries.md` shopping list.  
**in between:** Figure out the active phase, pull suitable ingredients from the food database, check previous months' history to ensure variety and avoid immediate repeats, filter out excluded items, and write out the Markdown checklist.

## 3. The Size
### What the first useful version does:
* Takes a start date and cycle length from the command line.
* Calculates the current cycle day and determines the active phase.
* Reads recommendations from a local JSON database of phase-specific foods.
* Tracks generated plans across cycles to rotate meals and avoid repetitive shopping lists.
* Exports a clean Markdown checklist for grocery shopping.
* Allows filtering out basic ingredients (like dairy or nuts).

### What it explicitly does NOT do this term:
* Symptom, mood, or pain logging.
* Irregular cycle prediction or medical diagnostics.
* Connecting to phones, fitness watches, or health apps.
* A web interface or mobile app; it stays as a simple command-line tool.

## 4. Evidence Basis for nutrition_rules.json

`nutrition_rules.json` has not been populated yet. It will be built alongside
an `EVIDENCE.md` file, not after it. For each phase-nutrient rule added to the
database, the following will be recorded before the rule is accepted into the
JSON:

1. **Source**: a specific citation (study, systematic review, or named
   consensus guideline) — not a wellness blog unless that blog cites a
   traceable primary source. I was planning to review the literature with AI and
   base the recommendations based on these.
3. **Evidence strength**, one of:
   - **Strong** — supported by systematic review/meta-analysis with
     consistent findings, or a well-established physiological mechanism
     (e.g. iron loss during menstruation).
   - **Moderate** — some supporting evidence, but reviews note inconsistency
     or lack of consensus.
   - **Weak** — based on a single small study, or a narrative (non-systematic)
     review only.
   - **Speculative** — appears in popular "cycle syncing" content but has no
     traceable primary study.
4. Rules labeled **Weak** or **Speculative** are still included in the tool
   (so the project isn't limited to only well-studied phases), but this label
   is surfaced to the user in the terminal output and in `groceries.md`,
   rather than presented with the same confidence as Strong rules.

`nutrition_rules.json` and `EVIDENCE.md` will be built together, entry by
entry: no rule is added to the JSON without a corresponding line in
`EVIDENCE.md`.

## 5. How We Would Know It Works
1. If I enter a date that is in the future, the script stops and prints an error saying the date is invalid.
2. If I set my last period start date to today, it always outputs Day 1 and identifies the phase as `Menstrual`.
3. 3. If I run the planner for two consecutive cycles in the same phase, the two generated groceries.md lists share at most N items, where N is fixed relative to the pool size for that phase (e.g., if a phase's food pool has P suitable ingredients and each list surfaces K of them, N is set close to the mathematical minimum overlap achievable given P and K, plus a small margin). This makes "varied" a checkable assertion rather than a subjective judgment. N is not a fixed constant across all phases — it is recalculated per phase based on that phase's ingredient pool size, so the threshold stays achievable even for phases with a small food database.
4. 4. If a phase-nutrient slot has exactly one valid candidate (after
   exclusions and other constraints are applied), `groceries.md` lists it
   with no alternative note. If two or more valid candidates conflict on
   ranking, `groceries.md` shows the chosen item plus a named alternative,
   and `--prefer-alternative` successfully swaps to it.

      
## 6. What Could Stop This
* **Date math edge cases:** Handling month ends, leap years, or long cycles without breaking. *Plan:* Use Python's built-in `datetime` and `timedelta` modules and write unit tests for month boundary transitions.
* **Rotation logic becoming too restrictive:** if a phase's food pool is small, the target overlap N may be difficult to satisfy. Plan: N is computed dynamically from pool size (soft constraint with a documented formula), and the tool logs when it must fall back to repeating items rather than silently producing an invalid list.

  ## 7. Constraint priorities
  1. **Exclusions (hard constraint, never violated).** An excluded ingredient
   is never shown, regardless of how well it fits other constraints.
2. **Nutrient coverage for the active phase (soft constraint, highest
   priority).** This is the project's reason for existing. Within this
   constraint, a rule labeled Strong evidence (see "Evidence Basis" section)
   is protected before a Weak-evidence rule when a choice must be made.
3. **No-repeat-within-N (soft constraint).** Keeps the shopping list from
   feeling identical month to month, but yields to nutrient coverage when
   the two conflict.
4. **Seasonality (soft constraint, lowest priority).** Preferred when it
   doesn't cost anything on the constraints above it, but the first thing
   sacrificed when it conflicts with them.

**How conflicts are resolved:** ingredients are first filtered to only those
that satisfy the hard constraint (exclusions). Among the remaining valid
candidates for a given nutrient slot:

- If exactly one valid ingredient remains, it is used directly —
  `groceries.md` lists it with no alternative note, since there is no real
  choice to surface.
- If two or more valid ingredients remain and they rank differently across
  the soft constraints (e.g. one is in-season but repeats last month's
  item, another is out-of-season but new), the tool does not silently pick
  one and hide the trade-off. It shows the top-ranked item in
  `groceries.md`, plus a short note naming the next-best alternative and why
  it wasn't chosen. A `--prefer-alternative` flag lets the user swap to it
  without needing an interactive prompt — keeping the tool CLI-only and
  non-interactive, per this term's scope.

Menstrual Cycle Phase Calculator and Targeted Nutrition Planner

## 1. The Demo
I open my terminal and run `python plan.py --last-period 2026-08-25 --cycle-length 28`. The script calculates that today is Day 15 of my cycle and tells me I am in the Ovulatory phase. It prints a short summary of the key nutrients that matter right now (like fiber and zinc) and, for each one, a food that contains it — for example, "zinc is important now, eat pumpkin seeds." Next to the script, it creates a clean file called `nutrients.md` listing those nutrient-food pairs for the current phase. Since it checks my previous logs in `history.json`, it rotates the suggested foods so I don't get the exact same list every single month. If I pass `--exclude dairy`, it automatically removes all dairy items from consideration.

## 2. The Shape
**in:** The start date of my last period, my average cycle length, any food exclusions (optional), a local `nutrition_rules.json` rulebook, and a lightweight `history.json` tracking recent recommendations.  
**out:** A short terminal summary + a freshly rotated `nutrients.md` list of nutrient-food pairs.  
**in between:** Figure out the active phase, pull suitable foods for each relevant nutrient from the food database, check previous cycles' history to ensure variety and avoid immediate repeats, filter out excluded items, and write out the Markdown list.

## 3. The Size
### What the first useful version does:
* Takes a start date and cycle length from the command line.
* Calculates the current cycle day and determines the active phase.
* Reads nutrient-food pairings from a local JSON database of phase-specific foods.
* Tracks generated suggestions across cycles to rotate foods and avoid repeating the same food for a nutrient too soon.
* Exports a clean Markdown list of nutrients and their suggested foods.
* Allows filtering out basic ingredients (like dairy or nuts).

### What it explicitly does NOT do this term:
* Symptom, mood, or pain logging.
* Irregular cycle prediction or medical diagnostics.
* Connecting to phones, fitness watches, or health apps.
* A web interface or mobile app; it stays as a simple command-line tool.
* Recipes, meal composition, or supplement suggestions — nutrition_rules.json only holds nutrients and the foods that contain them, nothing else.

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
   is surfaced to the user in the terminal output and in `nutrients.md`,
   rather than presented with the same confidence as Strong rules.

`nutrition_rules.json` and `EVIDENCE.md` will be built together, entry by
entry: no rule is added to the JSON without a corresponding line in
`EVIDENCE.md`.

## 5. How We Would Know It Works
1. If I enter a date that is in the future, the script stops and prints an error saying the date is invalid.
2. If I set my last period start date to today, it always outputs Day 1 and identifies the phase as `Menstrual`.
3. 3. If I run the planner across consecutive cycles in the same phase, no food is suggested for the same nutrient in either of the previous 2 cycles — checked per nutrient, not across the list as a whole, since each nutrient's own candidate pool is what determines whether a repeat can be avoided. If that nutrient's pool doesn't have enough distinct options left (e.g. after exclusions), the tool falls back to repeating and shows a note next to the item instead of silently repeating it.
4. 4. If a phase-nutrient slot has exactly one valid candidate (after
   exclusions and other constraints are applied), `nutrients.md` lists it
   with no alternative note. If two or more valid candidates conflict on
   ranking, `nutrients.md` shows the chosen item plus a named alternative,
   and `--prefer-alternative` successfully swaps to it.

      
## 6. What Could Stop This
* **Date math edge cases:** Handling month ends, leap years, or long cycles without breaking. *Plan:* Use Python's built-in `datetime` and `timedelta` modules and write unit tests for month boundary transitions.
* **Rotation logic becoming too restrictive:** if a specific nutrient's food pool is small, avoiding a repeat within the last 2 cycles may not be possible. Plan: every nutrient slot in the stub data carries at least 5 candidate foods — comfortably above the minimum a 2-cycle window needs. When a slot still can't avoid a repeat, the tool falls back to repeating and shows a short note next to that item, in both the terminal output and `nutrients.md`, rather than silently producing an invalid list or only recording it in a log.

  ## 7. Constraint priorities
  1. **Exclusions (hard constraint, never violated).** An excluded ingredient
   is never shown, regardless of how well it fits other constraints.
2. **Nutrient coverage for the active phase (soft constraint, highest
   priority).** This is the project's reason for existing. Within this
   constraint, a rule labeled Strong evidence (see "Evidence Basis" section)
   is protected before a Weak-evidence rule when a choice must be made.
3. **No-repeat-within-2-cycles (soft constraint).** Keeps the suggestions from
   feeling identical cycle to cycle, but yields to nutrient coverage when
   the two conflict.
4. **Seasonality (soft constraint, lowest priority).** Preferred when it
   doesn't cost anything on the constraints above it, but the first thing
   sacrificed when it conflicts with them.

**How conflicts are resolved:** ingredients are first filtered to only those
that satisfy the hard constraint (exclusions). Among the remaining valid
candidates for a given nutrient slot:

- If exactly one valid ingredient remains, it is used directly —
  `nutrients.md` lists it with no alternative note, since there is no real
  choice to surface.
- If two or more valid ingredients remain and they rank differently across
  the soft constraints (e.g. one is in-season but repeats last month's
  item, another is out-of-season but new), the tool does not silently pick
  one and hide the trade-off. It shows the top-ranked item in
  `nutrients.md`, plus a short note naming the next-best alternative and why
  it wasn't chosen. A `--prefer-alternative` flag lets the user swap to it
  without needing an interactive prompt — keeping the tool CLI-only and
  non-interactive, per this term's scope.

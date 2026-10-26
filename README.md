Menstrual Cycle Phase Calculator and Targeted Nutrition Planner

> **Evidence note.** The phase-nutrient pairings this tool uses are mostly
> *not* backed by phase-specific evidence. A review of all 12 pairs in
> `nutrition_rules.json` (see [EVIDENCE.md](EVIDENCE.md)) found **2 Strong,
> 4 Moderate, 1 Weak, and 5 Speculative**. The Follicular phase has no
> supported pairing at all, and one Ovulatory pairing (fiber) has evidence
> pointing the other way. Where support exists, it is for **daily
> supplementation to relieve PMS or period pain**, not for eating particular
> foods in a particular phase. Treat the output as a prompt to eat varied
> foods, not as medical or nutrition advice. See Section 4.

## Requirements
Python 3.10 or newer. `plan.py` uses the `dict | None` type-union syntax,
which older Python versions reject, so it checks the version at startup and
stops with a clear message on anything older (macOS's built-in
`/usr/bin/python3` is 3.9). There are no third-party dependencies; the tests
use Python's built-in `unittest` (`python3 -m unittest discover -s tests`).

The specs in `openspec/` were written with [OpenSpec](https://github.com/Fission-AI/OpenSpec)
1.13.0, which needs Node.js 20.19 or newer. OpenSpec is only needed for the spec workflow
(proposing, validating and archiving changes), not to run `plan.py` or its tests.

## 1. The Demo
I open my terminal and tell the planner that my period started two days ago. It says I am on day 3, in the Menstrual phase, and lists the three nutrients that matter now: iron, vitamin C and magnesium, with one food for each. These foods are real. Next to each one I can see how much of the nutrient it has, from USDA FoodData Central, and how strong the evidence is that this nutrient matters in this phase. Then I try a date in the Ovulatory phase. There the foods are still placeholders, and the tool clearly says so. I exclude fish and salmon is gone. I swap a food I don't want. At the end I open the file it created, where everything is written down with its sources.

A 5-minute demo, run alongside the slides. The output below is from an autumn
day; the season decides some picks (in autumn, broccoli is chosen over
oranges for Vitamin C).

**Before the demo.** The demo runs in a separate, empty folder, so my own `history.json`
is never read or changed. Only the script and the rulebook are copied:

```
mkdir <demo-folder>
cp plan.py nutrition_rules.json <demo-folder>/
cd <demo-folder>
```

**1. A Menstrual day: real, sourced foods.** Each food shows its amount per
100 g, its % of the EU nutrient reference value (NRV) and its USDA FoodData
Central ID, next to the evidence tier for the nutrient:

```
$ python3 plan.py --last-period <a date 2 days ago> --cycle-length 28
Not nutrition advice. Foods marked [placeholder] come from a stub database that has not been evidence-reviewed.

Day 3 of your 28-day cycle: Menstrual phase

Nutrients that matter now, and a food that contains each:
  Iron: lentils, cooked [3.33 mg/100 g, 24% NRV, FDC 172421] (evidence: Strong)
  Vitamin C: broccoli, cooked [64.9 mg/100 g, 81% NRV, FDC 169967] (evidence: Moderate)
    note: chosen over oranges - out of season; swap with --prefer-alternative vitamin c
  Magnesium: pumpkin seeds (dried) [592 mg/100 g, 158% NRV, FDC 170556] (evidence: Moderate)
```

**2. An Ovulatory day: placeholder foods.** The other three phases still use
hand-written stub foods, and they are labelled as such:

```
$ python3 plan.py --last-period <a date 14 days ago> --cycle-length 28
...
Day 15 of your 28-day cycle: Ovulatory phase
...
  Fiber: pears [placeholder] (evidence: Speculative)
  Zinc: pumpkin seeds [placeholder] (evidence: Speculative)
  Omega-3: salmon [placeholder] (evidence: Weak)
```

**3. Exclusions are a hard rule.** Excluding fish on the same day replaces
salmon:

```
$ python3 plan.py --last-period <a date 14 days ago> --cycle-length 28 --exclude fish
...
  Omega-3: walnuts [placeholder] (evidence: Weak)
```

**4. Swapping a food.** Back on the Menstrual day, `--prefer-alternative`
swaps one nutrient's food for the next candidate, for the rest of the cycle:

```
$ python3 plan.py --last-period <a date 2 days ago> --cycle-length 28 --prefer-alternative iron
...
  Iron: spinach, cooked [3.57 mg/100 g, 26% NRV, FDC 168463] (evidence: Strong)
    note: swapped in with --prefer-alternative
```

**5. The file.** Each run also writes `nutrients.md` next to the script, with
the same foods and notes plus the source for each evidence tier:

```
| Nutrient | Evidence | Food | Notes |
| --- | --- | --- | --- |
| Iron | Strong - Cochrane CD009747 (2016); NHS | spinach, cooked [3.57 mg/100 g, 26% NRV, FDC 168463] | swapped in with --prefer-alternative |
| Vitamin C | Moderate - EFSA 2014 opinion; Cook & Reddy 2001 | broccoli, cooked [64.9 mg/100 g, 81% NRV, FDC 169967] | chosen over oranges - out of season; swap with --prefer-alternative vitamin c |
| Magnesium | Moderate - Cochrane CD002124 (2001, 2016); Saei Ghare Naz 2020 | pumpkin seeds (dried) [592 mg/100 g, 158% NRV, FDC 170556] |  |
```

**Rotation, in one sentence:** a food is kept for the whole cycle, and
`history.json` makes sure it is not suggested again for the same nutrient in
the next 2 cycles, so the foods vary from month to month. A slide shows two
consecutive cycles side by side.

## 2. The Shape
**in:** The start date of my last period, my average cycle length, any food exclusions (optional), a local `nutrition_rules.json` rulebook, and a lightweight `history.json` tracking recent recommendations.  
**out:** A short terminal summary + a freshly rotated `nutrients.md` list of nutrient-food pairs.  
**in between:** Figure out the active phase, pull suitable foods for each relevant nutrient from the food database, check previous cycles' history to ensure variety and avoid immediate repeats, filter out excluded items, and write out the Markdown list.

## 3. The Size
### What the first useful version does:
* Takes a start date and cycle length from the command line.
* Calculates the current cycle day and determines the active phase.
* Reads nutrient-food pairings from a local JSON database that assigns nutrients to phases (these assignments are mostly not evidence-backed; see Section 4).
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

### What the evidence review found (2026-09-30)

`nutrition_rules.json` pairs 3 nutrients with each of the 4 phases (12
pairings). Each pair was checked against PubMed,
Cochrane, ACOG, NHS and EFSA for a source supporting that nutrient in that
specific phase. Full citations, DOIs and verbatim quotes are in
[EVIDENCE.md](EVIDENCE.md), which also has [the tier of each pair and the
count per tier](EVIDENCE.md#summary).

What this means for how the tool's output should be read:

- **The support is for daily supplements that relieve symptoms, not for
  eating certain foods in a certain phase.** The calcium, magnesium and
  vitamin B6 findings come from trials where supplements were taken every
  day, usually across the whole cycle, to relieve PMS or period pain. They
  show these nutrients help symptoms that occur in the luteal or menstrual
  phase. They do not show that eating them only in that phase matters. Even
  the iron pairing reflects blood loss during menstruation, but iron stores
  are rebuilt over weeks, not in one phase.
- **The Follicular phase has no supported pairing.**
- **Ovulatory Fiber has evidence against it.** The one direct study linked
  higher fiber intake to more cycles without ovulation.
- **The tool does not supplement or dose.** Section 3's no-supplements scope
  still holds, so even the Strong pairings are shown only as food examples.

The pairings were deliberately left unchanged after this review; only this
README's framing was corrected (PLANNING_LOG.md, 2026-09-30).

### Real food data for the Menstrual phase (2026-10-26)

The 15 Menstrual foods (5 each for Iron, Vitamin C and Magnesium) are real
data from [USDA FoodData Central](https://fdc.nal.usda.gov/), SR Legacy
dataset. Each one stores its FDC ID, the exact FDC description, and the amount
of the nutrient per 100 g of the food as eaten (cooked where it is normally
cooked). The tool shows the amount, the % of the nutrient reference value and
the FDC ID, for example `lentils, cooked [3.33 mg/100 g, 24% NRV, FDC 172421]`.
The values are copied into the file, so the tool never goes online.

When the file loads, every real food must be an EU "source of" its nutrient:
at least 15% of the nutrient reference value per 100 g (Regulation (EC)
1924/2006, with the reference values from Regulation (EU) 1169/2011 Annex
XIII). That means 2.1 mg iron, 12 mg vitamin C or 56.25 mg magnesium.

What "real" covers, and what it does not:

- **Real:** what the food contains. A real amount does **not** make the
  phase pairing any stronger; the evidence tier next to each nutrient still
  describes that.
- **Still hand-written:** every food in the other three phases (shown with
  `[placeholder]`), and the seasonal tags and categories of every food,
  real or not.

### How rules are graded

For each phase-nutrient rule, the following is recorded in `EVIDENCE.md`:

1. **Source**: a specific citation (study, systematic review, or named
   consensus guideline) — not a wellness blog unless that blog cites a
   traceable primary source. I was planning to review the literature with AI and
   base the recommendations based on these.
3. **Evidence strength**: Strong, Moderate, Weak or Speculative, as defined
   in [EVIDENCE.md](EVIDENCE.md#how-claims-were-graded).
4. Rules labeled **Weak** or **Speculative** are still included in the tool
   (so the project isn't limited to only well-studied phases), but this label
   is surfaced to the user in the terminal output and in `nutrients.md`,
   rather than presented with the same confidence as Strong rules.

From here on, `nutrition_rules.json` and `EVIDENCE.md` are kept in step:
no rule is added to the JSON without a corresponding entry in
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
2. **No-repeat-within-2-cycles (soft constraint, highest priority).** Keeps
   the suggestions from feeling identical cycle to cycle.
3. **Seasonality (soft constraint, lowest priority).** Preferred when it
   doesn't cost anything on the constraint above it, but the first thing
   sacrificed when the two conflict.

Candidates that rank equally keep their order in `nutrition_rules.json`.
Which nutrients appear is decided by the phase, and each nutrient's evidence
tier (see "Evidence Basis" section) is shown next to it. Foods within a slot
are not ranked by evidence, because the stub data has no per-food evidence.
Future work: once real per-food data exists, prioritize foods by evidence or
by how rich they are in the nutrient.

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

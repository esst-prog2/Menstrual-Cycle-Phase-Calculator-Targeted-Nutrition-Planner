# Cycle Nutrition Planner

Python · command line · offline

Advanced Programming · 2026

**A cycle food planner that tells you when it's guessing.**

This tool works out which phase of the menstrual cycle someone is in, then suggests the nutrients that may matter in that phase, with one food for each. It rotates the foods from cycle to cycle, never suggests anything you've excluded, and uses real USDA data for the Menstrual phase. Next to every suggestion it shows how strong the evidence is, from Strong to Speculative, so you always know how much to trust it.

---

## Same tool, two different days

Evidence grades, from strongest to weakest: Strong, Moderate, Weak, Speculative.

**Day 3, for a period that started 2 days ago (28-day cycle).** Real food data, and evidence that holds up:

```
Not nutrition advice. Foods marked [placeholder] come from a stub database that has not been evidence-reviewed.

Day 3 of your 28-day cycle: Menstrual phase

Nutrients that matter now, and a food that contains each:
  Iron: lentils, cooked [3.33 mg/100 g, 24% NRV, FDC 172421] (evidence: Strong)
  Vitamin C: broccoli, cooked [64.9 mg/100 g, 81% NRV, FDC 169967] (evidence: Moderate)
    note: chosen over oranges - out of season; swap with --prefer-alternative vitamin c
  Magnesium: pumpkin seeds (dried) [592 mg/100 g, 158% NRV, FDC 170556] (evidence: Moderate)
```

Each food comes from USDA FoodData Central, with its amount per 100 g and its share of the EU reference value. The foods change with the season. This run was in autumn, which is why it explains picking broccoli over oranges.

**Day 14, for a period that started 13 days ago (28-day cycle).** Here the tool admits it's guessing:

```
Not nutrition advice. Foods marked [placeholder] come from a stub database that has not been evidence-reviewed.

Day 14 of your 28-day cycle: Ovulatory phase

Nutrients that matter now, and a food that contains each:
  Fiber: pears [placeholder] (evidence: Speculative)
  Zinc: pumpkin seeds [placeholder] (evidence: Speculative)
  Omega-3: salmon [placeholder] (evidence: Weak)
```

The other three phases only have placeholder foods for now, and the tool says so. It also says the science linking these nutrients to this phase is speculative or weak. It doesn't hide that.

---

## The scoreboard

I had my coding agent check all 12 pairings against PubMed, Cochrane, NHS and EFSA sources, and reviewed the result.

**12 pairings checked**

| Strong | Moderate | Weak | Speculative |
|:------:|:--------:|:----:|:-----------:|
| 2 | 4 | 1 | 5 |

The full review, with citations, is in [EVIDENCE.md](EVIDENCE.md).

---

## What I chose to build

- **Evidence next to every pick.** Weak pairings aren't hidden, and they aren't dressed up as strong ones.
- **Real food data.** The Menstrual-phase foods are real USDA entries, each with its FDC ID.
- **Open about its choices.** When it picks one food over another, it tells you why and lets you swap.
- **Private by design.** It's one Python file and one JSON rulebook. It needs no account and no internet connection.

## What it isn't

- **It isn't medical or nutrition advice.** Where good evidence exists, it's for taking supplements every day to ease PMS or period pain, not for eating certain foods in certain phases.
- **Only the Menstrual phase has real food data so far.** The other three phases use placeholder foods, labelled `[placeholder]`.

The best way to read the output is as a friendly nudge to eat a variety of foods.

## How I built it

I built it with Claude Code as my coding agent. Every decision, and whether I or the agent made it, is recorded in the [planning log](PLANNING_LOG.md). The main changes, the first version and the real food data, went through OpenSpec: proposed, specified, implemented and archived. Each work step is in [PROCESS.md](PROCESS.md).

---

## Try it

You need Python 3.10 or newer, and nothing else. This is a template, so fill in your own values:

```
python3 plan.py --last-period YYYY-MM-DD --cycle-length DAYS
```

- `--last-period`: the start date of your most recent period. It can't be in the future, and it can't be more than your cycle length plus 7 days ago.
- `--cycle-length`: your average cycle length, from 21 to 38 days (for example, 28).
- To leave out a food category, add a flag such as `--exclude fish`.
- If the output has a `swap with --prefer-alternative ...` note, copy that flag to use the other food. Put quotes around a two-word nutrient, for example `--prefer-alternative "vitamin c"`.

It remembers recent picks in two local files (`history.json` and `nutrients.md`), written next to `plan.py`, so the foods rotate between cycles. Nothing leaves your computer.

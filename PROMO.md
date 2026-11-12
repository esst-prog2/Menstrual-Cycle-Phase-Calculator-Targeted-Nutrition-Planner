# Cycle Nutrition Planner

**A cycle food planner that tells you when it's guessing.**

Lots of apps promise to know the right foods for every phase of your cycle, and they say it with total confidence. When I checked those claims myself, most of them didn't hold up. So I built a planner that shows you how strong the evidence is behind every suggestion, including when it's weak.

---

## Same tool, two different days

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

I haven't finished this part yet. These foods are placeholders, and the tool says so. It also says the science linking these nutrients to this phase is speculative or weak. It doesn't hide that.

---

## The scoreboard

I checked all 12 phase–nutrient pairings the planner uses against PubMed, Cochrane, NHS and EFSA sources:

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

I built it spec-first with OpenSpec: each change was proposed and specified, then implemented and archived. Each decision, such as a number, a name or a threshold, is recorded in [PLANNING_LOG.md](PLANNING_LOG.md) with who made it, and each work step is in [PROCESS.md](PROCESS.md).

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

It remembers recent picks in two local files (`history.json` and `nutrients.md`) in the folder you run it from, so the foods rotate between cycles. Nothing leaves your computer.

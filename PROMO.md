# Cycle Nutrition Planner

**A small tool that tells you where you are in your cycle and suggests a few foods to try, and is honest about how much the science backs them.**

Lots of apps promise the "right foods for your phase". I wanted to build one that shows its evidence. You give it a date and a cycle length. It tells you your day and phase, picks three nutrients for that phase and one food for each, and labels every pick with how strong the evidence is.

```
$ python3 plan.py --last-period 2025-03-01 --cycle-length 28
Day 3 of your 28-day cycle: Menstrual phase

  Iron: lentils, cooked [3.33 mg/100 g, 24% NRV, FDC 172421] (evidence: Strong)
  Vitamin C: broccoli, cooked [64.9 mg/100 g, 81% NRV, FDC 169967] (evidence: Moderate)
  Magnesium: pumpkin seeds (dried) [592 mg/100 g, 158% NRV, FDC 170556] (evidence: Moderate)
```

---

## What I chose to build, and why

- **Evidence is shown next to every pick.** I reviewed all 12 phase–nutrient pairings against PubMed, Cochrane, NHS and EFSA sources and labelled each one Strong, Moderate, Weak or Speculative. Weak pairings aren't hidden, and they aren't dressed up as strong ones.
- **The foods are real data.** The Menstrual-phase foods come from USDA FoodData Central, each with its amount per 100 g, its share of the EU reference value, and its FDC ID.
- **It's open about its choices.** When it picks one food over another, for example because the other is out of season, it says so and lets you swap.
- **It's private by design.** It's one Python file and one JSON rulebook. It needs no account and no internet connection, and your history stays on your computer.

---

## What it isn't

- **It isn't medical or nutrition advice.** Of the 12 pairings, the review found 2 Strong, 4 Moderate, 1 Weak and 5 Speculative. Where good evidence exists, it's for taking supplements every day to ease PMS or period pain, not for eating certain foods in certain phases.
- **Only the Menstrual phase has real food data so far.** The other three phases use placeholder foods, and they're labelled `[placeholder]`.

The best way to read the output is as a friendly nudge to eat a variety of foods.

---

## How I built it

I built it spec-first with OpenSpec: each change was proposed and specified, then implemented and archived. Each decision, such as a number, a name or a threshold, is recorded in [PLANNING_LOG.md](PLANNING_LOG.md) with who made it, and each work step is in [PROCESS.md](PROCESS.md). The full evidence review, with citations, is in [EVIDENCE.md](EVIDENCE.md).

**Try it:** you need Python 3.10 or newer, and nothing else.
`python3 plan.py --last-period YYYY-MM-DD --cycle-length 28`

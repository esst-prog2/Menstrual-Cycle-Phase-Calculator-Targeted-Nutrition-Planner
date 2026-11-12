# Cycle Nutrition Planner

**Know where you are in your cycle, and get a few foods to try, with the evidence shown next to each one.**

You give it one date and one number. It tells you which day and phase of your cycle you're in, then picks three nutrients for that phase and one food for each. For every pick it shows how strong the evidence really is.

---

## How it works

1. **Tell it when your last period started and how long your cycle usually is.**
   `python3 plan.py --last-period 2025-03-01 --cycle-length 28`
2. **It works out your day and phase:** Menstrual, Follicular, Ovulatory or Luteal.
3. **It picks three nutrients for that phase and one food for each.** You see the picks in the terminal, and they're also saved to `nutrients.md`.

```
Day 3 of your 28-day cycle: Menstrual phase

Nutrients that matter now, and a food that contains each:
  Iron: lentils, cooked [3.33 mg/100 g, 24% NRV, FDC 172421] (evidence: Strong)
  Vitamin C: broccoli, cooked [64.9 mg/100 g, 81% NRV, FDC 169967] (evidence: Moderate)
  Magnesium: pumpkin seeds (dried) [592 mg/100 g, 158% NRV, FDC 170556] (evidence: Moderate)
```

---

## Why it's different

**It says how strong the evidence is.**
Every nutrient is labelled Strong, Moderate, Weak or Speculative, based on a review of PubMed, Cochrane, NHS and EFSA sources. The source of each label is in `nutrients.md`. The planner doesn't hide weak pairings, and it doesn't present them with the same confidence as strong ones.

**The Menstrual-phase foods are real, sourced data.**
All 15 Menstrual-phase foods come from USDA FoodData Central, with the amount per 100 g, the share of the EU nutrient reference value, and the FDC ID. Each one meets the EU "source of" threshold for its nutrient.

**Your foods change from month to month.**
The planner keeps one food per nutrient for the whole cycle, and doesn't suggest that food again for that nutrient for the next two cycles. If a repeat can't be avoided, it says so.

**Exclusions are never broken.**
With `--exclude fish` or `--exclude nuts`, you won't see that food, whatever else the planner is weighing.

**It doesn't make choices behind your back.**
When it has to choose between foods, for example an in-season food against one you haven't had lately, it tells you what it picked and what the alternative was. `--prefer-alternative` switches to the alternative.

**Your data stays on your computer.**
It's one Python file and one JSON rulebook. It needs no account and no internet connection, and sends nothing anywhere. Your history is a small local file.

---

## What it isn't

Please read this part before you rely on anything the planner says.

- **It isn't medical or nutrition advice.** Most of the phase–nutrient pairings aren't backed by phase-specific evidence. Of the 12 pairings, the review found 2 Strong, 4 Moderate, 1 Weak and 5 Speculative. Where good evidence exists, it's for taking supplements every day to ease PMS or period pain, not for eating certain foods in a certain phase.
- **Only the Menstrual phase has real food data so far.** Foods for the other three phases are placeholders, and they're labelled `[placeholder]`.
- **It doesn't track symptoms, predict irregular cycles, diagnose anything, suggest supplements, or connect to apps or devices.**

Treat it as a nudge to eat a variety of foods, with the evidence shown.

---

## Try it

You need Python 3.10 or newer. No other installs are needed.

```
python3 plan.py --last-period YYYY-MM-DD --cycle-length 28
python3 plan.py --last-period YYYY-MM-DD --cycle-length 28 --exclude dairy
python3 plan.py --last-period YYYY-MM-DD --cycle-length 28 --prefer-alternative iron
```

The full evidence review, with citations, is in [EVIDENCE.md](EVIDENCE.md). How the planner chooses foods is described in the [README](README.md).


# PhasePlate: Menstrual Cycle Phase Calculator & Targeted Nutrition Planner

## 1. The Demo
I open a terminal and run `phase-plate plan --last-period 2026-08-25 --cycle-length 28`. Within a second, it calculates that today is Day 15, placing me directly in the Ovulatory phase. The terminal displays a summary showing current hormone trends, the primary nutrient focus (fiber and zinc to support estrogen metabolism), and three suggested meal frameworks. I open the newly created `weekly_groceries.md`, which lists a categorized shopping list tailored specifically to the nutritional demands of the ovulatory window.

## 2. The Shape
**in:** A user profile (last period start date, average cycle length) and a structured JSON nutrition rulebook.  
**out:** A terminal phase status card + a generated Markdown grocery and meal planning file (`weekly_groceries.md`).  
**in between:** Calculate days elapsed since last period, determine the active cycle phase using calendar arithmetic, query the phase-to-nutrient rulebook, and compile targeted ingredients into an exportable checklist.

## 3. The Size
### What the first useful version does:
* Computes current cycle day and identifies which of the 4 phases (Menstrual, Follicular, Ovulatory, Luteal) the user is in.
* Maps the active phase to a local rulebook detailing key micronutrients, recommended food items, and items to minimize.
* Generates an exportable Markdown file with a phase-specific grocery checklist.
* Supports custom cycle lengths (e.g., 26 to 35 days) by dynamically scaling phase windows.

### What it explicitly does NOT do this term:
* Symptom tracking (cramps, mood logs, basal body temperature).
* Irregular cycle prediction via complex machine learning or probabilistic algorithms.
* Integration with third-party fitness or health platforms (Apple Health, Fitbit).
* Clinical medical advice or diagnosis.

## 4. How We Would Know It Works
1. Given a start date set to exactly today, it outputs Day 1 and labels the phase as `Menstrual`.
2. Given an invalid date in the future, it exits immediately with an error message indicating that the start date cannot be future-dated.
3. Given a 28-day cycle where elapsed days equal 20, the calculated phase is strictly reported as `Luteal`, and the generated file includes magnesium and complex carbohydrate recommendations.

## 5. What Could Stop This
* **Date Parsing & Month Boundaries:** Calculation bugs occurring over month ends or leap years. *Mitigation:* Use Python's standard `datetime.date` objects and `timedelta` exclusively to handle calendar edge cases cleanly.
* **Variable Phase Proportions:** Not everyone follows a textbook 28-day split. *Mitigation:* Implement standard follicular/luteal scaling ratios in the calculation logic based on the user's total entered cycle duration.

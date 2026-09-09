
Menstrual Cycle Phase Calculator & Targeted Nutrition Planner

1. The Demo
I open my terminal and run `python plan.py --last-period 2026-08-25 --cycle-length 28`. The script calculates that today is Day 15 of my cycle and tells me I am in the Ovulatory phase. It prints a short summary of the key nutrients I should focus on right now (like fiber and zinc) and suggests a few simple meals. Next to the script, it creates a clean file called `groceries.md` with a categorized shopping list for the week. Since it checks my previous logs in `history.json`, it rotates meal suggestions so I don't get the exact same grocery list every single month. If I pass `--exclude dairy`, it automatically removes all dairy items from that list.

 2. The Shape
**in:** The start date of my last period, my average cycle length, any food exclusions (optional), a local `nutrition_rules.json` rulebook, and a lightweight `history.json` tracking recent recommendations.  
**out:** A short terminal summary + a freshly rotated `groceries.md` shopping list.  
**in between:** Figure out the active phase, pull suitable ingredients from the food database, check previous months' history to ensure variety and avoid immediate repeats, filter out excluded items, and write out the Markdown checklist.

3. The Size
### What the first useful version does:
* Takes a start date and cycle length from the command line.
* Calculates the current cycle day and determines the active phase.
* Reads recommendations from a local JSON database of phase-specific foods.
* Tracks generated plans across cycles to rotate meals and avoid repetitive shopping lists.
* It offers different food recommendations for each season.
* Exports a clean Markdown checklist for grocery shopping.
* Allows filtering out basic ingredients (like dairy or nuts).
* Allows filtering different diet types (vegan, vegetarian, etc.)

### What it explicitly does NOT do this term:
* Symptom, mood, or pain logging.
* Irregular cycle prediction or medical diagnostics.
* Connecting to phones, fitness watches, or health apps.
* A web interface or mobile app; it stays as a simple command-line tool.

4. How We Would Know It Works
1. If I enter a date that is in the future, the script stops and prints an error saying the date is invalid.
2. If I set my last period start date to today, it always outputs Day 1 and identifies the phase as `Menstrual`.
3. If I run the planner for two consecutive cycles in the same phase, the generated `groceries.md` offers a varied list by rotating alternative ingredients from the database.

5. What Could Stop This
* **Date math edge cases:** Handling month ends, leap years, or long cycles without breaking. *Plan:* Use Python's built-in `datetime` and `timedelta` modules and write unit tests for month boundary transitions.
* **Rotation logic becoming too restrictive:** If the food pool is small, the rotation algorithm might run out of non-repeated items. *Plan:* Set up the rotation logic as a "prefer variety" soft rule with a fallback pool rather than a hard block that causes an error. years, or long cycles without breaking. *Plan:* Use Python's built-in `datetime` and `timedelta` modules and write tests for date edge cases early on.
* **Messy nutrition rules:** Putting random foods in the rulebook without a consistent structure. *Plan:* Keep the JSON schema very simple with fixed keys (`phase`, `nutrients`, `foods`) and define the list before writing the logic.

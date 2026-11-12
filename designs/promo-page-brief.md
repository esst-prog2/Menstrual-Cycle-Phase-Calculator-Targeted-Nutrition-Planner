# Design brief: promo page, "The Nutrition Label"

Shaped with Impeccable `/shape` on 2026-11-13. Status: CONFIRMED. Source text: [PROMO.md](../PROMO.md). Product record: [PRODUCT.md](../PRODUCT.md). Earlier content design: [promo-page.md](promo-page.md).

## 1. Job and audience

- Course/demo classmates. Most open a shared link on their own, on a laptop or phone. It may be shown briefly in the demo. Visitor mode: Persuade.
- They come in with no context and leave within a minute.

## 2. Outcome and proof

- Takeaway: "it tells you when it's guessing". Test: after 10 seconds on the first screen, a classmate repeats that line.
- Proof is only the real material: the two unedited output blocks, the 2 / 4 / 1 / 5 scoreboard, and links to EVIDENCE.md, PLANNING_LOG.md and PROCESS.md.
- What only this tool can show: a food label that grades its own claims, with day 14 openly marked weaker than day 3.

## 3. Selected direction

- **World:** a regulatory food-label panel: heavy black rules, a dense heavy sans-serif, and white card stock. The ground colour is open (section 7).
- **Main idea:** the whole page is one label, seen once. The headline is the product name at the top. Each PROMO.md section is a ruled section of the panel, with no cards and no feature grid.
- **The key moment:** day 3 and day 14 are two sections of the same label, with the output blocks inside them unedited. The evidence grade on each line is emphasised. The panel ends with the label's bottom row: the scoreboard as the label's own grade for itself.
- **Grades:** Strong, Moderate, Weak and Speculative each get their own black-ink mark. Any colour is extra, so nothing depends on it.
- **Known risk:** this is the familiar choice. It only works with real label discipline (exact rules, the label's own type sizes, dense rows), not as a vague "label-ish" style.

## 4. Scope and boundaries

- **What it is:** one production-ready static HTML/CSS page in `docs/`, published by GitHub Pages. `docs/` holds only the page and its own files. No build step and no JavaScript.
- **What doesn't change:** PROMO.md stays the source text. All wording and both output blocks are used word for word, in PROMO.md's section order: headline, promise, day 3 vs day 14, scoreboard, what I chose to build, what it isn't, how I built it, Try it.
- **Not allowed:** invented nutrition values, testimonials, app names, real dates, dates in captions or command lines, and wellness clichés (moon phases, cycle wheels, blush gradients). The label never makes a claim the tool doesn't make. "Not nutrition advice" stays visible.

## 5. Content and ranges

- **Fixed content:** two output blocks of 3 nutrient lines each, with lines up to about 85 characters (day 3 holds FDC IDs and a note line). The scoreboard has 4 numbers.
- **Season:** the day-3 note line and the food names change with the season. The layout must still work if the note line is missing (winter) or the foods are different. When the blocks are regenerated on demo day, only text changes.

## 6. Interaction and layout

- **Reading order:** top to bottom, one narrow column, the way a label is read. On phones the panel fills the width.
- **Long lines:** wide output lines never overflow on phones. They wrap at the line's own indent or scroll inside the block, but are never reworded.
- **Try it:** this is the page's action. It stays a template block with the bare flags and no copy button. Links to EVIDENCE.md and the repo are plain, clearly marked links.
- **Motion:** none needed. If any is added, it's at most one quiet entrance, turned off when the visitor's system asks for reduced motion.

## 7. Constraints and decisions

- **Accessibility:** output blocks stay real text (not images). There's a way to skip past each block, enough contrast on either ground, and a logical heading order.
- **Typeface:** a system font stack only. No font files, no external font host.
- **Privacy:** no tracking and no third-party requests.
- **No JavaScript:** there is no copy button.
- **Ground colour (open):** build two variants, a red ground and a strict black-on-white label, with Impeccable `generate`. The user picks one after seeing both.

# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Stack

The product itself is one Python 3.10+ file (`plan.py`) and one JSON rulebook (`nutrition_rules.json`), with no third-party dependencies. Its promo page is one static HTML file (plain HTML/CSS, no build step), published by GitHub Pages from `docs/`. `docs/` holds only the page and its own files.

## Users

A course/demo audience of classmates. They mostly open the promo page on their own from a shared link, on a laptop or a phone. It may also be shown briefly during a 5-minute demo.

## Product Purpose

A command-line cycle food planner. Given the start date of the last period and the cycle length (21 to 38 days), it names the day and phase, the nutrients that matter now, and one food for each. Each pick also shows how strong the evidence is for that phase–nutrient pairing. Success means a reader can say "it tells you when it's guessing".

## Positioning

The common "eat for your phase" promise is made with total confidence. This tool grades its own advice: Strong, Moderate, Weak or Speculative, shown next to every pick. It labels unfinished data `[placeholder]` instead of hiding it. Other apps are never named or quoted. The promise is described in the project's own words, and the counter-claim rests only on EVIDENCE.md.

## Operating Context

It runs in a terminal. Picks depend on the run date's season and on local history (`history.json`, `nutrients.md` in the folder it runs from), so foods rotate between cycles. Nothing leaves the computer. It was built spec-first with OpenSpec, and the decisions and steps are logged in PLANNING_LOG.md and PROCESS.md.

## Capabilities and Constraints

- Only the Menstrual phase has real food data (USDA FoodData Central entries with FDC IDs, amount per 100 g, % of the EU reference value). The other three phases use placeholder foods.
- Flags: `--exclude CATEGORY` and `--prefer-alternative NUTRIENT`.
- It is not medical or nutrition advice. Good evidence exists only for daily supplements for PMS or period pain, not for phase-timed food.
- The repository is public: invented dates only, no real cycle data, usernames or local paths.

## Brand Commitments

- Headline: "A cycle food planner that tells you when it's guessing."
- The page uses PROMO.md's wording and its unedited output blocks verbatim. Design changes only structure and emphasis.
- Sample captions use relative wording only, with no dates and no command lines.

## Evidence on Hand

- EVIDENCE.md: 12 phase–nutrient pairings checked against PubMed, Cochrane, NHS and EFSA, scored 2 Strong, 4 Moderate, 1 Weak and 5 Speculative.
- PROMO.md: two real, unedited output blocks (day 3 and day 14 of a 28-day cycle), generated with invented dates.
- There are no testimonials, users, logos, screenshots or outside studies. None may be invented.

## Product Principles

1. Honesty about evidence beats confident advice.
2. Show the tool's real output; never edit or stage it.
3. Unfinished parts are labelled, not hidden.
4. Private and local by design.

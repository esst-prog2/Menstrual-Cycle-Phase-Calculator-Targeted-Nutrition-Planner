# Process

One row per step: the step, what the tool did, and what the user decided.

| Date | Step | What the tool did | What I decided |
|------|------|-------------------|----------------|
| 2026-11-12 | Start a process record | Created PROCESS.md with this table, logged the rule in PLANNING_LOG.md, and committed on a new branch `process-log`. | After each step from now on, the tool commits and adds a row here. |
| 2026-11-12 | Write promo page content | Read the README and plan.py, then drafted PROMO.md: a headline, how it works in 3 steps, a sample Menstrual-day output, what makes it different, a "What it isn't" section with the evidence caveats, and how to try it. The example date is invented. | Asked for the promo page content. Audience and wording are open for review. |
| 2026-11-12 | Rewrite promo page for the demo audience | Noted that /office-hours isn't installed, asked who the page is for and what to change, then rewrote PROMO.md: a shorter and warmer pitch, the sample output, the design choices, the evidence caveats, and how it was built (OpenSpec, planning log, process log). The example date is invented. | The audience is the course/demo audience. Make it shorter and warmer. |
| 2026-11-12 | Install gstack for /office-hours | Read the official gstack README and install guide, listed what would be installed, from where and where it goes, then installed Bun to the home folder and cloned gstack into the user's Claude skills folder. Ran setup with team mode and the Stop hook turned off. Setup downloaded a headless Chromium to the user cache. Nothing was written into this repository. | Install it outside the repo, and skip the default Stop hook. |

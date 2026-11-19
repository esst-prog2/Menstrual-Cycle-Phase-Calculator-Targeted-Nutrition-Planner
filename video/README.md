# Promo video: Three cycles, one planner

A 30-second silent video for the promo page, written as HTML and rendered
with [HyperFrames](https://github.com/heygen-com/hyperframes) 0.9.70.
It needs Node.js 22+ and FFmpeg.

```
npm run check    # lint, layout and timing checks
npm run preview  # live preview in the browser
npm run render   # writes renders/three-cycles.mp4
```

## Where the text on screen comes from

Every terminal line in `index.html` is the real output of `plan.py`,
copied verbatim. The runs used `plan.main(argv, today=...)` (the same
hook the tests use) in an empty folder holding only `plan.py` and
`nutrition_rules.json`, so no real `history.json` was read or changed.
All dates are invented. The prompt is drawn as a bare `$ `.

| Scene | Arguments | "Today" |
| --- | --- | --- |
| Cycle 1 | `--last-period 2030-10-04 --cycle-length 28` | 2030-10-06 |
| Cycle 1, swap | the same plus `--prefer-alternative "vitamin c"` | 2030-10-06 |
| Cycle 2 | `--last-period 2030-11-01 --cycle-length 28` | 2030-11-03 |
| Cycle 3 | `--last-period 2030-11-29 --cycle-length 28` | 2030-12-01 |
| Cycle 3, exclusion | the same plus `--exclude meat` | 2030-12-01 |

The runs share one `history.json`, in this order, so cycles 2 and 3
rotate away from the earlier picks. The three-cycle table is the final
contents of that `history.json` (the last pick per nutrient per cycle),
laid out as a table; the tool itself does not print a table like it.

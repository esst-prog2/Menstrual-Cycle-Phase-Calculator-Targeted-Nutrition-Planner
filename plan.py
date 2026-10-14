"""Menstrual cycle phase calculator and targeted nutrient planner.

Usage: python plan.py --last-period YYYY-MM-DD --cycle-length N
                      [--exclude CATEGORY ...] [--prefer-alternative NUTRIENT]
"""

import argparse
import json
import re
import shutil
import sys
from dataclasses import dataclass, replace
from datetime import date
from pathlib import Path
from typing import NamedTuple

HERE = Path(__file__).resolve().parent

CATEGORIES = ["dairy", "eggs", "gluten", "nuts", "peanuts", "soy",
              "fish", "shellfish", "sesame", "meat", "pork"]
PHASES = ["Menstrual", "Follicular", "Ovulatory", "Luteal"]
SEASONS = ["winter", "spring", "summer", "autumn"]
MIN_CYCLE, MAX_CYCLE = 21, 38
MENSTRUAL_DAYS = 5
LUTEAL_LENGTH = 14          # ovulation_day = cycle_length - 14
GRACE_DAYS = 7              # a late period is tolerated for this many days
NUTRIENTS_PER_PHASE = 3
MIN_CANDIDATES = 5
NO_REPEAT_CYCLES = 2
HISTORY_ENTRIES = NO_REPEAT_CYCLES + 1   # current cycle plus the 2 before it
# Tiers for the per-claim "evidence" map in nutrition_rules.json. Foods are not ranked by
# evidence: no per-food evidence data exists yet.
EVIDENCE_RANK = {"Strong": 3, "Moderate": 2, "Weak": 1, "Speculative": 0}

DISCLAIMER = ("PLACEHOLDER DATA - not nutrition advice. Every food below comes from a "
              "stub database that has not been evidence-reviewed.")
NO_SOURCE = "no supporting source found"
SWAP_NOTE = "swapped in with --prefer-alternative"
REPEAT_NOTE = f"repeated: no other candidate was available within the last {NO_REPEAT_CYCLES} cycles"
NO_FOOD_NOTE = "no suitable food left because of your exclusions"
LATE_NOTE = ("period may be late: the cycle length has passed, so the Luteal phase "
             "is assumed until your next period starts")


class InputError(Exception):
    """A user input problem; main() reports it and exits without writing files."""


# ---------------------------------------------------------------- cycle math

def parse_iso_date(value):
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        raise argparse.ArgumentTypeError(f"invalid date format: '{value}' (expected YYYY-MM-DD)")
    try:
        return date.fromisoformat(value)
    except ValueError:
        raise argparse.ArgumentTypeError(f"invalid date format: '{value}' is not a real calendar date")


def parse_cycle_length(value):
    try:
        length = int(value)
    except ValueError:
        raise argparse.ArgumentTypeError(f"'{value}' is not a whole number of days")
    if not MIN_CYCLE <= length <= MAX_CYCLE:
        raise argparse.ArgumentTypeError(
            f"{length} is outside the supported range of {MIN_CYCLE}-{MAX_CYCLE} days")
    return length


def is_late(day, cycle_length):
    """The grace rule: a day past the cycle length (at most GRACE_DAYS past; cycle_day
    rejects later ones) is in the Luteal phase, and the period may be late."""
    return day > cycle_length


def cycle_day(last_period, today, cycle_length):
    """Return (day, is_late). Day is elapsed + 1, never wrapped into a new cycle."""
    elapsed = (today - last_period).days
    day = elapsed + 1
    if elapsed < 0:
        raise InputError(f"invalid date: --last-period {last_period.isoformat()} is in the future")
    if day > cycle_length + GRACE_DAYS:
        raise InputError(
            f"--last-period {last_period.isoformat()} is {elapsed} days ago, more than "
            f"{GRACE_DAYS} days past your {cycle_length}-day cycle (the {GRACE_DAYS}-day grace limit). "
            "Please enter the start date of your most recent period.")
    return day, is_late(day, cycle_length)


def phase_ranges(cycle_length):
    """Inclusive (first, last) day for each phase; Follicular may be empty (first > last)."""
    ovulation_day = cycle_length - LUTEAL_LENGTH
    return {
        "Menstrual": (1, MENSTRUAL_DAYS),
        "Follicular": (MENSTRUAL_DAYS + 1, ovulation_day - 2),
        "Ovulatory": (ovulation_day - 1, ovulation_day + 1),
        "Luteal": (ovulation_day + 2, cycle_length),
    }


def phase_for_day(day, cycle_length):
    if is_late(day, cycle_length):
        return "Luteal"
    for phase, (first, last) in phase_ranges(cycle_length).items():
        if first <= day <= last:
            return phase
    raise ValueError(f"day {day} is not in any phase of a {cycle_length}-day cycle")


def season_for(month):
    """Northern Hemisphere meteorological season: Dec-Feb winter, Mar-May spring, and so on."""
    return SEASONS[month % 12 // 3]


# ------------------------------------------------------- candidate selection

@dataclass
class Resolution:
    chosen: dict | None
    alternative: dict | None = None
    reason: str | None = None     # why the alternative lost; None on a full tie
    forced_repeat: bool = False
    swapped: bool = False


class NoAlternativeError(Exception):
    pass


class RankKey(NamedTuple):
    """Sort key for a candidate; fields in priority order, False ranks first."""
    repeats: bool
    out_of_season: bool


def _rank_key(candidate, recent_foods, season):
    return RankKey(repeats=candidate["food"] in recent_foods,
                   out_of_season=season not in candidate["seasons"])


def _deciding_reason(winner, loser, recent_foods, season):
    """Name the first constraint, in priority order, on which loser ranks below winner."""
    win_key = _rank_key(winner, recent_foods, season)
    lose_key = _rank_key(loser, recent_foods, season)
    if win_key.repeats != lose_key.repeats:
        if not lose_key.out_of_season and win_key.out_of_season:
            return "in season, but repeats a recent pick"
        return "repeats a recent pick"
    if win_key.out_of_season != lose_key.out_of_season:
        return "out of season"
    return None


def resolve_candidates(candidates, exclusions, recent_foods, prefer_alternative, season, keep=None):
    """Pick one food for a nutrient slot. Pure: all data comes in through arguments.

    Constraint order: exclusions (hard filter), then no-repeat within recent_foods,
    then seasonality. Ties keep list order. If `keep` names a food that is still
    allowed, that food is chosen (this cycle's saved pick); a "chosen over" reason is
    given only when the ranking agrees with it.
    """
    exclusions = set(exclusions)
    recent_foods = set(recent_foods)
    valid = [c for c in candidates if not exclusions & set(c["categories"])]
    if not valid:
        if prefer_alternative:
            raise NoAlternativeError("every candidate is excluded")
        return Resolution(chosen=None)

    ranked = sorted(valid, key=lambda c: _rank_key(c, recent_foods, season))
    top = ranked[0]
    runner_up = ranked[1] if len(ranked) > 1 else None
    kept = next((c for c in valid if c["food"] == keep), None)

    alternative = reason = None
    if prefer_alternative:
        if runner_up is None:
            raise NoAlternativeError("only one candidate remains")
        chosen, alternative = runner_up, top
    elif kept is not None and kept is not top:
        chosen = kept
    else:
        chosen = top
        if runner_up is not None:
            reason = _deciding_reason(top, runner_up, recent_foods, season)
            alternative = runner_up if reason else None
    # Repeats rank last, so a repeat is forced exactly when the top candidate repeats.
    return Resolution(chosen=chosen, alternative=alternative, reason=reason,
                      forced_repeat=_rank_key(top, recent_foods, season).repeats,
                      swapped=bool(prefer_alternative))


# ----------------------------------------------------------------- data I/O

def load_rules(path, warn):
    """Return (phases, evidence). Every nutrient must have an evidence tier, so no
    suggestion is ever shown without one; a source is required unless Speculative."""
    data = json.loads(Path(path).read_text())
    phases, evidence = data["phases"], data.get("evidence", {})
    name = Path(path).name
    for label, found in (("phases", phases), ("evidence", evidence)):
        if set(found) != set(PHASES):
            raise InputError(f"{name}: \"{label}\" must have exactly the phases {', '.join(PHASES)} "
                             f"(missing: {', '.join(sorted(set(PHASES) - set(found))) or 'none'}; "
                             f"unknown: {', '.join(sorted(set(found) - set(PHASES))) or 'none'})")
    for phase in PHASES:
        extra = set(evidence[phase]) - set(phases[phase])
        if extra:
            raise InputError(f"{name}: {phase}/{', '.join(sorted(extra))} has an evidence tier "
                             "but no foods in \"phases\"")
    for phase, nutrients in phases.items():
        if len(nutrients) != NUTRIENTS_PER_PHASE:
            warn(f"Warning: {phase} has {len(nutrients)} nutrients "
                 f"(expected {NUTRIENTS_PER_PHASE}).")
        for nutrient, candidates in nutrients.items():
            claim = evidence.get(phase, {}).get(nutrient)
            if not isinstance(claim, dict) or claim.get("tier") not in EVIDENCE_RANK:
                raise InputError(f"{name}: {phase}/{nutrient} has no evidence tier "
                                 f"(expected one of {', '.join(EVIDENCE_RANK)})")
            if (claim.get("source") is None) != (claim["tier"] == "Speculative"):
                raise InputError(f"{name}: {phase}/{nutrient} is {claim['tier']}, so its "
                                 "source must be " + ("null" if claim["tier"] == "Speculative" else "named"))
            for c in candidates:
                for field, allowed in (("categories", CATEGORIES), ("seasons", SEASONS)):
                    unknown = [v for v in c[field] if v not in allowed]
                    if unknown:
                        raise InputError(f"{name}: {phase}/{nutrient}/{c['food']} has unknown {field} "
                                         f"{', '.join(unknown)} (valid: {', '.join(allowed)})")
            if len(candidates) < MIN_CANDIDATES:
                warn(f"Warning: {phase}/{nutrient} has only {len(candidates)} candidate foods "
                     f"(minimum {MIN_CANDIDATES}); rotation may repeat foods sooner.")
    return phases, evidence


def _valid_history(data):
    if not isinstance(data, dict):
        return False
    for nutrients in data.values():
        if not isinstance(nutrients, dict):
            return False
        for entries in nutrients.values():
            if not isinstance(entries, list):
                return False
            for entry in entries:
                if not (isinstance(entry, dict) and isinstance(entry.get("cycle_start"), str)
                        and isinstance(entry.get("food"), str)):
                    return False
    return True


def load_history(path, warn, today):
    path = Path(path)
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text())
    except (json.JSONDecodeError, UnicodeDecodeError):
        data = None
    if data is not None and _valid_history(data):
        return data
    # Dated, and never overwrites an earlier backup: history.json.YYYY-MM-DD[-N].bak
    backup = path.with_name(f"{path.name}.{today.isoformat()}.bak")
    n = 2
    while backup.exists():
        backup = path.with_name(f"{path.name}.{today.isoformat()}-{n}.bak")
        n += 1
    shutil.copyfile(path, backup)
    warn(f"Warning: {path.name} could not be read, so it was backed up to {backup.name} "
         "and history starts fresh this run.")
    return {}


def save_history(path, history):
    Path(path).write_text(json.dumps(history, indent=2) + "\n")


# ------------------------------------------------------------------ planning

@dataclass
class Suggestion:
    nutrient: str
    resolution: Resolution
    evidence: dict      # {"tier": ..., "source": ... or None}


def plan_slot(nutrient, candidates, entries, cycle_start, exclusions, prefer, season):
    """Resolve one nutrient slot against its history entries (most recent first).

    Returns (Resolution, new_entries). new_entries is None when history for
    this slot should be left untouched.
    """
    same_cycle = bool(entries) and entries[0]["cycle_start"] == cycle_start
    previous = entries[1:] if same_cycle else entries
    recent_foods = [e["food"] for e in previous[:NO_REPEAT_CYCLES]]

    # Within a cycle, keep the saved pick while its food is still allowed.
    # Otherwise pick again and replace that cycle's entry.
    saved = entries[0] if same_cycle and not prefer else None
    res = resolve_candidates(candidates, exclusions, recent_foods, prefer, season,
                             keep=saved and saved["food"])
    if res.chosen is None:
        return res, None
    if saved and res.chosen["food"] == saved["food"]:
        return replace(res, swapped=bool(saved.get("swapped"))), None
    entry = {"cycle_start": cycle_start, "food": res.chosen["food"]}
    if res.swapped:
        entry["swapped"] = True
    if same_cycle:
        return res, [entry] + entries[1:HISTORY_ENTRIES]
    return res, ([entry] + entries)[:HISTORY_ENTRIES]


def item_notes(suggestion):
    res = suggestion.resolution
    if res.chosen is None:
        return [NO_FOOD_NOTE]
    notes = []
    if res.swapped:
        notes.append(SWAP_NOTE)
    elif res.alternative is not None:
        notes.append(f"chosen over {res.alternative['food']} - {res.reason}; swap with "
                     f"--prefer-alternative {suggestion.nutrient.lower()}")
    if res.forced_repeat:
        notes.append(REPEAT_NOTE)
    return notes


def food_label(suggestion):
    res = suggestion.resolution
    if res.chosen is None:
        return "(none)"
    label = " [placeholder]" if res.chosen.get("placeholder") is True else ""
    return res.chosen["food"] + label


def evidence_label(suggestion):
    return f"evidence: {suggestion.evidence['tier']}"


def evidence_detail(suggestion):
    return f"{suggestion.evidence['tier']} - {suggestion.evidence['source'] or NO_SOURCE}"


def render_terminal(day, cycle_length, phase, is_late, suggestions):
    lines = [DISCLAIMER, "", f"Day {day} of your {cycle_length}-day cycle: {phase} phase"]
    if is_late:
        lines.append(f"Note: {LATE_NOTE}")
    lines += ["", "Nutrients that matter now, and a food that contains each:"]
    for s in suggestions:
        lines.append(f"  {s.nutrient}: {food_label(s)} ({evidence_label(s)})")
        lines += [f"    note: {n}" for n in item_notes(s)]
    return "\n".join(lines) + "\n"


def render_markdown(day, cycle_length, phase, is_late, suggestions, today):
    lines = [f"# Nutrients for the {phase} phase", "",
             f"Generated {today.isoformat()} - day {day} of a {cycle_length}-day cycle.", "",
             f"> **{DISCLAIMER}**", ""]
    if is_late:
        lines += [f"> Note: {LATE_NOTE}", ""]
    lines += ["| Nutrient | Evidence | Food | Notes |", "| --- | --- | --- | --- |"]
    for s in suggestions:
        lines.append(f"| {s.nutrient} | {evidence_detail(s)} | {food_label(s)} | {'; '.join(item_notes(s))} |")
    return "\n".join(lines) + "\n"


def build_parser():
    parser = argparse.ArgumentParser(
        description="Show which nutrients matter in your current cycle phase, "
                    "and a food that contains each one.")
    parser.add_argument("--last-period", required=True, type=parse_iso_date, metavar="YYYY-MM-DD",
                        help="start date of your most recent period")
    parser.add_argument("--cycle-length", required=True, type=parse_cycle_length, metavar="DAYS",
                        help=f"your average cycle length, {MIN_CYCLE}-{MAX_CYCLE} days")
    parser.add_argument("--exclude", action="append", default=[], type=str.lower,
                        choices=CATEGORIES, metavar="CATEGORY",
                        help="leave out a food category (repeatable): " + ", ".join(CATEGORIES))
    parser.add_argument("--prefer-alternative", metavar="NUTRIENT",
                        help="swap this nutrient's food to its named alternative for the rest of the cycle")
    return parser


def main(argv=None, today=None, workdir=HERE, rules_path=None, out=sys.stdout, err=sys.stderr):
    parser = build_parser()
    args = parser.parse_args(argv)
    today = today or date.today()
    workdir = Path(workdir)
    warn = lambda msg: print(msg, file=err)

    try:
        day, is_late = cycle_day(args.last_period, today, args.cycle_length)
        phase = phase_for_day(day, args.cycle_length)
        rules, evidence = load_rules(rules_path or workdir / "nutrition_rules.json", warn)
        nutrients = rules[phase]

        prefer = None
        if args.prefer_alternative:
            names = {n.lower(): n for n in nutrients}
            prefer = names.get(args.prefer_alternative.lower())
            if prefer is None:
                raise InputError(f"--prefer-alternative: '{args.prefer_alternative}' is not tracked in the "
                                 f"{phase} phase (tracked: {', '.join(nutrients)})")

        history_path = workdir / "history.json"
        history = load_history(history_path, warn, today)
        cycle_start = args.last_period.isoformat()
        season = season_for(today.month)

        suggestions = []
        phase_history = dict(history.get(phase, {}))
        for nutrient, candidates in nutrients.items():
            try:
                res, new_entries = plan_slot(nutrient, candidates, phase_history.get(nutrient, []),
                                             cycle_start, args.exclude, nutrient == prefer, season)
            except NoAlternativeError as exc:
                raise InputError(f"--prefer-alternative {args.prefer_alternative}: no alternative "
                                 f"available for {nutrient} this cycle ({exc})")
            if new_entries is not None:
                phase_history[nutrient] = new_entries
            suggestions.append(Suggestion(nutrient, res, evidence[phase][nutrient]))
    except InputError as exc:
        parser.error(str(exc))

    if phase_history:
        history[phase] = phase_history
    save_history(history_path, history)
    (workdir / "nutrients.md").write_text(
        render_markdown(day, args.cycle_length, phase, is_late, suggestions, today))
    out.write(render_terminal(day, args.cycle_length, phase, is_late, suggestions))
    return 0


if __name__ == "__main__":
    sys.exit(main())

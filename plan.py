"""Menstrual cycle phase calculator and targeted nutrient planner.

Usage: python plan.py --last-period YYYY-MM-DD --cycle-length N
                      [--exclude CATEGORY ...] [--prefer-alternative NUTRIENT]
"""

import sys

# Checked before anything else runs: older versions fail on the `dict | None` syntax below.
if sys.version_info < (3, 10):
    sys.exit(f"plan.py needs Python 3.10 or newer; this is Python "
             f"{sys.version_info[0]}.{sys.version_info[1]}.")

import argparse
import json
import re
import shutil
from dataclasses import dataclass, replace
from datetime import date
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path
from typing import NamedTuple

HERE = Path(__file__).resolve().parent

CATEGORIES = ["dairy", "eggs", "gluten", "nuts", "peanuts", "soy",
              "fish", "shellfish", "sesame", "meat", "pork"]
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
EVIDENCE_TIERS = ["Strong", "Moderate", "Weak", "Speculative"]
FOOD_KEYS = ["food", "categories", "seasons", "placeholder", "fdc"]
FDC_KEYS = ["id", "description", "per_100g", "unit"]
CLAIM_KEYS = ["tier", "source"]
# A real food must be an EU "source of" its nutrient: at least 15% of the nutrient reference
# value (NRV) per 100 g. Regulation (EC) 1924/2006 Annex, with the significant amount and the
# NRVs from Regulation (EU) 1169/2011 Annex XIII Part A.
SOURCE_OF_PERCENT = 15
NRV = {"Iron": (14, "mg"), "Vitamin C": (80, "mg"), "Magnesium": (375, "mg")}

DISCLAIMER = ("Not nutrition advice. Foods marked [placeholder] come from a stub database "
              "that has not been evidence-reviewed.")
NO_SOURCE = "no supporting source found"
SWAP_NOTE = "swapped in with --prefer-alternative"
REPEAT_NOTE = f"repeated: no other candidate was available within the last {NO_REPEAT_CYCLES} cycles"
NO_FOOD_NOTE = "no suitable food left because of your exclusions"
NO_DATA_NOTE = "no foods for this nutrient in the data"
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
    if not re.fullmatch(r"[0-9]+", value):
        raise argparse.ArgumentTypeError(f"'{value}' is not a whole number of days (digits only)")
    length = int(value)
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


PHASES = list(phase_ranges(MIN_CYCLE))     # the one list of phases, in cycle order


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
    alternative: dict | None = None   # named in a "chosen over" note; None when swapped
    reason: str | None = None     # why the alternative lost; None on a full tie
    forced_repeat: bool = False
    swapped: bool = False
    no_data: bool = False         # the data has no foods at all for this nutrient


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
    if not candidates:
        if prefer_alternative:
            raise NoAlternativeError("there are no foods for this nutrient in the data")
        return Resolution(chosen=None, no_data=True)
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
        chosen = runner_up
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

def read_json(path):
    """Parse a JSON file as UTF-8. Any problem reading it becomes an InputError."""
    path = Path(path)
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise InputError(f"{path.name} was not found in {path.parent}")
    except OSError as exc:
        raise InputError(f"{path.name} could not be opened ({exc.strerror})")
    except UnicodeDecodeError:
        raise InputError(f"{path.name} is not valid UTF-8 text")
    except json.JSONDecodeError as exc:
        raise InputError(f"{path.name} is not valid JSON (line {exc.lineno}, column {exc.colno}: {exc.msg})")


def _check_rules_shape(data, name):
    """Stop with a clear error if the rules file does not have the expected structure."""
    def require(ok, where, what):
        if not ok:
            raise InputError(f"{name}: {where} must be {what}")
    require(isinstance(data, dict), "the file", "a JSON object")
    require(isinstance(data.get("phases"), dict), '"phases"', "an object")
    require(isinstance(data.get("evidence"), dict), '"evidence"', "an object")
    for label in ("phases", "evidence"):
        for phase, nutrients in data[label].items():
            require(isinstance(nutrients, dict), f'"{label}"/{phase}', "an object")
    for phase, nutrients in data["phases"].items():
        for nutrient, candidates in nutrients.items():
            require(isinstance(candidates, list), f"{phase}/{nutrient}", "a list of foods")
            for i, c in enumerate(candidates):
                where = f"{phase}/{nutrient} food {i + 1}"
                require(isinstance(c, dict), where, "an object")
                require(isinstance(c.get("food"), str), f'{where} "food"', "a string")
                where = f"{phase}/{nutrient}/{c['food']}"
                unknown = [k for k in c if k not in FOOD_KEYS]
                if unknown:
                    raise InputError(f"{name}: {where} has unknown key {', '.join(map(repr, unknown))}; "
                                     f"only {', '.join(FOOD_KEYS)}")
                for field in ("categories", "seasons"):
                    require(isinstance(c.get(field), list), f'{where} "{field}"', "a list")
                # A food is either a placeholder or real (has "fdc"), never both and never neither.
                if "fdc" not in c:
                    if c.get("placeholder") is not True:
                        raise InputError(f'{name}: {where} needs "placeholder": true or an "fdc" object')
                    continue
                if "placeholder" in c:
                    raise InputError(f'{name}: {where} has both "fdc" and "placeholder"; '
                                     "a real food has no placeholder flag")
                fdc, where = c["fdc"], f'{where} "fdc"'
                require(isinstance(fdc, dict), where, "an object")
                if set(fdc) != set(FDC_KEYS):
                    raise InputError(f"{name}: {where} must have exactly the keys {', '.join(FDC_KEYS)} "
                                     f"(missing: {', '.join(k for k in FDC_KEYS if k not in fdc) or 'none'}; "
                                     f"unknown: {', '.join(sorted(set(fdc) - set(FDC_KEYS))) or 'none'})")
                # type() rather than isinstance(): true and false are ints in Python.
                require(type(fdc["id"]) is int and fdc["id"] > 0, f'{where} "id"', "a positive whole number")
                require(isinstance(fdc["description"], str) and fdc["description"].strip(),
                        f'{where} "description"', "a non-empty string")
                require(type(fdc["per_100g"]) in (int, float) and fdc["per_100g"] >= 0,
                        f'{where} "per_100g"', "a number of at least 0")


def nrv_percent(nutrient, fdc):
    """Exact percentage of the NRV in 100 g. Decimal, so an amount on the threshold is not
    pushed below it by float rounding, and 66.5 can be rounded half up."""
    return Decimal(str(fdc["per_100g"])) * 100 / NRV[nutrient][0]


def _check_source_of(name, where, nutrient, fdc):
    """Stop unless a real food meets the EU "source of" threshold for its slot's nutrient."""
    if nutrient not in NRV:
        raise InputError(f'{name}: {where} has an "fdc" object, but {nutrient} has no "source of" '
                         f"threshold (only {', '.join(NRV)} have one)")
    nrv, unit = NRV[nutrient]
    if fdc["unit"] != unit:
        raise InputError(f"{name}: {where} has its amount in {fdc['unit']}, "
                         f"but the {nutrient} reference value is in {unit}")
    if nrv_percent(nutrient, fdc) < SOURCE_OF_PERCENT:
        threshold = Decimal(SOURCE_OF_PERCENT) * nrv / 100
        raise InputError(f"{name}: {where} has {fdc['per_100g']} {unit} {nutrient} per 100 g, below the "
                         f'EU "source of" threshold of {threshold} {unit} '
                         f"({SOURCE_OF_PERCENT}% of the {nrv} {unit} reference value)")


def load_rules(path, warn):
    """Return (phases, evidence). Every nutrient must have an evidence tier, so no
    suggestion is ever shown without one; a source is required unless Speculative."""
    name = Path(path).name
    data = read_json(path)
    _check_rules_shape(data, name)
    phases, evidence = data["phases"], data["evidence"]
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
            claim = evidence[phase].get(nutrient)
            if not isinstance(claim, dict) or claim.get("tier") not in EVIDENCE_TIERS:
                raise InputError(f"{name}: {phase}/{nutrient} has no evidence tier "
                                 f"(expected one of {', '.join(EVIDENCE_TIERS)})")
            unknown = [k for k in claim if k not in CLAIM_KEYS]
            if unknown:
                raise InputError(f"{name}: evidence {phase}/{nutrient} has unknown key "
                                 f"{', '.join(map(repr, unknown))}; only {', '.join(CLAIM_KEYS)}")
            # One rule for the source: required; null for Speculative, a non-empty string otherwise.
            if "source" not in claim:
                raise InputError(f"{name}: {phase}/{nutrient} has no \"source\" "
                                 "(use null when the tier is Speculative)")
            source = claim["source"]
            if claim["tier"] == "Speculative" and source is not None:
                raise InputError(f"{name}: {phase}/{nutrient} is Speculative, so its source must be null")
            if claim["tier"] != "Speculative" and not (isinstance(source, str) and source.strip()):
                raise InputError(f"{name}: {phase}/{nutrient} is {claim['tier']}, so its source must be "
                                 "named (a non-empty string)")
            for c in candidates:
                for field, allowed in (("categories", CATEGORIES), ("seasons", SEASONS)):
                    unknown = [v for v in c[field] if v not in allowed]
                    if unknown:
                        raise InputError(f"{name}: {phase}/{nutrient}/{c['food']} has unknown {field} "
                                         f"{', '.join(unknown)} (valid: {', '.join(allowed)})")
                if "fdc" in c:
                    _check_source_of(name, f"{phase}/{nutrient}/{c['food']}", nutrient, c["fdc"])
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
                        and isinstance(entry.get("food"), str)
                        and isinstance(entry.get("swapped", False), bool)):
                    return False
    return True


def load_history(path, warn, today):
    path = Path(path)
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        data = None                   # corrupt: backed up below
    except OSError as exc:
        # Cannot be read at all, so it cannot be backed up either: stop and leave it alone.
        raise InputError(f"{path.name} could not be opened ({exc.strerror}); it was left unchanged")
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
    Path(path).write_text(json.dumps(history, indent=2) + "\n", encoding="utf-8")


# ------------------------------------------------------------------ planning

@dataclass
class Suggestion:
    nutrient: str
    resolution: Resolution
    evidence: dict      # {"tier": ..., "source": ... or None}


def plan_slot(candidates, entries, cycle_start, exclusions, prefer, season):
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
        return [NO_DATA_NOTE if res.no_data else NO_FOOD_NOTE]
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
    fdc = res.chosen.get("fdc")
    if fdc is None:                                 # checked at load: then "placeholder" is true
        return res.chosen["food"] + " [placeholder]"
    percent = nrv_percent(suggestion.nutrient, fdc).quantize(Decimal(1), ROUND_HALF_UP)
    return (f"{res.chosen['food']} [{fdc['per_100g']} {fdc['unit']}/100 g, "
            f"{percent}% NRV, FDC {fdc['id']}]")


def evidence_label(suggestion):
    return f"evidence: {suggestion.evidence['tier']}"


def evidence_detail(suggestion):
    source = suggestion.evidence["source"]          # checked at load: None only for Speculative
    return f"{suggestion.evidence['tier']} - {NO_SOURCE if source is None else source}"


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


def main(argv=None, today=None, workdir=HERE, out=None, err=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    # Resolved at call time, so a caller's redirect of sys.stdout/sys.stderr is honoured.
    out = sys.stdout if out is None else out
    err = sys.stderr if err is None else err
    today = today or date.today()
    workdir = Path(workdir)
    warn = lambda msg: print(msg, file=err)

    try:
        day, is_late = cycle_day(args.last_period, today, args.cycle_length)
        phase = phase_for_day(day, args.cycle_length)
        rules, evidence = load_rules(workdir / "nutrition_rules.json", warn)
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
                res, new_entries = plan_slot(candidates, phase_history.get(nutrient, []),
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
    try:
        # nutrients.md first: if it cannot be written, the rotation is not advanced either.
        (workdir / "nutrients.md").write_text(
            render_markdown(day, args.cycle_length, phase, is_late, suggestions, today), encoding="utf-8")
        save_history(history_path, history)
    except OSError as exc:
        parser.error(f"{Path(exc.filename).name} could not be written ({exc.strerror})")
    out.write(render_terminal(day, args.cycle_length, phase, is_late, suggestions))
    return 0


if __name__ == "__main__":
    sys.exit(main())

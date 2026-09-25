import contextlib
import io
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import plan  # noqa: E402

TODAY = date(2026, 9, 25)   # autumn


def days_ago(n):
    return (TODAY - timedelta(days=n)).isoformat()


def food(name, cats=(), seasons=("winter", "spring", "summer", "autumn"), **extra):
    return {"food": name, "categories": list(cats), "seasons": list(seasons),
            "placeholder": True, "seasons_placeholder": True, **extra}


class Workspace(unittest.TestCase):
    """Each test gets a temp dir holding a copy of the real stub data."""

    def setUp(self):
        self.dir = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.dir)
        shutil.copy(ROOT / "nutrition_rules.json", self.dir)

    def run_plan(self, *argv, today=TODAY):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stderr(err):
            plan.main(list(argv), today=today, workdir=self.dir, out=out, err=err)
        return out.getvalue(), err.getvalue()

    def run_error(self, *argv, today=TODAY):
        err = io.StringIO()
        with contextlib.redirect_stderr(err), self.assertRaises(SystemExit) as cm:
            plan.main(list(argv), today=today, workdir=self.dir, out=io.StringIO(), err=err)
        self.assertNotEqual(cm.exception.code, 0)
        return err.getvalue()

    def history(self):
        return json.loads((self.dir / "history.json").read_text())

    def markdown(self):
        return (self.dir / "nutrients.md").read_text()

    def use_rules(self, phases):
        (self.dir / "nutrition_rules.json").write_text(json.dumps({"notice": "test", "phases": phases}))


# ------------------------------------------------------------------ 1. setup

class TestSetup(unittest.TestCase):
    def test_help_lists_all_flags(self):
        result = subprocess.run([sys.executable, str(ROOT / "plan.py"), "--help"],
                                capture_output=True, text=True, check=True)
        for flag in ("--last-period", "--cycle-length", "--exclude", "--prefer-alternative"):
            self.assertIn(flag, result.stdout)

    def test_rules_file_is_valid_json_with_phase_nutrient_shape(self):
        data = json.loads((ROOT / "nutrition_rules.json").read_text())
        for phase, nutrients in data["phases"].items():
            self.assertIn(phase, plan.PHASES)
            for candidates in nutrients.values():
                self.assertIsInstance(candidates, list)


# ------------------------------------------------------------ 2. cycle math

class TestInputValidation(Workspace):
    def test_non_iso_date_rejected_with_format_error(self):
        for bad in ("08/25/2026", "20260825", "2026-8-25", "2026-02-30"):
            err = self.run_error("--last-period", bad, "--cycle-length", "28")
            self.assertIn("invalid date format", err)

    def test_future_date_rejected(self):
        tomorrow = (TODAY + timedelta(days=1)).isoformat()
        err = self.run_error("--last-period", tomorrow, "--cycle-length", "28")
        self.assertIn("in the future", err)
        self.assertNotIn("invalid date format", err)
        self.assertFalse((self.dir / "nutrients.md").exists())

    def test_cycle_length_required(self):
        err = self.run_error("--last-period", days_ago(0))
        self.assertIn("--cycle-length", err)
        self.assertIn("required", err)

    def test_cycle_length_out_of_range(self):
        for bad in ("20", "39"):
            err = self.run_error("--last-period", days_ago(0), "--cycle-length", bad)
            self.assertIn("21-38", err)

    def test_cycle_length_boundaries_accepted(self):
        for ok in ("21", "38"):
            out, _ = self.run_plan("--last-period", days_ago(0), "--cycle-length", ok)
            self.assertIn(f"{ok}-day cycle", out)


class TestCycleMath(unittest.TestCase):
    def test_last_period_today_is_day_1(self):
        self.assertEqual(plan.cycle_day(TODAY, TODAY, 28), (1, False))

    def test_month_and_leap_year_boundaries(self):
        self.assertEqual(plan.cycle_day(date(2028, 2, 28), date(2028, 3, 1), 28), (3, False))
        self.assertEqual(plan.cycle_day(date(2026, 12, 30), date(2027, 1, 2), 28), (4, False))

    def test_28_day_cycle_day_15_is_ovulatory(self):
        self.assertEqual(plan.phase_for_day(15, 28), "Ovulatory")
        self.assertEqual(plan.phase_ranges(28)["Ovulatory"], (13, 15))

    def test_every_day_in_exactly_one_phase(self):
        for length in range(plan.MIN_CYCLE, plan.MAX_CYCLE + 1):
            ranges = plan.phase_ranges(length)
            for day in range(1, length + 1):
                owners = [p for p, (a, b) in ranges.items() if a <= day <= b]
                self.assertEqual(len(owners), 1, (length, day, owners))

    def test_21_day_cycle_has_empty_follicular(self):
        ranges = plan.phase_ranges(21)
        self.assertEqual(ranges["Menstrual"], (1, 5))
        self.assertEqual(ranges["Ovulatory"], (6, 8))
        self.assertEqual(ranges["Luteal"], (9, 21))
        first, last = ranges["Follicular"]
        self.assertGreater(first, last)
        self.assertEqual([plan.phase_for_day(d, 21) for d in range(1, 22)],
                         ["Menstrual"] * 5 + ["Ovulatory"] * 3 + ["Luteal"] * 13)

    def test_grace_window_forces_luteal(self):
        day, late = plan.cycle_day(TODAY - timedelta(days=30), TODAY, 28)
        self.assertEqual((day, late), (31, True))
        self.assertEqual(plan.phase_for_day(day, 28), "Luteal")
        # Last day of grace: elapsed = 28 + 7 - 1
        self.assertEqual(plan.cycle_day(TODAY - timedelta(days=34), TODAY, 28), (35, True))

    def test_past_grace_window_rejected(self):
        with self.assertRaises(plan.InputError) as cm:
            plan.cycle_day(TODAY - timedelta(days=35), TODAY, 28)
        self.assertIn("7-day grace limit", str(cm.exception))


class TestCycleEndToEnd(Workspace):
    def test_21_day_cycle_every_day_runs(self):
        for elapsed in range(21):
            out, _ = self.run_plan("--last-period", days_ago(elapsed), "--cycle-length", "21")
            self.assertNotIn("Follicular", out)

    def test_grace_window_note_in_both_outputs(self):
        out, _ = self.run_plan("--last-period", days_ago(30), "--cycle-length", "28")
        self.assertIn("Luteal phase", out)
        self.assertIn("period may be late", out)
        self.assertIn("period may be late", self.markdown())

    def test_past_grace_window_rejected_end_to_end(self):
        err = self.run_error("--last-period", days_ago(35), "--cycle-length", "28")
        self.assertIn("grace limit", err)


# ------------------------------------------------------------ 3. stub data

class TestStubData(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads((ROOT / "nutrition_rules.json").read_text())
        cls.entries = [c for n in cls.data["phases"].values() for cs in n.values() for c in cs]

    def test_three_nutrients_per_phase_and_five_candidates_per_slot(self):
        self.assertEqual(sorted(self.data["phases"]), sorted(plan.PHASES))
        for phase, nutrients in self.data["phases"].items():
            self.assertEqual(len(nutrients), plan.NUTRIENTS_PER_PHASE, phase)
            for nutrient, candidates in nutrients.items():
                self.assertGreaterEqual(len(candidates), plan.MIN_CANDIDATES, (phase, nutrient))

    def test_every_entry_is_placeholder_with_no_evidence_label(self):
        labels = set(plan.EVIDENCE_RANK)
        for entry in self.entries:
            self.assertIs(entry["placeholder"], True)
            self.assertNotIn("evidence", entry)
            self.assertFalse(labels & {str(v) for v in entry.values()}, entry)

    def test_every_entry_has_placeholder_season(self):
        for entry in self.entries:
            self.assertTrue(entry["seasons"], entry)
            self.assertTrue(set(entry["seasons"]) <= {"winter", "spring", "summer", "autumn"})
            self.assertIs(entry["seasons_placeholder"], True)

    def test_category_tags_from_fixed_set_and_pork_is_meat(self):
        for entry in self.entries:
            self.assertIsInstance(entry["categories"], list)
            self.assertTrue(set(entry["categories"]) <= set(plan.CATEGORIES), entry)
            if "pork" in entry["categories"]:
                self.assertIn("meat", entry["categories"])
        self.assertTrue(any("pork" in e["categories"] for e in self.entries))


# ------------------------------------------------- 4. candidate resolution

class TestResolveCandidates(unittest.TestCase):
    def test_strong_evidence_outranks_new_and_in_season(self):
        # Constraint #2 tie-break, synthetic fixtures only.
        cands = [food("weak-new", evidence="Weak"),
                 food("strong-old", seasons=["summer"], evidence="Strong")]
        res = plan.resolve_candidates(cands, [], ["strong-old"], False, "autumn")
        self.assertEqual(res.chosen["food"], "strong-old")
        self.assertEqual(res.alternative["food"], "weak-new")
        self.assertIn("weaker evidence", res.reason)
        self.assertFalse(res.forced_repeat)

    def test_excluded_food_never_returned_even_when_top_ranked(self):
        cands = [food("yogurt", ["dairy"], evidence="Strong"), food("kale", seasons=["summer"])]
        res = plan.resolve_candidates(cands, ["dairy"], ["kale"], False, "autumn")
        self.assertEqual(res.chosen["food"], "kale")
        self.assertIsNone(res.alternative)

    def test_untagged_food_never_excluded(self):
        res = plan.resolve_candidates([food("spinach")], plan.CATEGORIES, [], False, "autumn")
        self.assertEqual(res.chosen["food"], "spinach")

    def test_single_candidate_has_no_alternative(self):
        res = plan.resolve_candidates([food("a", ["nuts"]), food("b")], ["nuts"], [], False, "autumn")
        self.assertEqual(res.chosen["food"], "b")
        self.assertIsNone(res.alternative)
        self.assertIsNone(res.reason)

    def test_no_repeat_outranks_seasonality_with_real_reason(self):
        cands = [food("in-season-old", seasons=["autumn"]), food("off-season-new", seasons=["summer"])]
        res = plan.resolve_candidates(cands, [], ["in-season-old"], False, "autumn")
        self.assertEqual(res.chosen["food"], "off-season-new")
        self.assertEqual(res.alternative["food"], "in-season-old")
        self.assertEqual(res.reason, "in season, but repeats a recent pick")

    def test_seasonality_reason(self):
        cands = [food("off", seasons=["summer"]), food("on", seasons=["autumn"])]
        res = plan.resolve_candidates(cands, [], [], False, "autumn")
        self.assertEqual(res.chosen["food"], "on")
        self.assertEqual(res.reason, "out of season")

    def test_plain_repeat_reason(self):
        cands = [food("old"), food("new")]
        res = plan.resolve_candidates(cands, [], ["old"], False, "autumn")
        self.assertEqual((res.chosen["food"], res.reason), ("new", "repeats a recent pick"))

    def test_full_tie_has_no_alternative_note_but_can_swap(self):
        cands = [food("a"), food("b")]
        res = plan.resolve_candidates(cands, [], [], False, "autumn")
        self.assertEqual(res.chosen["food"], "a")
        self.assertIsNone(res.alternative)
        swapped = plan.resolve_candidates(cands, [], [], True, "autumn")
        self.assertEqual(swapped.chosen["food"], "b")

    def test_prefer_alternative_swaps(self):
        cands = [food("off", seasons=["summer"]), food("on", seasons=["autumn"])]
        res = plan.resolve_candidates(cands, [], [], True, "autumn")
        self.assertEqual(res.chosen["food"], "off")
        self.assertEqual(res.alternative["food"], "on")
        self.assertTrue(res.swapped)

    def test_prefer_alternative_without_alternative_raises(self):
        with self.assertRaises(plan.NoAlternativeError):
            plan.resolve_candidates([food("only")], [], [], True, "autumn")

    def test_all_excluded_returns_empty_slot(self):
        res = plan.resolve_candidates([food("x", ["fish"]), food("y", ["fish", "meat"])],
                                      ["fish"], [], False, "autumn")
        self.assertIsNone(res.chosen)

    def test_forced_repeat_flagged(self):
        res = plan.resolve_candidates([food("a"), food("b")], [], ["a", "b"], False, "autumn")
        self.assertTrue(res.forced_repeat)

    def test_is_pure(self):
        cands = [food("a", seasons=["summer"]), food("b")]
        snapshot = json.dumps(cands)
        plan.resolve_candidates(cands, ["nuts"], ["a"], False, "autumn")
        self.assertEqual(json.dumps(cands), snapshot)


class TestSelectionEndToEnd(Workspace):
    # Day 15 of a 28-day cycle -> Ovulatory: Fiber, Zinc, Omega-3.
    OVULATORY = ("--last-period", days_ago(14), "--cycle-length", "28")

    def test_prefer_alternative_swaps_only_named_nutrient(self):
        base, _ = self.run_plan(*self.OVULATORY)
        shutil.rmtree(self.dir); self.dir.mkdir()
        shutil.copy(ROOT / "nutrition_rules.json", self.dir)
        swapped, _ = self.run_plan(*self.OVULATORY, "--prefer-alternative", "zinc")
        base_lines = dict(l.strip().split(": ", 1) for l in base.splitlines() if l.startswith("  ") and ": " in l and "note" not in l)
        swap_lines = dict(l.strip().split(": ", 1) for l in swapped.splitlines() if l.startswith("  ") and ": " in l and "note" not in l)
        self.assertNotEqual(base_lines["Zinc"], swap_lines["Zinc"])
        self.assertEqual(base_lines["Fiber"], swap_lines["Fiber"])
        self.assertEqual(base_lines["Omega-3"], swap_lines["Omega-3"])

    def test_prefer_alternative_no_alternative_errors(self):
        # Only pumpkin seeds survives these exclusions for Zinc.
        err = self.run_error(*self.OVULATORY, "--exclude", "shellfish", "--exclude", "meat",
                             "--exclude", "dairy", "--prefer-alternative", "zinc")
        self.assertIn("no alternative available for Zinc", err)
        self.assertFalse((self.dir / "nutrients.md").exists())

    def test_prefer_alternative_unknown_nutrient_errors(self):
        err = self.run_error(*self.OVULATORY, "--prefer-alternative", "iron")
        self.assertIn("not tracked in the Ovulatory phase", err)

    def test_all_candidates_excluded_note_in_both_outputs(self):
        self.use_rules({p: {"A": [food("a1", ["fish"]), food("a2", ["fish"])],
                            "B": [food("b1")], "C": [food("c1")]} for p in plan.PHASES})
        out, _ = self.run_plan(*self.OVULATORY, "--exclude", "fish")
        self.assertIn(plan.NO_FOOD_NOTE, out)
        self.assertIn("b1", out)
        self.assertIn("c1", out)
        self.assertIn(plan.NO_FOOD_NOTE, self.markdown())

    def test_thin_slot_warns_but_runs(self):
        self.use_rules({p: {"A": [food("a1"), food("a2")], "B": [food(f"b{i}") for i in range(5)],
                            "C": [food(f"c{i}") for i in range(5)]} for p in plan.PHASES})
        out, err = self.run_plan(*self.OVULATORY)
        self.assertIn("Ovulatory/A has only 2 candidate foods", err)
        self.assertIn("a1", out)
        self.assertTrue((self.dir / "nutrients.md").exists())


# ------------------------------------------------------- 5. rotation history

class TestHistory(Workspace):
    def ovulatory(self, cycles_back=0, *extra):
        """Day 15 of a 28-day cycle, `cycles_back` whole cycles ago."""
        today = TODAY - timedelta(days=28 * cycles_back)
        return self.run_plan("--last-period", (today - timedelta(days=14)).isoformat(),
                             "--cycle-length", "28", *extra, today=today)

    def test_round_trip(self):
        path = self.dir / "history.json"
        data = {"Luteal": {"Calcium": [{"cycle_start": "2026-09-01", "food": "kale"},
                                       {"cycle_start": "2026-08-04", "food": "yogurt"}]}}
        plan.save_history(path, data)
        self.assertEqual(plan.load_history(path, lambda m: self.fail(m)), data)

    def test_missing_history_is_created_without_error(self):
        _, err = self.ovulatory()
        self.assertEqual(err, "")
        self.assertEqual(set(self.history()["Ovulatory"]), {"Fiber", "Zinc", "Omega-3"})

    def test_identical_rerun_reuses_pick_and_leaves_history_unchanged(self):
        first, _ = self.ovulatory()
        before = (self.dir / "history.json").read_text()
        second, _ = self.ovulatory()
        self.assertEqual(first, second)
        self.assertEqual(before, (self.dir / "history.json").read_text())

    def test_rerun_with_new_exclusion_updates_in_place(self):
        self.ovulatory()
        omega = self.history()["Ovulatory"]["Omega-3"][0]["food"]
        self.assertEqual(omega, "salmon")
        out, _ = self.ovulatory(0, "--exclude", "fish")
        self.assertNotIn("salmon", out)
        entries = self.history()["Ovulatory"]["Omega-3"]
        self.assertEqual(len(entries), 1)
        self.assertNotEqual(entries[0]["food"], "salmon")

    def test_repeat_avoided_across_two_cycles(self):
        picks = []
        for back in (2, 1, 0):
            self.ovulatory(back)
            picks.append(self.history()["Ovulatory"]["Zinc"][0]["food"])
        self.assertEqual(len(set(picks)), 3, picks)
        entries = self.history()["Ovulatory"]["Zinc"]
        self.assertEqual([e["food"] for e in entries], picks[::-1])

    def test_fourth_cycle_evicts_oldest_keeping_three(self):
        picks = []
        for back in (3, 2, 1, 0):
            self.ovulatory(back)
            picks.append(self.history()["Ovulatory"]["Zinc"][0]["food"])
        entries = self.history()["Ovulatory"]["Zinc"]
        self.assertEqual([e["food"] for e in entries], picks[:0:-1])

    def test_same_cycle_recompute_still_avoids_both_earlier_cycles(self):
        self.use_rules({p: {"A": [food("a1"), food("a2"), food("a3", ["fish"]), food("a4")],
                            "B": [food(f"b{i}") for i in range(5)],
                            "C": [food(f"c{i}") for i in range(5)]} for p in plan.PHASES})
        self.ovulatory(2)                                      # a1
        self.ovulatory(1)                                      # a2
        self.ovulatory(0)                                      # a3
        self.assertEqual([e["food"] for e in self.history()["Ovulatory"]["A"]], ["a3", "a2", "a1"])
        out, _ = self.ovulatory(0, "--exclude", "fish")        # a3 removed -> must skip a1 and a2
        self.assertIn("A: a4 [placeholder]", out)
        self.assertEqual([e["food"] for e in self.history()["Ovulatory"]["A"]], ["a4", "a2", "a1"])

    def test_forced_repeat_note_in_both_outputs(self):
        self.use_rules({p: {"A": [food("a1"), food("a2")], "B": [food(f"b{i}") for i in range(5)],
                            "C": [food(f"c{i}") for i in range(5)]} for p in plan.PHASES})
        self.ovulatory(2)
        self.ovulatory(1)
        out, _ = self.ovulatory(0)
        self.assertIn(plan.REPEAT_NOTE, out)
        self.assertIn(plan.REPEAT_NOTE, self.markdown())
        self.assertEqual(out.count(plan.REPEAT_NOTE), 1)       # only slot A

    def test_corrupt_history_backed_up_and_reset(self):
        (self.dir / "history.json").write_text("{not json")
        out, err = self.ovulatory()
        self.assertEqual((self.dir / "history.json.bak").read_text(), "{not json")
        self.assertIn("could not be read", err)
        self.assertNotIn("could not be read", out)
        self.assertNotIn("history", self.markdown().lower())
        self.assertIn("Ovulatory", self.history())

    def test_wrong_shape_history_treated_as_corrupt(self):
        (self.dir / "history.json").write_text('{"Ovulatory": ["salmon"]}')
        _, err = self.ovulatory()
        self.assertIn("could not be read", err)
        self.assertTrue((self.dir / "history.json.bak").exists())

    def test_prefer_alternative_persists_for_the_cycle(self):
        swapped, _ = self.ovulatory(0, "--prefer-alternative", "zinc")
        zinc = self.history()["Ovulatory"]["Zinc"]
        self.assertEqual(len(zinc), 1)
        self.assertTrue(zinc[0]["swapped"])
        later, _ = self.ovulatory()
        self.assertIn(f"Zinc: {zinc[0]['food']} [placeholder]", later)
        self.assertEqual(swapped, later)
        self.assertEqual(len(self.history()["Ovulatory"]["Zinc"]), 1)

    def test_new_cycle_after_swap_rotates_normally(self):
        self.ovulatory(1, "--prefer-alternative", "zinc")
        self.ovulatory(0)
        entries = self.history()["Ovulatory"]["Zinc"]
        self.assertEqual(len(entries), 2)                      # both cycles kept (cap is 3)
        self.assertNotIn("swapped", entries[0])
        self.assertNotEqual(entries[0]["food"], entries[1]["food"])


# -------------------------------------------------------------- 6. output

class TestOutput(Workspace):
    OVULATORY = ("--last-period", days_ago(14), "--cycle-length", "28")

    def test_markdown_lists_all_three_nutrients(self):
        self.run_plan(*self.OVULATORY)
        md = self.markdown()
        for nutrient in ("Fiber", "Zinc", "Omega-3"):
            self.assertIn(f"| {nutrient} |", md)

    def test_disclaimer_and_placeholder_labels_in_both(self):
        out, _ = self.run_plan(*self.OVULATORY)
        md = self.markdown()
        for text in (out, md):
            self.assertEqual(text.count(plan.DISCLAIMER), 1)
            self.assertEqual(text.count("[placeholder]"), 3)

    def test_alternative_note_with_real_reason_in_both(self):
        self.use_rules({p: {"Fiber": [food("raspberries", seasons=["summer"]),
                                      food("pears", seasons=["autumn"])],
                            "B": [food("b1")], "C": [food("c1")]} for p in plan.PHASES})
        out, _ = self.run_plan(*self.OVULATORY)
        note = "chosen over raspberries - out of season; swap with --prefer-alternative fiber"
        self.assertIn("Fiber: pears", out)
        self.assertIn(note, out)
        self.assertIn(note, self.markdown())

    def test_unknown_exclude_category_lists_valid_ones(self):
        err = self.run_error(*self.OVULATORY, "--exclude", "diary")
        self.assertIn("diary", err)
        for category in plan.CATEGORIES:
            self.assertIn(category, err)
        self.assertFalse((self.dir / "nutrients.md").exists())
        self.assertFalse((self.dir / "history.json").exists())

    def test_valid_exclude_removes_category_everywhere(self):
        data = json.loads((self.dir / "nutrition_rules.json").read_text())
        fish = {c["food"] for n in data["phases"].values() for cs in n.values()
                for c in cs if "fish" in c["categories"]}
        for phase_args in (("--last-period", days_ago(d), "--cycle-length", "28") for d in (0, 8, 14, 20)):
            out, _ = self.run_plan(*phase_args, "--exclude", "FISH")
            for name in fish:
                self.assertNotIn(name, out)
                self.assertNotIn(name, self.markdown())


# ------------------------------------------------------------ 7. gitignore

class TestGitignore(Workspace):
    def test_history_files_ignored(self):
        for name in ("history.json", "history.json.bak", "nutrients.md"):
            result = subprocess.run(["git", "check-ignore", name], cwd=ROOT,
                                    capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, name)


if __name__ == "__main__":
    unittest.main()

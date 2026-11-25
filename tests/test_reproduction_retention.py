import contextlib
import io
from pathlib import Path
import subprocess
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from script import run_all


class ReproductionRetentionTests(unittest.TestCase):
    def setUp(self):
        root = self.enterContext(TemporaryDirectory())
        self.output = Path(root) / "reproduction"
        self.enterContext(contextlib.redirect_stdout(io.StringIO()))
        self.enterContext(patch.object(run_all, "stage_inputs", return_value=None))

    def run_fixture(self, value, **options):
        def save(run, *, keep_full):
            (run / "tables").mkdir()
            (run / "tables/value.txt").write_text(value, encoding="utf-8")
            if not keep_full:
                (run / "work").rmdir()

        with patch.object(run_all, "pipeline_tasks", return_value=[]):
            with patch.object(run_all, "save_results", side_effect=save):
                run_all.reproduce(self.output, **options)

    def test_next_success_replaces_latest_and_removes_numbered_runs(self):
        previous = self.output / "run_06"
        previous.mkdir(parents=True)
        (previous / "status.txt").write_text("완료\n", encoding="utf-8")
        self.run_fixture("first", keep_full=True)
        self.assertTrue((self.output / "latest/work").is_dir())
        self.run_fixture("second")
        self.assertEqual({path.name for path in self.output.iterdir()}, {"latest"})
        self.assertEqual((self.output / "latest/tables/value.txt").read_text(encoding="utf-8"), "second")
        self.assertFalse((self.output / "latest/work").exists())

    def test_failed_analysis_preserves_last_success(self):
        self.run_fixture("good")
        with patch.object(run_all, "stage_inputs", side_effect=subprocess.CalledProcessError(1, "preprocess")):
            with self.assertRaises(subprocess.CalledProcessError):
                run_all.reproduce(self.output)
        self.assertEqual({path.name for path in self.output.iterdir()}, {"latest"})
        self.assertEqual((self.output / "latest/tables/value.txt").read_text(encoding="utf-8"), "good")

    def test_failed_replacement_restores_previous_result(self):
        self.run_fixture("good")
        rename = Path.rename

        def fail_publish(path, target):
            if path.name == "result":
                raise PermissionError("simulated failure while replacing latest")
            return rename(path, target)

        with patch.object(Path, "rename", fail_publish):
            with self.assertRaises(PermissionError):
                self.run_fixture("new")
        self.assertEqual({path.name for path in self.output.iterdir()}, {"latest"})
        self.assertEqual((self.output / "latest/tables/value.txt").read_text(encoding="utf-8"), "good")

    def test_dry_run_creates_no_result_directory(self):
        run_all.reproduce(self.output, dry_run=True)
        self.assertFalse(self.output.exists())

    def test_second_execution_cannot_touch_in_progress_run(self):
        active = self.output / ".running"
        active.mkdir(parents=True)
        (active / "marker").touch()
        with self.assertRaisesRegex(FileExistsError, "[.]running"):
            self.run_fixture("second")
        self.assertTrue((active / "marker").is_file())

    def test_unrelated_latest_is_not_overwritten(self):
        unrelated = self.output / "latest"
        unrelated.mkdir(parents=True)
        (unrelated / "notes.txt").touch()
        with self.assertRaisesRegex(ValueError, "latest"):
            self.run_fixture("run")
        self.assertTrue((unrelated / "notes.txt").is_file())

import argparse
import csv
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from scripts import voxtral_voice_clone_api
from scripts import publish_check
from scripts import voice_lab


class VoiceLabParsingTests(unittest.TestCase):
    def test_parse_duration_to_seconds(self):
        self.assertEqual(voice_lab.parse_duration_to_seconds("00:01:02.500"), 62.5)

    def test_parse_tts_metrics(self):
        output = """
        Audio successfully generated and saving as: ./runs/demo/audio/test_000.wav
        Duration:              00:00:04.160
        Real-time factor:      1.73x
        Processing time:       2.23s
        Peak memory usage:     6.58GB
        """
        metrics = voice_lab.parse_tts_metrics(output)
        self.assertEqual(metrics["output_audio_duration_sec"], 4.16)
        self.assertEqual(metrics["processing_time_sec"], 2.23)
        self.assertEqual(metrics["rtfx"], 1.73)
        self.assertEqual(metrics["peak_memory_gb"], 6.58)
        self.assertEqual(len(metrics["output_files"]), 1)

    def test_parse_stt_metrics(self):
        output = """
        Saving file to: ./runs/demo/transcripts/parakeet_transcript.txt
        Processing time: 22.96 seconds
        Peak memory: 0.56 GB
        """
        metrics = voice_lab.parse_stt_metrics(output)
        self.assertEqual(metrics["processing_time_sec"], 22.96)
        self.assertEqual(metrics["peak_memory_gb"], 0.56)
        self.assertEqual(len(metrics["output_files"]), 1)

    def test_parse_stt_metrics_preserves_absolute_output_path(self):
        output = "Saving file to: /tmp/parakeet_transcript.txt"
        metrics = voice_lab.parse_stt_metrics(output)
        self.assertEqual(metrics["output_files"], ["/tmp/parakeet_transcript.txt"])

    def test_validate_slug_rejects_path_traversal(self):
        with self.assertRaises(SystemExit):
            voice_lab.validate_slug("../bad", "run id")
        with self.assertRaises(SystemExit):
            voice_lab.validate_slug("bad/name", "file prefix")

    def test_display_path_redacts_repo_root(self):
        self.assertEqual(
            voice_lab.display_path(voice_lab.ROOT / "runs" / "demo.wav"),
            "runs/demo.wav",
        )

    def test_custom_reference_requires_explicit_consent(self):
        args = argparse.Namespace(
            ref_audio="voice.wav",
            ref_text="hello",
            confirm_consent=False,
        )
        with self.assertRaises(SystemExit):
            voice_lab.resolve_reference(args)

    def test_csv_roundtrip_fields(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "results.csv"
            with path.open("w", newline="", encoding="utf-8") as fh:
                writer = csv.DictWriter(fh, fieldnames=voice_lab.CSV_FIELDS)
                writer.writeheader()
                writer.writerow({field: "" for field in voice_lab.CSV_FIELDS})
            with path.open(encoding="utf-8") as fh:
                rows = list(csv.DictReader(fh))
            self.assertEqual(set(rows[0]), set(voice_lab.CSV_FIELDS))

    def test_publish_check_allows_current_tracked_files(self):
        failures = publish_check.run_checks()
        self.assertEqual(failures, [])

    def test_read_tracked_text_prefers_git_index(self):
        with mock.patch("scripts.publish_check.subprocess.run") as run_mock:
            run_mock.return_value = mock.Mock(returncode=0, stdout="indexed text")
            text = publish_check.read_tracked_text("README.md")
        self.assertEqual(text, "indexed text")

    def test_sample_tts_commands_include_required_arguments(self):
        sample = voice_lab.ROOT / "reports" / "sample_voice_lab_results.csv"
        with sample.open(encoding="utf-8") as fh:
            rows = list(csv.DictReader(fh))
        for row in rows:
            if row["task"] in {"voxtral-tts", "qwen3-clone", "higgs-clone"}:
                command = row["command"]
                self.assertIn("--text", command)
                self.assertIn("--output_path", command)

    def test_api_reference_audio_rejects_unsupported_suffix(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "voice.txt"
            path.write_text("not audio", encoding="utf-8")
            with self.assertRaises(SystemExit):
                voxtral_voice_clone_api.validate_reference_audio(path, max_mb=20)

    def test_read_only_main_command_does_not_create_artifact_dirs(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            old_cwd = Path.cwd()
            old_argv = list(os.sys.argv)
            try:
                os.chdir(tmpdir)
                os.sys.argv = ["voice-lab", "models"]
                with mock.patch("builtins.print"):
                    voice_lab.main()
                self.assertFalse((Path(tmpdir) / "reports").exists())
                self.assertFalse((Path(tmpdir) / "runs").exists())
                self.assertFalse((Path(tmpdir) / "artifacts").exists())
            finally:
                os.sys.argv = old_argv
                os.chdir(old_cwd)


if __name__ == "__main__":
    unittest.main()

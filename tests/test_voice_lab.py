import argparse
import csv
import tempfile
import unittest
from pathlib import Path

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


if __name__ == "__main__":
    unittest.main()

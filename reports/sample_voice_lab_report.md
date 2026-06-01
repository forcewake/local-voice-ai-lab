# Local Voice AI Lab Sample Report

This is a sanitized example report for GitHub readers. Local generated reports
are intentionally ignored because they can contain machine paths, private
transcripts, and benchmark artifacts.

## Environment

- Platform: `macOS arm64`
- Python: `3.12`
- Runner: `MLX-Audio`

## Sample Results

| run_id | task | status | model | wall_time_sec | RTFx | peak_memory_gb | output |
| --- | --- | --- | --- | ---: | ---: | ---: | --- |
| 20260601_smoke | voxtral-tts | ok | Voxtral-4B-TTS-2603-mlx-4bit | 4.2675 | 3.4700 | 2.7600 | `voxtral_tts_000.wav` |
| 20260601_smoke | qwen3-clone | ok | Qwen3-TTS-12Hz-0.6B-Base-bf16 | 3.9713 | 1.7300 | 6.5800 | `qwen3_clone_000.wav` |
| 20260601_smoke | parakeet-small | ok | parakeet-tdt_ctc-110m | 31.7399 | 0.1512 | 0.5600 | `parakeet_transcript.txt` |
| 20260601_all | higgs-clone | ok | higgs-audio-v2-3B-mlx-q6 | 64.2490 | 0.9900 | 6.5100 | `higgs_clone_000.wav` |

## How To Reproduce Locally

```bash
make setup
.venv/bin/python scripts/voice_lab.py doctor
make smoke
make all
make report
```

Generated local artifacts are written under ignored `runs/`, `artifacts/`, and
`reports/voice_lab_*` paths.

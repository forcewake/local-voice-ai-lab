# Benchmark Methodology

This lab is designed for repeatable local smoke benchmarks, not universal model
leaderboard claims.

## Metrics

| metric | meaning |
| --- | --- |
| `wall_time_sec` | End-to-end subprocess runtime measured by the lab wrapper. |
| `processing_time_sec` | Model runner processing time when MLX-Audio reports it. |
| `input_audio_duration_sec` | Duration of reference or transcription input audio. |
| `output_audio_duration_sec` | Duration of generated TTS output audio. |
| `rtfx` | Audio duration divided by processing/wall time, depending on task. Higher is faster. |
| `peak_memory_gb` | MLX peak memory as reported by MLX-Audio. |
| `model_size_gib` | Local Hugging Face snapshot size when downloaded; remote repo file size otherwise. |

## RTFx Formula

```text
RTFx = audio_duration_seconds / processing_seconds
```

For TTS, the lab uses MLX-Audio's reported real-time factor when present. For
STT, the lab computes input duration divided by wrapper wall time.

## Reproducible Commands

```bash
make setup
make smoke
make higgs-clone
make report
```

Run a heavier Parakeet model:

```bash
.venv/bin/python scripts/voice_lab.py parakeet \
  --preset v3 \
  --audio path/to/audio.wav
```

## Interpretation Rules

- Do not compare this smoke report directly to public WER leaderboards.
- Do not compare first-run downloads to warm-cache runs.
- Treat synthetic-reference voice-clone results as pipeline validation, not quality proof.
- Use your own audio set before making accuracy or quality claims.
- Report hardware, OS, Python, model id, model size, and exact command with every result.

## External Benchmark References

- Open ASR Leaderboard: https://github.com/huggingface/open_asr_leaderboard
- FluidAudio benchmarks: https://github.com/FluidInference/FluidAudio/blob/main/benchmarks.md
- ML research code release checklist: https://github.com/paperswithcode/releasing-research-code


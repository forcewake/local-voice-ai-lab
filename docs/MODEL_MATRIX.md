# Model Matrix

| preset | task | default model | local? | command |
| --- | --- | --- | --- | --- |
| `voxtral-tts` | TTS | `mlx-community/Voxtral-4B-TTS-2603-mlx-4bit` | yes | `make voxtral` |
| `qwen3-clone` | voice clone TTS | `mlx-community/Qwen3-TTS-12Hz-0.6B-Base-bf16` | yes | `make qwen3-clone` |
| `higgs-clone` | voice clone TTS | `mlx-community/higgs-audio-v2-3B-mlx-q6` | yes | `make higgs-clone` |
| `parakeet-small` | STT | `mlx-community/parakeet-tdt_ctc-110m` | yes | `make parakeet` |
| `parakeet-v3` | STT | `mlx-community/parakeet-tdt-0.6b-v3` | yes | `python scripts/voice_lab.py parakeet --preset v3 --audio path/to/audio.wav` |

## Notes

- Voxtral local MLX path uses preset voices.
- Qwen3 and Higgs accept local reference audio plus transcript.
- Parakeet small is the default smoke-test preset because it keeps first-run downloads smaller.
- Parakeet v3 is the heavier multilingual transcription preset.
- Model licenses differ; check upstream model cards before redistribution or commercial use.

## Commands

```bash
.venv/bin/python scripts/voice_lab.py models
.venv/bin/python scripts/voice_lab.py doctor
```


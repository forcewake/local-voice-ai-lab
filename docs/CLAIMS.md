# Claims Ledger

This file tracks claims that appear in README, docs, or articles. It exists to
separate verified facts from lab observations and opinions.

| claim | source | checked | scope | caveat |
| --- | --- | --- | --- | --- |
| ML code repos benefit from dependencies, evaluation code, pretrained model references, and README result tables with exact commands. | https://github.com/paperswithcode/releasing-research-code | 2026-06-01 | repo publishing best practice | General ML guidance, not voice-specific. |
| Open ASR Leaderboard reports WER and RTFx from reproducible evaluation outputs. | https://github.com/huggingface/open_asr_leaderboard | 2026-06-01 | benchmark design | Public leaderboard methodology is broader than this local smoke lab. |
| Voxtral TTS official open weights are published as `mistralai/Voxtral-4B-TTS-2603`. | https://huggingface.co/mistralai/Voxtral-4B-TTS-2603 | 2026-06-01 | model identity | Local MLX conversion is a separate community model. |
| Local MLX Voxtral TTS in this repo uses preset voices rather than arbitrary local reference-audio cloning. | Local inspection and smoke test of `mlx_audio.tts.generate` with Voxtral path | 2026-06-01 | this repo's tested path | Mistral's hosted API supports richer voice workflows. |
| FluidAudio is a Swift/CoreML local audio AI SDK for Apple devices. | https://github.com/FluidInference/FluidAudio | 2026-06-01 | ecosystem comparison | This repo currently uses MLX-Audio, not FluidAudio. |
| Parakeet models are ASR models, not TTS models. | https://huggingface.co/nvidia/parakeet-tdt-0.6b-v3 | 2026-06-01 | model role | Diarization and TTS require other components. |


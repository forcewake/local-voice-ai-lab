# Claims Ledger

This file tracks claims that appear in README, docs, or articles. It exists to
separate verified facts from lab observations and opinions.

| claim | source | checked | scope | caveat |
| --- | --- | --- | --- | --- |
| ML code repos benefit from dependencies, evaluation code, pretrained model references, and README result tables with exact commands. | https://github.com/paperswithcode/releasing-research-code | 2026-06-01 | repo publishing best practice | General ML guidance, not voice-specific. |
| Open ASR Leaderboard reports WER and RTFx from reproducible evaluation outputs. | https://github.com/huggingface/open_asr_leaderboard | 2026-06-01 | benchmark design | Public leaderboard methodology is broader than this local smoke lab. |
| Voxtral TTS official open weights are published as `mistralai/Voxtral-4B-TTS-2603`. | https://huggingface.co/mistralai/Voxtral-4B-TTS-2603 | 2026-06-01 | model identity | Local MLX conversion is a separate community model. |
| Local MLX Voxtral TTS in this repo uses preset voices rather than arbitrary local reference-audio cloning. | Local inspection and smoke test of `mlx_audio.tts.generate` with Voxtral path | 2026-06-01 | this repo's tested path | Mistral's hosted API supports richer voice workflows. |
| Voxtral TTS model card lists 9 languages, 20 preset voices, 24 kHz output, and CC BY-NC 4.0 licensing. | https://huggingface.co/mistralai/Voxtral-4B-TTS-2603 | 2026-06-01 | model capabilities and license | Hosted API capabilities and local MLX conversion behavior differ. |
| Qwen3-TTS 0.6B Base supports voice cloning from user-provided audio and is listed as Apache-2.0 on its model card. | https://huggingface.co/Qwen/Qwen3-TTS-12Hz-0.6B-Base | 2026-06-01 | upstream Qwen model identity/license | This repo runs a community MLX conversion, so conversion-specific behavior should be tested locally. |
| Higgs Audio v2 MLX q6 is an MLX port of `bosonai/higgs-audio-v2-generation-3B-base` and lists local voice cloning. | https://huggingface.co/mlx-community/higgs-audio-v2-3B-mlx-q6 | 2026-06-01 | local Higgs model identity | The conversion card and upstream license presentation conflict; treat license as review-required. |
| Higgs Audio v2 upstream links a custom Boson Higgs Audio 2 Community License with Meta Llama 3 terms. | https://huggingface.co/bosonai/higgs-audio-v2-generation-3B-base/blob/main/LICENSE | 2026-06-01 | Higgs license caveat | Do not treat Higgs as plain Apache-2.0 without resolving upstream terms. |
| NVIDIA Parakeet TDT 0.6B v3 is an ASR model with Open ASR Leaderboard WER and RTFx results and CC-BY-4.0 licensing. | https://huggingface.co/nvidia/parakeet-tdt-0.6b-v3 | 2026-06-01 | upstream Parakeet v3 model identity/license | Local MLX conversion speed can differ substantially from leaderboard hardware. |
| FluidAudio is a Swift/CoreML local audio AI SDK for Apple devices. | https://github.com/FluidInference/FluidAudio | 2026-06-01 | ecosystem comparison | This repo currently uses MLX-Audio, not FluidAudio. |
| Parakeet models are ASR models, not TTS models. | https://huggingface.co/nvidia/parakeet-tdt-0.6b-v3 | 2026-06-01 | model role | Diarization and TTS require other components. |

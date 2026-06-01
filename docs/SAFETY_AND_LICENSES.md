# Safety and Licensing

This repo is for local benchmarking, engineering evaluation, and consenting
voice experiments.

## Voice Safety

Rules for responsible use:

- Clone only your own voice or a voice with explicit permission.
- Keep reference recordings private.
- Do not impersonate people.
- Do not generate deceptive audio.
- Label generated audio when sharing it.
- Store consent metadata for any reusable voice sample.

## Model Licensing

This project is a runner and benchmark harness. It does not grant rights to
third-party model weights.

Check upstream model cards before publishing outputs, shipping products, or
using a model commercially.

Known caveats:

- Voxtral TTS open weights are listed as CC BY-NC 4.0 by the official model card.
- Qwen3-TTS 0.6B Base is listed as Apache-2.0 by the upstream Qwen model card.
- Higgs Audio needs explicit review: the MLX conversion page lists Apache-2.0,
  but the upstream Boson model card links a custom Boson Higgs Audio 2
  Community License with Meta Llama 3 terms.
- NVIDIA Parakeet v2 and v3 model cards are listed as CC-BY-4.0; community
  conversions and other Parakeet-family checkpoints still need exact-card review.
- FluidAudio's SDK and individual model pipelines have separate licensing surfaces.
- Generated reports include model ids so license review can trace each run.

## Data Privacy

- `runs/`, `artifacts/`, and `audio/` are ignored because they may contain voice data.
- Do not commit personal reference audio.
- Do not commit API keys.
- Prefer local-only runs for sensitive speech.

## API Safety

The script `scripts/voxtral_voice_clone_api.py` requires `MISTRAL_API_KEY`.
Keep that value in your shell environment or secret manager, not in source code.

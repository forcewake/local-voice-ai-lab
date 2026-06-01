# Local Voice AI Lab

![Python](https://img.shields.io/badge/python-3.12-blue)
![Apple Silicon](https://img.shields.io/badge/Apple%20Silicon-MLX-black)
![Local First](https://img.shields.io/badge/local--first-audio%20AI-green)
![Benchmarks](https://img.shields.io/badge/reports-CSV%20%2B%20Markdown-orange)
[![GitHub Pages](https://img.shields.io/badge/GitHub%20Pages-live-4ee6c3)](https://forcewake.github.io/local-voice-ai-lab/)

A repeatable Apple Silicon voice AI lab for testing local TTS, local
reference-audio voice cloning, and local transcription.

It wraps MLX-Audio model runners, captures raw command logs, parses runtime and
memory metrics, computes model sizes, and writes reproducible CSV plus Markdown
reports.

The repository code is MIT licensed. Model weights, generated outputs, hosted
API use, and third-party voice data are governed by their own upstream licenses
and terms. Voxtral open weights are non-commercial CC BY-NC 4.0; always check
[licenses/models.yml](licenses/models.yml) and the upstream model card before
redistribution or commercial use.

## What This Repo Runs

| workflow | model | command | purpose |
| --- | --- | --- | --- |
| Voxtral TTS | `mlx-community/Voxtral-4B-TTS-2603-mlx-4bit` | `make voxtral` | Local preset-voice TTS |
| Qwen3 clone | `mlx-community/Qwen3-TTS-12Hz-0.6B-Base-bf16` | `make qwen3-clone` | Local reference-audio voice clone |
| Higgs clone | `mlx-community/higgs-audio-v2-3B-mlx-q6` | `make higgs-clone` | Larger local voice clone |
| Parakeet STT | `mlx-community/parakeet-tdt_ctc-110m` | `make parakeet` | Fast local transcription smoke test |
| Parakeet v3 | `mlx-community/parakeet-tdt-0.6b-v3` | CLI preset | Heavier multilingual transcription |

## Quickstart

Project site: https://forcewake.github.io/local-voice-ai-lab/

```bash
git clone https://github.com/forcewake/local-voice-ai-lab.git
cd local-voice-ai-lab

make setup
.venv/bin/python scripts/voice_lab.py doctor
make smoke
```

The smoke suite runs:

```text
Voxtral local TTS -> Qwen3 local clone -> Parakeet local transcription
```

## One-Command Workflows

```bash
make voxtral       # Voxtral local TTS
make qwen3-clone  # Qwen3 local reference-audio voice clone
make higgs-clone  # Higgs Audio local reference-audio voice clone
make parakeet     # Parakeet local transcription, 110M preset
make smoke        # Voxtral + Qwen3 + Parakeet small
make all          # Smoke suite plus Higgs clone
make report       # Regenerate Markdown report from CSV
make publish-check # Check for publish blockers before pushing to GitHub
```

Use your own reference voice:

```bash
ffmpeg -y -i my_voice_original.m4a -ac 1 -ar 24000 my_voice_sample.wav

.venv/bin/python scripts/voice_lab.py qwen3-clone \
  --ref-audio my_voice_sample.wav \
  --ref-text "Exact words spoken in my reference sample." \
  --confirm-consent

.venv/bin/python scripts/voice_lab.py higgs-clone \
  --ref-audio my_voice_sample.wav \
  --ref-text "Exact words spoken in my reference sample." \
  --confirm-consent
```

Run Parakeet v3:

```bash
.venv/bin/python scripts/voice_lab.py parakeet \
  --preset v3 \
  --audio path/to/audio.wav
```

## Example Results

Sanitized sample rows from local smoke and Higgs runs:

| task | status | wall time | RTFx | peak memory | output |
| --- | --- | ---: | ---: | ---: | --- |
| Voxtral TTS | ok | 4.27s | 3.47 | 2.76 GB | `voxtral_tts_000.wav` |
| Qwen3 clone | ok | 3.97s | 1.73 | 6.58 GB | `qwen3_clone_000.wav` |
| Parakeet small | ok | 31.74s | 0.15 | 0.56 GB | `parakeet_transcript.txt` |
| Higgs clone | ok | 64.25s | 0.99 | 6.51 GB | `higgs_clone_000.wav` |

See:

- [reports/sample_voice_lab_report.md](reports/sample_voice_lab_report.md)
- [reports/sample_voice_lab_results.csv](reports/sample_voice_lab_results.csv)

## Project Docs

- [Project spec](docs/PROJECT_SPEC.md)
- [Roadmap](docs/ROADMAP.md)
- [Architecture](docs/ARCHITECTURE.md)
- [Benchmark methodology](docs/BENCHMARK_METHODOLOGY.md)
- [Model matrix](docs/MODEL_MATRIX.md)
- [Claims ledger](docs/CLAIMS.md)
- [Safety and licensing](docs/SAFETY_AND_LICENSES.md)
- [Publishing checklist](docs/PUBLISHING_CHECKLIST.md)
- [Examples](examples/README.md)
- [Deep technical article](blog/voxtral-fluidaudio-parakeet-deep-comparison.md)

## Metrics Captured

- wall-clock runtime
- MLX-Audio processing time when reported
- input/output audio duration
- RTFx
- peak memory
- model size
- output files
- raw command logs
- transcript text for STT runs

## Before Publishing Results

Generated benchmark reports can contain private transcripts or local machine
paths. The tracked `reports/sample_*` files are sanitized examples; local
`reports/voice_lab_*` files are ignored.

```bash
make report
make publish-check
```

The publish check verifies required repo files, blocks generated audio/report
artifacts from Git, and scans tracked text files for obvious secrets or local
absolute paths.

## Sample Local Environment

- Architecture: `arm64`
- macOS on Apple Silicon
- `uv` available on PATH
- `ffmpeg` and `ffprobe` available on PATH
- Python in lab: `3.12.11`

Use a project-local Python 3.12 environment. The global Python on this machine
is 3.14.3, which may be too new for parts of the ML stack.

## What Voxtral TTS Is

Voxtral TTS is Mistral AI's open-weight text-to-speech model family. The public
local model is `mistralai/Voxtral-4B-TTS-2603`; the hosted API model id is
`voxtral-mini-tts-2603`.

Key properties:

- 4B-parameter multilingual TTS model.
- 9 supported languages: English, French, Spanish, German, Italian, Portuguese,
  Dutch, Arabic, and Hindi.
- 20 preset voices in the public model builds.
- 24 kHz speech output.
- Mistral API supports saved voices and one-off reference audio.
- Open weights are CC BY-NC 4.0, so treat local/offline use as non-commercial
  unless you have separate rights.

Primary sources:

- Mistral docs: https://docs.mistral.ai/models/model-cards/voxtral-tts-26-03
- Mistral speech API docs: https://docs.mistral.ai/api/endpoint/audio/speech
- Mistral voice docs: https://docs.mistral.ai/studio-api/audio/text_to_speech/voices
- Mistral announcement: https://mistral.ai/news/voxtral-tts/
- Hugging Face official weights: https://huggingface.co/mistralai/Voxtral-4B-TTS-2603
- MLX 4-bit build: https://huggingface.co/mlx-community/Voxtral-4B-TTS-2603-mlx-4bit
- MLX-Audio runner: https://github.com/Blaizzy/mlx-audio

## Recommended Local Path: MLX-Audio

This is the most practical path on Apple Silicon today. It uses Apple's MLX
stack and downloads an MLX-converted model from Hugging Face.

```bash
cd VoxtralTTS

uv venv --python 3.12 --seed
source .venv/bin/activate

uv pip install -U mlx-audio "mistral-common[audio]" "huggingface_hub[hf_xet]"
```

Generate a first WAV using the 4-bit model:

```bash
mkdir -p audio

mlx_audio.tts.generate \
  --model mlx-community/Voxtral-4B-TTS-2603-mlx-4bit \
  --text "Hello, this is Voxtral text to speech running locally on Apple Silicon." \
  --voice casual_male \
  --output_path ./audio \
  --verbose
```

The first run downloads about 2.5 GB of model weights. Play the generated WAV:

```bash
ffplay audio/*.wav
```

If your Mac has plenty of memory and you want the full-precision build:

```bash
mlx_audio.tts.generate \
  --model mlx-community/Voxtral-4B-TTS-2603-mlx-bf16 \
  --text "This is the BF16 Voxtral model on Apple Silicon." \
  --voice neutral_female \
  --output_path ./audio \
  --verbose
```

Use the 4-bit model first on 8 GB or 16 GB Macs. The BF16 model is around 8 GB
on disk and needs more unified memory at runtime.

## Available Preset Voices

English:

- `casual_male`
- `casual_female`
- `cheerful_female`
- `neutral_male`
- `neutral_female`

Other languages:

- French: `fr_male`, `fr_female`
- Spanish: `es_male`, `es_female`
- German: `de_male`, `de_female`
- Italian: `it_male`, `it_female`
- Portuguese: `pt_male`, `pt_female`
- Dutch: `nl_male`, `nl_female`
- Arabic: `ar_male`
- Hindi: `hi_male`, `hi_female`

## Hosted API Path

Use this when you need the official Mistral service, reliable streaming, or
one-off reference audio voice cloning.

```bash
source .venv/bin/activate
uv pip install -U mistralai
export MISTRAL_API_KEY="your-api-key"
```

```python
import base64
import os
from pathlib import Path

from mistralai.client import Mistral

client = Mistral(api_key=os.environ["MISTRAL_API_KEY"])
response = client.audio.speech.complete(
    model="voxtral-mini-tts-2603",
    input="Hello. This is Voxtral through the Mistral hosted API.",
    voice_id="your-voice-id",
    response_format="mp3",
)

Path("output.mp3").write_bytes(base64.b64decode(response.audio_data))
```

## Voice Cloning

Yes, you can clone your own voice, but there are two different paths:

- Local voice cloning on Apple Silicon: supported with another MLX-Audio model,
  such as Qwen3-TTS or Higgs Audio v2.
- Hosted Mistral API: supported. Use either a saved voice (`voice_id`) or a
  one-off reference audio clip (`ref_audio`).
- Local MLX-Audio Voxtral: preset voices only in the current implementation.
  The generic CLI exposes `--ref_audio`, but the Voxtral model path currently
  ignores it and uses the 20 bundled voice presets.

Use only your own voice or a voice you have explicit consent to clone.

Record a clean 10-30 second sample. Use a quiet room, one speaker, no music,
and read a normal sentence in the language you want to generate. Convert it to
mono 24 kHz WAV:

```bash
ffmpeg -y -i my_voice_original.m4a -ac 1 -ar 24000 my_voice_sample.wav
```

### Local-Only Voice Clone: Qwen3-TTS

This is the smallest local voice-cloning setup tested in this workspace. It
downloads about 2.34 GiB of weights and peaked at about 6.72 GB memory in a
short smoke test on Apple Silicon.

The upstream Qwen3-TTS model card describes 10-language TTS, rapid voice
cloning from user-provided audio, and Apache-2.0 licensing. This repo uses the
MLX conversion `mlx-community/Qwen3-TTS-12Hz-0.6B-Base-bf16`, so local behavior
should be validated through the benchmark runner.

You must provide both:

- `--ref_audio`: your voice sample.
- `--ref_text`: the exact transcript of that sample.

```bash
source .venv/bin/activate

mlx_audio.tts.generate \
  --model mlx-community/Qwen3-TTS-12Hz-0.6B-Base-bf16 \
  --text "Hello, this is my locally cloned voice running on Apple Silicon." \
  --ref_audio my_voice_sample.wav \
  --ref_text "Exact words spoken in my voice sample." \
  --output_path ./audio \
  --file_prefix my_local_voice_clone \
  --verbose
```

Smoke-test output from this workspace:

```bash
afplay audio/qwen3_local_clone_smoke_000.wav
```

For better quality at higher memory cost, try:

```bash
mlx_audio.tts.generate \
  --model mlx-community/Qwen3-TTS-12Hz-1.7B-Base-bf16 \
  --text "Hello, this is a higher quality local voice clone." \
  --ref_audio my_voice_sample.wav \
  --ref_text "Exact words spoken in my voice sample." \
  --output_path ./audio \
  --file_prefix my_local_voice_clone_qwen3_17b \
  --verbose
```

### Local-Only Voice Clone: Higgs Audio v2

Higgs Audio v2 is another Apple Silicon local option with reference-audio voice
cloning. It is larger than Qwen3 0.6B but is designed for local voice cloning.

License caveat: the MLX conversion page lists Apache-2.0, while the upstream
Boson model card links a custom Boson Higgs Audio 2 Community License with Meta
Llama 3 terms. Treat Higgs as license-review-required for publication or
commercial use until that boundary is resolved.

```bash
mlx_audio.tts.generate \
  --model mlx-community/higgs-audio-v2-3B-mlx-q6 \
  --text "Hello, this is a local Higgs Audio voice clone." \
  --ref_audio my_voice_sample.wav \
  --ref_text "Exact words spoken in my voice sample." \
  --output_path ./audio \
  --file_prefix my_local_voice_clone_higgs \
  --verbose
```

### Hosted Voxtral Voice Clone

One-off voice clone through the Mistral API:

```bash
source .venv/bin/activate
uv pip install -U requests
export MISTRAL_API_KEY="your-api-key"

python scripts/voxtral_voice_clone_api.py \
  --ref-audio my_voice_sample.wav \
  --text "Hello, this is my cloned voice generated with Voxtral." \
  --output audio/my_voice_clone.mp3 \
  --confirm-consent
```

Saved voice workflow through the Mistral API:

```bash
source .venv/bin/activate
uv pip install -U mistralai
export MISTRAL_API_KEY="your-api-key"
```

```python
import base64
from pathlib import Path
from mistralai.client import Mistral

client = Mistral(api_key="your-api-key")
sample_audio_b64 = base64.b64encode(Path("my_voice_sample.wav").read_bytes()).decode()

voice = client.audio.voices.create(
    name="my-voice",
    sample_audio=sample_audio_b64,
    sample_filename="my_voice_sample.wav",
    languages=["en"],
    gender="male",
)

print(voice.id)
```

## Official Local Serving Path: vLLM Omni

Mistral's official Hugging Face instructions recommend `vLLM Omni`:

```bash
uv pip install -U vllm
uv pip install -U vllm-omni

vllm serve mistralai/Voxtral-4B-TTS-2603 --omni
```

That path is aimed at server GPUs. The model card says the BF16 model needs a
single GPU with at least 16 GB memory. For a MacBook or Mac Studio without an
NVIDIA GPU, use the MLX path above.

## Advanced Apple Silicon Path: ExecuTorch MLX

There is also a pre-exported ExecuTorch MLX build:

https://huggingface.co/younghan-meta/Voxtral-4B-TTS-2603-ExecuTorch-MLX

It is lower level than MLX-Audio. Use it if you specifically want a C++ runner
or ExecuTorch integration. The workflow is:

```bash
git clone https://github.com/pytorch/executorch ~/executorch
cd ~/executorch

./install_executorch.sh
pip install -e . --no-build-isolation
make voxtral_tts-mlx
```

Then download the exported artifacts plus tokenizer and voice embeddings, and
run `voxtral_tts_runner` as shown in the model card.

## Troubleshooting

- If `mlx_audio.tts.generate` is not found, activate `.venv` or run it through
  `uv run`.
- If Voxtral reports that Tekken tokenizers require `mistral-common[audio]`,
  install it with `uv pip install -U "mistral-common[audio]"`.
- If downloads are slow or fail, keep `"huggingface_hub[hf_xet]"` installed.
- If Hugging Face asks for authentication, run `hf auth login`.
- If output has odd pronunciations, spell out numbers and abbreviations.
- Keep text prompts under about 300 words for best quality.
- For custom voice cloning, the hosted Mistral API is currently the safer path;
  the simple MLX-Audio flow above is preset-voice focused.

# Examples

These examples are copy-pasteable starting points for local runs. Generated
audio and transcripts should stay under ignored paths such as `runs/` or
`artifacts/`.

## Voxtral TTS

```bash
make voxtral
```

Custom text:

```bash
.venv/bin/python scripts/voice_lab.py voxtral \
  --text "$(cat examples/prompts/tts_en.txt)" \
  --voice casual_male
```

## Qwen3 Local Voice Clone

```bash
ffmpeg -y -i my_voice_original.m4a -ac 1 -ar 24000 my_voice_sample.wav

.venv/bin/python scripts/voice_lab.py qwen3-clone \
  --ref-audio my_voice_sample.wav \
  --ref-text "$(cat examples/prompts/reference_transcript.txt)" \
  --text "$(cat examples/prompts/clone_target.txt)" \
  --confirm-consent
```

## Higgs Audio Local Voice Clone

```bash
.venv/bin/python scripts/voice_lab.py higgs-clone \
  --ref-audio my_voice_sample.wav \
  --ref-text "$(cat examples/prompts/reference_transcript.txt)" \
  --text "$(cat examples/prompts/clone_target.txt)" \
  --confirm-consent
```

## Parakeet STT

```bash
.venv/bin/python scripts/voice_lab.py parakeet \
  --preset small \
  --audio path/to/audio.wav
```

Run the heavier v3 preset:

```bash
.venv/bin/python scripts/voice_lab.py parakeet \
  --preset v3 \
  --audio path/to/audio.wav
```

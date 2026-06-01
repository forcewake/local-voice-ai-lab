## Summary

Describe the change and why it matters.

## Validation

- [ ] `.venv/bin/python -m py_compile scripts/voice_lab.py scripts/voxtral_voice_clone_api.py scripts/publish_check.py`
- [ ] `.venv/bin/python -m unittest`
- [ ] `.venv/bin/python scripts/publish_check.py`

## Safety

- [ ] No private reference audio, generated voice samples, or private transcripts are committed.
- [ ] Voice-clone examples require explicit consent.
- [ ] Model/license claims are linked to upstream sources.

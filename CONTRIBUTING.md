# Contributing

Contributions should preserve the lab's main value: repeatable local voice AI
benchmarks with auditable commands and source-grounded claims.

## Development Setup

```bash
make setup
.venv/bin/python scripts/voice_lab.py doctor
python -m unittest
```

## Contribution Rules

- Do not commit personal voice recordings.
- Do not commit API keys.
- Add source links for new model claims.
- Keep model downloads out of CI by default.
- Include exact commands for any benchmark numbers.
- Prefer small, reviewable changes.

## Good First Contributions

- Add a new model preset to `scripts/voice_lab.py`.
- Add a reproducible example under `examples/`.
- Improve report rendering.
- Add parser tests for a new model's logs.
- Add source-grounded entries to `docs/CLAIMS.md`.

# Security Policy

## Supported Versions

This project is pre-1.0. Security fixes apply to the current `main` branch.

## Reporting a Vulnerability

Use GitHub private vulnerability reporting for the published repository, or
open a private draft security advisory against `forcewake/local-voice-ai-lab`.
Do not publish exploit details in a public issue before the maintainer has had
time to respond.

Please include:

- affected commit or release
- exact command or input needed to reproduce
- impact and whether private audio, transcripts, or tokens may be exposed
- sanitized logs only

Do not attach private voice recordings, API keys, or model cache files. Expect
an initial maintainer response within 7 days for security reports.

## Sensitive Data

The repo intentionally ignores:

- `runs/`
- `artifacts/`
- `audio/`
- local model caches

These paths may contain voice data, transcripts, or generated speech. Review
them before sharing logs or benchmark outputs.

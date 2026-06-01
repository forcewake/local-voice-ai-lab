# Security Policy

## Supported Versions

This project is pre-1.0. Security fixes apply to the current `main` branch.

## Reporting a Vulnerability

Open a private advisory or contact the maintainer directly before publishing
details. Do not attach private voice recordings, API keys, or model cache files
to public issues.

## Sensitive Data

The repo intentionally ignores:

- `runs/`
- `artifacts/`
- `audio/`
- local model caches

These paths may contain voice data, transcripts, or generated speech. Review
them before sharing logs or benchmark outputs.

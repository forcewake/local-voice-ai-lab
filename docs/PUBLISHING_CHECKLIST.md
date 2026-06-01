# GitHub Publishing Checklist

Use this before publishing the repo.

## Required

- [ ] Choose and confirm repository license.
- [ ] Remove personal or private audio from tracked files.
- [ ] Confirm `.gitignore` excludes `runs/`, `artifacts/`, `audio/`, and caches.
- [ ] Run `make smoke`.
- [ ] Run `.venv/bin/python scripts/voice_lab.py doctor`.
- [ ] Regenerate local reports with `make report`.
- [ ] Review ignored local `reports/voice_lab_results.csv` for private paths or sensitive transcripts.
- [ ] Commit only sanitized sample reports such as `reports/sample_voice_lab_report.md` and `reports/sample_voice_lab_results.csv`.
- [ ] Verify README install steps from a clean checkout.
- [ ] Confirm all source claims in docs have links.
- [ ] Run `make publish-check`.

## Recommended

- [ ] Add a short demo GIF or screenshot.
- [ ] Add badges after CI is enabled on GitHub.
- [ ] Add GitHub repo topics: `voice-ai`, `speech-ai`, `mlx`, `apple-silicon`, `tts`, `asr`, `parakeet`, `voxtral`.
- [ ] Create a first release after the smoke suite is green.
- [ ] Add a public benchmark issue template for community submissions.

## Preflight Commands

```bash
make setup
.venv/bin/python scripts/voice_lab.py doctor
make smoke
make report
make publish-check
.venv/bin/python -m py_compile scripts/voice_lab.py scripts/voxtral_voice_clone_api.py scripts/publish_check.py
```

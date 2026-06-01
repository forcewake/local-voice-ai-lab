# Local Voice AI Lab Roadmap

Last updated: 2026-06-01

## Direction

Local Voice AI Lab should become a trustworthy local speech-model evaluation
workspace: easy to run, honest about benchmark limits, careful with voice data,
and useful for deciding whether a model is ready for a local product prototype.

The roadmap favors small, auditable milestones over a large application rewrite.
The current CLI-first design is valuable because it keeps exact commands,
artifacts, and raw logs visible.

## Guiding Principles

- Keep local privacy and consent requirements explicit.
- Prefer repeatable shell commands over hidden notebook state.
- Track enough metadata to reproduce or challenge every benchmark claim.
- Separate model speed evidence from model quality evidence.
- Treat model licenses as a release blocker, not an afterthought.
- Avoid committing generated voice data unless publication rights are clear.

## Current Baseline

Completed baseline capabilities:

- Local setup through `make setup`.
- Single-model commands for Voxtral, Qwen3 clone, Higgs clone, and Parakeet.
- `make smoke` suite for Voxtral TTS, Qwen3 clone, and Parakeet small STT.
- `make all` suite that adds Higgs clone.
- Ignored local CSV benchmark history in `reports/voice_lab_results.csv`.
- Ignored generated Markdown report in `reports/voice_lab_report.md`.
- Sanitized sample reports under `reports/sample_*`.
- Ignored run artifacts under `runs/`, `artifacts/`, and `audio/`.
- Hosted Mistral Voxtral one-off reference-audio helper.
- Consent gates on custom reference-audio clone commands.
- Basic model license registry and consent example.
- Pre-publication check for required files, generated artifacts, local paths,
  and obvious secrets.

Known gaps:

- No repeated-run statistics or variance reporting.
- No quality scoring rubric captured in the report.
- No machine-readable per-run manifest.
- No semantic transcript classifier for private content beyond basic publish
  checks.

## Milestone Plan

| Milestone | Status | Outcome | Exit Criteria |
| --- | --- | --- | --- |
| M0 - Baseline lab | Complete | CLI lab can run local TTS, clone TTS, and STT smoke tests. | Existing report has successful Voxtral, Qwen3, Higgs, and Parakeet rows. |
| M1 - GitHub-ready documentation | Current | Project has a publishable spec, roadmap, and supporting docs. | `docs/PROJECT_SPEC.md` and `docs/ROADMAP.md` explain goals, personas, model matrix, methodology, commands, artifacts, safety, licensing, and milestones. |
| M2 - Benchmark rigor | Planned | Results can support stable local comparisons. | Repeated warm-cache runs, median/range summaries, run manifests, and cold-vs-warm labels exist. |
| M3 - Quality evaluation | Planned | Audio quality and transcription quality are reviewed separately from speed. | Prompt set, MOS-style rubric, WER/CER workflow, and quality summary are documented and captured. |
| M4 - Safety and license controls | Planned | Publishing blockers are visible before artifacts leave the local machine. | Consent records, license registry, report redaction checks, and API-key hygiene checks exist. |
| M5 - Model expansion | Planned | Larger and alternative models can be compared without changing the benchmark contract. | Voxtral BF16, Qwen3 1.7B, Parakeet v3, multilingual prompts, and hosted API rows are represented consistently. |
| M6 - Reporting and publishing | Planned | Results are easier to consume from GitHub. | Reports include charts/tables, hardware metadata, caveats, and a release checklist. |
| M7 - Productization experiments | Later | The lab can inform local app or service prototypes. | A minimal local service or UI consumes benchmarked models without weakening safety controls. |

## M1 - GitHub-Ready Documentation

Deliverables:

- Technical project specification.
- Roadmap with milestone plan.
- Links or alignment with architecture, benchmark methodology, model matrix,
  publishing, and safety docs when present.

Exit criteria:

- A new contributor can understand what the lab does without running a model.
- Commands are copy-pasteable from the docs.
- Safety and licensing limits are visible before clone commands.
- Generated and tracked artifacts are clearly separated.

## M2 - Benchmark Rigor

Deliverables:

- Repeated-run option for each command or suite.
- Warm-cache and cold-cache labels.
- Per-run manifest saved as JSON next to logs.
- Hardware and environment snapshot per run.
- Median, min, max, and standard deviation in generated reports.

Candidate CLI shape:

```bash
.venv/bin/python scripts/voice_lab.py suite --suite smoke --repeat 3
.venv/bin/python scripts/voice_lab.py report --group-by model,task
```

Exit criteria:

- The report can distinguish one-off smoke runs from repeated benchmark runs.
- A failed row includes enough environment and command context to reproduce it.
- Speed claims are based on repeated warm-cache data.

## M3 - Quality Evaluation

Deliverables:

- Fixed prompt pack for TTS and clone evaluation.
- Reference transcript set for STT evaluation.
- Human review rubric with 1-5 scores for naturalness, similarity,
  intelligibility, pronunciation, noise, and pacing.
- Optional WER/CER computation for STT.
- Quality notes column or sidecar file per run.

Candidate artifacts:

```text
benchmarks/prompts/tts_en.json
benchmarks/prompts/multilingual.json
benchmarks/references/stt_manifest.csv
runs/<run_id>/quality_review.json
```

Exit criteria:

- A model can be faster but lower quality without the report hiding that tradeoff.
- Clone similarity is reviewed only against consenting voices.
- STT accuracy claims cite a reference transcript and scoring method.

## M4 - Safety and License Controls

Deliverables:

- Consent manifest template for reusable reference voices.
- License registry mapping model ids to upstream model cards and local notes.
- Report publishing check that flags private paths, transcripts, API keys, and
  generated voice files.
- Safety checklist for shared demos and blog posts.

Candidate artifacts:

```text
docs/SAFETY_AND_LICENSES.md
licenses/models.yml
artifacts/reference/CONSENT.example.md
```

Exit criteria:

- Every model in the default matrix has a license review status.
- Every reusable reference voice has documented consent.
- GitHub-published reports do not accidentally expose private voice data.

## M5 - Model Expansion

Deliverables:

- Voxtral BF16 local run option for higher-memory machines.
- Qwen3 1.7B clone option.
- Parakeet v3 benchmark rows.
- Multilingual Voxtral prompt coverage for supported voices.
- Hosted Voxtral API rows in the same report schema or a clearly separate API
  report.

Candidate commands:

```bash
.venv/bin/python scripts/voice_lab.py voxtral \
  --model mlx-community/Voxtral-4B-TTS-2603-mlx-bf16

.venv/bin/python scripts/voice_lab.py qwen3-clone \
  --model mlx-community/Qwen3-TTS-12Hz-1.7B-Base-bf16 \
  --ref-audio my_voice_sample.wav \
  --ref-text "Exact words spoken in my reference sample." \
  --confirm-consent

.venv/bin/python scripts/voice_lab.py parakeet --preset v3 --audio path/to/audio.wav
```

Exit criteria:

- Model additions do not require a new CSV schema.
- Heavier models are marked with expected memory and download cautions.
- Multilingual results name the prompt language and voice preset.

## M6 - Reporting and Publishing

Deliverables:

- Markdown report sections for environment, latest results, repeated-run
  summaries, quality notes, and caveats.
- Optional charts generated from CSV.
- Publishing checklist that can be run before pushing docs and reports.
- README badges or links that point to docs without embedding private artifacts.

Candidate commands:

```bash
make report
.venv/bin/python scripts/voice_lab.py report
```

Exit criteria:

- GitHub readers can understand the latest benchmark without opening raw CSV.
- Reports make benchmark limitations obvious.
- Private paths and voice data are reviewed before publication.

## M7 - Productization Experiments

Deliverables:

- Minimal local service or app wrapper around selected model commands.
- Queueing and cancellation behavior for long model runs.
- Artifact browser for local audio and transcripts.
- Explicit consent and labeling flow before exporting generated audio.

Exit criteria:

- The prototype consumes the same benchmarked commands or shared runner layer.
- Safety controls remain visible in the user workflow.
- Product experiments do not hide model ids, prompts, or reference-audio usage.

## Workstreams

### Benchmark Harness

- Add repeated-run execution.
- Add run manifests.
- Capture environment metadata once per run.
- Preserve failed rows with structured error categories.

### Model Coverage

- Validate optional larger models on target hardware.
- Keep default smoke suite small enough for frequent local checks.
- Add multilingual prompt coverage without making smoke tests heavy.

### Quality Evaluation

- Define prompt packs and reference transcripts.
- Add human review templates.
- Add automated WER/CER for STT when reference text is known.

### Safety and Licensing

- Track consent for reusable voices.
- Track model license review state.
- Add publish checks for private artifacts and transcripts.

### Developer Experience

- Keep Make targets stable.
- Keep direct CLI commands documented.
- Avoid requiring model downloads for lightweight docs or lint checks.

## Success Metrics

- A new user can run `make setup` and `make smoke` from a clean checkout.
- A maintainer can reproduce a report row from the stored command and log.
- Default smoke tests remain small enough to run during normal local development.
- Published reports include caveats, model ids, hardware context, and licensing
  notes.
- No private reference voice data is committed by default.

## Risks

| Risk | Impact | Mitigation |
| --- | --- | --- |
| Model licenses change or are misunderstood. | Outputs may be unusable for publishing or commercial work. | Maintain a license registry and block releases until reviewed. |
| Benchmarks overstate general model quality. | Readers may draw invalid conclusions. | Label smoke tests clearly and add quality evaluation before claims. |
| Private voice data is committed. | Privacy and consent breach. | Keep generated paths ignored and add publish checks. |
| First-run downloads distort speed results. | Inaccurate performance comparisons. | Mark cold runs and report warm-cache repeated runs separately. |
| Larger models exceed local memory. | Failed runs and poor user experience. | Keep smoke defaults small and document memory cautions for heavier models. |

## Near-Term Next Steps

1. Add repeated-run support and report aggregation.
2. Add per-run JSON manifests with environment metadata.
3. Add a small quality prompt pack and review rubric.
4. Add model license registry and consent template.
5. Add a publishing checklist that scans reports for private paths and generated
   voice artifact references.

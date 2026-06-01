# Architecture

Local Voice AI Lab is a thin orchestration layer around proven model runners.
It keeps the benchmark path close to what a user actually runs in a terminal.

```mermaid
flowchart LR
    A["Make target or CLI"] --> B["scripts/voice_lab.py"]
    B --> C["MLX-Audio TTS CLI"]
    B --> D["MLX-Audio STT CLI"]
    B --> E["ffprobe duration"]
    B --> F["Hugging Face cache sizing"]
    C --> G["Audio artifacts"]
    D --> H["Transcript artifacts"]
    B --> I["Raw logs"]
    B --> J["CSV report"]
    B --> K["Markdown report"]
```

## Design Principles

- Keep model execution external and inspectable.
- Store raw command logs for auditability.
- Prefer reproducible commands over hidden notebooks.
- Separate generated artifacts from tracked documentation.
- Make lightweight checks possible without downloading models.

## Data Flow

```mermaid
sequenceDiagram
    participant User
    participant CLI as voice_lab.py
    participant Runner as MLX-Audio
    participant Probe as ffprobe
    participant Report as reports/

    User->>CLI: make smoke
    CLI->>Runner: Voxtral TTS command
    Runner-->>CLI: audio + verbose metrics
    CLI->>Runner: Qwen3 clone command
    Runner-->>CLI: audio + verbose metrics
    CLI->>Runner: Parakeet STT command
    Runner-->>CLI: transcript + verbose metrics
    CLI->>Probe: measure audio durations
    CLI->>Report: append CSV and regenerate Markdown
```

## Tracked vs Generated Files

Tracked:

- `scripts/voice_lab.py`
- `Makefile`
- `requirements.txt`
- `docs/`
- `reports/sample_voice_lab_results.csv`
- `reports/sample_voice_lab_report.md`

Ignored/generated:

- `runs/`
- `artifacts/`
- `audio/`
- `reports/voice_lab_results.csv`
- `reports/voice_lab_report.md`
- `reports/index.html`
- local model caches

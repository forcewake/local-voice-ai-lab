#!/usr/bin/env python3
"""Repeatable local voice AI benchmark/demo lab.

The lab intentionally wraps the public MLX-Audio CLIs instead of importing
model internals. That keeps the benchmark path close to the commands a user
would actually run from a terminal.
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import json
import os
import platform
import re
import shutil
import shlex
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parents[1]
REPORTS_DIR = ROOT / "reports"
RUNS_DIR = ROOT / "runs"
ARTIFACTS_DIR = ROOT / "artifacts"
REFERENCE_DIR = ARTIFACTS_DIR / "reference"

RESULTS_CSV = REPORTS_DIR / "voice_lab_results.csv"
REPORT_MD = REPORTS_DIR / "voice_lab_report.md"
REPORT_HTML = REPORTS_DIR / "index.html"

VOXTRAL_MODEL = "mlx-community/Voxtral-4B-TTS-2603-mlx-4bit"
QWEN3_MODEL = "mlx-community/Qwen3-TTS-12Hz-0.6B-Base-bf16"
HIGGS_MODEL = "mlx-community/higgs-audio-v2-3B-mlx-q6"
PARAKEET_SMALL_MODEL = "mlx-community/parakeet-tdt_ctc-110m"
PARAKEET_V3_MODEL = "mlx-community/parakeet-tdt-0.6b-v3"

MODEL_CATALOG = {
    "voxtral-tts": {
        "task": "TTS",
        "model": VOXTRAL_MODEL,
        "command": "make voxtral",
        "notes": "Local preset-voice Voxtral TTS via MLX-Audio.",
    },
    "qwen3-clone": {
        "task": "TTS voice clone",
        "model": QWEN3_MODEL,
        "command": "make qwen3-clone",
        "notes": "Local reference-audio voice clone; provide ref_text for custom samples.",
    },
    "higgs-clone": {
        "task": "TTS voice clone",
        "model": HIGGS_MODEL,
        "command": "make higgs-clone",
        "notes": "Larger local reference-audio voice clone path.",
    },
    "parakeet-small": {
        "task": "STT",
        "model": PARAKEET_SMALL_MODEL,
        "command": "make parakeet",
        "notes": "Fast local Parakeet smoke transcription preset.",
    },
    "parakeet-v3": {
        "task": "STT",
        "model": PARAKEET_V3_MODEL,
        "command": "python scripts/voice_lab.py parakeet --preset v3 --audio path/to/audio.wav",
        "notes": "Heavier multilingual Parakeet v3 transcription preset.",
    },
}

REFERENCE_TEXT = "Hello, Voxtral is now running on Apple Silicon."
VOXTRAL_TEXT = "Hello, this is Voxtral text to speech running locally on Apple Silicon."
CLONE_TEXT = "This is a local voice cloning benchmark running fully on Apple Silicon."

CSV_FIELDS = [
    "timestamp",
    "run_id",
    "task",
    "status",
    "model",
    "model_size_gib",
    "wall_time_sec",
    "processing_time_sec",
    "input_audio_duration_sec",
    "output_audio_duration_sec",
    "rtfx",
    "peak_memory_gb",
    "output_files",
    "log_file",
    "transcript",
    "command",
    "error",
]


ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")
SLUG_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]{0,127}$")


@dataclass
class CommandResult:
    status: str
    stdout: str
    stderr: str
    returncode: int
    wall_time_sec: float
    command: list[str]

    @property
    def combined_output(self) -> str:
        return strip_ansi("\n".join([self.stdout, self.stderr]).strip())


def strip_ansi(value: str) -> str:
    return ANSI_RE.sub("", value)


def utc_timestamp() -> str:
    return dt.datetime.now(dt.UTC).replace(microsecond=0).isoformat()


def local_run_id(prefix: str) -> str:
    stamp = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{stamp}_{prefix}"


def ensure_dirs() -> None:
    for directory in (REPORTS_DIR, RUNS_DIR, ARTIFACTS_DIR, REFERENCE_DIR):
        directory.mkdir(parents=True, exist_ok=True)


def shell_join(command: Iterable[str]) -> str:
    return " ".join(shlex.quote(part) for part in command)


def redact_text(value: object) -> str:
    text = str(value)
    root = str(ROOT)
    home = str(Path.home())
    text = text.replace(root + os.sep, "")
    text = text.replace(root, ".")
    text = text.replace(home + os.sep, "~" + os.sep)
    text = text.replace(home, "~")
    return text


def display_path(path: Path | str) -> str:
    path_obj = Path(path)
    try:
        return str(path_obj.resolve().relative_to(ROOT))
    except Exception:
        return redact_text(path_obj)


def validate_slug(value: str, field_name: str) -> str:
    if not SLUG_RE.match(value):
        raise SystemExit(
            f"Unsafe {field_name}: {value!r}. Use letters, numbers, dot, dash, "
            "or underscore; no path separators."
        )
    if ".." in value or "/" in value or "\\" in value:
        raise SystemExit(f"Unsafe {field_name}: {value!r}. Path traversal is not allowed.")
    return value


def run_command(command: list[str], timeout_sec: int | None = None) -> CommandResult:
    started = time.perf_counter()
    try:
        proc = subprocess.run(
            command,
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
            timeout=timeout_sec,
        )
    except subprocess.TimeoutExpired as exc:
        elapsed = time.perf_counter() - started
        stdout = exc.stdout or ""
        stderr = exc.stderr or ""
        if isinstance(stdout, bytes):
            stdout = stdout.decode("utf-8", errors="replace")
        if isinstance(stderr, bytes):
            stderr = stderr.decode("utf-8", errors="replace")
        return CommandResult(
            status="failed",
            stdout=stdout,
            stderr=f"{stderr}\nCommand timed out after {timeout_sec} seconds.".strip(),
            returncode=124,
            wall_time_sec=elapsed,
            command=command,
        )
    elapsed = time.perf_counter() - started
    return CommandResult(
        status="ok" if proc.returncode == 0 else "failed",
        stdout=proc.stdout,
        stderr=proc.stderr,
        returncode=proc.returncode,
        wall_time_sec=elapsed,
        command=command,
    )


def python_module_command(module: str, args: list[str]) -> list[str]:
    return [sys.executable, "-m", module, *args]


def parse_duration_to_seconds(value: str) -> float | None:
    match = re.match(r"(?P<h>\d+):(?P<m>\d+):(?P<s>\d+(?:\.\d+)?)", value.strip())
    if not match:
        return None
    return (
        int(match.group("h")) * 3600
        + int(match.group("m")) * 60
        + float(match.group("s"))
    )


def first_float(pattern: str, text: str) -> float | None:
    match = re.search(pattern, text, flags=re.IGNORECASE)
    if not match:
        return None
    return float(match.group(1))


def parse_tts_metrics(output: str) -> dict[str, float | list[str]]:
    files = re.findall(r"saving as:\s*(.+)", output, flags=re.IGNORECASE)
    duration_match = re.search(r"Duration:\s*([0-9:.]+)", output)
    parsed_duration = (
        parse_duration_to_seconds(duration_match.group(1)) if duration_match else None
    )
    return {
        "output_files": [
            display_path((ROOT / f).resolve() if not Path(f).is_absolute() else f)
            for f in files
        ],
        "output_audio_duration_sec": parsed_duration,
        "processing_time_sec": first_float(r"Processing time:\s*([0-9.]+)s", output),
        "rtfx": first_float(r"Real-time factor:\s*([0-9.]+)x", output),
        "peak_memory_gb": first_float(r"Peak memory usage:\s*([0-9.]+)\s*GB", output),
    }


def parse_stt_metrics(output: str) -> dict[str, float | list[str]]:
    saved = re.search(r"Saving file to:\s*\.?/?(.+)", output, flags=re.IGNORECASE)
    output_files: list[str] = []
    if saved:
        path = saved.group(1).strip()
        output_files.append(display_path((ROOT / path).resolve() if not Path(path).is_absolute() else path))
    return {
        "output_files": output_files,
        "processing_time_sec": first_float(r"Processing time:\s*([0-9.]+)\s*seconds", output),
        "peak_memory_gb": first_float(r"Peak memory:\s*([0-9.]+)\s*GB", output),
    }


def ffprobe_duration(path: Path) -> float | None:
    if not path.exists():
        return None
    proc = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            str(path),
        ],
        text=True,
        capture_output=True,
        check=False,
    )
    if proc.returncode != 0:
        return None
    try:
        return float(proc.stdout.strip())
    except ValueError:
        return None


def artifact_path(value: str | Path) -> Path:
    path = Path(value)
    return path if path.is_absolute() else ROOT / path


def total_audio_duration(files: Iterable[str | Path]) -> float | None:
    total = 0.0
    count = 0
    for file_name in files:
        duration = ffprobe_duration(artifact_path(file_name))
        if duration is not None:
            total += duration
            count += 1
    return total if count else None


def model_cache_dir(model_id: str) -> Path | None:
    if "/" not in model_id or Path(model_id).exists():
        path = Path(model_id)
        return path if path.exists() else None

    cache_home = Path(os.environ.get("HF_HOME", Path.home() / ".cache" / "huggingface"))
    hub = cache_home / "hub"
    namespace, name = model_id.split("/", 1)
    path = hub / f"models--{namespace}--{name}"
    return path if path.exists() else None


def directory_size_gib(path: Path) -> float:
    seen: set[Path] = set()
    total = 0
    if (path / "refs" / "main").exists() and (path / "snapshots").exists():
        revision = (path / "refs" / "main").read_text(encoding="utf-8").strip()
        candidates = [path / "snapshots" / revision]
    elif (path / "snapshots").exists():
        candidates = sorted((path / "snapshots").iterdir(), key=lambda p: p.stat().st_mtime, reverse=True)[:1]
    else:
        candidates = [path]

    for candidate in candidates:
        if not candidate.exists():
            continue
        for item in candidate.rglob("*"):
            if not item.is_file():
                continue
            resolved = item.resolve()
            if resolved in seen:
                continue
            seen.add(resolved)
            total += resolved.stat().st_size
    return total / 1024**3


def remote_model_size_gib(model_id: str) -> float | None:
    try:
        from huggingface_hub import HfApi

        api = HfApi()
        total = 0
        for item in api.list_repo_tree(model_id, recursive=True):
            size = getattr(item, "size", None)
            if size:
                total += int(size)
        return total / 1024**3 if total else None
    except Exception:
        return None


def model_size_gib(model_id: str) -> float | None:
    local_dir = model_cache_dir(model_id)
    if local_dir is not None:
        size = directory_size_gib(local_dir)
        if size > 0:
            return size
    return remote_model_size_gib(model_id)


def write_log(run_dir: Path, name: str, result: CommandResult) -> Path:
    log_path = run_dir / f"{name}.log"
    log_path.write_text(
        "\n".join(
            [
                f"$ {shell_join(result.command)}",
                "",
                "[stdout]",
                result.stdout,
                "",
                "[stderr]",
                result.stderr,
            ]
        ),
        encoding="utf-8",
    )
    return log_path


def read_csv_rows() -> list[dict[str, str]]:
    if not RESULTS_CSV.exists():
        return []
    with RESULTS_CSV.open("r", newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def append_csv(row: dict[str, object]) -> None:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    exists = RESULTS_CSV.exists()
    with RESULTS_CSV.open("a", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=CSV_FIELDS)
        if not exists:
            writer.writeheader()
        writer.writerow({field: stringify_csv_value(row.get(field)) for field in CSV_FIELDS})


def stringify_csv_value(value: object) -> str:
    if value is None:
        return ""
    if isinstance(value, float):
        return f"{value:.4f}"
    if isinstance(value, (list, tuple)):
        return json.dumps(value)
    return str(value)


def markdown_table(rows: list[dict[str, str]]) -> str:
    headers = [
        "run_id",
        "task",
        "status",
        "model",
        "wall_time_sec",
        "rtfx",
        "peak_memory_gb",
        "output_files",
    ]
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    for row in rows:
        values = []
        for header in headers:
            value = row.get(header, "")
            if header == "model":
                value = value.split("/")[-1]
            if header == "output_files":
                value = compact_output_files(value)
            values.append(value.replace("|", "\\|"))
        lines.append("| " + " | ".join(values) + " |")
    return "\n".join(lines)


def compact_output_files(value: str) -> str:
    if not value:
        return ""
    try:
        files = json.loads(value)
        if isinstance(files, list):
            return ", ".join(Path(item).name for item in files)
    except json.JSONDecodeError:
        pass
    return Path(value).name


def generate_report() -> Path:
    ensure_dirs()
    rows = read_csv_rows()
    recent = rows[-20:]
    lines = [
        "# Local Voice AI Lab Report",
        "",
        f"Generated: {dt.datetime.now().isoformat(timespec='seconds')}",
        "",
        "## Environment",
        "",
        f"- Platform: `{platform.platform()}`",
        f"- Machine: `{platform.machine()}`",
        f"- Python: `{platform.python_version()}`",
        f"- Executable: `{redact_text(sys.executable)}`",
        "",
        "## Recent Results",
        "",
        markdown_table(recent) if recent else "No benchmark rows yet.",
        "",
        "## CSV",
        "",
        f"Full result history: `{display_path(RESULTS_CSV)}`",
        "",
        "## Notes",
        "",
        "- TTS RTFx is parsed from MLX-Audio when available.",
        "- STT RTFx is computed as input audio duration divided by wall time.",
        "- Model size is local Hugging Face cache size when downloaded; otherwise it is remote repository file size when available.",
        "- Output artifacts live under `runs/`; aggregate reports live under `reports/`.",
        "",
        "## Model Catalog",
        "",
        model_catalog_markdown(),
        "",
    ]
    REPORT_MD.write_text("\n".join(lines), encoding="utf-8")
    generate_html_report(rows)
    return REPORT_MD


def generate_html_report(rows: list[dict[str, str]]) -> Path:
    table_rows = []
    for row in rows[-50:]:
        table_rows.append(
            "<tr>"
            f"<td>{html_escape(row.get('run_id', ''))}</td>"
            f"<td>{html_escape(row.get('task', ''))}</td>"
            f"<td>{html_escape(row.get('status', ''))}</td>"
            f"<td>{html_escape(row.get('model', '').split('/')[-1])}</td>"
            f"<td>{html_escape(row.get('wall_time_sec', ''))}</td>"
            f"<td>{html_escape(row.get('rtfx', ''))}</td>"
            f"<td>{html_escape(row.get('peak_memory_gb', ''))}</td>"
            f"<td>{html_escape(compact_output_files(row.get('output_files', '')))}</td>"
            "</tr>"
        )

    html = f"""<!doctype html>
<html lang=\"en\">
<head>
  <meta charset=\"utf-8\">
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">
  <title>Local Voice AI Lab Report</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; margin: 0; color: #111827; background: #f8fafc; }}
    header {{ background: #0f172a; color: white; padding: 32px 40px; }}
    main {{ padding: 32px 40px; }}
    h1 {{ margin: 0 0 8px; font-size: 32px; }}
    .subtitle {{ color: #cbd5e1; }}
    .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 16px; margin: 24px 0; }}
    .card {{ background: white; border: 1px solid #e5e7eb; border-radius: 8px; padding: 16px; }}
    table {{ width: 100%; border-collapse: collapse; background: white; border: 1px solid #e5e7eb; }}
    th, td {{ padding: 10px 12px; border-bottom: 1px solid #e5e7eb; text-align: left; font-size: 14px; }}
    th {{ background: #f1f5f9; }}
    code {{ background: #e5e7eb; padding: 2px 4px; border-radius: 4px; }}
  </style>
</head>
<body>
  <header>
    <h1>Local Voice AI Lab Report</h1>
    <div class=\"subtitle\">Generated {html_escape(dt.datetime.now().isoformat(timespec='seconds'))}</div>
  </header>
  <main>
    <div class=\"grid\">
      <div class=\"card\"><strong>Rows</strong><br>{len(rows)}</div>
      <div class=\"card\"><strong>Machine</strong><br>{html_escape(platform.machine())}</div>
      <div class=\"card\"><strong>Python</strong><br>{html_escape(platform.python_version())}</div>
      <div class=\"card\"><strong>CSV</strong><br><code>voice_lab_results.csv</code></div>
    </div>
    <h2>Recent Results</h2>
    <table>
      <thead>
        <tr><th>Run</th><th>Task</th><th>Status</th><th>Model</th><th>Wall time</th><th>RTFx</th><th>Peak GB</th><th>Outputs</th></tr>
      </thead>
      <tbody>
        {''.join(table_rows)}
      </tbody>
    </table>
  </main>
</body>
</html>
"""
    REPORT_HTML.write_text(html, encoding="utf-8")
    return REPORT_HTML


def html_escape(value: object) -> str:
    return (
        str(value)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def model_catalog_markdown() -> str:
    lines = [
        "| preset | task | model | command | notes |",
        "| --- | --- | --- | --- | --- |",
    ]
    for name, entry in MODEL_CATALOG.items():
        lines.append(
            "| "
            + " | ".join(
                [
                    name,
                    entry["task"],
                    entry["model"],
                    f"`{entry['command']}`",
                    entry["notes"],
                ]
            )
            + " |"
        )
    return "\n".join(lines)


def record_result(
    run_id: str,
    task: str,
    model: str,
    result: CommandResult,
    log_file: Path,
    metrics: dict[str, object],
    input_audio: Path | None = None,
    transcript: str = "",
) -> dict[str, object]:
    output_files = metrics.get("output_files") or []
    if not isinstance(output_files, list):
        output_files = [str(output_files)]

    output_duration = metrics.get("output_audio_duration_sec")
    if output_duration is None and output_files:
        output_duration = total_audio_duration(output_files)

    input_duration = ffprobe_duration(input_audio) if input_audio else None
    rtfx = metrics.get("rtfx")
    if rtfx is None and input_duration and result.wall_time_sec > 0:
        rtfx = input_duration / result.wall_time_sec

    row = {
        "timestamp": utc_timestamp(),
        "run_id": run_id,
        "task": task,
        "status": result.status,
        "model": model,
        "model_size_gib": model_size_gib(model),
        "wall_time_sec": result.wall_time_sec,
        "processing_time_sec": metrics.get("processing_time_sec"),
        "input_audio_duration_sec": input_duration,
        "output_audio_duration_sec": output_duration,
        "rtfx": rtfx,
        "peak_memory_gb": metrics.get("peak_memory_gb"),
        "output_files": output_files,
        "log_file": display_path(log_file),
        "transcript": transcript,
        "command": redact_text(shell_join(result.command)),
        "error": "" if result.status == "ok" else redact_text(result.combined_output[-2000:]),
    }
    metadata_file = write_metadata(run_id, task, row, result)
    if transcript:
        write_prediction_jsonl(run_id, task, model, input_audio, transcript)
    append_csv(row)
    generate_report()
    print(f"  metadata: {metadata_file}")
    return row


def write_metadata(
    run_id: str,
    task: str,
    row: dict[str, object],
    result: CommandResult,
) -> Path:
    run_dir = RUNS_DIR / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    path = run_dir / f"{task}.metadata.json"
    payload = {
        "row": row,
        "returncode": result.returncode,
        "command": [redact_text(part) for part in result.command],
        "stdout_tail": redact_text(result.stdout[-4000:]),
        "stderr_tail": redact_text(result.stderr[-4000:]),
    }
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return path


def write_prediction_jsonl(
    run_id: str,
    task: str,
    model: str,
    input_audio: Path | None,
    transcript: str,
) -> Path:
    run_dir = RUNS_DIR / run_id
    path = run_dir / f"{task}.predictions.jsonl"
    payload = {
        "run_id": run_id,
        "task": task,
        "model": model,
        "audio": display_path(input_audio) if input_audio else "",
        "prediction": transcript,
    }
    path.write_text(json.dumps(payload, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


def print_row_summary(row: dict[str, object]) -> None:
    print(f"{row['task']}: {row['status']}")
    print(f"  model: {row['model']}")
    print(f"  wall_time_sec: {stringify_csv_value(row.get('wall_time_sec'))}")
    print(f"  rtfx: {stringify_csv_value(row.get('rtfx'))}")
    print(f"  peak_memory_gb: {stringify_csv_value(row.get('peak_memory_gb'))}")
    output_files = row.get("output_files") or []
    if output_files:
        print("  output_files:")
        for file_name in output_files:
            print(f"    {file_name}")
    print(f"  report: {display_path(REPORT_MD)}")


def run_tts(
    task: str,
    model: str,
    text: str,
    run_id: str,
    output_dir: Path,
    file_prefix: str,
    voice: str | None = None,
    ref_audio: Path | None = None,
    ref_text: str | None = None,
    extra_args: list[str] | None = None,
    timeout_sec: int | None = None,
) -> dict[str, object]:
    run_id = validate_slug(run_id, "run id")
    file_prefix = validate_slug(file_prefix, "file prefix")
    output_dir.mkdir(parents=True, exist_ok=True)
    run_dir = RUNS_DIR / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    args = [
        "--model",
        model,
        "--text",
        text,
        "--output_path",
        str(output_dir),
        "--file_prefix",
        file_prefix,
        "--verbose",
    ]
    if voice:
        args.extend(["--voice", voice])
    if ref_audio:
        args.extend(["--ref_audio", str(ref_audio)])
    if ref_text:
        args.extend(["--ref_text", ref_text])
    if extra_args:
        args.extend(extra_args)

    result = run_command(python_module_command("mlx_audio.tts.generate", args), timeout_sec)
    log_file = write_log(run_dir, task, result)
    metrics = parse_tts_metrics(result.combined_output)
    row = record_result(run_id, task, model, result, log_file, metrics, input_audio=ref_audio)
    print_row_summary(row)
    return row


def run_stt(
    task: str,
    model: str,
    audio: Path,
    run_id: str,
    output_path: Path,
    output_format: str,
    language: str,
    timeout_sec: int | None = None,
) -> dict[str, object]:
    run_id = validate_slug(run_id, "run id")
    validate_slug(output_path.name, "file prefix")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    run_dir = RUNS_DIR / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    args = [
        "--model",
        model,
        "--audio",
        str(audio),
        "--output-path",
        str(output_path),
        "--format",
        output_format,
        "--language",
        language,
        "--verbose",
    ]
    result = run_command(python_module_command("mlx_audio.stt.generate", args), timeout_sec)
    log_file = write_log(run_dir, task, result)
    metrics = parse_stt_metrics(result.combined_output)

    transcript = ""
    transcript_path = output_path.with_suffix(f".{output_format}")
    if transcript_path.exists() and output_format == "txt":
        transcript = transcript_path.read_text(encoding="utf-8").strip()
    elif transcript_path.exists() and output_format == "json":
        try:
            transcript = json.loads(transcript_path.read_text(encoding="utf-8")).get("text", "")
        except json.JSONDecodeError:
            transcript = ""

    row = record_result(
        run_id,
        task,
        model,
        result,
        log_file,
        metrics,
        input_audio=audio,
        transcript=transcript,
    )
    print_row_summary(row)
    if transcript:
        print(f"  transcript: {transcript[:240]}")
    return row


def ensure_reference_audio() -> tuple[Path, str]:
    existing = sorted(REFERENCE_DIR.glob("voxtral_reference_*.wav"))
    if existing:
        return existing[-1], REFERENCE_TEXT

    run_id = local_run_id("reference")
    output_dir = RUNS_DIR / run_id / "audio"
    row = run_tts(
        task="reference-voxtral",
        model=VOXTRAL_MODEL,
        text=REFERENCE_TEXT,
        run_id=run_id,
        output_dir=output_dir,
        file_prefix="voxtral_reference",
        voice="casual_male",
    )
    files = row.get("output_files") or []
    if not files:
        raise RuntimeError("Reference generation did not produce an audio file.")
    source = artifact_path(files[0])
    target = REFERENCE_DIR / source.name
    target.write_bytes(source.read_bytes())
    return target, REFERENCE_TEXT


def command_voxtral(args: argparse.Namespace) -> None:
    ensure_dirs()
    run_id = args.run_id or local_run_id("voxtral")
    run_tts(
        task="voxtral-tts",
        model=args.model,
        text=args.text,
        run_id=run_id,
        output_dir=RUNS_DIR / run_id / "audio",
        file_prefix=args.file_prefix,
        voice=args.voice,
        timeout_sec=args.timeout_sec,
    )


def resolve_reference(args: argparse.Namespace) -> tuple[Path, str]:
    if args.ref_audio:
        if not getattr(args, "confirm_consent", False):
            raise SystemExit(
                "Voice cloning with --ref-audio requires --confirm-consent. "
                "Use only your own voice or a voice you have explicit permission to clone."
            )
        ref_audio = Path(args.ref_audio).expanduser()
        if not ref_audio.is_absolute():
            ref_audio = ROOT / ref_audio
        if not ref_audio.exists():
            raise SystemExit(f"Reference audio not found: {ref_audio}")
        if not args.ref_text:
            raise SystemExit("--ref-text is required when --ref-audio is provided.")
        return ref_audio, args.ref_text
    return ensure_reference_audio()


def command_qwen3(args: argparse.Namespace) -> None:
    ensure_dirs()
    ref_audio, ref_text = resolve_reference(args)
    run_id = args.run_id or local_run_id("qwen3_clone")
    run_tts(
        task="qwen3-clone",
        model=args.model,
        text=args.text,
        run_id=run_id,
        output_dir=RUNS_DIR / run_id / "audio",
        file_prefix=args.file_prefix,
        ref_audio=ref_audio,
        ref_text=ref_text,
        timeout_sec=args.timeout_sec,
    )


def command_higgs(args: argparse.Namespace) -> None:
    ensure_dirs()
    ref_audio, ref_text = resolve_reference(args)
    run_id = args.run_id or local_run_id("higgs_clone")
    run_tts(
        task="higgs-clone",
        model=args.model,
        text=args.text,
        run_id=run_id,
        output_dir=RUNS_DIR / run_id / "audio",
        file_prefix=args.file_prefix,
        ref_audio=ref_audio,
        ref_text=ref_text,
        timeout_sec=args.timeout_sec,
    )


def resolve_audio_for_stt(audio: str | None) -> Path:
    if audio:
        path = Path(audio).expanduser()
        if not path.is_absolute():
            path = ROOT / path
        if not path.exists():
            raise SystemExit(f"Audio file not found: {path}")
        return path
    ref_audio, _ = ensure_reference_audio()
    return ref_audio


def command_parakeet(args: argparse.Namespace) -> None:
    ensure_dirs()
    audio = resolve_audio_for_stt(args.audio)
    run_id = args.run_id or local_run_id("parakeet")
    file_prefix = validate_slug(args.file_prefix, "file prefix")
    model = args.model or PARAKEET_PRESETS[args.preset]
    run_stt(
        task=f"parakeet-{args.preset}",
        model=model,
        audio=audio,
        run_id=run_id,
        output_path=RUNS_DIR / run_id / "transcripts" / file_prefix,
        output_format=args.format,
        language=args.language,
        timeout_sec=args.timeout_sec,
    )


def command_suite(args: argparse.Namespace) -> None:
    ensure_dirs()
    suite_id = validate_slug(args.run_id or local_run_id(args.suite), "run id")
    base_dir = RUNS_DIR / suite_id
    base_dir.mkdir(parents=True, exist_ok=True)

    voxtral_row = run_tts(
        task="voxtral-tts",
        model=args.voxtral_model,
        text=args.text,
        run_id=suite_id,
        output_dir=base_dir / "audio",
        file_prefix="voxtral_tts",
        voice=args.voice,
        timeout_sec=args.timeout_sec,
    )
    voxtral_files = voxtral_row.get("output_files") or []
    ref_audio = artifact_path(voxtral_files[0]) if voxtral_files else None
    ref_text = args.text

    if ref_audio is None:
        ref_audio, ref_text = ensure_reference_audio()

    run_tts(
        task="qwen3-clone",
        model=args.qwen3_model,
        text=args.clone_text,
        run_id=suite_id,
        output_dir=base_dir / "audio",
        file_prefix="qwen3_clone",
        ref_audio=ref_audio,
        ref_text=ref_text,
        timeout_sec=args.timeout_sec,
    )

    parakeet_model = PARAKEET_PRESETS[args.parakeet_preset]
    run_stt(
        task=f"parakeet-{args.parakeet_preset}",
        model=parakeet_model,
        audio=ref_audio,
        run_id=suite_id,
        output_path=base_dir / "transcripts" / "parakeet_transcript",
        output_format="txt",
        language=args.language,
        timeout_sec=args.timeout_sec,
    )

    if args.suite == "all" or args.include_higgs:
        run_tts(
            task="higgs-clone",
            model=args.higgs_model,
            text=args.clone_text,
            run_id=suite_id,
            output_dir=base_dir / "audio",
            file_prefix="higgs_clone",
            ref_audio=ref_audio,
            ref_text=ref_text,
            timeout_sec=args.timeout_sec,
        )

    print(f"Suite complete: {suite_id}")
    print(f"Report: {display_path(REPORT_MD)}")


PARAKEET_PRESETS = {
    "small": PARAKEET_SMALL_MODEL,
    "v3": PARAKEET_V3_MODEL,
}


def command_report(_: argparse.Namespace) -> None:
    path = generate_report()
    print(display_path(path))


def command_models(args: argparse.Namespace) -> None:
    if args.format == "json":
        print(json.dumps(MODEL_CATALOG, indent=2))
        return
    print(model_catalog_markdown())


def check_import(module_name: str) -> tuple[bool, str]:
    try:
        __import__(module_name)
        return True, "ok"
    except Exception as exc:
        return False, f"{type(exc).__name__}: {exc}"


def command_doctor(_: argparse.Namespace) -> None:
    checks: list[tuple[str, bool, str]] = []
    checks.append(("python>=3.12", sys.version_info >= (3, 12), platform.python_version()))
    checks.append(("ffmpeg", shutil.which("ffmpeg") is not None, shutil.which("ffmpeg") or "missing"))
    checks.append(("ffprobe", shutil.which("ffprobe") is not None, shutil.which("ffprobe") or "missing"))

    for module_name in ("mlx", "mlx_audio", "huggingface_hub"):
        ok, detail = check_import(module_name)
        checks.append((f"import {module_name}", ok, detail))

    checks.append(("repo root", ROOT.exists(), display_path(ROOT)))
    checks.append(("reports dir", REPORTS_DIR.exists(), display_path(REPORTS_DIR)))

    failed = False
    for name, ok, detail in checks:
        marker = "OK" if ok else "FAIL"
        print(f"[{marker}] {name}: {detail}")
        failed = failed or not ok

    print("")
    print("Downloaded/known model sizes:")
    for name, entry in MODEL_CATALOG.items():
        size = model_size_gib(entry["model"])
        size_text = f"{size:.2f} GiB" if size is not None else "unknown"
        print(f"- {name}: {size_text} ({entry['model']})")

    if failed:
        raise SystemExit(1)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Local Voice AI Lab")
    sub = parser.add_subparsers(dest="command", required=True)

    voxtral = sub.add_parser("voxtral", help="Run local Voxtral TTS benchmark")
    voxtral.add_argument("--model", default=VOXTRAL_MODEL)
    voxtral.add_argument("--text", default=VOXTRAL_TEXT)
    voxtral.add_argument("--voice", default="casual_male")
    voxtral.add_argument("--file-prefix", default="voxtral_tts")
    voxtral.add_argument("--run-id", default=None)
    voxtral.add_argument("--timeout-sec", type=int, default=7200)
    voxtral.set_defaults(func=command_voxtral)

    qwen3 = sub.add_parser("qwen3-clone", help="Run local Qwen3 voice clone benchmark")
    qwen3.add_argument("--model", default=QWEN3_MODEL)
    qwen3.add_argument("--text", default=CLONE_TEXT)
    qwen3.add_argument("--ref-audio", default=None)
    qwen3.add_argument("--ref-text", default=None)
    qwen3.add_argument(
        "--confirm-consent",
        action="store_true",
        help="Confirm you own or have explicit permission to clone the reference voice.",
    )
    qwen3.add_argument("--file-prefix", default="qwen3_clone")
    qwen3.add_argument("--run-id", default=None)
    qwen3.add_argument("--timeout-sec", type=int, default=7200)
    qwen3.set_defaults(func=command_qwen3)

    higgs = sub.add_parser("higgs-clone", help="Run local Higgs Audio voice clone benchmark")
    higgs.add_argument("--model", default=HIGGS_MODEL)
    higgs.add_argument("--text", default=CLONE_TEXT)
    higgs.add_argument("--ref-audio", default=None)
    higgs.add_argument("--ref-text", default=None)
    higgs.add_argument(
        "--confirm-consent",
        action="store_true",
        help="Confirm you own or have explicit permission to clone the reference voice.",
    )
    higgs.add_argument("--file-prefix", default="higgs_clone")
    higgs.add_argument("--run-id", default=None)
    higgs.add_argument("--timeout-sec", type=int, default=7200)
    higgs.set_defaults(func=command_higgs)

    parakeet = sub.add_parser("parakeet", help="Run local Parakeet transcription benchmark")
    parakeet.add_argument("--preset", choices=sorted(PARAKEET_PRESETS), default="small")
    parakeet.add_argument("--model", default=None)
    parakeet.add_argument("--audio", default=None)
    parakeet.add_argument("--language", default="en")
    parakeet.add_argument("--format", choices=["txt", "json", "srt", "vtt"], default="txt")
    parakeet.add_argument("--file-prefix", default="parakeet_transcript")
    parakeet.add_argument("--run-id", default=None)
    parakeet.add_argument("--timeout-sec", type=int, default=7200)
    parakeet.set_defaults(func=command_parakeet)

    suite = sub.add_parser("suite", help="Run a repeatable benchmark suite")
    suite.add_argument("--suite", choices=["smoke", "all"], default="smoke")
    suite.add_argument("--run-id", default=None)
    suite.add_argument("--text", default=REFERENCE_TEXT)
    suite.add_argument("--clone-text", default=CLONE_TEXT)
    suite.add_argument("--voice", default="casual_male")
    suite.add_argument("--language", default="en")
    suite.add_argument("--include-higgs", action="store_true")
    suite.add_argument("--parakeet-preset", choices=sorted(PARAKEET_PRESETS), default="small")
    suite.add_argument("--voxtral-model", default=VOXTRAL_MODEL)
    suite.add_argument("--qwen3-model", default=QWEN3_MODEL)
    suite.add_argument("--higgs-model", default=HIGGS_MODEL)
    suite.add_argument("--timeout-sec", type=int, default=7200)
    suite.set_defaults(func=command_suite)

    report = sub.add_parser("report", help="Regenerate Markdown report from CSV")
    report.set_defaults(func=command_report)

    models = sub.add_parser("models", help="Print the model catalog")
    models.add_argument("--format", choices=["markdown", "json"], default="markdown")
    models.set_defaults(func=command_models)

    doctor = sub.add_parser("doctor", help="Check local lab prerequisites")
    doctor.set_defaults(func=command_doctor)

    return parser


def main() -> None:
    ensure_dirs()
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()

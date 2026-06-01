#!/usr/bin/env python3
"""Pre-publication checks for the Local Voice AI Lab repository."""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = {
    "README.md",
    "LICENSE",
    "NOTICE",
    "SECURITY.md",
    "CONTRIBUTING.md",
    "CITATION.cff",
    "pyproject.toml",
    "uv.lock",
    "reports/sample_voice_lab_report.md",
    "reports/sample_voice_lab_results.csv",
    "docs/CLAIMS.md",
    "docs/SAFETY_AND_LICENSES.md",
    "licenses/models.yml",
}

FORBIDDEN_TRACKED_PATHS = (
    ".venv/",
    "runs/",
    "artifacts/",
    "audio/",
    "__pycache__/",
    "reports/voice_lab_results.csv",
    "reports/voice_lab_report.md",
    "reports/index.html",
)

FORBIDDEN_FILE_NAMES = {".DS_Store"}

LOCAL_WORKSPACE_PATTERN = re.compile(
    r"/Users/[A-Za-z0-9_.-]+/" + re.escape("/".join(("Documents", "VoxtralTTS")))
)

SECRET_PATTERNS = {
    "local absolute path": LOCAL_WORKSPACE_PATTERN,
    "GitHub token": re.compile(r"gh[opsu]_[A-Za-z0-9_]{20,}"),
    "Mistral key assignment": re.compile(r"MISTRAL_API_KEY\s*=\s*['\"]?(?!your-api-key)[A-Za-z0-9_-]{16,}"),
    "private key block": re.compile(r"-----BEGIN (?:RSA |OPENSSH |EC |DSA )?PRIVATE KEY-----"),
}

BINARY_AUDIO_SUFFIXES = {".wav", ".mp3", ".flac", ".opus", ".aac", ".m4a", ".ogg", ".webm", ".pcm"}


def git_ls_files() -> list[str]:
    proc = subprocess.run(
        ["git", "ls-files"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip() or "git ls-files failed")
    return [line for line in proc.stdout.splitlines() if line]


def read_tracked_text(path: str) -> str:
    proc = subprocess.run(
        ["git", "show", f":{path}"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if proc.returncode == 0:
        return proc.stdout
    return (ROOT / path).read_text(encoding="utf-8", errors="ignore")


def check_required_files(tracked: set[str]) -> list[str]:
    return [f"missing required file: {path}" for path in sorted(REQUIRED_FILES - tracked)]


def check_forbidden_paths(tracked: list[str]) -> list[str]:
    failures: list[str] = []
    for path in tracked:
        if Path(path).name in FORBIDDEN_FILE_NAMES:
            failures.append(f"forbidden tracked file: {path}")
        if any(path == item.rstrip("/") or path.startswith(item) for item in FORBIDDEN_TRACKED_PATHS):
            failures.append(f"generated/private path is tracked: {path}")
        if Path(path).suffix.lower() in BINARY_AUDIO_SUFFIXES and not path.startswith("examples/audio/"):
            failures.append(f"audio artifact should not be tracked: {path}")
    return failures


def check_secrets(tracked: list[str]) -> list[str]:
    failures: list[str] = []
    for path in tracked:
        if Path(path).suffix.lower() in BINARY_AUDIO_SUFFIXES:
            continue
        text = read_tracked_text(path)
        for label, pattern in SECRET_PATTERNS.items():
            if pattern.search(text):
                failures.append(f"{label} found in {path}")
    return failures


def run_checks() -> list[str]:
    tracked = git_ls_files()
    tracked_set = set(tracked)
    failures: list[str] = []
    failures.extend(check_required_files(tracked_set))
    failures.extend(check_forbidden_paths(tracked))
    failures.extend(check_secrets(tracked))
    return failures


def main() -> None:
    failures = run_checks()
    if failures:
        print("Publish check failed:", file=sys.stderr)
        for failure in failures:
            print(f"- {failure}", file=sys.stderr)
        raise SystemExit(1)
    print("Publish check passed.")


if __name__ == "__main__":
    main()

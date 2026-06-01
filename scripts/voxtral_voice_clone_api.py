#!/usr/bin/env python3
"""Generate Voxtral TTS from a one-off reference voice clip via Mistral API."""

import argparse
import base64
import os
import time
from pathlib import Path

import requests


ALLOWED_REFERENCE_SUFFIXES = {".wav", ".mp3", ".flac", ".m4a", ".ogg", ".opus"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Clone a consenting reference voice with Mistral Voxtral TTS."
    )
    parser.add_argument("--ref-audio", required=True, help="Reference audio file path")
    parser.add_argument("--text", required=True, help="Text to synthesize")
    parser.add_argument(
        "--output", default="audio/voice_clone.mp3", help="Output audio file"
    )
    parser.add_argument(
        "--model", default="voxtral-mini-tts-2603", help="Mistral TTS model id"
    )
    parser.add_argument(
        "--format",
        default="mp3",
        choices=["mp3", "wav", "pcm", "flac", "opus"],
        help="Response audio format",
    )
    parser.add_argument(
        "--confirm-consent",
        action="store_true",
        help="Confirm you own or have explicit permission to clone the reference voice.",
    )
    parser.add_argument(
        "--max-ref-audio-mb",
        type=float,
        default=20.0,
        help="Reject reference audio larger than this many megabytes.",
    )
    parser.add_argument("--retries", type=int, default=2, help="Retry transient API failures")
    return parser.parse_args()


def validate_reference_audio(path: Path, max_mb: float) -> None:
    if not path.exists():
        raise SystemExit(f"Reference audio not found: {path}")
    if path.suffix.lower() not in ALLOWED_REFERENCE_SUFFIXES:
        allowed = ", ".join(sorted(ALLOWED_REFERENCE_SUFFIXES))
        raise SystemExit(f"Unsupported reference audio type {path.suffix!r}. Use: {allowed}")
    size_mb = path.stat().st_size / 1024**2
    if size_mb > max_mb:
        raise SystemExit(f"Reference audio is {size_mb:.1f} MB; limit is {max_mb:.1f} MB.")


def post_with_retries(
    url: str,
    headers: dict[str, str],
    payload: dict[str, str],
    retries: int,
) -> requests.Response:
    last_error: Exception | None = None
    for attempt in range(max(retries, 0) + 1):
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=120)
            if response.status_code < 500:
                return response
            last_error = RuntimeError(f"HTTP {response.status_code}: {response.text[:500]}")
        except requests.RequestException as exc:
            last_error = exc

        if attempt < retries:
            time.sleep(2**attempt)

    raise SystemExit(f"Mistral API request failed after retries: {last_error}")


def main() -> None:
    args = parse_args()
    if not args.confirm_consent:
        raise SystemExit(
            "Voice cloning requires --confirm-consent. Use only your own voice or a "
            "voice you have explicit permission to clone."
        )

    api_key = os.environ.get("MISTRAL_API_KEY")
    if not api_key:
        raise SystemExit("Set MISTRAL_API_KEY first.")

    ref_audio_path = Path(args.ref_audio)
    validate_reference_audio(ref_audio_path, args.max_ref_audio_mb)

    ref_audio_b64 = base64.b64encode(ref_audio_path.read_bytes()).decode("ascii")
    response = post_with_retries(
        "https://api.mistral.ai/v1/audio/speech",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        payload={
            "model": args.model,
            "input": args.text,
            "ref_audio": ref_audio_b64,
            "response_format": args.format,
        },
        retries=args.retries,
    )

    if response.status_code >= 400:
        raise SystemExit(f"Mistral API error {response.status_code}: {response.text[:1000]}")

    try:
        data = response.json()
    except ValueError as exc:
        raise SystemExit(f"Mistral API returned non-JSON response: {exc}") from exc

    audio_b64 = data.get("audio_data")
    if not audio_b64:
        raise SystemExit(f"No audio_data in response: {str(data)[:1000]}")

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        audio_bytes = base64.b64decode(audio_b64, validate=True)
    except ValueError as exc:
        raise SystemExit(f"Mistral API returned invalid base64 audio: {exc}") from exc
    output_path.write_bytes(audio_bytes)
    print(f"Saved {output_path}")


if __name__ == "__main__":
    main()

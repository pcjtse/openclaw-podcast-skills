#!/usr/bin/env python3
"""
generate_audio.py - Convert a podcast script to numbered MP3 segments via ElevenLabs TTS.

Usage:
    python3 generate_audio.py <script_file>

Input format (script_file):
    [HOSTNAME]: dialogue text
    [SEGMENT: Segment Name]
    [HOSTNAME]: more dialogue...

Output:
    ./output/segments/0001_ALEX.mp3
    ./output/segments/0002_JORDAN.mp3
    ...
    ./output/segments/segments.json   (segment boundary metadata)
"""

import json
import os
import sys
import time
from pathlib import Path

from elevenlabs.client import ElevenLabs

# ---------------------------------------------------------------------------
# Voice configuration — override any of these via environment variables
# ---------------------------------------------------------------------------
VOICE_IDS = {
    "ALEX":   os.getenv("ALEX_VOICE_ID",   "21m00Tcm4TlvDq8ikWAM"),  # Rachel
    "JORDAN": os.getenv("JORDAN_VOICE_ID", "pNInz6obpgDQGcFmaJgB"),  # Adam
    "SAM":    os.getenv("SAM_VOICE_ID",    "TxGEqnHWrfWFTfGW9XjX"),  # Josh
    "MORGAN": os.getenv("MORGAN_VOICE_ID", "EXAVITQu4vr4xnSDxMaL"),  # Bella
}

MODEL_ID = os.getenv("ELEVENLABS_MODEL_ID", "eleven_multilingual_v2")
OUTPUT_FORMAT = "mp3_44100_128"
SEGMENTS_DIR = Path("./output/segments")


def parse_script(script_path: str) -> list[dict]:
    """
    Parse script file into a list of entries.

    Each entry is one of:
      {"type": "line",    "index": int, "host": str, "text": str}
      {"type": "segment", "index": int, "name": str}
    """
    entries = []
    line_index = 0

    with open(script_path, "r", encoding="utf-8") as f:
        for raw_line in f:
            line = raw_line.strip()
            if not line:
                continue

            # Segment marker: [SEGMENT: Name]
            if line.startswith("[SEGMENT:") and line.endswith("]"):
                name = line[len("[SEGMENT:"):].rstrip("]").strip()
                entries.append({"type": "segment", "index": line_index, "name": name})
                line_index += 1
                continue

            # Dialogue line: [HOSTNAME]: text
            if line.startswith("[") and "]: " in line:
                bracket_end = line.index("]")
                host = line[1:bracket_end].strip().upper()
                text = line[bracket_end + 2:].strip()  # skip "]: "
                if host in VOICE_IDS and text:
                    entries.append({"type": "line", "index": line_index, "host": host, "text": text})
                    line_index += 1
                    continue

    return entries


def synthesize_line(client: ElevenLabs, text: str, voice_id: str, retries: int = 4) -> bytes | None:
    """Call ElevenLabs TTS with exponential backoff retry on rate limit errors."""
    delay = 2
    for attempt in range(retries):
        try:
            audio_generator = client.text_to_speech.convert(
                text=text,
                voice_id=voice_id,
                model_id=MODEL_ID,
                output_format=OUTPUT_FORMAT,
            )
            # The SDK returns a generator; collect all chunks into bytes
            return b"".join(audio_generator)
        except Exception as e:
            error_str = str(e)
            if "429" in error_str or "rate" in error_str.lower():
                if attempt < retries - 1:
                    print(f"  Rate limited. Retrying in {delay}s...", flush=True)
                    time.sleep(delay)
                    delay *= 2
                else:
                    print(f"  ERROR: Rate limit persists after {retries} attempts. Skipping line.", flush=True)
                    return None
            else:
                print(f"  ERROR synthesizing line: {e}", flush=True)
                return None
    return None


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python3 generate_audio.py <script_file>", file=sys.stderr)
        sys.exit(1)

    script_path = sys.argv[1]
    if not os.path.isfile(script_path):
        print(f"ERROR: Script file not found: {script_path}", file=sys.stderr)
        sys.exit(1)

    api_key = os.getenv("ELEVENLABS_API_KEY")
    if not api_key:
        print("ERROR: ELEVENLABS_API_KEY environment variable is not set.", file=sys.stderr)
        sys.exit(1)

    SEGMENTS_DIR.mkdir(parents=True, exist_ok=True)

    client = ElevenLabs(api_key=api_key)
    entries = parse_script(script_path)

    if not entries:
        print("ERROR: No dialogue lines found in script file.", file=sys.stderr)
        sys.exit(1)

    total_lines = sum(1 for e in entries if e["type"] == "line")
    print(f"Parsed {total_lines} dialogue lines from script.", flush=True)

    # Track segment boundary info for the mixer
    segment_boundaries: list[dict] = []
    audio_file_index = 0  # counts only saved MP3 files
    failed_lines = 0

    for entry in entries:
        if entry["type"] == "segment":
            segment_boundaries.append({
                "name": entry["name"],
                "audio_file_index": audio_file_index,  # index of next audio file after this marker
            })
            print(f"\n[SEGMENT: {entry['name']}]", flush=True)
            continue

        # Dialogue line
        host = entry["host"]
        text = entry["text"]
        seq = f"{audio_file_index + 1:04d}"
        filename = f"{seq}_{host}.mp3"
        out_path = SEGMENTS_DIR / filename

        print(f"  {seq} [{host}]: {text[:60]}{'...' if len(text) > 60 else ''}", flush=True)

        audio_bytes = synthesize_line(client, text, VOICE_IDS[host])

        if audio_bytes:
            out_path.write_bytes(audio_bytes)
            audio_file_index += 1
        else:
            failed_lines += 1

        # Small pause between API calls to be a good citizen
        time.sleep(0.1)

    # Save segment boundary metadata for mix_audio.py
    metadata = {
        "total_files": audio_file_index,
        "failed_lines": failed_lines,
        "segment_boundaries": segment_boundaries,
        "voice_ids": VOICE_IDS,
        "model_id": MODEL_ID,
    }
    metadata_path = SEGMENTS_DIR / "segments.json"
    metadata_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")

    print(f"\nDone. Generated {audio_file_index} audio segments ({failed_lines} failed).")
    print(f"Segments saved to: {SEGMENTS_DIR}/")
    print(f"Metadata saved to: {metadata_path}")


if __name__ == "__main__":
    main()

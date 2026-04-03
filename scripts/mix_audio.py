#!/usr/bin/env python3
"""
mix_audio.py - Combine numbered MP3 segments into a single podcast MP3.

Usage:
    python3 mix_audio.py <segments_dir> <output_path>

Reads:
    <segments_dir>/0001_ALEX.mp3, 0002_JORDAN.mp3, ...
    <segments_dir>/segments.json   (segment boundary metadata from generate_audio.py)

Output:
    <output_path>  — final podcast MP3 at 128kbps

Mixing behaviour:
    - 300ms silence between consecutive speaker turns
    - 800ms silence at [SEGMENT:] boundaries
    - Each segment normalised to -20 dBFS before concatenation
"""

import json
import sys
from pathlib import Path

from pydub import AudioSegment

# Silence durations in milliseconds
SPEAKER_PAUSE_MS = 300
SEGMENT_PAUSE_MS = 800
TARGET_DBFS = -20.0


def load_segments_metadata(segments_dir: Path) -> dict:
    meta_path = segments_dir / "segments.json"
    if meta_path.exists():
        return json.loads(meta_path.read_text(encoding="utf-8"))
    return {"segment_boundaries": [], "total_files": None}


def build_boundary_set(metadata: dict) -> set[int]:
    """Return the set of audio_file_index values that precede a segment boundary."""
    return {b["audio_file_index"] for b in metadata.get("segment_boundaries", [])}


def normalize(segment: AudioSegment, target_dbfs: float = TARGET_DBFS) -> AudioSegment:
    """Normalise an AudioSegment to the target dBFS level."""
    delta = target_dbfs - segment.dBFS
    if delta > 0:
        return segment + delta  # amplify
    return segment  # don't reduce — let natural quietness stay


def collect_mp3_files(segments_dir: Path) -> list[Path]:
    """Return sorted list of MP3 segment files (excluding segments.json)."""
    files = sorted(segments_dir.glob("*.mp3"))
    return files


def main() -> None:
    if len(sys.argv) < 3:
        print("Usage: python3 mix_audio.py <segments_dir> <output_path>", file=sys.stderr)
        sys.exit(1)

    segments_dir = Path(sys.argv[1])
    output_path = Path(sys.argv[2])

    if not segments_dir.is_dir():
        print(f"ERROR: Segments directory not found: {segments_dir}", file=sys.stderr)
        sys.exit(1)

    mp3_files = collect_mp3_files(segments_dir)
    if not mp3_files:
        print(f"ERROR: No MP3 files found in {segments_dir}", file=sys.stderr)
        sys.exit(1)

    metadata = load_segments_metadata(segments_dir)
    boundary_set = build_boundary_set(metadata)

    print(f"Mixing {len(mp3_files)} audio segments...", flush=True)

    speaker_silence = AudioSegment.silent(duration=SPEAKER_PAUSE_MS)
    segment_silence = AudioSegment.silent(duration=SEGMENT_PAUSE_MS)

    podcast = AudioSegment.empty()
    prev_host = None

    for i, mp3_path in enumerate(mp3_files):
        # Derive the sequence number from filename (e.g. "0042_SAM.mp3" → 42, host "SAM")
        stem = mp3_path.stem  # e.g. "0042_SAM"
        parts = stem.split("_", 1)
        host = parts[1] if len(parts) == 2 else "UNKNOWN"

        try:
            clip = AudioSegment.from_mp3(str(mp3_path))
        except Exception as e:
            print(f"  WARNING: Could not load {mp3_path.name}: {e}. Skipping.", flush=True)
            continue

        clip = normalize(clip)

        # Determine pause before this clip
        if i == 0:
            pause = AudioSegment.empty()  # no leading silence
        elif i in boundary_set:
            pause = segment_silence
        elif host != prev_host:
            pause = speaker_silence
        else:
            # Same host speaking back-to-back (unusual but possible) — small gap
            pause = AudioSegment.silent(duration=100)

        podcast = podcast + pause + clip
        prev_host = host

        if (i + 1) % 50 == 0:
            print(f"  Processed {i + 1}/{len(mp3_files)} segments...", flush=True)

    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)

    print(f"Exporting podcast to {output_path}...", flush=True)
    podcast.export(str(output_path), format="mp3", bitrate="128k")

    duration_ms = len(podcast)
    duration_min = duration_ms // 60000
    duration_sec = (duration_ms % 60000) // 1000
    print(f"\nDone! Podcast duration: {duration_min}m {duration_sec:02d}s")
    print(f"Output: {output_path}")


if __name__ == "__main__":
    main()

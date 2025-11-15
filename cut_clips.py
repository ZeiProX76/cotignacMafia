#!/usr/bin/env python3
import json
import subprocess
import re
from pathlib import Path


def sanitize_filename(name: str) -> str:
    """Remove unsafe chars, keep readable names"""
    name = name.strip()
    name = re.sub(r"[^\w\-\. ]+", "_", name, flags=re.UNICODE)
    name = re.sub(r"\s+", "_", name)
    return name or "clip"


def run_ffmpeg(cmd: list[str]) -> None:
    """Run ffmpeg command and handle errors"""
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    if proc.returncode != 0:
        print(proc.stdout)
        raise SystemExit(f"ffmpeg failed with exit code {proc.returncode}")


def cut_clip_fast(input_path: Path, start: str, end: str, out_path: Path) -> None:
    """
    Fast (keyframe-based) cut. No re-encode, super quick.
    Uses -ss and -to both after -i for accurate timestamps.
    """
    cmd = [
        "ffmpeg",
        "-hide_banner", "-y",
        "-i", str(input_path),
        "-ss", start,
        "-to", end,
        "-c", "copy",
        "-avoid_negative_ts", "make_zero",
        str(out_path),
    ]
    run_ffmpeg(cmd)


def cut_best_clips(video_path: str, json_path: str, output_dir: str = "clips_out"):
    """
    Read JSON response and cut the product_demos using ffmpeg
    """
    # Validate inputs
    video_file = Path(video_path).expanduser().resolve()
    if not video_file.exists():
        raise SystemExit(f"Video file not found: {video_file}")

    json_file = Path(json_path).expanduser().resolve()
    if not json_file.exists():
        raise SystemExit(f"JSON file not found: {json_file}")

    # Create output directory
    out_dir = Path(output_dir).expanduser().resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    # Load JSON
    with open(json_file, 'r') as f:
        data = json.load(f)

    best_clips = data.get("product_demos", [])
    if not best_clips:
        raise SystemExit("No product_demos found in JSON")

    print(f"Found {len(best_clips)} product demos")
    print(f"Input video: {video_file}")
    print(f"Output directory: {out_dir}")
    print("-" * 60)

    # Cut each clip
    output_metadata = []

    for i, clip in enumerate(best_clips, start=1):
        start = clip.get("start", "")
        end = clip.get("end", "")
        demo_type = clip.get("demo_type", "")
        description = clip.get("description", "")

        # Create filename from demo_type
        filename_base = sanitize_filename(demo_type)
        output_path = out_dir / f"clip_{i:02d}_{filename_base}.mp4"

        print(f"[{i}/{len(best_clips)}] Cutting: {start} → {end}")
        print(f"  Type: {demo_type}")
        print(f"  Description: {description}")
        print(f"  Output: {output_path.name}")

        # Cut the clip
        cut_clip_fast(video_file, start, end, output_path)

        # Save metadata
        output_metadata.append({
            "clip_number": i,
            "filename": output_path.name,
            "start": start,
            "end": end,
            "demo_type": demo_type,
            "description": description,
            "visual_quality": clip.get("visual_quality", ""),
            "content_potential": clip.get("content_potential", "")
        })

        print(f"  ✓ Done\n")

    # Save metadata JSON
    metadata_path = out_dir / "clips_metadata.json"
    with open(metadata_path, 'w') as f:
        json.dump({
            "source_video": str(video_file),
            "clips": output_metadata
        }, f, indent=2)

    print("-" * 60)
    print(f"✓ All clips saved to: {out_dir}")
    print(f"✓ Metadata saved to: {metadata_path}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Cut product demo clips from video using JSON response")
    parser.add_argument("video", help="Path to the source video file")
    parser.add_argument("json", help="Path to the JSON response file")
    parser.add_argument("--out-dir", default="clips_out", help="Output directory (default: clips_out)")

    args = parser.parse_args()

    cut_best_clips(args.video, args.json, args.out_dir)

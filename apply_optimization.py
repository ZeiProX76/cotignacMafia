#!/usr/bin/env python3
import json
import subprocess
import pathlib
import shutil

def get_duration(path):
    """Get video duration"""
    result = subprocess.run([
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        str(path)
    ], capture_output=True, text=True, check=True)
    return float(result.stdout.strip())

def mmss_to_seconds(ts):
    """MM:SS or MM:SS.ms -> seconds"""
    parts = ts.split(":")
    return int(parts[0]) * 60 + float(parts[1])

def cut_clip(input_path, start, end, output_path):
    """Cut clip"""
    subprocess.run([
        "ffmpeg", "-hide_banner", "-y",
        "-i", str(input_path),
        "-ss", start,
        "-to", end,
        "-c", "copy",
        "-avoid_negative_ts", "make_zero",
        str(output_path)
    ], capture_output=True, check=True)

def main():
    with open("clips_optimization.json") as f:
        data = json.load(f)

    clips_dir = pathlib.Path("clips_out")
    output_dir = pathlib.Path("clips_clean")
    output_dir.mkdir(exist_ok=True)

    print(f"Processing {len(data['clips'])} clips\n")

    for i, clip in enumerate(data["clips"], 1):
        src = clips_dir / clip["source_filename"]
        if not src.exists():
            continue

        human_at = clip.get("human_at", "none")
        output_file = output_dir / clip["output_filename"]

        print(f"[{i}] {clip['source_filename']}")

        # No human → keep clip
        if human_at == "none":
            print(f"    No human, keeping clip")
            shutil.copy2(src, output_file)
            print(f"    ✓ {output_file.name}\n")
        else:
            # Has human → SKIP IT
            print(f"    Human detected at {human_at}, filtering out (skipping)\n")

    print(f"✓ All clips saved to: {output_dir}")

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Cut the 9 clean segments with millisecond precision."""

import sys
from pathlib import Path

# Add firsttrial directory to path
sys.path.insert(0, str(Path(__file__).parent / "firsttrial"))

from steps.step5_cut_clips import cut_clips

# Paths
VIDEO_PATH = "/home/hugues/Downloads/videoplayback (1).mp4"
SCENE_SELECTION = Path(__file__).parent / "firsttrial" / "outputs" / "step4_clean_segments.json"
OUTPUT_DIR = Path(__file__).parent / "firsttrial" / "outputs" / "clean_clips"

print("=" * 60)
print("CUTTING 9 CLEAN SEGMENTS - MILLISECOND PRECISION")
print("=" * 60)
print(f"Video: {VIDEO_PATH}")
print(f"Scenes: {SCENE_SELECTION}")
print(f"Output: {OUTPUT_DIR}")
print()

# Cut clips
result = cut_clips(
    video_path=VIDEO_PATH,
    scene_selection_path=SCENE_SELECTION,
    output_dir=OUTPUT_DIR,
    verbose=True
)

print()
print(f"✅ Successfully cut {len(result.clips)} clips!")
print(f"📁 Clips saved to: {OUTPUT_DIR}")

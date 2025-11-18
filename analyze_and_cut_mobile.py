#!/usr/bin/env python3
"""Analyze clip_04 and extract ONLY mobile animation."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "firsttrial"))

from steps.step4_targeted_analysis import targeted_analysis
from steps.step5_cut_clips import cut_clips

# Paths
VIDEO_PATH = "/home/hugues/qwenTest/firsttrial/outputs/clean_clips/clip_04_Mobile_preview_animation_with_engagement_elements.mp4"
PROMPT_PATH = Path(__file__).parent / "clip04_prompt.txt"
ANALYSIS_OUTPUT = Path(__file__).parent / "clip04_mobile_only.json"
FINAL_OUTPUT_DIR = Path(__file__).parent / "firsttrial" / "outputs" / "mobile_only"

print("=" * 60)
print("EXTRACT MOBILE ANIMATION ONLY")
print("=" * 60)
print(f"Source: {VIDEO_PATH}")
print()

# Step 1: Analyze to find mobile animation
print("STEP 1: Finding mobile animation timestamps...")
result = targeted_analysis(
    video_url=VIDEO_PATH,
    prompt_path=PROMPT_PATH,
    output_path=ANALYSIS_OUTPUT,
    verbose=True
)

print()
print("=" * 60)
print(f"Found {len(result.scenes)} segment(s)")
for scene in result.scenes:
    print(f"  [{scene.start} → {scene.end}] {scene.description}")
print("=" * 60)
print()

# Step 2: Cut the mobile animation
print("STEP 2: Cutting mobile animation...")
cut_clips(
    video_path=VIDEO_PATH,
    scene_selection_path=ANALYSIS_OUTPUT,
    output_dir=FINAL_OUTPUT_DIR,
    verbose=True
)

print()
print(f"✅ Mobile animation extracted to: {FINAL_OUTPUT_DIR}")

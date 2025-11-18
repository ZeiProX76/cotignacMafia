#!/usr/bin/env python3
"""Run step4 targeted analysis to find clean UI segments."""

import sys
from pathlib import Path

# Add firsttrial directory to path
sys.path.insert(0, str(Path(__file__).parent / "firsttrial"))

from steps.step4_targeted_analysis import targeted_analysis

# Video path
VIDEO_PATH = "/home/hugues/Downloads/videoplayback (1).mp4"
PROMPT_PATH = Path(__file__).parent / "firsttrial" / "outputs" / "step3_generated_prompt.txt"
OUTPUT_PATH = Path(__file__).parent / "firsttrial" / "outputs" / "step4_clean_segments.json"

print("=" * 60)
print("FINDING CLEAN UI SEGMENTS")
print("=" * 60)
print(f"Video: {VIDEO_PATH}")
print(f"Prompt: {PROMPT_PATH}")
print(f"Output: {OUTPUT_PATH}")
print()

# Run targeted analysis
result = targeted_analysis(
    video_url=VIDEO_PATH,
    prompt_path=PROMPT_PATH,
    output_path=OUTPUT_PATH,
    verbose=True
)

print()
print("=" * 60)
print(f"✅ Found {len(result.scenes)} clean segments!")
print("=" * 60)
for i, scene in enumerate(result.scenes, 1):
    print(f"{i}. [{scene.start} → {scene.end}] {scene.description}")

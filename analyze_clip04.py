#!/usr/bin/env python3
"""Analyze clip_04 to find ONLY mobile animation (no text)."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "firsttrial"))

from steps.step2_analyze_screen import analyze_screen

VIDEO_PATH = "/home/hugues/qwenTest/firsttrial/outputs/clean_clips/clip_04_Mobile_preview_animation_with_engagement_elements.mp4"
OUTPUT_PATH = Path(__file__).parent / "clip04_analysis.json"

print("Analyzing clip_04 for mobile animation only...")
print(f"Video: {VIDEO_PATH}")
print()

result = analyze_screen(
    video_url=VIDEO_PATH,
    output_path=OUTPUT_PATH,
    verbose=True
)

print(f"\n✅ Found {len(result.activities)} segments")

#!/usr/bin/env python3
"""Quick script to analyze a new video using step2."""

import sys
from pathlib import Path

# Add firsttrial directory to path
sys.path.insert(0, str(Path(__file__).parent / "firsttrial"))

from steps.step2_analyze_screen import analyze_screen
from pathlib import Path

# Video to analyze
VIDEO_PATH = "/home/hugues/Downloads/videoplayback (1).mp4"
OUTPUT_PATH = Path(__file__).parent / "firsttrial" / "outputs" / "new_video_analysis.json"

print(f"Analyzing video: {VIDEO_PATH}")
print(f"Output will be saved to: {OUTPUT_PATH}")
print()

# Run analysis
result = analyze_screen(
    video_url=VIDEO_PATH,
    output_path=OUTPUT_PATH,
    verbose=True
)

print(f"\n✅ Analysis complete! Found {len(result.activities)} activities")
print(f"📄 Results saved to: {OUTPUT_PATH}")

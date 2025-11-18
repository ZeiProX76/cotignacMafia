#!/usr/bin/env python3
"""
Step 2: Analyze ALL screen activities in main video.

Captures every screen activity from start to finish, including segments with humans.
The filtering for humans happens later in the pipeline (step 4).
"""

import sys
import os
import json
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

import dashscope
from dotenv import load_dotenv
from utils import parse_and_save_json
from schemas import ScreenAnalysisOutput
import config

load_dotenv()

dashscope.base_http_api_url = 'https://dashscope-intl.aliyuncs.com/api/v1'

SCREEN_ANALYSIS_PROMPT = """Analyze this ENTIRE video from start to finish.

Describe what's shown on screen in segments (you choose the granularity - every 10-20 seconds works well).

IMPORTANT:
- Start from 00:00 and cover the ENTIRE video timeline
- Include ALL segments (even those with humans talking)
- For each segment, note what's being shown on screen (UI, demos, animations, text, graphics, etc.)
- Keep descriptions focused and under 15 words each

Output JSON only:

{
  "activities": [
    {"start": "00:00", "end": "00:10", "description": "brief description of what's on screen", "activity_type": "demo"},
    {"start": "00:10", "end": "00:30", "description": "next segment description", "activity_type": "demo"}
  ]
}

activity_type can be: "demo", "ui", "animation", "text", "graphics", "product", "code", etc.

Make sure to cover the COMPLETE video from beginning to end."""


def analyze_screen(
    video_url: str = None,
    video_id: str = None,
    output_path: Path = None,
    verbose: bool = True
) -> ScreenAnalysisOutput:
    """
    Analyze ALL screen activities in video from start to finish.

    Args:
        video_url: Video URL for VLM (optional if video_id provided)
        video_id: Video identifier for multi-video support (e.g., 'video_001')
        output_path: Custom output path (optional)
        verbose: Print progress messages

    Returns:
        ScreenAnalysisOutput with all screen activities

    Note:
        If video_id is provided, uses outputs/{video_id}/ directory.
        Otherwise uses legacy single-video output path.
    """
    # Multi-video mode: load from config if video_id provided
    if video_id:
        from schemas import VideoConfig
        videos_cfg = config.load_videos_config()
        video_cfg = next((v for v in videos_cfg.videos if v.id == video_id), None)
        if not video_cfg:
            raise ValueError(f"Video ID '{video_id}' not found in videos_config.json")

        video_url = video_cfg.url
        output_path = output_path or config.get_video_step_output(video_id, 2)
        config.create_video_directories(video_id)
    else:
        # Legacy single-video mode
        video_url = video_url or config.AVATAR_VIDEO_URL  # Fallback since MAIN_VIDEO_URL removed
        output_path = output_path or config.STEP2_OUTPUT

    # Additional output paths for debugging
    reasoning_output = output_path.parent / f"{output_path.stem}_reasoning.txt"
    full_response_output = output_path.parent / f"{output_path.stem}_full_response.json"

    if verbose:
        print("=" * 60)
        print("STEP 2: ANALYZE ALL SCREEN ACTIVITIES")
        print("=" * 60)
        if video_id:
            print(f"Video ID: {video_id}")
        print(f"Video URL: {video_url}")
        print(f"Model: {config.QWEN_VIDEO_MODEL}")
        print(f"Output: {output_path}")
        print(f"Reasoning: {reasoning_output}")
        print(f"Full response: {full_response_output}")
        print()

    # Validate configuration
    config.validate_config()

    messages = [{
        "role": "user",
        "content": [
            {"video": video_url},
            {"text": SCREEN_ANALYSIS_PROMPT}
        ]
    }]

    if verbose:
        print("🎬 Analyzing ALL screen activities from 00:00 to end...")
        print("   (This may take a few minutes)")
        print()

    response = dashscope.MultiModalConversation.call(
        api_key=os.getenv("DASHSCOPE_API_KEY"),
        model='qwen3-vl-32b-thinking',
        messages=messages
    )

    # Extract result text
    try:
        result_text = response.output.choices[0].message.content[0]["text"]
    except (IndexError, KeyError, TypeError) as e:
        print(f"Primary format failed: {e}")
        # Try alternative formats
        if hasattr(response.output, 'text'):
            result_text = response.output.text
        elif isinstance(response.output.choices[0].message.content, str):
            result_text = response.output.choices[0].message.content
        else:
            print("Full response structure:")
            print(response)
            raise Exception("Could not extract text from response")

    # Extract reasoning content if available
    reasoning_text = ""
    try:
        reasoning_text = response.output.choices[0].message.reasoning_content
    except (IndexError, KeyError, TypeError, AttributeError):
        if verbose:
            print("⚠️  No reasoning content available")

    # Save reasoning content
    if reasoning_text and verbose:
        print(f"\n💾 Saving reasoning content to: {reasoning_output}")
        with open(reasoning_output, 'w', encoding='utf-8') as f:
            f.write(reasoning_text)

    # Save full response for debugging
    try:
        full_response_dict = {
            "result_text": result_text,
            "reasoning_text": reasoning_text,
            "raw_output": str(response.output)
        }
        with open(full_response_output, 'w', encoding='utf-8') as f:
            json.dump(full_response_dict, f, indent=2, ensure_ascii=False)
        if verbose:
            print(f"💾 Saved full response to: {full_response_output}")
    except Exception as e:
        if verbose:
            print(f"⚠️  Could not save full response: {e}")

    if verbose:
        print("\n📝 Model Response:")
        print("-" * 60)
        print(result_text[:1000] + ("..." if len(result_text) > 1000 else ""))
        print("-" * 60)
        print()

    # Parse and save JSON
    if verbose:
        print("💾 Parsing and saving JSON...")

    parsed_data = parse_and_save_json(result_text, output_path)

    # Validate with Pydantic
    if verbose:
        print("✅ Validating output schema...")

    validated = ScreenAnalysisOutput(**parsed_data)

    # Check if we got early segments
    earliest_start = min(activity.start for activity in validated.activities) if validated.activities else "N/A"

    # Display results
    if verbose:
        print()
        print("=" * 60)
        print("RESULTS")
        print("=" * 60)
        print(f"Total activities detected: {len(validated.activities)}")
        print(f"Earliest timestamp: {earliest_start}")
        print()

        if earliest_start != "00:00" and earliest_start not in ["00:01", "00:02", "00:03", "00:04", "00:05"]:
            print("⚠️  WARNING: Analysis doesn't start near 00:00!")
            print(f"   First segment starts at: {earliest_start}")
            print("   Early content may be missing!")
            print()

        print("First 5 activities:")
        for i, activity in enumerate(validated.activities[:5], 1):
            print(f"\n{i}. [{activity.start} → {activity.end}]")
            if activity.activity_type:
                print(f"   Type: {activity.activity_type}")
            print(f"   {activity.description}")

        if len(validated.activities) > 5:
            print(f"\n... and {len(validated.activities) - 5} more activities")

        print()
        print(f"✅ Screen analysis saved to: {output_path}")
        print("=" * 60)

    return validated


if __name__ == "__main__":
    try:
        analyze_screen(verbose=True)
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        sys.exit(1)

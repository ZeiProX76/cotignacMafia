#!/usr/bin/env python3
"""
Step 8: Create final timeline JSON.

Maps b-roll clips to avatar video timestamps based on transcript and clip descriptions.
"""

import sys
import os
import json
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from openai import OpenAI
from dotenv import load_dotenv
from utils import load_json, save_json
import config

load_dotenv()

MODEL = "gpt-5-mini-2025-08-07"

SYSTEM_PROMPT = """You are a video editing AI. Your job is to create a timeline that maps b-roll clips to an avatar video.

Given:
1. Avatar video transcript with timestamps
2. Available b-roll clips with descriptions

Create a JSON timeline that specifies:
- When to show each b-roll clip
- What text overlays to display
- Scene types (hook, speaking, tutorial, cta)

Rules:
- B-roll should match the narration content
- Don't overlap clips
- Use EVERY available b-roll clip if possible
- Keep text overlays short and impactful
- Align timing with natural speech pauses

Output ONLY valid JSON, no explanation."""


def create_timeline(
    transcript_path: Path = None,
    clips_summary_path: Path = None,
    avatar_video_path: str = None,
    output_path: Path = None,
    verbose: bool = True
) -> dict:
    """
    Create timeline JSON using GPT-5.

    Args:
        transcript_path: Path to step 1 output (default: from config)
        clips_summary_path: Path to step 7 summary (default: from config)
        avatar_video_path: Path to avatar video (default: from config)
        output_path: Output path for timeline JSON (default: from config)
        verbose: Print progress messages

    Returns:
        Timeline dictionary
    """
    # Use config defaults if not provided
    transcript_path = transcript_path or config.STEP1_OUTPUT
    clips_summary_path = clips_summary_path or (config.CLIPS_FINAL_DIR / "final_summary.json")
    avatar_video_path = avatar_video_path or config.MAIN_VIDEO_LOCAL
    output_path = output_path or (config.OUTPUTS_DIR / "step8_timeline.json")

    if verbose:
        print("=" * 60)
        print("STEP 8: CREATE TIMELINE")
        print("=" * 60)
        print(f"Transcript: {transcript_path}")
        print(f"Clips summary: {clips_summary_path}")
        print(f"Output: {output_path}")
        print()

    # Validate inputs
    if not transcript_path.exists():
        raise ValueError(f"Transcript not found: {transcript_path}\nRun step 1 first!")

    if not clips_summary_path.exists():
        raise ValueError(f"Clips summary not found: {clips_summary_path}\nRun step 7 first!")

    # Load transcript
    if verbose:
        print("📂 Loading transcript...")

    transcript_data = load_json(transcript_path)

    if verbose:
        print(f"   ✓ Loaded {len(transcript_data['sentences'])} sentences")

    # Load clips summary
    if verbose:
        print("📂 Loading clips summary...")

    clips_data = load_json(clips_summary_path)
    kept_clips = clips_data.get("kept", [])

    if verbose:
        print(f"   ✓ Loaded {len(kept_clips)} clean clips")
        print()

    if not kept_clips:
        print("⚠️  No clean clips available - cannot create timeline")
        return None

    # Build clips info for GPT
    clips_info = []
    for clip in kept_clips:
        context = clip.get("context") or {}
        description = context.get("description", "Unknown") if isinstance(context, dict) else "Unknown"

        clip_info = {
            "filename": clip["final"],
            "duration": f"{clip['start']} → {clip['end']}",
            "description": description
        }
        clips_info.append(clip_info)

    # Create prompt
    user_prompt = f"""Create a video timeline that maps these b-roll clips to the avatar video narration.

AVATAR VIDEO: {avatar_video_path}

TRANSCRIPT:
{json.dumps(transcript_data['sentences'], indent=2)}

AVAILABLE B-ROLL CLIPS:
{json.dumps(clips_info, indent=2)}

Create a timeline JSON with this structure:
{{
  "avatarVideo": "{avatar_video_path}",
  "scenes": [
    {{
      "type": "hook|speaking|tutorial|cta",
      "startTime": 0.0,
      "endTime": 2.5,
      "text": "OVERLAY TEXT",
      "broll": "clip_filename.mp4"
    }}
  ]
}}

Map ALL available b-roll clips to appropriate timestamps based on narration content."""

    if verbose:
        print("🤖 Asking GPT-5 to create timeline...")
        print()

    # Call GPT-5 using Responses API
    try:
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        # Combine system prompt and user prompt for GPT-5
        full_input = f"{SYSTEM_PROMPT}\n\n{user_prompt}"

        response = client.responses.create(
            model=MODEL,
            input=full_input,
            reasoning={"effort": "medium"},
            text={"verbosity": "medium"}
        )

        result_text = response.output_text

        if verbose:
            print("=" * 60)
            print("GPT-5 RESPONSE:")
            print("=" * 60)
            print(result_text)
            print("=" * 60)
            print()

        # Clean JSON
        cleaned = result_text.strip()
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]
        if cleaned.startswith("```"):
            cleaned = cleaned[3:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]

        timeline = json.loads(cleaned.strip())

        # Save timeline
        save_json(timeline, output_path)

        if verbose:
            print("=" * 60)
            print("RESULTS")
            print("=" * 60)
            print(f"Scenes created: {len(timeline.get('scenes', []))}")
            print(f"Output: {output_path}")
            print("=" * 60)

        return timeline

    except Exception as e:
        print(f"\n❌ Error: {e}")
        raise


if __name__ == "__main__":
    try:
        create_timeline(verbose=True)
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        sys.exit(1)

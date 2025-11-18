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
    top15_metadata_path: Path = None,
    avatar_video_url: str = None,
    output_path: Path = None,
    verbose: bool = True
) -> dict:
    """
    Create timeline JSON using GPT-5 from TOP 15 clips.

    Args:
        transcript_path: Path to step 1 output (default: from config)
        top15_metadata_path: Path to step 7 top15 metadata (default: from config)
        avatar_video_url: URL to avatar video (default: from config)
        output_path: Output path for timeline JSON (default: from config)
        verbose: Print progress messages

    Returns:
        Timeline dictionary

    Note:
        Updated for multi-video pipeline: Uses top15/ clips selected by GPT-5 Mini
        instead of clips_final/. Timeline references clips in outputs/top15/.
    """
    # Use config defaults if not provided
    transcript_path = transcript_path or config.STEP1_OUTPUT
    top15_metadata_path = top15_metadata_path or config.STEP7_OUTPUT
    avatar_video_url = avatar_video_url or config.AVATAR_VIDEO_URL
    output_path = output_path or config.STEP8_OUTPUT

    if verbose:
        print("=" * 60)
        print("STEP 8: CREATE REMOTION TIMELINE FROM TOP 15 CLIPS")
        print("=" * 60)
        print(f"Transcript: {transcript_path}")
        print(f"Top 15 metadata: {top15_metadata_path}")
        print(f"Avatar video: {avatar_video_url[:60]}...")
        print(f"Output: {output_path}")
        print()

    # Validate inputs
    if not transcript_path.exists():
        raise ValueError(f"Transcript not found: {transcript_path}\nRun step 1 first!")

    if not top15_metadata_path.exists():
        raise ValueError(f"Top 15 metadata not found: {top15_metadata_path}\nRun step 7 first!")

    # Load transcript
    if verbose:
        print("📂 Loading transcript...")

    transcript_data = load_json(transcript_path)

    if verbose:
        print(f"   ✓ Loaded {len(transcript_data['sentences'])} sentences")

    # Load top 15 clips metadata
    if verbose:
        print("📂 Loading top 15 clips...")

    from schemas import Top15Selection
    top15_data = load_json(top15_metadata_path)
    top15 = Top15Selection(**top15_data)

    if verbose:
        print(f"   ✓ Loaded {len(top15.selected_clips)} top 15 clips")
        print(f"   Selection reasoning: {top15.selection_criteria[:80]}...")
        print()

    if not top15.selected_clips:
        print("⚠️  No clips in top 15 - cannot create timeline")
        return None

    # Build clips info for GPT from top 15
    clips_info = []
    for clip in top15.selected_clips:
        clip_info = {
            "filename": clip.top15_filename,  # Use top15 filename
            "rank": clip.rank,
            "video_source": clip.video_id,
            "duration_seconds": clip.duration_seconds,
            "clean_timestamps": f"{clip.clean_start or 'N/A'} → {clip.clean_end or 'N/A'}",
            "description": clip.description,
            "reason": clip.reason or "N/A",
            "quality_score": f"{clip.normalized_score:.1f}/100"
        }
        clips_info.append(clip_info)

    # Create prompt
    user_prompt = f"""Create a video timeline that maps these TOP 15 b-roll clips to the avatar video narration.

AVATAR VIDEO: {avatar_video_url}

TRANSCRIPT:
{json.dumps(transcript_data['sentences'], indent=2)}

AVAILABLE B-ROLL CLIPS (ranked by quality):
{json.dumps(clips_info, indent=2)}

Create a timeline JSON with this structure:
{{
  "avatarVideo": "{avatar_video_url}",
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

#!/usr/bin/env python3
"""
Step 1: Transcribe avatar video audio to sentences with timestamps.

Uses Qwen3-Omni-Flash (audio-aware model) to extract every sentence
spoken in the video with precise start/end timestamps.
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils import QwenClient, parse_and_save_json
from schemas import TranscriptionOutput
import config


TRANSCRIPTION_PROMPT = """Listen carefully to the audio in this video.

Extract EVERY SENTENCE spoken with its exact start and end timestamps.

Output ONLY valid JSON in this format:
{
  "sentences": [
    {
      "start": "MM:SS",
      "end": "MM:SS",
      "text": "The exact sentence spoken"
    }
  ]
}

Requirements:
- Each sentence must have its own entry
- Use MM:SS format for timestamps (e.g., "01:23" for 1 minute 23 seconds)
- Capture the exact words spoken
- Include ALL sentences from start to finish
- Maintain chronological order
"""


def transcribe_avatar(
    video_url: str = None,
    output_path: Path = None,
    verbose: bool = True
) -> TranscriptionOutput:
    """
    Transcribe avatar video audio to sentences with timestamps.

    Args:
        video_url: URL to avatar video (default: from config)
        output_path: Output JSON path (default: from config)
        verbose: Print progress messages

    Returns:
        TranscriptionOutput object with validated sentences

    Raises:
        ValueError: If API keys not configured
        Exception: If API call fails or JSON parsing fails
    """
    # Use config defaults if not provided
    video_url = video_url or config.AVATAR_VIDEO_URL
    output_path = output_path or config.STEP1_OUTPUT

    if verbose:
        print("=" * 60)
        print("STEP 1: TRANSCRIBE AVATAR VIDEO")
        print("=" * 60)
        print(f"Video URL: {video_url}")
        print(f"Model: {config.QWEN_AUDIO_MODEL}")
        print(f"Output: {output_path}")
        print()

    # Validate configuration
    config.validate_config()

    # Initialize Qwen client
    if verbose:
        print("🔄 Initializing Qwen client...")
    client = QwenClient()

    # Analyze video with streaming model (supports audio)
    if verbose:
        print("🎤 Transcribing audio with timestamps...")
        print("   (This may take a few minutes)")
        print()

    response_text = client.analyze_video_streaming(
        video_url=video_url,
        prompt=TRANSCRIPTION_PROMPT,
        model=config.QWEN_AUDIO_MODEL,
        modalities=["text"]
    )

    if verbose:
        print("\n📝 Model Response:")
        print("-" * 60)
        print(response_text[:500] + ("..." if len(response_text) > 500 else ""))
        print("-" * 60)
        print()

    # Parse and save JSON
    if verbose:
        print("💾 Parsing and saving JSON...")

    parsed_data = parse_and_save_json(response_text, output_path)

    # Validate with Pydantic
    if verbose:
        print("✅ Validating output schema...")

    validated = TranscriptionOutput(**parsed_data)

    # Display results
    if verbose:
        print()
        print("=" * 60)
        print("RESULTS")
        print("=" * 60)
        print(f"Total sentences: {len(validated.sentences)}")
        print()
        print("Sample sentences:")
        for i, sentence in enumerate(validated.sentences[:3], 1):
            print(f"\n{i}. [{sentence.start} → {sentence.end}]")
            print(f"   {sentence.text[:100]}{'...' if len(sentence.text) > 100 else ''}")

        if len(validated.sentences) > 3:
            print(f"\n... and {len(validated.sentences) - 3} more sentences")

        print()
        print(f"✅ Transcription saved to: {output_path}")
        print("=" * 60)

    return validated


if __name__ == "__main__":
    try:
        transcribe_avatar(verbose=True)
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        sys.exit(1)

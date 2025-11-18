#!/usr/bin/env python3
"""
Transcribe two Instagram videos for script analysis.
"""

import sys
from pathlib import Path

# Add firsttrial to path
sys.path.insert(0, str(Path(__file__).parent / "firsttrial"))

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


def transcribe_video(video_url: str, output_name: str, video_label: str, verbose: bool = True):
    """Transcribe a video from URL."""

    output_path = Path(config.OUTPUTS_DIR) / f"{output_name}.json"

    if verbose:
        print("=" * 80)
        print(f"TRANSCRIBING: {video_label}")
        print("=" * 80)
        print(f"URL: {video_url}")
        print(f"Model: {config.QWEN_AUDIO_MODEL}")
        print(f"Output: {output_path}")
        print()

    # Validate API keys
    config.validate_config()

    # Initialize client
    if verbose:
        print("🔄 Initializing Qwen client...")
    client = QwenClient()

    # Transcribe
    if verbose:
        print("🎤 Transcribing audio... (this may take a few minutes)")
        print()

    try:
        response_text = client.analyze_video_streaming(
            video_url=video_url,
            prompt=TRANSCRIPTION_PROMPT,
            model=config.QWEN_AUDIO_MODEL,
            modalities=["text"]
        )

        if verbose:
            print("\n📝 Model Response:")
            print("-" * 80)
            print(response_text[:800] + ("..." if len(response_text) > 800 else ""))
            print("-" * 80)
            print()

        # Parse and save
        if verbose:
            print("💾 Parsing and saving JSON...")

        parsed_data = parse_and_save_json(response_text, output_path)

        # Validate
        if verbose:
            print("✅ Validating output schema...")

        validated = TranscriptionOutput(**parsed_data)

        # Display results
        if verbose:
            print()
            print("=" * 80)
            print("RESULTS")
            print("=" * 80)
            print(f"Total sentences: {len(validated.sentences)}")
            print()
            print("All sentences:")
            print()
            for i, sentence in enumerate(validated.sentences, 1):
                print(f"{i}. [{sentence.start} → {sentence.end}]")
                print(f"   {sentence.text}")
                print()

            print(f"✅ Transcription saved to: {output_path}")
            print("=" * 80)
            print()

        return validated

    except Exception as e:
        print(f"\n❌ Error transcribing {video_label}: {e}")
        raise


if __name__ == "__main__":
    try:
        # Video 1
        print("\n\n")
        print("█" * 80)
        print("VIDEO 1: get (1).mp4")
        print("█" * 80)
        result1 = transcribe_video(
            "https://efuozhjlnyrcyritksiy.supabase.co/storage/v1/object/public/cotignac/get%20(1).mp4",
            "instagram_video_1_transcription",
            "get (1).mp4"
        )

        print("\n\n")

        # Video 2
        print("█" * 80)
        print("VIDEO 2: get (2).mp4")
        print("█" * 80)
        result2 = transcribe_video(
            "https://efuozhjlnyrcyritksiy.supabase.co/storage/v1/object/public/cotignac/get%20(2).mp4",
            "instagram_video_2_transcription",
            "get (2).mp4"
        )

        print("\n\n")
        print("█" * 80)
        print("✅ BOTH TRANSCRIPTIONS COMPLETE!")
        print("█" * 80)
        print(f"\nVideo 1: {len(result1.sentences)} sentences")
        print(f"Video 2: {len(result2.sentences)} sentences")
        print("\nFiles saved in: firsttrial/outputs/")
        print("  - instagram_video_1_transcription.json")
        print("  - instagram_video_2_transcription.json")
        print()

    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

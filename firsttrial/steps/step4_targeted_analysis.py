#!/usr/bin/env python3
"""
Step 4: Run targeted video analysis with the GPT-5 crafted prompt.

Uses the precise prompt from step 3 to extract the best video clips
with exact timestamps and descriptions.
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils import QwenClient, parse_and_save_json
from schemas import TargetedAnalysisOutput
import config


def targeted_analysis(
    video_url: str = None,
    prompt_path: Path = None,
    output_path: Path = None,
    verbose: bool = True
) -> TargetedAnalysisOutput:
    """
    Run targeted video analysis with crafted prompt.

    Args:
        video_url: URL to main video (default: from config)
        prompt_path: Path to crafted prompt from step 3 (default: from config)
        output_path: Output JSON path (default: from config)
        verbose: Print progress messages

    Returns:
        TargetedAnalysisOutput object with validated scenes

    Raises:
        ValueError: If prompt file not found or API keys not configured
        Exception: If API call fails or JSON parsing fails
    """
    # Use config defaults if not provided
    video_url = video_url or config.MAIN_VIDEO_URL
    prompt_path = prompt_path or config.STEP3_OUTPUT
    output_path = output_path or config.STEP4_OUTPUT

    if verbose:
        print("=" * 60)
        print("STEP 4: TARGETED VIDEO ANALYSIS")
        print("=" * 60)
        print(f"Video URL: {video_url}")
        print(f"Prompt: {prompt_path}")
        print(f"Model: {config.QWEN_VIDEO_MODEL}")
        print(f"Output: {output_path}")
        print()

    # Validate configuration
    config.validate_config()

    # Load crafted prompt
    if verbose:
        print("📂 Loading crafted prompt...")

    if not prompt_path.exists():
        raise ValueError(f"Step 3 prompt not found: {prompt_path}\nRun step 3 first!")

    with open(prompt_path, 'r', encoding='utf-8') as f:
        crafted_prompt = f.read().strip()

    if verbose:
        print("   ✓ Prompt loaded")
        print()
        print("Prompt preview:")
        print("-" * 60)
        print(crafted_prompt[:300] + ("..." if len(crafted_prompt) > 300 else ""))
        print("-" * 60)
        print()

    # Add JSON format instruction to ensure proper output
    full_prompt = f"""{crafted_prompt}"""

    # Initialize Qwen client
    if verbose:
        print("🔄 Initializing Qwen client...")
    client = QwenClient()

    # Analyze video
    if verbose:
        print("🎯 Running targeted video analysis...")
        print("   (This may take several minutes)")
        print()

    response_text = client.analyze_video(
        video_url=video_url,
        prompt=full_prompt,
        model=config.QWEN_VIDEO_MODEL
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

    validated = TargetedAnalysisOutput(**parsed_data)

    # Display results
    if verbose:
        print()
        print("=" * 60)
        print("RESULTS")
        print("=" * 60)
        print(f"Total scenes selected: {len(validated.scenes)}")
        print()
        print("Selected scenes:")
        for i, scene in enumerate(validated.scenes, 1):
            print(f"\n{i}. [{scene.start} → {scene.end}]")
            print(f"   Description: {scene.description[:100]}{'...' if len(scene.description) > 100 else ''}")
            if scene.reason:
                print(f"   Reason: {scene.reason[:100]}{'...' if len(scene.reason) > 100 else ''}")

        print()
        print(f"✅ Scene selection saved to: {output_path}")
        print("=" * 60)

    return validated


if __name__ == "__main__":
    try:
        targeted_analysis(verbose=True)
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        sys.exit(1)

#!/usr/bin/env python3
"""
Step 3: Use GPT-5 Mini to craft a precise prompt for targeted video analysis.

GPT-5 Mini analyzes avatar speech + screen activities to understand the context,
then outputs a SHORT, CONCISE prompt that tells the VLM exactly what visual clips to extract.

The output prompt should NEVER mention "avatar" - it's pure instructions for video analysis.
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils import OpenAIClient, load_json
from schemas import TranscriptionOutput, ScreenAnalysisOutput
import config


GPT5_PROMPT_TEMPLATE = """You are an expert at video analysis. Analyze the data and create a SHORT prompt for a VLM.

CONTEXT (what's being discussed):
{transcription}

VISUALS (what's shown):
{screen_analysis}

YOUR TASK:
1. Internally: Match context with visuals to identify the BEST visual moments across the ENTIRE timeline
2. Output: A CONCISE prompt that tells the VLM to analyze the COMPLETE video and select the TOP clips

CRITICAL RULES FOR YOUR OUTPUT:
- 2-4 sentences MAXIMUM
- NEVER mention: "speech", "audio", "narrator", "talking", "spoken", "narration", "avatar", "lines"
- ONLY list: visual elements (UI, demos, animations, products, logos, text, transitions)
- List specific visuals from the screen analysis
- The VLM has NO ACCESS to audio - only video frames!
- MUST instruct: analyze ENTIRE video, rank ALL candidates, return TOP clips spread across full timeline

OUTPUT FORMAT:
"Analyze the COMPLETE video from start to end. Identify ALL instances of [visual elements]. Rank by visual quality and clarity. Select the TOP 15-20 best clips spread across the entire timeline. Target visuals at: [timestamp ranges]. NO HUMANS VISIBLE. JSON: {{"scenes": [{{"start": "MM:SS", "end": "MM:SS", "description": "...", "reason": "..."}}]}}"

EXAMPLE (DO THIS):
"Analyze the COMPLETE video (00:00 to end). Find ALL instances of: JSON documents, OpenArt UI screens, room transformation animations (Labubu, Tom&Jerry, Pikachu), product showcases (Apple, Ferrari, Samsung, Coca-Cola), model logos, animated graphics. Rank by visual quality. Select TOP 15-20 clips across entire timeline. Focus on 00:00-00:10, 01:20-02:00, 02:20-04:30, 04:40-08:00. NO HUMANS VISIBLE. JSON with start, end, description, reason."

Output ONLY the prompt."""


def craft_prompt(
    transcription_path: Path = None,
    screen_analysis_path: Path = None,
    output_path: Path = None,
    pause_for_review: bool = True,
    verbose: bool = True
) -> str:
    """
    Use GPT-5 Mini to craft a targeted video analysis prompt.

    Args:
        transcription_path: Path to step 1 output (default: from config)
        screen_analysis_path: Path to step 2 output (default: from config)
        output_path: Output text file path (default: from config)
        pause_for_review: Wait for user approval before returning (default: True)
        verbose: Print progress messages

    Returns:
        Generated prompt text

    Raises:
        ValueError: If input files not found or API keys not configured
        Exception: If API call fails
    """
    # Use config defaults if not provided
    transcription_path = transcription_path or config.STEP1_OUTPUT
    screen_analysis_path = screen_analysis_path or config.STEP2_OUTPUT
    output_path = output_path or config.STEP3_OUTPUT

    if verbose:
        print("=" * 60)
        print("STEP 3: CRAFT TARGETED PROMPT WITH GPT-5 MINI")
        print("=" * 60)
        print(f"Transcription: {transcription_path}")
        print(f"Screen analysis: {screen_analysis_path}")
        print(f"Model: {config.GPT5_MODEL}")
        print(f"Output: {output_path}")
        print()

    # Validate configuration
    config.validate_config()

    # Load input data
    if verbose:
        print("📂 Loading input data...")

    try:
        transcription_data = load_json(transcription_path)
        transcription = TranscriptionOutput(**transcription_data)
    except FileNotFoundError:
        raise ValueError(f"Step 1 output not found: {transcription_path}\nRun step 1 first!")

    try:
        screen_analysis_data = load_json(screen_analysis_path)
        screen_analysis = ScreenAnalysisOutput(**screen_analysis_data)
    except FileNotFoundError:
        raise ValueError(f"Step 2 output not found: {screen_analysis_path}\nRun step 2 first!")

    if verbose:
        print(f"   ✓ Loaded {len(transcription.sentences)} sentences")
        print(f"   ✓ Loaded {len(screen_analysis.activities)} activities")
        print()

    # Format ALL transcription data (no truncation)
    transcription_full = "\n".join([
        f"[{s.start}-{s.end}] {s.text}"
        for s in transcription.sentences
    ])

    # Format ALL screen analysis data (no truncation)
    screen_full = "\n".join([
        f"[{a.start}-{a.end}] {a.description}" + (f" ({a.activity_type})" if a.activity_type else "")
        for a in screen_analysis.activities
    ])

    # Build GPT-5 Mini prompt with FULL context
    gpt5_input = GPT5_PROMPT_TEMPLATE.format(
        transcription=transcription_full,
        screen_analysis=screen_full
    )

    # Call GPT-5 Mini
    if verbose:
        print("🤖 Calling GPT-5 Mini to analyze and generate prompt...")
        print(f"   Effort: {config.GPT5_REASONING_EFFORT}")
        print(f"   Verbosity: {config.GPT5_TEXT_VERBOSITY}")
        print(f"   Context: {len(transcription.sentences)} sentences + {len(screen_analysis.activities)} activities")
        print()

    client = OpenAIClient()
    result = client.generate_with_reasoning(
        prompt=gpt5_input,
        model=config.GPT5_MODEL,
        reasoning_effort=config.GPT5_REASONING_EFFORT,
        text_verbosity=config.GPT5_TEXT_VERBOSITY
    )

    generated_prompt = result["output_text"].strip()

    # Save to file
    if verbose:
        print("💾 Saving generated prompt...")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(generated_prompt)

    # Display result
    if verbose:
        print()
        print("=" * 60)
        print("GENERATED PROMPT FOR VIDEO ANALYSIS")
        print("=" * 60)
        print(generated_prompt)
        print("=" * 60)
        print()
        print(f"Prompt length: {len(generated_prompt)} characters")
        print(f"Prompt sentences: ~{generated_prompt.count('.')} sentences")
        print()
        print(f"✅ Prompt saved to: {output_path}")
        print()

    # Pause for review if requested
    if pause_for_review:
        print("=" * 60)
        print("MANUAL REVIEW CHECKPOINT")
        print("=" * 60)
        print("Please review the generated prompt above.")
        print(f"You can edit it at: {output_path}")
        print()
        print("The prompt should:")
        print("  ✓ Be SHORT (2-4 sentences)")
        print("  ✓ NEVER mention 'avatar', 'speech', 'audio', 'narration'")
        print("  ✓ Instruct to analyze COMPLETE video and RANK clips")
        print("  ✓ Ask for TOP 15-20 clips across ENTIRE timeline")
        print("  ✓ Only describe VISUAL elements to extract")
        print("  ✓ Specify timestamp ranges")
        print("  ✓ Request NO HUMANS visible")
        print()
        response = input("Continue with this prompt? [y/N]: ").strip().lower()
        print()

        if response != 'y':
            print("⚠️  Prompt not approved. Edit the file and run step 4 manually.")
            sys.exit(0)

        print("✅ Prompt approved! Continuing...\n")

    return generated_prompt


if __name__ == "__main__":
    try:
        craft_prompt(verbose=True, pause_for_review=True)
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        sys.exit(1)

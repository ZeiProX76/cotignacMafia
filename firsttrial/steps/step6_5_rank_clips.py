#!/usr/bin/env python3
"""
Step 6.5: Rank ALL clips using Qwen VLM on 4 quality criteria.

Uses the SAME Qwen VLM as step 6 to actually WATCH each video and rank on:
1. Human visibility (100 = no humans)
2. Animation completeness (100 = fully complete)
3. Reason match (100 = perfectly matches selection reason)
4. B-roll overlay quality (100 = perfect for overlay)

Outputs rankings sorted by total score.
"""

import sys
import os
import json
import time
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

import dashscope
from dotenv import load_dotenv
from utils import load_json, save_json
from schemas import OptimizationOutput, RankingsOutput, ClipRanking, ClipRankingCriteria
import config

load_dotenv()

dashscope.base_http_api_url = 'https://dashscope-intl.aliyuncs.com/api/v1'

MODEL = "qwen-vl-max-latest"  # Same as step 6

QWEN_RANKING_PROMPT = """You are an expert video quality analyst. Watch this clip and rank it on 4 criteria (0-100 each).

CLIP CONTEXT:
Description: {description}
Reason for selection: {reason}
Original timestamps: {start} → {end}

CRITERIA TO EVALUATE:

1. HUMAN VISIBILITY (0-100, higher = better)
   - 100: Zero humans visible throughout entire clip
   - 75: Humans briefly visible but mostly clean
   - 50: Humans visible in significant portions
   - 25: Humans frequently visible
   - 0: Humans prominent throughout

2. ANIMATION COMPLETENESS (0-100, higher = better)
   - 100: Animation/demo fully complete, natural start/end points
   - 75: Animation mostly complete with minor cuts
   - 50: Animation partially cut off but still usable
   - 25: Animation significantly truncated
   - 0: Animation severely cut or jarring transitions

3. REASON MATCH (0-100, higher = better)
   - 100: Clip perfectly represents the stated selection reason
   - 75: Clip strongly matches the reason with minor gaps
   - 50: Clip somewhat matches but missing key elements
   - 25: Clip barely matches the reason
   - 0: Clip doesn't match stated reason at all

4. B-ROLL OVERLAY QUALITY (0-100, higher = better)
   - 100: Perfect for overlay - dynamic, clear, engaging visuals, professional
   - 75: Good for overlay - interesting visuals, mostly clear
   - 50: Acceptable for overlay but not ideal - somewhat static or unclear
   - 25: Poor for overlay - very static, confusing, or low visual interest
   - 0: Unusable for overlay - completely static, unclear, or boring

WATCH THE VIDEO and output JSON ONLY (no markdown, no explanation):
{{
  "human_visibility_score": 0-100,
  "human_reasoning": "brief explanation (1-2 sentences)",
  "animation_completeness_score": 0-100,
  "animation_reasoning": "brief explanation (1-2 sentences)",
  "reason_match_score": 0-100,
  "reason_reasoning": "brief explanation (1-2 sentences)",
  "broll_quality_score": 0-100,
  "broll_reasoning": "brief explanation (1-2 sentences)"
}}
"""


def rank_single_clip_with_qwen(
    clip_path: Path,
    original_context: dict,
    verbose: bool = False
) -> ClipRankingCriteria:
    """
    Rank a single clip using Qwen VLM by actually watching it.

    Args:
        clip_path: Path to the video clip file
        original_context: Original context from step 5 (description, reason, etc.)
        verbose: Print progress

    Returns:
        ClipRankingCriteria with scores and reasoning

    Raises:
        Exception: If API call fails or JSON parsing fails
    """
    # Format prompt with context
    prompt = QWEN_RANKING_PROMPT.format(
        description=original_context.get('description', 'N/A') if original_context else 'N/A',
        reason=original_context.get('reason', 'N/A') if original_context else 'N/A',
        start=original_context.get('start', 'N/A') if original_context else 'N/A',
        end=original_context.get('end', 'N/A') if original_context else 'N/A'
    )

    if verbose:
        print(f"      Ranking with Qwen VLM...")

    # Call Qwen VLM with video
    messages = [{
        "role": "user",
        "content": [
            {"video": f"file://{clip_path.absolute()}"},
            {"text": prompt}
        ]
    }]

    for retry in range(3):
        try:
            response = dashscope.MultiModalConversation.call(
                api_key=os.getenv("DASHSCOPE_API_KEY"),
                model=MODEL,
                messages=messages
            )

            # Extract response text
            try:
                result_text = response.output.choices[0].message.content[0]["text"]
            except (IndexError, KeyError, TypeError) as e:
                if hasattr(response.output, 'text'):
                    result_text = response.output.text
                elif isinstance(response.output.choices[0].message.content, str):
                    result_text = response.output.choices[0].message.content
                else:
                    raise Exception(f"Could not extract text from response: {e}")

            # Clean markdown if present
            cleaned = result_text.strip()
            if cleaned.startswith("```json"):
                cleaned = cleaned[7:]
            if cleaned.startswith("```"):
                cleaned = cleaned[3:]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]

            criteria_data = json.loads(cleaned.strip())
            return ClipRankingCriteria(**criteria_data)

        except Exception as e:
            if retry < 2:
                if verbose:
                    print(f"      Retry {retry + 1}/3...")
                time.sleep(2)
            else:
                raise Exception(f"Ranking failed: {e}")


def rank_clips(
    clips_analysis_path: Path = None,
    clips_raw_dir: Path = None,
    output_path: Path = None,
    verbose: bool = True
) -> RankingsOutput:
    """
    Rank all clips from step 6 using Qwen VLM.

    Args:
        clips_analysis_path: Path to step 6 output (default: from config)
        clips_raw_dir: Directory with clip files (default: clips_raw/)
        output_path: Output path for rankings (default: step6_5_rankings.json)
        verbose: Print progress messages

    Returns:
        RankingsOutput with all clips ranked and sorted

    Raises:
        ValueError: If input files not found
        Exception: If API calls fail
    """
    clips_analysis_path = clips_analysis_path or config.STEP6_OUTPUT
    clips_raw_dir = clips_raw_dir or config.CLIPS_RAW_DIR
    output_path = output_path or config.STEP6_5_OUTPUT

    if verbose:
        print("=" * 60)
        print(f"STEP 6.5: RANK ALL CLIPS WITH QWEN VLM - {MODEL}")
        print("=" * 60)
        print(f"Analysis: {clips_analysis_path}")
        print(f"Clips dir: {clips_raw_dir}")
        print(f"Output: {output_path}")
        print()

    # Validate
    config.validate_config()

    if not clips_analysis_path.exists():
        raise ValueError(f"Step 6 output not found: {clips_analysis_path}\nRun step 6 first!")

    # Load step 6 analysis
    if verbose:
        print("📂 Loading step 6 analysis...")

    analysis_data = load_json(clips_analysis_path)
    optimization = OptimizationOutput(**analysis_data)

    if verbose:
        print(f"   ✓ Loaded analysis for {len(optimization.clips)} clips")
        print()

    # Filter to only "clean" clips (status == "clean")
    clean_clips = [c for c in optimization.clips if c.status == "clean"]

    if verbose:
        print(f"Filtering: {len(clean_clips)} clean clips (out of {len(optimization.clips)} total)")
        print()

    if len(clean_clips) == 0:
        print("⚠️  WARNING: No clean clips found! All clips were unsaveable or failed.")
        print("   Ranking all clips anyway for analysis purposes...")
        clips_to_rank = optimization.clips
    else:
        clips_to_rank = clean_clips

    # Rank each clip
    rankings = []

    if verbose:
        print("🎯 Ranking clips with Qwen VLM...")
        print("-" * 60)

    for i, clip in enumerate(clips_to_rank, 1):
        if verbose:
            print(f"\n[{i}/{len(clips_to_rank)}] {clip.source_filename}")

        try:
            # Get clip path
            clip_path = clips_raw_dir / clip.source_filename

            if not clip_path.exists():
                if verbose:
                    print(f"      ✗ File not found: {clip_path}")
                continue

            # Rank with Qwen VLM
            criteria = rank_single_clip_with_qwen(
                clip_path=clip_path,
                original_context=clip.original_context,
                verbose=verbose
            )

            # Calculate total and normalized scores
            total_score = (
                criteria.human_visibility_score +
                criteria.animation_completeness_score +
                criteria.reason_match_score +
                criteria.broll_quality_score
            )
            normalized_score = total_score / 4.0

            # Create ranking (use temporary rank=1, will reassign after sorting)
            ranking = ClipRanking(
                video_id=clip.video_id or "unknown",
                clip_filename=clip.source_filename,
                clip_path=str(clip_path),
                criteria=criteria,
                total_score=total_score,
                normalized_score=normalized_score,
                rank=1,  # Temporary value, will be reassigned after sorting
                original_context=clip.original_context,
                optimization_result=clip.model_dump()
            )

            rankings.append(ranking)

            if verbose:
                print(f"      Scores: H={criteria.human_visibility_score} "
                      f"A={criteria.animation_completeness_score} "
                      f"R={criteria.reason_match_score} "
                      f"B={criteria.broll_quality_score}")
                print(f"      Total: {total_score}/400 ({normalized_score:.1f}/100)")

        except Exception as e:
            if verbose:
                print(f"      ✗ Failed to rank: {e}")
            continue

    # Sort by total_score descending
    rankings.sort(key=lambda x: x.total_score, reverse=True)

    # Assign ranks
    for i, ranking in enumerate(rankings, 1):
        ranking.rank = i

    # Create output
    output = RankingsOutput(
        total_clips=len(rankings),
        rankings=rankings
    )

    # Save
    if verbose:
        print()
        print("-" * 60)
        print("\n💾 Saving rankings...")

    save_json(output.model_dump(), output_path)

    # Display results
    if verbose:
        print()
        print("=" * 60)
        print("RESULTS")
        print("=" * 60)
        print(f"Total clips ranked: {len(rankings)}")
        print()
        print("Top 10 clips:")
        for i, ranking in enumerate(rankings[:10], 1):
            print(f"\n{i}. {ranking.clip_filename}")
            print(f"   Video: {ranking.video_id}")
            print(f"   Total Score: {ranking.total_score}/400 ({ranking.normalized_score:.1f}/100)")
            print(f"   H:{ranking.criteria.human_visibility_score} "
                  f"A:{ranking.criteria.animation_completeness_score} "
                  f"R:{ranking.criteria.reason_match_score} "
                  f"B:{ranking.criteria.broll_quality_score}")

        if len(rankings) > 10:
            print(f"\n... and {len(rankings) - 10} more clips")

        print()
        print(f"✅ Rankings saved to: {output_path}")
        print("=" * 60)

    return output


if __name__ == "__main__":
    try:
        rank_clips(verbose=True)
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

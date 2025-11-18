#!/usr/bin/env python3
"""
Step 7: Select TOP 15 clips by highest ranking scores.

Simply takes the top 15 highest-scoring clips from step 6.5 rankings.
No AI selection needed - just sort by score and take top 15.

Copies selected clips to top15/ directory with clear naming.
"""

import sys
import shutil
from pathlib import Path
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils import load_json, save_json, get_duration
from schemas import RankingsOutput, Top15Selection, Top15Clip
import config


def select_top15(
    rankings_path: Path = None,
    clips_raw_dir: Path = None,
    output_dir: Path = None,
    output_metadata: Path = None,
    verbose: bool = True
) -> Top15Selection:
    """
    Select top 15 clips by highest scores and copy to top15/ directory.

    Args:
        rankings_path: Path to step 6.5 output (default: from config)
        clips_raw_dir: Directory with raw clips (default: clips_raw/)
        output_dir: Top 15 output directory (default: top15/)
        output_metadata: Metadata output path (default: step7_top15.json)
        verbose: Print progress messages

    Returns:
        Top15Selection with selected clips and metadata

    Raises:
        ValueError: If input files not found
        Exception: If file operations fail
    """
    rankings_path = rankings_path or config.STEP6_5_OUTPUT
    clips_raw_dir = clips_raw_dir or config.CLIPS_RAW_DIR
    output_dir = output_dir or config.TOP15_DIR
    output_metadata = output_metadata or config.STEP7_OUTPUT

    if verbose:
        print("=" * 60)
        print("STEP 7: SELECT TOP 15 CLIPS BY SCORE")
        print("=" * 60)
        print(f"Rankings: {rankings_path}")
        print(f"Clips dir: {clips_raw_dir}")
        print(f"Output dir: {output_dir}")
        print(f"Metadata: {output_metadata}")
        print()

    # Validate
    config.validate_config()

    if not rankings_path.exists():
        raise ValueError(f"Step 6.5 output not found: {rankings_path}\nRun step 6.5 first!")

    # Load rankings
    if verbose:
        print("📂 Loading rankings...")

    rankings_data = load_json(rankings_path)
    rankings = RankingsOutput(**rankings_data)

    if verbose:
        print(f"   ✓ Loaded {rankings.total_clips} ranked clips")
        print()

    # Check if we have at least 15 clips
    num_to_select = min(15, len(rankings.rankings))

    if len(rankings.rankings) < 15:
        print(f"⚠️  WARNING: Only {len(rankings.rankings)} clips available (need 15)")
        print(f"   Selecting all {len(rankings.rankings)} available clips...")
        print()

    # Select top N clips (already sorted by rank in step 6.5)
    top_clips = rankings.rankings[:num_to_select]

    if verbose:
        print(f"✓ Selected top {len(top_clips)} clips by score")
        print()

    # Create output directory
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Process selected clips
    selected_clips = []

    if verbose:
        print("📋 Processing selected clips...")
        print("-" * 60)

    for i, ranking in enumerate(top_clips, 1):
        # Source and destination paths
        source_path = clips_raw_dir / ranking.clip_filename
        dest_filename = f"rank{i:02d}_{ranking.video_id}_{ranking.clip_filename}"
        dest_path = output_dir / dest_filename

        if verbose:
            print(f"\n[{i}/{num_to_select}] {ranking.clip_filename}")
            print(f"   Video: {ranking.video_id}")
            print(f"   Score: {ranking.total_score}/400 ({ranking.normalized_score:.1f}/100)")
            print(f"   Scores: H={ranking.criteria.human_visibility_score} "
                  f"A={ranking.criteria.animation_completeness_score} "
                  f"R={ranking.criteria.reason_match_score} "
                  f"B={ranking.criteria.broll_quality_score}")
            print(f"   Destination: {dest_filename}")

        # Copy file
        try:
            if not source_path.exists():
                if verbose:
                    print(f"   ✗ Source file not found: {source_path}")
                continue

            shutil.copy2(source_path, dest_path)

            # Get duration
            try:
                duration = get_duration(dest_path)
            except:
                duration = 0.0
                if verbose:
                    print(f"   ⚠️  Could not get duration")

            # Get clean timestamps from optimization
            clean_start = ranking.optimization_result.get("clean_start") if ranking.optimization_result else None
            clean_end = ranking.optimization_result.get("clean_end") if ranking.optimization_result else None

            # Get description and reason from original context
            description = ranking.original_context.get("description", "N/A") if ranking.original_context else "N/A"
            reason = ranking.original_context.get("reason") if ranking.original_context else None

            # Create Top15Clip
            top15_clip = Top15Clip(
                rank=i,
                video_id=ranking.video_id,
                original_filename=ranking.clip_filename,
                top15_filename=dest_filename,
                final_path=str(dest_path),
                total_score=ranking.total_score,
                normalized_score=ranking.normalized_score,
                ranking_details=ranking.criteria,
                duration_seconds=duration,
                clean_start=clean_start,
                clean_end=clean_end,
                description=description,
                reason=reason
            )

            selected_clips.append(top15_clip)

            if verbose:
                print(f"   ✓ Copied ({duration:.1f}s)")

        except Exception as e:
            if verbose:
                print(f"   ✗ Failed: {e}")
            continue

    # Create selection output
    selection_criteria = f"Selected top {len(selected_clips)} clips by total ranking score (out of {rankings.total_clips} total candidates)"

    selection = Top15Selection(
        selection_timestamp=datetime.now().isoformat(),
        total_candidates=rankings.total_clips,
        selected_clips=selected_clips,
        selection_criteria=selection_criteria
    )

    # Save metadata
    if verbose:
        print()
        print("-" * 60)
        print("\n💾 Saving metadata...")

    save_json(selection.model_dump(), output_metadata)

    # Display results
    if verbose:
        print()
        print("=" * 60)
        print("RESULTS")
        print("=" * 60)
        print(f"Selected: {len(selected_clips)} clips")
        print(f"Total duration: {sum(c.duration_seconds for c in selected_clips):.1f}s")
        print()
        print("Top 15 clips:")
        for clip in selected_clips:
            print(f"\n{clip.rank}. {clip.top15_filename}")
            print(f"   Video: {clip.video_id}")
            print(f"   Score: {clip.total_score}/400 ({clip.normalized_score:.1f}/100)")
            print(f"   Duration: {clip.duration_seconds:.1f}s")
            print(f"   Description: {clip.description[:60]}..." if len(clip.description) > 60 else f"   Description: {clip.description}")

        print()
        print(f"✅ Top 15 saved to: {output_dir}")
        print(f"✅ Metadata saved to: {output_metadata}")
        print("=" * 60)

    return selection


if __name__ == "__main__":
    try:
        select_top15(verbose=True)
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

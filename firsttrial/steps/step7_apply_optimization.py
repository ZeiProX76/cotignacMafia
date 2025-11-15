#!/usr/bin/env python3
"""
Step 7: Cut final clean clips based on Step 6 analysis.

Reads safe timestamps from step 6 and cuts final clips.
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils import load_json, save_json, cut_clip, mmss_to_seconds, seconds_to_mmss
from schemas import OptimizationOutput
import config

# Safety margin: subtract 0.4s from end to avoid human appearances
SAFETY_MARGIN_SECONDS = 0.4


def apply_optimization(
    clips_dir: Path = None,
    optimization_path: Path = None,
    output_dir: Path = None,
    verbose: bool = True
) -> dict:
    """
    Cut final clean clips based on step 6 timestamps.

    Args:
        clips_dir: Directory containing raw clips (default: from config)
        optimization_path: Path to step 6 output (default: from config)
        output_dir: Output directory for clean clips (default: from config)
        verbose: Print progress messages

    Returns:
        Dictionary with statistics about filtering
    """
    # Use config defaults if not provided
    clips_dir = clips_dir or config.CLIPS_RAW_DIR
    optimization_path = optimization_path or (config.OUTPUTS_DIR / "step6_analysis.json")
    output_dir = output_dir or config.CLIPS_FINAL_DIR

    if verbose:
        print("=" * 60)
        print("STEP 7: CUT FINAL CLEAN CLIPS")
        print("=" * 60)
        print(f"Source clips: {clips_dir}")
        print(f"Step 6 analysis: {optimization_path}")
        print(f"Output directory: {output_dir}")
        print()

    # Validate inputs
    clips_dir = Path(clips_dir)
    if not clips_dir.exists():
        raise ValueError(f"Raw clips directory not found: {clips_dir}\nRun step 5 first!")

    if not optimization_path.exists():
        raise ValueError(f"Step 6 output not found: {optimization_path}\nRun step 6 first!")

    # Create output directory
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Load optimization results
    if verbose:
        print("📂 Loading optimization results...")

    optimization_data = load_json(optimization_path)
    optimization = OptimizationOutput(**optimization_data)

    if verbose:
        print(f"   ✓ Loaded {len(optimization.clips)} clip results")
        print()

    # Process each clip
    kept_clips = []
    skipped_clips = []

    if verbose:
        print("✂️  Cutting final clips...")
        print("-" * 60)

    for i, clip_data in enumerate(optimization.clips, 1):
        if verbose:
            print(f"\n[{i}/{len(optimization.clips)}] {clip_data.source_filename}")

        if clip_data.status == "clean":
            # Must have timestamps
            if not clip_data.clean_start or not clip_data.clean_end:
                if verbose:
                    print(f"   ✗ No timestamps found")
                skipped_clips.append({
                    "filename": clip_data.source_filename,
                    "reason": "Missing timestamps",
                    "status": clip_data.status
                })
                continue

            # Find source clip
            source_path = clips_dir / clip_data.source_filename
            if not source_path.exists():
                if verbose:
                    print(f"   ✗ Source not found: {source_path}")
                skipped_clips.append({
                    "filename": clip_data.source_filename,
                    "reason": "Source file not found",
                    "status": clip_data.status
                })
                continue

            # Apply safety margin to end timestamp
            end_seconds = mmss_to_seconds(clip_data.clean_end)
            safe_end_seconds = max(0, end_seconds - SAFETY_MARGIN_SECONDS)
            safe_end = seconds_to_mmss(safe_end_seconds)

            # Cut to final directory
            output_path = output_dir / clip_data.output_filename

            if verbose:
                print(f"   ✓ Cutting: {clip_data.clean_start} → {safe_end} (original end: {clip_data.clean_end}, -0.4s margin)")
                print(f"   → {output_path.name}")

            try:
                cut_clip(
                    input_path=source_path,
                    start=clip_data.clean_start,
                    end=safe_end,
                    output_path=output_path,
                    fast_mode=config.FFMPEG_FAST_MODE
                )

                kept_clips.append({
                    "original": clip_data.source_filename,
                    "final": clip_data.output_filename,
                    "start": clip_data.clean_start,
                    "end": safe_end,
                    "original_end": clip_data.clean_end,
                    "context": clip_data.original_context
                })
            except Exception as e:
                if verbose:
                    print(f"   ✗ Cut failed: {e}")
                skipped_clips.append({
                    "filename": clip_data.source_filename,
                    "reason": f"FFmpeg error: {e}",
                    "status": "failed"
                })

        elif clip_data.status == "unsaveable":
            if verbose:
                print(f"   ✗ UNSAVEABLE - Humans throughout")

            skipped_clips.append({
                "filename": clip_data.source_filename,
                "reason": "Humans throughout entire video",
                "status": clip_data.status
            })

        else:  # failed
            if verbose:
                print(f"   ⚠️  FAILED - Analysis failed")

            skipped_clips.append({
                "filename": clip_data.source_filename,
                "reason": "Step 6 analysis failed",
                "status": clip_data.status
            })

    # Save summary
    summary = {
        "total_clips": len(optimization.clips),
        "kept_clips": len(kept_clips),
        "skipped_clips": len(skipped_clips),
        "kept": kept_clips,
        "skipped": skipped_clips
    }

    summary_path = output_dir / "final_summary.json"
    save_json(summary, summary_path)

    # Display results
    if verbose:
        print()
        print("-" * 60)
        print()
        print("=" * 60)
        print("RESULTS")
        print("=" * 60)
        print(f"Total clips processed: {summary['total_clips']}")
        print(f"✓ Clean clips saved: {summary['kept_clips']}")
        print(f"✗ Clips skipped: {summary['skipped_clips']}")
        print()
        print(f"Final clips directory: {output_dir}")
        print(f"Summary: {summary_path}")
        print()

        if kept_clips:
            print("Final clean clips:")
            for clip in kept_clips:
                print(f"  • {clip['final']} ({clip['start']} → {clip['end']})")

        if skipped_clips:
            print()
            print(f"Skipped clips:")
            for clip in skipped_clips[:5]:  # Show first 5
                print(f"  • {clip['filename']}: {clip['reason']}")
            if len(skipped_clips) > 5:
                print(f"  ... and {len(skipped_clips) - 5} more")

        print()
        print("=" * 60)
        print("✅ DONE - FINAL CLIPS CUT WITH ZERO HUMANS!")
        print("=" * 60)

    return summary


if __name__ == "__main__":
    try:
        apply_optimization(verbose=True)
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        sys.exit(1)

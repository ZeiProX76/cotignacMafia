#!/usr/bin/env python3
"""
Interactive pipeline orchestrator for video analysis workflow.

Provides a user-friendly menu interface to run individual steps
or the complete pipeline.
"""

import sys
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from steps import (
    transcribe_avatar,
    analyze_screen,
    craft_prompt,
    targeted_analysis,
    cut_clips,
    preprocess_clips,
    optimize_clips,
    apply_optimization,
    create_timeline
)
# Import new multi-video steps
from steps.step6_5_rank_clips import rank_clips
from steps.step7_select_top15 import select_top15

import config
from utils import verify_ffmpeg_installed


def display_header():
    """Display pipeline header."""
    print("\n" + "=" * 60)
    print("VIDEO ANALYSIS PIPELINE")
    print("=" * 60)
    print()


def display_menu():
    """Display interactive menu."""
    print("\nAvailable steps:")
    print()
    print("  1.   Transcribe avatar audio (Step 1)")
    print("  2.   Analyze screen activities (Step 2)")
    print("  3.   Craft prompt with GPT-5 (Step 3)")
    print("  4.   Run targeted analysis (Step 4)")
    print("  5.   Cut video clips (Step 5)")
    print("  5.5  Preprocess clips (Step 5.5)")
    print("  6.   Analyze clips for humans (Step 6)")
    print("  6.5  Rank all clips with Qwen VLM (Step 6.5) 🆕")
    print("  7.   Select top 15 clips by score (Step 7) 🆕")
    print("  8.   Generate Remotion timeline (Step 8)")
    print()
    print("  A.   Run ALL steps (complete pipeline)")
    print("  M.   Run MULTI-VIDEO pipeline (all videos) 🆕")
    print("  C.   Show configuration")
    print("  Q.   Quit")
    print()


def run_step(step_num) -> bool:
    """
    Run a specific pipeline step.

    Args:
        step_num: Step number (1, 2, 3, 4, 5, 5.5, 6, 7) as int or float

    Returns:
        True if step succeeded, False otherwise
    """
    try:
        if step_num == 1:
            print("\n" + "=" * 60)
            print("Running Step 1: Transcribe Avatar Audio")
            print("=" * 60)
            transcribe_avatar(verbose=True)

        elif step_num == 2:
            print("\n" + "=" * 60)
            print("Running Step 2: Analyze Screen Activities")
            print("=" * 60)
            analyze_screen(verbose=True)

        elif step_num == 3:
            print("\n" + "=" * 60)
            print("Running Step 3: Craft Prompt with GPT-5")
            print("=" * 60)
            craft_prompt(verbose=True, pause_for_review=True)

        elif step_num == 4:
            print("\n" + "=" * 60)
            print("Running Step 4: Targeted Video Analysis")
            print("=" * 60)
            targeted_analysis(verbose=True)

        elif step_num == 5:
            print("\n" + "=" * 60)
            print("Running Step 5: Cut Video Clips")
            print("=" * 60)
            cut_clips(verbose=True)

        elif step_num == 5.5:
            print("\n" + "=" * 60)
            print("Running Step 5.5: Preprocess Clips")
            print("=" * 60)
            preprocess_clips(verbose=True)

        elif step_num == 6:
            print("\n" + "=" * 60)
            print("Running Step 6: Analyze Clips for Humans")
            print("=" * 60)
            optimize_clips(verbose=True)

        elif step_num == 6.5:
            print("\n" + "=" * 60)
            print("Running Step 6.5: Rank All Clips with Qwen VLM")
            print("=" * 60)
            rank_clips(verbose=True)

        elif step_num == 7:
            print("\n" + "=" * 60)
            print("Running Step 7: Select Top 15 Clips")
            print("=" * 60)
            select_top15(verbose=True)

        elif step_num == 8:
            print("\n" + "=" * 60)
            print("Running Step 8: Generate Remotion Timeline")
            print("=" * 60)
            create_timeline(verbose=True)

        else:
            print(f"❌ Invalid step number: {step_num}")
            return False

        print("\n✅ Step completed successfully!")
        return True

    except KeyboardInterrupt:
        print("\n\n⚠️  Step interrupted by user")
        return False

    except Exception as e:
        print(f"\n\n❌ Step failed: {e}")
        return False


def run_all_steps():
    """Run all pipeline steps in sequence."""
    print("\n" + "=" * 60)
    print("RUNNING COMPLETE PIPELINE")
    print("=" * 60)
    print("\nThis will run all 9 steps in sequence.")
    print("Note: Step 3 will pause for prompt review.")
    print()

    response = input("Continue? [y/N]: ").strip().lower()
    if response != 'y':
        print("Cancelled.")
        return

    steps = [
        (1, "Transcribe avatar audio"),
        (2, "Analyze screen activities"),
        (3, "Craft prompt with GPT-5"),
        (4, "Run targeted analysis"),
        (5, "Cut video clips"),
        (5.5, "Preprocess clips"),
        (6, "Analyze clips for humans"),
        (7, "Cut final clean clips"),
        (8, "Create timeline JSON")
    ]

    completed = []
    failed = None

    for step_num, step_name in steps:
        print(f"\n{'=' * 60}")
        print(f"STEP {step_num}/9: {step_name}")
        print("=" * 60)

        success = run_step(step_num)

        if success:
            completed.append(step_num)
        else:
            failed = step_num
            break

    # Display summary
    print("\n" + "=" * 60)
    print("PIPELINE SUMMARY")
    print("=" * 60)

    if failed:
        print(f"\n⚠️  Pipeline stopped at step {failed}")
        print(f"Completed steps: {', '.join(map(str, completed))}")
        print(f"\nTo resume, run step {failed} from the menu.")
    else:
        print("\n✅ All steps completed successfully!")
        print(f"\nFinal clips are in: {config.CLIPS_FINAL_DIR}")

    print("=" * 60)


def run_multi_video_pipeline():
    """Run multi-video pipeline: Steps 2-5 for each video, then 6-8 aggregated."""
    print("\n" + "=" * 60)
    print("RUNNING MULTI-VIDEO PIPELINE")
    print("=" * 60)
    print("\nThis will:")
    print("  1. Transcribe avatar audio (once)")
    print("  2-5. Process EACH video (analyze, prompt, select, cut)")
    print("  6. Analyze all clips for humans")
    print("  6.5. Rank all clips with Qwen VLM")
    print("  7. Select top 15 clips by score")
    print("  8. Generate Remotion timeline")
    print()

    # Load videos config
    try:
        videos_cfg = config.load_videos_config()
        print(f"Found {len(videos_cfg.videos)} videos to process:")
        for video in videos_cfg.videos:
            print(f"  - {video.id}: {video.name}")
        print()
    except Exception as e:
        print(f"❌ Error loading videos config: {e}")
        print("Make sure videos_config.json exists and is valid.")
        return

    response = input("Continue with multi-video pipeline? [y/N]: ").strip().lower()
    if response != 'y':
        print("Cancelled.")
        return

    # Step 1: Transcribe avatar (once)
    print("\n" + "=" * 60)
    print("STEP 1: Transcribe Avatar Audio")
    print("=" * 60)
    try:
        transcribe_avatar(verbose=True)
        print("\n✅ Step 1 completed!")
    except Exception as e:
        print(f"\n❌ Step 1 failed: {e}")
        return

    # Steps 2-5: For each video
    for i, video in enumerate(videos_cfg.videos, 1):
        print("\n" + "=" * 80)
        print(f"PROCESSING VIDEO {i}/{len(videos_cfg.videos)}: {video.id} - {video.name}")
        print("=" * 80)

        # Step 2: Analyze screen
        print(f"\nSTEP 2 ({video.id}): Analyze Screen Activities")
        print("-" * 60)
        try:
            analyze_screen(video_id=video.id, verbose=True)
            print(f"\n✅ Step 2 completed for {video.id}!")
        except Exception as e:
            print(f"\n❌ Step 2 failed for {video.id}: {e}")
            print("Continuing with next video...")
            continue

        # Step 3: Craft prompt
        print(f"\nSTEP 3 ({video.id}): Craft Prompt with GPT-5")
        print("-" * 60)
        try:
            craft_prompt(video_id=video.id, verbose=True, pause_for_review=False)
            print(f"\n✅ Step 3 completed for {video.id}!")
        except Exception as e:
            print(f"\n❌ Step 3 failed for {video.id}: {e}")
            print("Continuing with next video...")
            continue

        # Step 4: Targeted analysis
        print(f"\nSTEP 4 ({video.id}): Run Targeted Analysis")
        print("-" * 60)
        try:
            targeted_analysis(video_id=video.id, verbose=True)
            print(f"\n✅ Step 4 completed for {video.id}!")
        except Exception as e:
            print(f"\n❌ Step 4 failed for {video.id}: {e}")
            print("Continuing with next video...")
            continue

        # Step 5: Cut clips
        print(f"\nSTEP 5 ({video.id}): Cut Video Clips")
        print("-" * 60)
        try:
            cut_clips(video_id=video.id, verbose=True)
            print(f"\n✅ Step 5 completed for {video.id}!")
        except Exception as e:
            print(f"\n❌ Step 5 failed for {video.id}: {e}")
            print("Continuing with next video...")
            continue

    # Steps 6-8: Aggregate processing
    print("\n" + "=" * 80)
    print("AGGREGATE PROCESSING (ALL VIDEOS)")
    print("=" * 80)

    # Step 6: Analyze all clips
    print("\nSTEP 6: Analyze All Clips for Humans")
    print("-" * 60)
    try:
        optimize_clips(verbose=True)
        print("\n✅ Step 6 completed!")
    except Exception as e:
        print(f"\n❌ Step 6 failed: {e}")
        return

    # Step 6.5: Rank all clips
    print("\nSTEP 6.5: Rank All Clips with Qwen VLM")
    print("-" * 60)
    try:
        rank_clips(verbose=True)
        print("\n✅ Step 6.5 completed!")
    except Exception as e:
        print(f"\n❌ Step 6.5 failed: {e}")
        return

    # Step 7: Select top 15
    print("\nSTEP 7: Select Top 15 Clips")
    print("-" * 60)
    try:
        select_top15(verbose=True)
        print("\n✅ Step 7 completed!")
    except Exception as e:
        print(f"\n❌ Step 7 failed: {e}")
        return

    # Step 8: Generate timeline
    print("\nSTEP 8: Generate Remotion Timeline")
    print("-" * 60)
    try:
        create_timeline(verbose=True)
        print("\n✅ Step 8 completed!")
    except Exception as e:
        print(f"\n❌ Step 8 failed: {e}")
        return

    # Summary
    print("\n" + "=" * 60)
    print("MULTI-VIDEO PIPELINE COMPLETE!")
    print("=" * 60)
    print(f"\n✅ Processed {len(videos_cfg.videos)} videos")
    print(f"✅ Top 15 clips selected: {config.TOP15_DIR}")
    print(f"✅ Timeline generated: {config.STEP8_OUTPUT}")
    print("=" * 60)


def show_configuration():
    """Display current configuration."""
    config.display_config()
    input("\nPress Enter to continue...")


def validate_environment():
    """Validate that the environment is properly configured."""
    print("Validating environment...")

    errors = []

    # Check API keys
    try:
        config.validate_config()
    except ValueError as e:
        errors.append(str(e))

    # Check FFmpeg
    if not verify_ffmpeg_installed():
        errors.append("FFmpeg/FFprobe not found. Please install FFmpeg.")

    if errors:
        print("\n❌ Environment validation failed:")
        for error in errors:
            print(f"   {error}")
        print()
        return False

    print("✅ Environment validated successfully!\n")
    return True


def main():
    """Main interactive loop."""
    display_header()

    # Validate environment
    if not validate_environment():
        print("Please fix the errors above and try again.")
        sys.exit(1)

    # Interactive loop
    while True:
        display_menu()

        try:
            choice = input("Select option: ").strip().upper()

            if choice == 'Q':
                print("\nGoodbye!")
                break

            elif choice == 'C':
                show_configuration()

            elif choice == 'A':
                run_all_steps()

            elif choice == 'M':
                run_multi_video_pipeline()

            elif choice == '5.5':
                run_step(5.5)

            elif choice == '6.5':
                run_step(6.5)

            elif choice.isdigit() and 1 <= int(choice) <= 8:
                run_step(int(choice))

            else:
                print(f"\n❌ Invalid option: {choice}")

        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break

        except Exception as e:
            print(f"\n❌ Error: {e}")
            continue


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nGoodbye!")
        sys.exit(0)

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
    print("  1. Transcribe avatar audio (Step 1)")
    print("  2. Analyze screen activities (Step 2)")
    print("  3. Craft prompt with GPT-5 (Step 3)")
    print("  4. Run targeted analysis (Step 4)")
    print("  5. Cut video clips (Step 5)")
    print("  5.5 Preprocess clips (Step 5.5)")
    print("  6. Analyze clips for humans (Step 6)")
    print("  7. Cut final clean clips (Step 7)")
    print("  8. Create timeline JSON (Step 8)")
    print()
    print("  A. Run ALL steps (complete pipeline)")
    print("  C. Show configuration")
    print("  Q. Quit")
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
            print("Running Step 6: Analyze Clips")
            print("=" * 60)
            optimize_clips(verbose=True)

        elif step_num == 7:
            print("\n" + "=" * 60)
            print("Running Step 7: Cut Final Clean Clips")
            print("=" * 60)
            apply_optimization(verbose=True)

        elif step_num == 8:
            print("\n" + "=" * 60)
            print("Running Step 8: Create Timeline JSON")
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

            elif choice == '5.5':
                run_step(5.5)

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

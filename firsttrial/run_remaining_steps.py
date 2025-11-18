#!/usr/bin/env python3
"""
Run remaining steps 6.5, 7, 8 automatically.
Use this after completing steps 1-6.
"""

import sys
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from steps.step6_5_rank_clips import rank_clips
from steps.step7_select_top15 import select_top15
from steps.step8_create_timeline import create_timeline


def main():
    """Run steps 6.5, 7, 8 in sequence."""
    print("\n" + "=" * 60)
    print("RUNNING REMAINING STEPS: 6.5 → 7 → 8")
    print("=" * 60)
    print()

    # Step 6.5: Rank all clips with Qwen VLM
    print("STEP 6.5: Rank All Clips with Qwen VLM")
    print("-" * 60)
    try:
        rank_clips(verbose=True)
        print("\n✅ Step 6.5 completed!")
    except Exception as e:
        print(f"\n❌ Step 6.5 failed: {e}")
        import traceback
        traceback.print_exc()
        return

    # Step 7: Select top 15 by score
    print("\n" + "=" * 60)
    print("STEP 7: Select Top 15 Clips by Score")
    print("-" * 60)
    try:
        select_top15(verbose=True)
        print("\n✅ Step 7 completed!")
    except Exception as e:
        print(f"\n❌ Step 7 failed: {e}")
        import traceback
        traceback.print_exc()
        return

    # Step 8: Generate timeline
    print("\n" + "=" * 60)
    print("STEP 8: Generate Remotion Timeline")
    print("-" * 60)
    try:
        create_timeline(verbose=True)
        print("\n✅ Step 8 completed!")
    except Exception as e:
        print(f"\n❌ Step 8 failed: {e}")
        import traceback
        traceback.print_exc()
        return

    # Summary
    print("\n" + "=" * 60)
    print("ALL STEPS COMPLETE!")
    print("=" * 60)
    print("\n✅ Rankings: outputs/step6_5_rankings.json")
    print("✅ Top 15 clips: outputs/top15/")
    print("✅ Top 15 metadata: outputs/step7_top15.json")
    print("✅ Timeline: outputs/final_timeline.json")
    print("=" * 60)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

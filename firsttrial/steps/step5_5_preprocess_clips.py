#!/usr/bin/env python3
"""
Step 5.5: Preprocess video clips for optimal analysis.

Applies official Qwen3-VL preprocessing parameters:
- 5 FPS for 0.2 second precision
- Consistent resolution (max 512x512 per frame)
- Optimized encoding for fast API processing
"""

import sys
import subprocess
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from utils import save_json, load_json
import config


def preprocess_clip(
    input_path: Path,
    output_path: Path,
    verbose: bool = False
) -> None:
    """
    Preprocess a single video clip.

    Args:
        input_path: Source video path
        output_path: Output preprocessed video path
        verbose: Print progress messages

    Raises:
        subprocess.CalledProcessError: If FFmpeg fails
    """
    if verbose:
        print(f"   Processing: {input_path.name}")

    # Official Qwen3-VL preprocessing parameters
    # - 5 FPS for 0.2s precision
    # - Scale to max 512x512 (maintains aspect ratio)
    # - Fast encoding for quick API processing
    cmd = [
        "ffmpeg",
        "-hide_banner", "-y",
        "-i", str(input_path),
        "-vf", "fps=5,scale='min(512,iw)':'min(512,ih)':force_original_aspect_ratio=decrease",
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "23",
        "-c:a", "aac",
        "-b:a", "128k",
        "-movflags", "+faststart",
        str(output_path)
    ]

    result = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )

    if result.returncode != 0:
        print(f"FFmpeg error:")
        print(result.stdout)
        raise subprocess.CalledProcessError(
            result.returncode,
            cmd,
            output=result.stdout
        )

    if verbose:
        print(f"   ✓ Preprocessed")


def preprocess_clips(
    clips_dir: Path = None,
    output_dir: Path = None,
    verbose: bool = True
) -> dict:
    """
    Preprocess all clips with optimal parameters.

    Args:
        clips_dir: Directory containing raw clips (default: from config)
        output_dir: Output directory for preprocessed clips (default: from config)
        verbose: Print progress messages

    Returns:
        Dictionary with statistics

    Raises:
        ValueError: If input directory not found
    """
    clips_dir = clips_dir or config.CLIPS_RAW_DIR
    output_dir = output_dir or config.CLIPS_OPTIMIZED_DIR

    if verbose:
        print("=" * 60)
        print("STEP 5.5: PREPROCESS CLIPS")
        print("=" * 60)
        print(f"Input: {clips_dir}")
        print(f"Output: {output_dir}")
        print(f"Settings:")
        print(f"  - FPS: 5 (0.2s precision)")
        print(f"  - Max resolution: 512x512")
        print(f"  - Encoding: H.264 (fast, CRF 23)")
        print()

    # Validate input
    clips_dir = Path(clips_dir)
    if not clips_dir.exists():
        raise ValueError(f"Clips directory not found: {clips_dir}")

    # Create output directory
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Get all clips
    clip_files = sorted(clips_dir.glob("*.mp4"))
    if not clip_files:
        raise ValueError(f"No clips found in {clips_dir}")

    if verbose:
        print(f"Found {len(clip_files)} clips to preprocess")
        print("-" * 60)

    # Preprocess each clip
    processed = []
    failed = []

    for i, clip_path in enumerate(clip_files, 1):
        if verbose:
            print(f"\n[{i}/{len(clip_files)}] {clip_path.name}")

        output_path = output_dir / clip_path.name

        try:
            preprocess_clip(clip_path, output_path, verbose)
            processed.append(clip_path.name)
        except Exception as e:
            if verbose:
                print(f"   ✗ Failed: {e}")
            failed.append({
                "filename": clip_path.name,
                "error": str(e)
            })

    # Summary
    if verbose:
        print()
        print("-" * 60)
        print()
        print("=" * 60)
        print("RESULTS")
        print("=" * 60)
        print(f"Total clips: {len(clip_files)}")
        print(f"✓ Preprocessed: {len(processed)}")
        print(f"✗ Failed: {len(failed)}")
        print()
        print(f"Output directory: {output_dir}")
        print("=" * 60)

    return {
        "total": len(clip_files),
        "processed": len(processed),
        "failed": len(failed),
        "processed_files": processed,
        "failed_files": failed
    }


if __name__ == "__main__":
    try:
        preprocess_clips(verbose=True)
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        sys.exit(1)

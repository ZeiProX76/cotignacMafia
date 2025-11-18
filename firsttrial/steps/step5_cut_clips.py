#!/usr/bin/env python3
"""
Step 5: Cut video clips based on targeted analysis.

Reads scene selections from step 4 and uses FFmpeg to extract clips
from the source video.
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils import load_json, save_json, cut_clip, sanitize_filename
from schemas import TargetedAnalysisOutput, ClipsMetadataOutput, ClipMetadata
import config


def cut_clips(
    video_path: str = None,
    scene_selection_path: Path = None,
    output_dir: Path = None,
    video_id: str = None,
    verbose: bool = True
) -> ClipsMetadataOutput:
    """
    Cut video clips based on scene selections.

    Args:
        video_path: Path to source video file (default: from config or video_id)
        scene_selection_path: Path to step 4 output (default: from config or video_id)
        output_dir: Output directory for clips (default: clips_raw/)
        video_id: Video identifier for multi-video support (e.g., 'video_001')
        verbose: Print progress messages

    Returns:
        ClipsMetadataOutput with metadata for all cut clips

    Raises:
        ValueError: If input files not found
        Exception: If FFmpeg fails

    Note:
        If video_id is provided:
        - Clips are prefixed with video_id (e.g., video_001_clip_01_*.mp4)
        - Metadata saved to outputs/{video_id}/clips_metadata.json
        - ClipMetadata includes video_id field
    """
    # Multi-video mode: load from config if video_id provided
    if video_id:
        videos_cfg = config.load_videos_config()
        video_cfg = next((v for v in videos_cfg.videos if v.id == video_id), None)
        if not video_cfg:
            raise ValueError(f"Video ID '{video_id}' not found in videos_config.json")

        video_path = video_path or video_cfg.local_path
        scene_selection_path = scene_selection_path or config.get_video_step_output(video_id, 4)
        config.create_video_directories(video_id)
    else:
        # Legacy single-video mode
        video_path = video_path or config.AVATAR_VIDEO_URL  # Fallback
        scene_selection_path = scene_selection_path or config.STEP4_OUTPUT

    output_dir = output_dir or config.CLIPS_RAW_DIR

    if verbose:
        print("=" * 60)
        print("STEP 5: CUT VIDEO CLIPS")
        print("=" * 60)
        if video_id:
            print(f"Video ID: {video_id}")
        print(f"Source video: {video_path}")
        print(f"Scene selection: {scene_selection_path}")
        print(f"Output directory: {output_dir}")
        print()

    # Validate inputs
    video_file = Path(video_path).expanduser().resolve()
    if not video_file.exists():
        raise ValueError(f"Video file not found: {video_file}")

    if not scene_selection_path.exists():
        raise ValueError(f"Step 4 output not found: {scene_selection_path}\nRun step 4 first!")

    # Create output directory
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Load scene selections
    if verbose:
        print("📂 Loading scene selections...")

    scene_data = load_json(scene_selection_path)
    scenes = TargetedAnalysisOutput(**scene_data)

    if verbose:
        print(f"   ✓ Loaded {len(scenes.scenes)} scenes to cut")
        print()

    # Cut each clip
    clip_metadata_list = []

    if verbose:
        print("✂️  Cutting clips...")
        print("-" * 60)

    for i, scene in enumerate(scenes.scenes, 1):
        # Create filename from description
        filename_base = sanitize_filename(scene.description[:50])
        # Prefix with video_id if in multi-video mode
        if video_id:
            output_path = output_dir / f"{video_id}_clip_{i:02d}_{filename_base}.mp4"
        else:
            output_path = output_dir / f"clip_{i:02d}_{filename_base}.mp4"

        if verbose:
            print(f"\n[{i}/{len(scenes.scenes)}] {scene.start} → {scene.end}")
            print(f"   Description: {scene.description[:80]}{'...' if len(scene.description) > 80 else ''}")
            print(f"   Output: {output_path.name}")

        # Cut the clip
        try:
            cut_clip(
                input_path=video_file,
                start=scene.start,
                end=scene.end,
                output_path=output_path,
                fast_mode=config.FFMPEG_FAST_MODE
            )

            # Save metadata
            clip_metadata_list.append(ClipMetadata(
                clip_number=i,
                filename=output_path.name,
                start=scene.start,
                end=scene.end,
                description=scene.description,
                reason=scene.reason if scene.reason else None,
                video_id=video_id  # Track source video
            ))

            if verbose:
                print(f"   ✓ Done")

        except Exception as e:
            if verbose:
                print(f"   ✗ Failed: {e}")
            continue

    # Save metadata
    metadata_output = ClipsMetadataOutput(
        source_video=str(video_file),
        clips=clip_metadata_list
    )

    # Save to video-specific path if multi-video mode, otherwise legacy path
    if video_id:
        metadata_path = config.get_video_step_output(video_id, 5)
    else:
        metadata_path = config.STEP5_METADATA

    save_json(metadata_output.model_dump(), metadata_path)

    # Display results
    if verbose:
        print()
        print("-" * 60)
        print()
        print("=" * 60)
        print("RESULTS")
        print("=" * 60)
        print(f"Total clips cut: {len(clip_metadata_list)}")
        print(f"Output directory: {output_dir}")
        print(f"Metadata: {metadata_path}")
        print()

        if len(clip_metadata_list) < len(scenes.scenes):
            print(f"⚠️  {len(scenes.scenes) - len(clip_metadata_list)} clips failed to cut")

        print("=" * 60)

    return metadata_output


if __name__ == "__main__":
    try:
        cut_clips(verbose=True)
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        sys.exit(1)

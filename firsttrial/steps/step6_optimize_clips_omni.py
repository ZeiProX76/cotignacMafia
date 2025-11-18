#!/usr/bin/env python3
"""Step 6: Remove humans - qwen-vl-max-latest"""

import sys
import os
import json
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import dashscope
from dotenv import load_dotenv
from utils import save_json, load_json, cut_clip
from schemas import OptimizationOutput, HumanDetection, ClipsMetadataOutput
import config

load_dotenv()

dashscope.base_http_api_url = 'https://dashscope-intl.aliyuncs.com/api/v1'

MODEL = "qwen-vl-max-latest"

PROMPT = """BE CONSERVATIVE. Find portions of this video with ZERO humans visible.

It's better to give SHORTER clips with NO humans than risk including a human.

If you see ANY human face, body, or person - exclude that portion.

Output the SAFEST timestamps with 0.1s precision:
{"start": "MM:SS.S", "end": "MM:SS.S"}

If humans throughout entire video:
{"unsaveable": true}"""


def ask_vlm(video_path: Path, verbose: bool = False) -> dict:
    """Ask VLM for clean timestamps."""
    messages = [{
        "role": "user",
        "content": [
            {"video": f"file://{video_path.absolute()}"},
            {"text": PROMPT}
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

            # Clean JSON
            cleaned = result_text.strip()
            if cleaned.startswith("```json"):
                cleaned = cleaned[7:]
            if cleaned.startswith("```"):
                cleaned = cleaned[3:]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]

            return json.loads(cleaned.strip())

        except Exception as e:
            if retry < 2:
                if verbose:
                    print(f"      Retry {retry + 1}/3...")
                time.sleep(2)
            else:
                raise Exception(f"API failed: {e}")


def extract_video_id_from_filename(filename: str) -> str:
    """
    Extract video_id from clip filename.

    Examples:
        video_001_clip_01_demo.mp4 -> video_001
        clip_01_demo.mp4 -> None (legacy single-video)
    """
    parts = filename.split('_')
    if len(parts) >= 3 and parts[0].startswith('video'):
        return parts[0]
    return None


def process_clip(clip_path: Path, clip_context: dict, video_id: str = None, verbose: bool = False) -> HumanDetection:
    """Process single clip - analyze only, no cutting."""
    if verbose:
        print(f"\n   {clip_path.name}")

    try:
        # Get timestamps from VLM
        result = ask_vlm(clip_path, verbose)

        if result.get("unsaveable"):
            if verbose:
                print(f"      ✗ Unsaveable - humans throughout")
            return HumanDetection(
                source_filename=clip_path.name,
                output_filename=clip_path.stem + "_clean" + clip_path.suffix,
                status="unsaveable",
                attempts=1,
                final_result="all",
                video_id=video_id,
                original_context=clip_context
            )

        start = result.get("start")
        end = result.get("end")

        if not start or not end:
            raise Exception("No timestamps returned")

        if verbose:
            print(f"      ✓ Safe timestamps: {start} → {end}")

        return HumanDetection(
            source_filename=clip_path.name,
            output_filename=clip_path.stem + "_clean" + clip_path.suffix,
            status="clean",
            clean_start=start,
            clean_end=end,
            attempts=1,
            final_result="none",
            video_id=video_id,
            original_context=clip_context
        )

    except Exception as e:
        if verbose:
            print(f"      ✗ Failed: {e}")
        return HumanDetection(
            source_filename=clip_path.name,
            output_filename=clip_path.stem + "_clean" + clip_path.suffix,
            status="failed",
            attempts=1,
            final_result="all",
            video_id=video_id,
            original_context=clip_context
        )


def optimize_clips(
    clips_dir: Path = None,
    output_path: Path = None,
    verbose: bool = True
) -> OptimizationOutput:
    """
    Analyze ALL clips from all videos and save safe timestamps.

    This aggregates clips from all video sources, tracking video_id for each clip.

    Args:
        clips_dir: Directory containing all clips (default: clips_raw/)
        output_path: Output path for aggregated analysis (default: step6_all_clips_analysis.json)
        verbose: Print progress messages

    Returns:
        OptimizationOutput with analysis for all clips

    Note:
        Automatically loads metadata from all video directories (outputs/{video_id}/)
        and extracts video_id from clip filenames.
    """
    clips_dir = clips_dir or config.CLIPS_RAW_DIR
    output_path = output_path or config.STEP6_OUTPUT  # Updated to use aggregated output

    if verbose:
        print("=" * 60)
        print(f"STEP 6: ANALYZE ALL CLIPS (MULTI-VIDEO) - {MODEL}")
        print("=" * 60)
        print(f"Clips: {clips_dir}")
        print(f"Output: {output_path}")
        print()

    config.validate_config()

    clips_dir = Path(clips_dir)

    # Load metadata from all video directories
    clip_context = {}

    # Try to load videos config to get all video IDs
    try:
        videos_cfg = config.load_videos_config()
        video_ids = [v.id for v in videos_cfg.videos]

        for video_id in video_ids:
            metadata_path = config.get_video_step_output(video_id, 5)
            if metadata_path.exists():
                try:
                    metadata = load_json(metadata_path)
                    clips_metadata = ClipsMetadataOutput(**metadata)
                    for clip in clips_metadata.clips:
                        clip_context[clip.filename] = clip.model_dump()
                    if verbose:
                        print(f"✓ Loaded metadata for {video_id}: {len(clips_metadata.clips)} clips")
                except Exception as e:
                    if verbose:
                        print(f"⚠️  Failed to load metadata for {video_id}: {e}")
    except Exception as e:
        if verbose:
            print(f"⚠️  Videos config not found, using legacy mode: {e}")
        # Fall back to legacy single-video metadata
        if config.STEP5_METADATA.exists():
            try:
                metadata = load_json(config.STEP5_METADATA)
                clips_metadata = ClipsMetadataOutput(**metadata)
                clip_context = {clip.filename: clip.model_dump() for clip in clips_metadata.clips}
            except:
                pass

    # Get all clips
    clip_files = sorted(clips_dir.glob("*.mp4"))
    if verbose:
        print(f"\nFound {len(clip_files)} total clips to analyze\n")

    # Process
    results = []
    for i, clip_path in enumerate(clip_files, 1):
        if verbose:
            print(f"[{i}/{len(clip_files)}]", end="")
        try:
            context = clip_context.get(clip_path.name)
            # Extract video_id from filename
            video_id = extract_video_id_from_filename(clip_path.name)
            result = process_clip(clip_path, context, video_id=video_id, verbose=verbose)
            results.append(result)
        except Exception as e:
            if verbose:
                print(f" ✗ {e}")
            # Extract video_id for error case too
            video_id = extract_video_id_from_filename(clip_path.name)
            results.append(HumanDetection(
                source_filename=clip_path.name,
                output_filename=clip_path.stem + "_clean" + clip_path.suffix,
                status="failed",
                attempts=0,
                final_result="all",
                video_id=video_id,
                original_context=None
            ))

    # Save
    output = OptimizationOutput(clips=results)
    save_json(output.model_dump(), output_path)

    # Summary
    if verbose:
        print()
        print("=" * 60)
        clean = sum(1 for r in results if r.status == "clean")
        unsaveable = sum(1 for r in results if r.status == "unsaveable")
        failed = sum(1 for r in results if r.status == "failed")
        print(f"Clean: {clean} | Unsaveable: {unsaveable} | Failed: {failed}")
        print(f"Output: {output_path}")
        print("=" * 60)

    return output


if __name__ == "__main__":
    try:
        optimize_clips(verbose=True)
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        sys.exit(1)

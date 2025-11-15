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


def process_clip(clip_path: Path, clip_context: dict, verbose: bool = False) -> HumanDetection:
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
            original_context=clip_context
        )


def optimize_clips(
    clips_dir: Path = None,
    metadata_path: Path = None,
    output_path: Path = None,
    verbose: bool = True
) -> OptimizationOutput:
    """Analyze all clips and save safe timestamps."""
    clips_dir = clips_dir or config.CLIPS_RAW_DIR
    metadata_path = metadata_path or config.STEP5_METADATA
    output_path = output_path or (config.OUTPUTS_DIR / "step6_analysis.json")

    if verbose:
        print("=" * 60)
        print(f"STEP 6: ANALYZE CLIPS - {MODEL}")
        print("=" * 60)
        print(f"Clips: {clips_dir}")
        print(f"Output: {output_path}")
        print()

    config.validate_config()

    clips_dir = Path(clips_dir)

    # Load metadata
    clip_context = {}
    if metadata_path.exists():
        try:
            metadata = load_json(metadata_path)
            clips_metadata = ClipsMetadataOutput(**metadata)
            clip_context = {clip.filename: clip.model_dump() for clip in clips_metadata.clips}
        except:
            pass

    # Get clips
    clip_files = sorted(clips_dir.glob("*.mp4"))
    if verbose:
        print(f"Found {len(clip_files)} clips\n")

    # Process
    results = []
    for i, clip_path in enumerate(clip_files, 1):
        if verbose:
            print(f"[{i}/{len(clip_files)}]", end="")
        try:
            context = clip_context.get(clip_path.name)
            result = process_clip(clip_path, context, verbose)
            results.append(result)
        except Exception as e:
            if verbose:
                print(f" ✗ {e}")
            results.append(HumanDetection(
                source_filename=clip_path.name,
                output_filename=clip_path.stem + "_clean" + clip_path.suffix,
                status="failed",
                attempts=0,
                final_result="all",
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

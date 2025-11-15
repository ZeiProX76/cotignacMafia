#!/usr/bin/env python3
import os
import json
import pathlib
import dashscope
from dotenv import load_dotenv

load_dotenv()

print("Setting up DashScope...")
dashscope.base_http_api_url = 'https://dashscope-intl.aliyuncs.com/api/v1'

# Load original clip context
clips_context_file = pathlib.Path("shortform_clips_20251113_151210.json")
if not clips_context_file.exists():
    print(f"Warning: {clips_context_file} not found. Clips will be analyzed without context.")
    clips_context = {"product_demos": []}
else:
    with open(clips_context_file, 'r') as f:
        clips_context = json.load(f)

# Get all mp4 files from clips_out/
clips_dir = pathlib.Path("clips_out")
clip_files = sorted(clips_dir.glob("*.mp4"))

print(f"Found {len(clip_files)} clips to analyze")

# Storage for recommendations
optimization_results = {"clips": []}

# Detect if human visible at start or end
DETECTION_PROMPT = """Is there a visible human at the very start or very end?
Output JSON: {"human_at": "start" | "end" | "none", "timestamp": "MM:SS"}
If no human: {"human_at": "none"}"""

def calculate_speed_multiplier(duration_seconds):
    """Programmatic speed-up based on clip duration"""
    if duration_seconds < 5:
        return 1.0  # No speed-up
    elif duration_seconds <= 10:
        return 2.0
    elif duration_seconds <= 20:
        return 3.0
    else:
        return 4.0  # Very long clips

# Process each clip
for idx, clip_path in enumerate(clip_files, 1):
    print(f"\n[{idx}/{len(clip_files)}] Analyzing: {clip_path.name}")

    # Get original context if available
    clip_context = None
    if idx - 1 < len(clips_context.get("product_demos", [])):
        clip_context = clips_context["product_demos"][idx - 1]
        print(f"  Context: {clip_context.get('why', 'N/A')}")

    messages = [{
        "role": "user",
        "content": [
            {"video": str(clip_path.absolute())},
            {"text": DETECTION_PROMPT}
        ]
    }]

    try:
        response = dashscope.MultiModalConversation.call(
            api_key=os.getenv("DASHSCOPE_API_KEY"),
            model='qwen3-vl-32b-thinking',
            messages=messages
        )

        # Handle different response formats
        if not response or not response.output:
            raise Exception("Empty response from API")

        # Try to extract text from various response structures
        try:
            content = response.output.choices[0].message.content
            # Handle list or dict content
            if isinstance(content, list):
                if len(content) == 0:
                    response_text = "[]"
                elif isinstance(content[0], dict) and "text" in content[0]:
                    response_text = content[0]["text"]
                else:
                    response_text = str(content)
            elif isinstance(content, str):
                response_text = content
            else:
                response_text = str(content)
        except (AttributeError, IndexError, KeyError) as e:
            print(f"  Response structure issue: {e}")
            print(f"  Full response: {response}")
            raise Exception(f"Could not parse response structure: {e}")

        print(f"Response: {response_text[:200]}...")

        # Parse JSON response
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0].strip()

        # Handle edge cases
        response_text = response_text.strip()
        detection = json.loads(response_text)

        human_at = detection.get("human_at", "none")
        timestamp = detection.get("timestamp", "00:00")

        result = {
            "source_filename": clip_path.name,
            "output_filename": clip_path.stem + "_clean" + clip_path.suffix,
            "human_at": human_at,
            "timestamp": timestamp,
            "original_context": clip_context
        }

        optimization_results["clips"].append(result)

        if human_at == "none":
            print(f"✓ No human - keep full clip")
        else:
            print(f"✓ Human at {human_at} (timestamp: {timestamp})")

    except Exception as e:
        print(f"✗ Error processing {clip_path.name}: {e}")
        optimization_results["clips"].append({
            "source_filename": clip_path.name,
            "output_filename": clip_path.stem + "_clean" + clip_path.suffix,
            "human_at": "none",
            "error": str(e)
        })

# Save results
output_path = pathlib.Path("clips_optimization.json")
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(optimization_results, f, indent=2, ensure_ascii=False)

print(f"\n{'='*60}")
print(f"✓ Optimization recommendations saved to: {output_path}")
print(f"{'='*60}")
print(json.dumps(optimization_results, indent=2))

#!/usr/bin/env python3
import os
from openai import OpenAI
from dotenv import load_dotenv
import json
from datetime import datetime

load_dotenv()

# Initialize OpenAI client for Dashscope
client = OpenAI(
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url="https://dashscope-intl.aliyuncs.com/compatible-mode/v1",
)

avatar_video_url = "https://efuozhjlnyrcyritksiy.supabase.co/storage/v1/object/public/cotignac/InfiniteTalk_00005-audio.mp4"

print("Analyzing avatar video for overlay moments...")
print("Using Qwen3-Omni-Flash (supports audio in video)...\n")

completion = client.chat.completions.create(
    model="qwen3-omni-flash",
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "video_url",
                    "video_url": {"url": avatar_video_url},
                },
                {
                    "type": "text",
                    "text": """Listen to what the avatar says about tools/software.
Identify moments when specific tools are mentioned that need visual demos.
Output JSON only:

{
  "overlay_moments": [
    {"start": "MM:SS", "end": "MM:SS", "visual": "tool name", "why": "what was said"}
  ]
}"""
                },
            ],
        }
    ],
    modalities=["text"],  # Text output only
    stream=True,  # Required by Qwen-Omni
    stream_options={"include_usage": True},
)

# Collect the streaming response
result_text = ""
print("=== Model Response ===")
for chunk in completion:
    if chunk.choices and chunk.choices[0].delta.content:
        content = chunk.choices[0].delta.content
        print(content, end="", flush=True)
        result_text += content
    elif not chunk.choices and hasattr(chunk, 'usage'):
        print(f"\n\n=== Usage: {chunk.usage} ===")

print("\n" + "="*50 + "\n")

# Clean the response - remove markdown code blocks if present
cleaned_json = result_text.strip()
if cleaned_json.startswith("```json"):
    cleaned_json = cleaned_json[7:]
if cleaned_json.startswith("```"):
    cleaned_json = cleaned_json[3:]
if cleaned_json.endswith("```"):
    cleaned_json = cleaned_json[:-3]
cleaned_json = cleaned_json.strip()

output_file = f"avatar_overlays_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
with open(output_file, 'w') as f:
    f.write(cleaned_json)

print(f"\n✅ Saved to {output_file}")

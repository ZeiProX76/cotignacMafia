#!/usr/bin/env python3
import os
import dashscope
from dotenv import load_dotenv
import json
from datetime import datetime

load_dotenv()

dashscope.base_http_api_url = 'https://dashscope-intl.aliyuncs.com/api/v1'
video_url = "/home/hugues/Downloads/get.mp4"
local_video_path = "/home/hugues/Downloads/get.mp4"

messages = [{
    "role": "user",
    "content": [
        {"video": video_url},
        {"text": """You are analyzing a reference video (Instagram/TikTok short - Style Blueprint) to understand its OUTPUT style.

Analyze this short-form viral content (15-60 seconds) at 2 fps for:

2. **Format**: Split screen, talking head dominant, B-roll style, etc.
3. **Energy and Rhythm**: Fast-paced? Calm? Beat-driven?
4. **Jump Cut Frequency**: How often? Every second? Every few seconds?
5. **Transition Styles**: Hard cuts? Fades? Zooms? Effects?
6. **Overall Quality and Vibe**: Professional? Raw? Energetic? Chill?
7. **What's shown at each timestamp**: Visual content second-by-second

Output detailed JSON with timestamps:

{
  "style_analysis": {
    "overall_pacing": "description",
    "format": "description",
    "energy_rhythm": "description",
    "jump_cut_frequency": "description",
    "transition_styles": "description",
    "overall_vibe": "description"
  },
}"""}
    ]
}]

print("Analyzing video style...")
response = dashscope.MultiModalConversation.call(
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    model='qwen-vl-max-latest',
    messages=messages
)

# Debug: print the full response structure
print("\n=== DEBUG: Full Response ===")
print(f"Response type: {type(response)}")
print(f"Response output: {response.output}")
print("="*50 + "\n")

# Handle different response formats
try:
    result_text = response.output.choices[0].message.content[0]["text"]
except (IndexError, KeyError, TypeError) as e:
    print(f"Primary format failed: {e}")
    # Try alternative formats
    if hasattr(response.output, 'text'):
        result_text = response.output.text
    elif isinstance(response.output.choices[0].message.content, str):
        result_text = response.output.choices[0].message.content
    else:
        print("Full response structure:")
        print(response)
        raise Exception("Could not extract text from response")

print(result_text)

# Clean the response - remove markdown code blocks if present
cleaned_json = result_text.strip()
if cleaned_json.startswith("```json"):
    cleaned_json = cleaned_json[7:]
if cleaned_json.startswith("```"):
    cleaned_json = cleaned_json[3:]
if cleaned_json.endswith("```"):
    cleaned_json = cleaned_json[:-3]
cleaned_json = cleaned_json.strip()

output_file = f"style_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
with open(output_file, 'w') as f:
    f.write(cleaned_json)

print(f"\n✅ Style analysis saved to {output_file}")

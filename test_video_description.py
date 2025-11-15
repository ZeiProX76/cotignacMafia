import os
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def test_video_description():
    """Test video description using Qwen VL model"""

    # Initialize the client
    client = OpenAI(
        api_key=os.getenv("DASHSCOPE_API_KEY"),
        base_url="https://dashscope-intl.aliyuncs.com/compatible-mode/v1",
    )

    # Path to your local video file
    video_path = "https://efuozhjlnyrcyritksiy.supabase.co/storage/v1/object/public/cotignac/Wispr%20Flow%20for%20iPhone%20-%20Wispr%20Flow%20AI%20(1080p,%20h264).mp4"

    print("Testing video description with Qwen VL model...")
    print(f"Video path: {video_path}")
    print("-" * 50)

    # Make the API call with streaming
    completion = client.chat.completions.create(
        model="qwen-vl-max",
        messages=[{
            "role": "user",
            "content": [
                {
                    "type": "video_url",
                    "video_url": {"url": video_path}
                },
                {
                    "type": "text",
                    "text": """You are a world-class multimodal content analyst specialized in video understanding.

Your task is to **analyze the given video** and produce a **precise, structured report** identifying:
1. **Product Demonstration Moments** — When and how the product is actively showcased, used, or explained.
2. **Timestamps (Start–End in seconds)** — For each demo segment, give accurate time intervals.
3. **Demo Type** — (choose: "product in use", "feature showcase", "tutorial moment", "branding segment", "before/after result", "voice-over explanation", or "UI walkthrough").
4. **Visual Quality** — Rate from 1–10 based on clarity, camera stability, lighting, and visibility of the product.
5. **Content Potential Score** — Rate each segment from 1–10 for how strong it is for content reuse (shorts, reels, ads, hero shots, thumbnails, etc.).
6. **Short Clip Candidates** — Suggest 2–4 timestamps (max 15s each) that would perform best for content creation.
7. **Summary Insights** — Short paragraph describing overall storytelling, emotional tone, pacing, and moments of peak engagement.

Output strictly in the following JSON format:
{
  "product_demos": [
    {
      "start": "00:15",
      "end": "00:32",
      "demo_type": "feature showcase",
      "description": "The user demonstrates the main product function using clear close-up shots.",
      "visual_quality": 9,
      "content_potential": 8
    },
    {
      "start": "01:04",
      "end": "01:21",
      "demo_type": "before/after result",
      "description": "Side-by-side comparison highlighting the product effect.",
      "visual_quality": 8,
      "content_potential": 10
    }
  ],
  "best_clip_candidates": [
    { "start": "00:16", "end": "00:30", "reason": "perfect lighting, clear use-case" },
    { "start": "01:10", "end": "01:22", "reason": "great hook for ads or reels" }
  ],
  "summary_insights": "The video effectively showcases the product with multiple clear demonstrations, especially between 0:15–0:30 and 1:10–1:22. These segments show strong visual storytelling and are ideal for content repurposing."
}"""
                }
            ]
        }],
        stream=True,
    )

    # Collect and display the streaming response
    full_content = ""
    print("\nStreaming output:")
    print("-" * 50)

    for chunk in completion:
        if chunk.choices[0].delta.content is None:
            continue
        content = chunk.choices[0].delta.content
        full_content += content
        print(content, end="", flush=True)

    print("\n" + "-" * 50)
    print(f"\nComplete response length: {len(full_content)} characters")

    return full_content

if __name__ == "__main__":
    try:
        result = test_video_description()
        print("\n✓ Test completed successfully!")
    except Exception as e:
        print(f"\n✗ Test failed with error: {e}")
        raise

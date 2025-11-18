# Video Analysis Pipeline - Complete Documentation

## Table of Contents
1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Configuration](#configuration)
4. [Pipeline Steps (Detailed)](#pipeline-steps-detailed)
5. [SDK Integrations](#sdk-integrations)
6. [Prompt Engineering](#prompt-engineering)
7. [Data Schemas](#data-schemas)
8. [File Structure](#file-structure)
9. [Execution Guide](#execution-guide)

---

## Overview

### Purpose
This is an **AI-powered multi-video analysis pipeline** that:
- Extracts B-roll clips from multiple demo videos
- Matches them to avatar narration content
- Ranks clips by quality using vision-language models
- Generates a Remotion-compatible timeline for video production

### Key Features
- **Multi-video processing**: Process multiple source videos in parallel
- **AI-powered selection**: Uses GPT-5 + Qwen VL models for intelligent clip selection
- **Quality ranking**: VLM watches each clip and scores on 4 criteria (0-400 total)
- **Human detection**: Automatically finds safe timestamps with zero human visibility
- **Complete automation**: Run entire pipeline with one command

### Technology Stack
- **Qwen VL** (Alibaba): Video/audio analysis, human detection, quality ranking
- **GPT-5 Mini** (OpenAI): Prompt crafting, timeline generation
- **FFmpeg**: Video cutting and processing
- **Pydantic**: Data validation and type safety
- **DashScope SDK**: Qwen model API access

---

## Architecture

### Pipeline Modes

#### 1. Single-Video Mode (Legacy)
Process one avatar video through all steps sequentially.

#### 2. Multi-Video Mode (Recommended)
**Phase 1: Avatar Analysis** (Run once)
- Step 1: Transcribe avatar audio

**Phase 2: Demo Video Processing** (Per video)
- Step 2: Analyze screen activities
- Step 3: Craft targeted prompt with GPT-5
- Step 4: Run targeted scene selection
- Step 5: Cut raw video clips

**Phase 3: Aggregation & Selection** (All videos)
- Step 6: Detect humans in all clips
- Step 6.5: Rank all clips with VLM (NEW)
- Step 7: Select top 15 by score (NEW)
- Step 8: Generate Remotion timeline

### Data Flow Diagram

```
┌─────────────────┐
│  Avatar Video   │
│  (with speech)  │
└────────┬────────┘
         │
         ▼
   ┌──────────┐
   │  Step 1  │  Transcribe audio → sentences with timestamps
   └──────────┘
         │
         ▼
   [Transcription JSON]
         │
         ├──────────────────────────────────────┐
         │                                      │
         ▼                                      ▼
┌─────────────────┐                   ┌─────────────────┐
│ Demo Video #1   │                   │ Demo Video #2   │
└────────┬────────┘                   └────────┬────────┘
         │                                      │
    ┌────▼────┐                            ┌────▼────┐
    │ Step 2  │  Analyze screen            │ Step 2  │
    └────┬────┘                            └────┬────┘
         │                                      │
    ┌────▼────┐                            ┌────▼────┐
    │ Step 3  │  GPT-5 crafts prompt       │ Step 3  │
    └────┬────┘                            └────┬────┘
         │                                      │
    ┌────▼────┐                            ┌────▼────┐
    │ Step 4  │  VLM selects scenes        │ Step 4  │
    └────┬────┘                            └────┬────┘
         │                                      │
    ┌────▼────┐                            ┌────▼────┐
    │ Step 5  │  FFmpeg cuts clips         │ Step 5  │
    └────┬────┘                            └────┬────┘
         │                                      │
         └──────────┬───────────────────────────┘
                    │
                    ▼
            [All Raw Clips]
                    │
              ┌─────▼─────┐
              │  Step 6   │  Detect humans → find safe timestamps
              └─────┬─────┘
                    │
              ┌─────▼─────┐
              │ Step 6.5  │  VLM ranks clips (4 criteria, 0-400 score)
              └─────┬─────┘
                    │
              ┌─────▼─────┐
              │  Step 7   │  Select top 15 by total score
              └─────┬─────┘
                    │
                [Top 15 Clips]
                    │
              ┌─────▼─────┐
              │  Step 8   │  GPT-5 maps clips to avatar timeline
              └─────┬─────┘
                    │
                    ▼
          [Remotion Timeline JSON]
```

---

## Configuration

### 1. config.py

**Location**: `firsttrial/config.py`

**Purpose**: Centralized configuration for the entire pipeline

#### API Keys
```python
import os
from dotenv import load_dotenv

load_dotenv()

# Required API keys
DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY")  # For Qwen models
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")        # For GPT-5
```

#### Model Configuration
```python
# Audio transcription (Step 1)
QWEN_AUDIO_MODEL = "qwen3-omni-flash"
# Streaming audio-aware model with text output

# Video analysis (Steps 2, 4, 6, 6.5)
QWEN_VIDEO_MODEL = "qwen-vl-max-latest"
# Vision-language model for video understanding

# Prompt crafting & timeline (Steps 3, 8)
GPT5_MODEL = "gpt-5-mini-2025-08-07"
# GPT-5 Mini with reasoning capabilities

# GPT-5 Reasoning Settings
GPT5_REASONING_EFFORT = "medium"  # low/medium/high
GPT5_TEXT_VERBOSITY = "low"       # low/medium/high
```

#### Video Sources
```python
# Single avatar video
AVATAR_VIDEO_URL = "https://example.com/avatar.mp4"

# Multi-video configuration
VIDEOS_CONFIG_PATH = Path("videos_config.json")
```

#### Directory Structure
```python
OUTPUTS_DIR = Path("outputs")
CLIPS_RAW_DIR = OUTPUTS_DIR / "clips_raw"      # All raw clips
TOP15_DIR = OUTPUTS_DIR / "top15"              # Final top 15 clips

# Step outputs
STEP1_OUTPUT = OUTPUTS_DIR / "step1_transcription.json"
STEP6_OUTPUT = OUTPUTS_DIR / "step6_all_clips_analysis.json"
STEP6_5_OUTPUT = OUTPUTS_DIR / "step6_5_rankings.json"
STEP7_OUTPUT = OUTPUTS_DIR / "step7_top15.json"
STEP8_OUTPUT = OUTPUTS_DIR / "final_timeline.json"
```

#### FFmpeg Settings
```python
FFMPEG_FAST_MODE = False  # False = accurate re-encode (prevents corruption)
MAX_API_RETRIES = 3       # Number of retry attempts for API calls
```

#### Helper Functions
```python
def load_videos_config() -> VideosConfig:
    """Load and validate videos_config.json"""

def get_video_output_dir(video_id: str) -> Path:
    """Get outputs/{video_id}/ directory"""

def get_video_step_output(video_id: str, step: str) -> Path:
    """Get specific step output for a video"""
    # Example: outputs/video_001/step2_screen_analysis.json

def create_video_directories(video_id: str):
    """Create all necessary directories for a video"""
```

---

### 2. videos_config.json

**Location**: `firsttrial/videos_config.json`

**Purpose**: Define multiple demo video sources for processing

#### Structure
```json
{
  "videos": [
    {
      "id": "video_001",
      "name": "Main Demo Video",
      "url": "https://cloud.video.taobao.com/play/u/xxx/video_001.mp4",
      "local_path": "/home/user/videos/demo1.mp4",
      "priority": 1
    },
    {
      "id": "video_002",
      "name": "Secondary Demo",
      "url": "https://cloud.video.taobao.com/play/u/xxx/video_002.mp4",
      "local_path": "/home/user/videos/demo2.mp4",
      "priority": 2
    }
  ]
}
```

#### Field Descriptions

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | Yes | Unique identifier (used in filenames and directories) |
| `name` | string | Yes | Human-readable name for display |
| `url` | string | Yes | Video URL for VLM API calls (must be publicly accessible) |
| `local_path` | string | Yes | Local file path for FFmpeg cutting |
| `priority` | integer | No | Video priority (higher = more important, default: 1) |

#### Usage
- Steps 2-5 iterate through all videos
- Each video gets its own output directory: `outputs/{video_id}/`
- Clips are prefixed with video ID: `{video_id}_clip_01_*.mp4`

---

### 3. Environment Variables (.env)

**Location**: `.env` (root directory)

**Required Variables**:
```bash
# Qwen VL API (DashScope)
DASHSCOPE_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# OpenAI GPT-5
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

**Setup**:
```bash
# Create .env file
cp .env.example .env

# Edit with your API keys
nano .env
```

---

## Pipeline Steps (Detailed)

### Step 1: Transcribe Avatar Audio

**File**: `firsttrial/steps/step1_transcribe_avatar.py`

**Model**: `qwen3-omni-flash` (Qwen audio-streaming model)

**Purpose**: Extract every sentence from avatar video with precise timestamps

#### Input
- Avatar video URL from `config.AVATAR_VIDEO_URL`

#### Output
- `outputs/step1_transcription.json`

```json
{
  "sentences": [
    {
      "start": "00:00",
      "end": "00:03",
      "text": "Welcome to this tutorial on video generation."
    },
    {
      "start": "00:03",
      "end": "00:07",
      "text": "Today we'll explore how to create amazing B-roll clips."
    }
  ]
}
```

#### Complete Prompt
```python
TRANSCRIPTION_PROMPT = """Listen carefully to the audio in this video.
Extract EVERY SENTENCE spoken with its exact start and end timestamps.

Output ONLY valid JSON in this exact format:
{
  "sentences": [
    {"start": "MM:SS", "end": "MM:SS", "text": "exact sentence text"},
    {"start": "MM:SS", "end": "MM:SS", "text": "next sentence"}
  ]
}

Requirements:
- Each sentence must have its own entry
- Use MM:SS format (e.g., "00:05", "02:30")
- Capture the exact words spoken
- Include ALL sentences from start to end
- Maintain chronological order
- Do NOT include markdown formatting - output raw JSON only
"""
```

#### API Call (OpenAI-Compatible Streaming)
```python
from openai import OpenAI

# Initialize client with DashScope endpoint
client = OpenAI(
    api_key=config.DASHSCOPE_API_KEY,
    base_url="https://dashscope-intl.aliyuncs.com/compatible-mode/v1"
)

# Create streaming completion
completion = client.chat.completions.create(
    model="qwen3-omni-flash",
    messages=[{
        "role": "user",
        "content": [
            {"type": "video_url", "video_url": {"url": avatar_url}},
            {"type": "text", "text": TRANSCRIPTION_PROMPT}
        ]
    }],
    modalities=["text"],  # Can also include "audio" for audio responses
    stream=True,
    stream_options={"include_usage": True}
)

# Stream response
result_text = ""
for chunk in completion:
    if chunk.choices and chunk.choices[0].delta.content:
        result_text += chunk.choices[0].delta.content
```

#### Why This Approach
- **Streaming**: Real-time feedback on long videos
- **Audio-aware model**: Specifically trained for audio transcription
- **OpenAI-compatible API**: Familiar interface, easy integration
- **Precise timestamps**: Essential for timeline synchronization

---

### Step 2: Analyze Screen Activities

**File**: `firsttrial/steps/step2_analyze_screen.py`

**Model**: `qwen3-vl-32b-thinking` (Vision-language with reasoning)

**Purpose**: Analyze ALL screen activities in demo video (no filtering yet)

#### Multi-Video Support
- **Input parameter**: `video_id` (optional)
- If provided: Uses video from `videos_config.json`
- Output directory: `outputs/{video_id}/`

#### Input
- Demo video URL (from config or `videos_config.json`)

#### Output
- `outputs/{video_id}/step2_screen_analysis.json`
- `outputs/{video_id}/step2_screen_analysis_reasoning.txt` (model's thinking process)

```json
{
  "activities": [
    {
      "start": "00:00",
      "end": "00:10",
      "description": "Google Docs interface showing JSON prompt structure",
      "activity_type": "ui"
    },
    {
      "start": "00:10",
      "end": "00:25",
      "description": "OpenArt platform with text-to-video generation",
      "activity_type": "demo"
    },
    {
      "start": "00:25",
      "end": "00:35",
      "description": "Person explaining features while pointing at screen",
      "activity_type": "presentation"
    }
  ]
}
```

#### Complete Prompt
```python
SCREEN_ANALYSIS_PROMPT = """Analyze this ENTIRE video from start to finish.
Describe what's being shown on screen in segments (approximately every 10-20 seconds).

IMPORTANT INSTRUCTIONS:
- Start from 00:00 and continue through the ENTIRE video timeline to the end
- Include ALL segments, even those with humans talking or presenting
- For each segment, focus on what's being SHOWN ON SCREEN (not what's being said)
- Note the visual content: UI interfaces, demos, animations, products, text, graphics
- Keep each description focused and under 15 words

Activity types: "ui", "demo", "animation", "product", "text", "presentation"

Output ONLY valid JSON (no markdown formatting):
{
  "activities": [
    {
      "start": "MM:SS",
      "end": "MM:SS",
      "description": "Brief description of screen content",
      "activity_type": "type"
    }
  ]
}

Analyze the COMPLETE video now.
"""
```

#### API Call (DashScope with Reasoning)
```python
import dashscope

# Set international endpoint
dashscope.base_http_api_url = 'https://dashscope-intl.aliyuncs.com/api/v1'

# Call VLM with video
response = dashscope.MultiModalConversation.call(
    api_key=config.DASHSCOPE_API_KEY,
    model='qwen3-vl-32b-thinking',
    messages=[{
        "role": "user",
        "content": [
            {"video": video_url},
            {"text": SCREEN_ANALYSIS_PROMPT}
        ]
    }]
)

# Extract result
result_text = response.output.choices[0].message.content[0]["text"]

# Extract reasoning (thinking process)
reasoning_text = response.output.choices[0].message.reasoning_content
```

#### Why This Approach
- **Complete coverage**: Analyzes ENTIRE video (no gaps)
- **No filtering**: Includes segments with humans (filtering happens in step 6)
- **Reasoning model**: Extended thinking improves accuracy
- **Saves reasoning**: Helpful for debugging and understanding model decisions

---

### Step 3: Craft Prompt with GPT-5

**File**: `firsttrial/steps/step3_craft_prompt.py`

**Model**: `gpt-5-mini-2025-08-07` (Reasoning model)

**Purpose**: Analyze avatar speech + screen activities, then craft a CONCISE prompt for targeted clip extraction

#### Multi-Video Support
- Reads from `outputs/{video_id}/step2_screen_analysis.json`
- Saves to `outputs/{video_id}/step3_generated_prompt.txt`

#### Input
- Step 1 transcription (avatar sentences)
- Step 2 screen analysis (per-video activities)

#### Output
- `outputs/{video_id}/step3_generated_prompt.txt`

Example output:
```
Analyze the COMPLETE video from 00:00 to end. Identify ALL instances of:
JSON documents with prompt structures, OpenArt UI screens with generation
controls, room transformation animations (Labubu box opening, Tom & Jerry
chaos, Pikachu Pokéball), product showcases (Apple Vision Pro, Samsung phone,
Ferrari car reveal). Rank all candidates by visual quality and animation
completeness. Select TOP 15-20 clips spread across the entire timeline.
Focus on these ranges: 00:00-00:10, 01:20-02:00, 02:20-04:30. Exclude any
frames with humans visible. Return JSON with start, end, description, reason.
```

#### Complete Prompt (System + User)
```python
SYSTEM_PROMPT = """You are an expert at video analysis and prompt engineering.

Your task is to analyze two data sources:
1. Avatar video transcription (what's being discussed)
2. Demo video screen analysis (what's being shown)

Then create a SHORT, FOCUSED prompt for a vision-language model.

CRITICAL CONSTRAINTS:
- Output must be 2-4 sentences MAXIMUM
- NEVER mention: "speech", "audio", "narrator", "avatar", "talking", "discussion"
- ONLY reference: visual elements (UI, animations, products, text, graphics)
- The VLM has NO ACCESS to audio - it can only see visuals
- MUST instruct: analyze ENTIRE video, rank candidates, return TOP clips

OUTPUT FORMAT (follow exactly):
"Analyze COMPLETE video from [start] to [end]. Identify ALL instances of:
[list specific visual elements from screen analysis]. Rank all candidates
by [quality criteria]. Select TOP [number] clips spread across timeline.
Focus on: [timestamp ranges]. Exclude [constraints]. Return JSON with
start, end, description, reason."
"""

USER_PROMPT = f"""CONTEXT - What the avatar is discussing:
{transcription_text}

VISUALS - What's shown in the demo video:
{screen_analysis_text}

YOUR TASK:
1. Internally: Match the discussion context with the visual content to identify
   the BEST moments worth extracting as B-roll clips
2. Output: A CONCISE prompt (2-4 sentences MAX) for the VLM to use

EXAMPLE OUTPUT:
"Analyze COMPLETE video (00:00 to end). Find ALL: JSON documents, OpenArt UI,
animations (Labubu, Tom&Jerry), products (Apple, Ferrari). Rank by quality.
Select TOP 15-20 across timeline. Focus: 00:00-00:10, 01:20-02:00. NO HUMANS.
JSON format."

Now create the prompt for this video.
"""
```

#### API Call (Responses API)
```python
from openai import OpenAI

client = OpenAI(api_key=config.OPENAI_API_KEY)

response = client.responses.create(
    model="gpt-5-mini-2025-08-07",
    input=f"{SYSTEM_PROMPT}\n\n{USER_PROMPT}",
    reasoning={
        "effort": config.GPT5_REASONING_EFFORT  # "medium"
    },
    text={
        "verbosity": config.GPT5_TEXT_VERBOSITY  # "low"
    }
)

generated_prompt = response.output_text
```

#### Manual Review Checkpoint
```python
def craft_prompt(video_id=None, pause_for_review=True):
    # ... generate prompt ...

    if pause_for_review:
        print(f"\nGenerated prompt:\n{generated_prompt}\n")
        input("Press Enter to continue or Ctrl+C to cancel...")
```

#### Why This Approach
- **Two-stage reasoning**: GPT-5 thinks deeply, then outputs concisely
- **Context-aware**: Matches discussion topics with visual content
- **Constraint enforcement**: Prevents audio references (VLM can't hear)
- **Quality control**: Manual review before expensive VLM call

---

### Step 4: Targeted Video Analysis

**File**: `firsttrial/steps/step4_targeted_analysis.py`

**Model**: `qwen-vl-max-latest` (Video analysis)

**Purpose**: Use GPT-5 crafted prompt to extract specific scenes

#### Multi-Video Support
- Uses prompt from `outputs/{video_id}/step3_generated_prompt.txt`
- Saves to `outputs/{video_id}/step4_scene_selection.json`

#### Input
- Demo video URL
- GPT-5 crafted prompt from step 3

#### Output
- `outputs/{video_id}/step4_scene_selection.json`

```json
{
  "scenes": [
    {
      "start": "00:05",
      "end": "00:12",
      "description": "Google Docs showing detailed JSON prompt structure",
      "reason": "Clear demonstration of prompt engineering format"
    },
    {
      "start": "00:45",
      "end": "00:58",
      "description": "OpenArt UI with Veo 3 model selection dropdown",
      "reason": "Shows the actual tool interface for video generation"
    }
  ]
}
```

#### Prompt Strategy
Simply passes through the GPT-5 crafted prompt from step 3. The prompt already contains all necessary instructions.

#### API Call (with Retry Logic)
```python
from utils.api_clients import QwenClient

client = QwenClient(api_key=config.DASHSCOPE_API_KEY)

# Retry wrapper
for attempt in range(config.MAX_API_RETRIES):
    try:
        response = client.analyze_video(
            model=config.QWEN_VIDEO_MODEL,
            video_url=video_url,
            prompt=generated_prompt
        )
        break
    except Exception as e:
        if attempt < config.MAX_API_RETRIES - 1:
            time.sleep(2 ** attempt)  # Exponential backoff
        else:
            raise
```

#### QwenClient Implementation
```python
class QwenClient:
    def analyze_video(self, model, video_url, prompt):
        response = dashscope.MultiModalConversation.call(
            api_key=self.api_key,
            model=model,
            messages=[{
                "role": "user",
                "content": [
                    {"video": video_url},
                    {"text": prompt}
                ]
            }]
        )

        return response.output.choices[0].message.content[0]["text"]
```

---

### Step 5: Cut Video Clips

**File**: `firsttrial/steps/step5_cut_clips.py`

**Tool**: FFmpeg (no AI model)

**Purpose**: Physically cut clips from demo videos using scene timestamps

#### Multi-Video Support
- Clips prefixed with `{video_id}_clip_XX_*.mp4`
- Metadata saved to `outputs/{video_id}/clips_metadata.json`

#### Input
- Local video file path (from `videos_config.json`)
- Scene selections from step 4

#### Output
- Raw clips: `outputs/clips_raw/{video_id}_clip_01_description.mp4`
- Metadata: `outputs/{video_id}/clips_metadata.json`

```json
{
  "source_video": "video_001",
  "clips": [
    {
      "clip_number": 1,
      "filename": "video_001_clip_01_Google_Docs_JSON_structure.mp4",
      "start": "00:05",
      "end": "00:12",
      "description": "Google Docs showing detailed JSON prompt structure",
      "reason": "Clear demonstration of prompt engineering format",
      "video_id": "video_001"
    }
  ]
}
```

#### FFmpeg Command (Accurate Re-encode)
```python
def cut_clip(input_path, start, end, output_path):
    cmd = [
        "ffmpeg",
        "-hide_banner",        # Clean output
        "-y",                  # Overwrite existing
        "-i", str(input_path), # Input file
        "-ss", start,          # Start time (AFTER -i for accuracy)
        "-to", end,            # End time
        "-c:v", "libx264",     # Video codec (re-encode)
        "-preset", "ultrafast", # Speed preset
        "-crf", "18",          # Quality (18 = high quality)
        "-c:a", "aac",         # Audio codec
        "-movflags", "+faststart", # Web optimization
        str(output_path)
    ]

    subprocess.run(cmd, check=True)
```

#### Why Re-encode (Not Stream Copy)
```python
# BAD - Stream copy can cause corruption
# ffmpeg -ss 00:05 -i input.mp4 -to 00:12 -c copy output.mp4

# GOOD - Re-encode ensures accurate timestamps
# ffmpeg -i input.mp4 -ss 00:05 -to 00:12 -c:v libx264 output.mp4
```

**Reason**: Stream copy (`-c copy`) copies frames as-is, which can cause:
- Inaccurate start/end points (keyframe alignment issues)
- Corrupted clips with missing frames
- Timeline synchronization problems

Re-encoding ensures pixel-perfect accuracy at the specified timestamps.

#### Filename Sanitization
```python
def sanitize_filename(description, max_length=50):
    # Remove unsafe characters
    safe = re.sub(r'[^\w\s-]', '', description)
    # Replace spaces with underscores
    safe = re.sub(r'[-\s]+', '_', safe)
    # Truncate to max length
    return safe[:max_length].strip('_')

# Example
"Google Docs showing JSON?" → "Google_Docs_showing_JSON"
```

---

### Step 6: Analyze Clips for Humans

**File**: `firsttrial/steps/step6_optimize_clips_omni.py`

**Model**: `qwen-vl-max-latest` (VLM watches each clip)

**Purpose**: Detect humans in EVERY clip and find safe timestamps with zero visibility

#### Multi-Video Support
- **AGGREGATES** all clips from `outputs/clips_raw/`
- Extracts `video_id` from filename pattern (`{video_id}_clip_XX_*.mp4`)
- Loads metadata from all `outputs/{video_id}/clips_metadata.json` files
- Saves aggregated results to `outputs/step6_all_clips_analysis.json`

#### Input
- All raw clips: `outputs/clips_raw/*.mp4`
- Metadata from per-video step 5 outputs

#### Output
- `outputs/step6_all_clips_analysis.json`

```json
{
  "clips": [
    {
      "source_filename": "video_001_clip_01_Google_Docs.mp4",
      "output_filename": null,
      "status": "clean",
      "clean_start": "00:05.0",
      "clean_end": "00:12.0",
      "attempts": 1,
      "final_result": "none",
      "video_id": "video_001",
      "original_context": {
        "description": "Google Docs showing JSON structure",
        "reason": "Clear demonstration of format"
      }
    },
    {
      "source_filename": "video_001_clip_05_Person_talking.mp4",
      "output_filename": null,
      "status": "unsaveable",
      "clean_start": null,
      "clean_end": null,
      "attempts": 1,
      "final_result": "all",
      "video_id": "video_001",
      "original_context": {...}
    }
  ]
}
```

#### Status Values
- `"clean"`: Zero humans detected, safe timestamps found
- `"unsaveable"`: Humans throughout entire clip, cannot salvage
- `"failed"`: API error or parsing failure

#### Complete Prompt (Conservative Safety)
```python
HUMAN_DETECTION_PROMPT = """CRITICAL TASK: Analyze this video clip for human presence.

BE EXTREMELY CONSERVATIVE. Your goal is to find portions of this clip with
ABSOLUTELY ZERO humans visible.

IMPORTANT:
- It's better to return SHORTER clips with NO humans than to risk including a human
- If you see ANY human face, body part, silhouette, or person - EXCLUDE that portion
- Even brief human appearances (1 frame) should result in exclusion
- If uncertain whether something is a human - exclude it to be safe

Watch the ENTIRE clip and identify the safest continuous segment with zero humans.

Output ONLY valid JSON (no markdown):

If you find a safe segment:
{
  "start": "MM:SS.S",
  "end": "MM:SS.S"
}

If humans are visible throughout the entire clip:
{
  "unsaveable": true
}

Use 0.1 second precision (e.g., "00:05.3", "00:12.7").

Analyze now.
"""
```

#### API Call (Local File Access)
```python
def analyze_clip_for_humans(clip_path):
    # Use file:// protocol for local files
    file_url = f"file://{clip_path.absolute()}"

    response = dashscope.MultiModalConversation.call(
        api_key=config.DASHSCOPE_API_KEY,
        model=config.QWEN_VIDEO_MODEL,
        messages=[{
            "role": "user",
            "content": [
                {"video": file_url},
                {"text": HUMAN_DETECTION_PROMPT}
            ]
        }]
    )

    result = response.output.choices[0].message.content[0]["text"]

    # Parse JSON response
    data = json.loads(clean_json(result))

    if data.get("unsaveable"):
        return {"status": "unsaveable"}
    else:
        return {
            "status": "clean",
            "start": data["start"],
            "end": data["end"]
        }
```

#### Why This Approach
- **Conservative bias**: Shorter safe clips > risk of humans
- **Local file access**: No need to re-upload clips
- **0.1s precision**: Fine-grained control for accuracy
- **Aggregated processing**: Handles all clips regardless of source video

---

### Step 6.5: Rank All Clips (NEW)

**File**: `firsttrial/steps/step6_5_rank_clips.py`

**Model**: `qwen-vl-max-latest` (VLM actually watches videos)

**Purpose**: Watch each clean clip and rank on 4 quality criteria (0-100 each)

#### Multi-Video Support
- Ranks all clean clips from step 6
- Tracks `video_id` for each clip
- Saves aggregated rankings to `outputs/step6_5_rankings.json`

#### Input
- Step 6 analysis: `outputs/step6_all_clips_analysis.json`
- Raw clip files: `outputs/clips_raw/*.mp4`

#### Output
- `outputs/step6_5_rankings.json`

```json
{
  "total_clips": 25,
  "rankings": [
    {
      "video_id": "video_001",
      "clip_filename": "video_001_clip_03_animation.mp4",
      "clip_path": "outputs/clips_raw/video_001_clip_03_animation.mp4",
      "criteria": {
        "human_visibility_score": 100,
        "human_reasoning": "Zero humans visible throughout entire clip",
        "animation_completeness_score": 95,
        "animation_reasoning": "Box opening animation fully complete with natural ending",
        "reason_match_score": 90,
        "reason_reasoning": "Strongly matches stated reason about product reveal",
        "broll_quality_score": 92,
        "broll_reasoning": "Dynamic animation, clear visuals, engaging for overlay"
      },
      "total_score": 377,
      "normalized_score": 94.25,
      "rank": 1,
      "original_context": {...},
      "optimization_result": {...}
    }
  ]
}
```

#### Ranking Criteria (Complete Rubric)

**1. Human Visibility Score (0-100, higher = better)**
```
100: Zero humans visible throughout entire clip
75:  Humans briefly visible (< 10% of clip) but mostly clean
50:  Humans visible in significant portions (10-40% of clip)
25:  Humans frequently visible (40-70% of clip)
0:   Humans prominent throughout (> 70% of clip)
```

**2. Animation Completeness Score (0-100, higher = better)**
```
100: Animation/action fully complete with natural start and end points
75:  Animation mostly complete with minor abrupt cuts
50:  Animation partially cut but still usable and understandable
25:  Animation severely cut, missing key transitions
0:   Clip mid-action with jarring cuts on both ends
```

**3. Reason Match Score (0-100, higher = better)**
```
100: Clip PERFECTLY represents the stated selection reason
75:  Clip STRONGLY matches reason with minor gaps
50:  Clip SOMEWHAT matches reason but missing some elements
25:  Clip WEAKLY related to stated reason
0:   Clip does NOT match stated reason at all
```

**4. B-Roll Overlay Quality Score (0-100, higher = better)**
```
100: PERFECT for overlay - dynamic, clear, engaging, professional quality
75:  GOOD for overlay - interesting visuals, decent production value
50:  ACCEPTABLE but not ideal - somewhat static, mediocre visual interest
25:  POOR for overlay - very static, unclear, low production value
0:   UNUSABLE for overlay - completely static, boring, or technically flawed
```

#### Complete Ranking Prompt
```python
QWEN_RANKING_PROMPT = """You are an expert video quality analyst for B-roll selection.

Watch this clip and rank it on 4 criteria (0-100 each).

CLIP CONTEXT:
- Description: {description}
- Reason for selection: {reason}
- Original timestamps: {start} → {end}
- Video source: {video_id}

RANKING CRITERIA:

1. HUMAN VISIBILITY SCORE (0-100, higher = better)
   - 100: Zero humans visible throughout entire clip
   - 75: Humans briefly visible (< 10%) but mostly clean
   - 50: Humans in significant portions (10-40%)
   - 25: Humans frequently visible (40-70%)
   - 0: Humans prominent throughout (> 70%)

2. ANIMATION COMPLETENESS SCORE (0-100, higher = better)
   - 100: Animation fully complete, natural start/end
   - 75: Mostly complete with minor cuts
   - 50: Partially cut but usable
   - 25: Severely cut, missing key transitions
   - 0: Mid-action with jarring cuts

3. REASON MATCH SCORE (0-100, higher = better)
   - 100: PERFECTLY represents stated reason
   - 75: STRONGLY matches with minor gaps
   - 50: SOMEWHAT matches but incomplete
   - 25: WEAKLY related to reason
   - 0: Does NOT match reason

4. B-ROLL OVERLAY QUALITY SCORE (0-100, higher = better)
   - 100: PERFECT - dynamic, clear, engaging, professional
   - 75: GOOD - interesting visuals, decent production
   - 50: ACCEPTABLE - somewhat static, mediocre interest
   - 25: POOR - very static, unclear, low value
   - 0: UNUSABLE - static, boring, technically flawed

WATCH THE VIDEO CAREFULLY and output ONLY valid JSON (no markdown):
{{
  "human_visibility_score": 0-100,
  "human_reasoning": "1-2 sentence explanation based on what you saw",
  "animation_completeness_score": 0-100,
  "animation_reasoning": "1-2 sentence explanation",
  "reason_match_score": 0-100,
  "reason_reasoning": "1-2 sentence explanation",
  "broll_quality_score": 0-100,
  "broll_reasoning": "1-2 sentence explanation"
}}

Analyze now.
"""
```

#### Scoring System
```python
# Total score: Sum of 4 criteria
total_score = (human_visibility_score +
               animation_completeness_score +
               reason_match_score +
               broll_quality_score)
# Range: 0-400

# Normalized score: Average of 4 criteria
normalized_score = total_score / 4
# Range: 0-100

# Rank: 1 = highest total score
rankings.sort(key=lambda x: x.total_score, reverse=True)
for i, clip in enumerate(rankings, 1):
    clip.rank = i
```

#### API Call (VLM Watches Video)
```python
def rank_clip(clip_path, context):
    file_url = f"file://{clip_path.absolute()}"

    prompt = QWEN_RANKING_PROMPT.format(
        description=context["description"],
        reason=context["reason"],
        start=context["start"],
        end=context["end"],
        video_id=context["video_id"]
    )

    response = dashscope.MultiModalConversation.call(
        api_key=config.DASHSCOPE_API_KEY,
        model=config.QWEN_VIDEO_MODEL,
        messages=[{
            "role": "user",
            "content": [
                {"video": file_url},
                {"text": prompt}
            ]
        }]
    )

    result = response.output.choices[0].message.content[0]["text"]
    criteria = json.loads(clean_json(result))

    # Calculate scores
    total_score = (criteria["human_visibility_score"] +
                  criteria["animation_completeness_score"] +
                  criteria["reason_match_score"] +
                  criteria["broll_quality_score"])

    return ClipRanking(
        video_id=context["video_id"],
        clip_filename=clip_path.name,
        criteria=criteria,
        total_score=total_score,
        normalized_score=total_score / 4,
        ...
    )
```

#### Why This Approach
- **VLM actually watches**: Not based on metadata, evaluates real visuals
- **Objective criteria**: Detailed rubric prevents arbitrary scoring
- **Reasoning required**: Forces model to explain each score
- **Multiple dimensions**: Captures different aspects of quality
- **Aggregated ranking**: Fair comparison across all source videos

---

### Step 7: Select Top 15 Clips (NEW)

**File**: `firsttrial/steps/step7_select_top15.py`

**Tool**: Pure logic (no AI model)

**Purpose**: Select top 15 highest-scoring clips and copy to dedicated directory

#### Multi-Video Support
- Selects from all ranked clips regardless of source video
- Copies to `outputs/top15/` with ranked filenames

#### Input
- Step 6.5 rankings: `outputs/step6_5_rankings.json`
- Raw clips: `outputs/clips_raw/*.mp4`

#### Output
- Copied clips: `outputs/top15/rank{01-15}_{video_id}_{filename}.mp4`
- Metadata: `outputs/step7_top15.json`

```json
{
  "selection_timestamp": "2025-01-16T10:30:00Z",
  "total_candidates": 25,
  "selected_clips": [
    {
      "rank": 1,
      "video_id": "video_001",
      "original_filename": "video_001_clip_03_animation.mp4",
      "top15_filename": "rank01_video_001_clip_03_animation.mp4",
      "final_path": "outputs/top15/rank01_video_001_clip_03_animation.mp4",
      "total_score": 377,
      "normalized_score": 94.25,
      "ranking_details": {
        "human_visibility_score": 100,
        "animation_completeness_score": 95,
        "reason_match_score": 90,
        "broll_quality_score": 92
      },
      "duration_seconds": 7.5,
      "clean_start": "00:05.0",
      "clean_end": "00:12.5",
      "description": "Box opening animation with product reveal",
      "reason": "Perfect example of smooth transformation"
    }
  ],
  "selection_criteria": "Top 15 clips by total_score (descending)"
}
```

#### Selection Logic
```python
def select_top15():
    # Load rankings (already sorted by total_score descending)
    rankings = load_json(config.STEP6_5_OUTPUT)

    # Take top 15 (or fewer if < 15 available)
    top_clips = rankings["rankings"][:15]

    # Create top15 directory
    config.TOP15_DIR.mkdir(exist_ok=True)

    selected = []
    for rank, clip_data in enumerate(top_clips, 1):
        # Build new filename
        original_path = Path(clip_data["clip_path"])
        new_filename = f"rank{rank:02d}_{original_path.name}"
        dest_path = config.TOP15_DIR / new_filename

        # Copy clip
        shutil.copy2(original_path, dest_path)

        # Extract metadata
        duration = get_duration(dest_path)

        selected.append(Top15Clip(
            rank=rank,
            video_id=clip_data["video_id"],
            original_filename=original_path.name,
            top15_filename=new_filename,
            final_path=str(dest_path),
            total_score=clip_data["total_score"],
            normalized_score=clip_data["normalized_score"],
            ranking_details=clip_data["criteria"],
            duration_seconds=duration,
            clean_start=clip_data["optimization_result"]["clean_start"],
            clean_end=clip_data["optimization_result"]["clean_end"],
            description=clip_data["original_context"]["description"],
            reason=clip_data["original_context"]["reason"]
        ))

    # Save metadata
    output = Top15Selection(
        selection_timestamp=datetime.now().isoformat(),
        total_candidates=len(rankings["rankings"]),
        selected_clips=selected,
        selection_criteria="Top 15 clips by total_score (descending)"
    )

    save_json(output.dict(), config.STEP7_OUTPUT)
```

#### Filename Format
```
rank01_video_001_clip_03_animation.mp4
│     │ │        │       └─ Original description
│     │ │        └─ Original clip number
│     │ └─ Video source ID
│     └─ Rank (01 = best)
└─ Prefix

Examples:
- rank01_video_001_clip_03_Labubu_box_opening.mp4 (Best clip)
- rank02_video_003_clip_12_Apple_Vision_Pro.mp4 (2nd best)
- rank15_video_002_clip_08_UI_interface.mp4 (15th best)
```

#### Why This Approach
- **Pure logic**: No AI bias in final selection
- **Transparent ranking**: Based on objective VLM scores
- **Clear naming**: Rank visible in filename
- **Complete metadata**: All context preserved for step 8
- **Efficient**: No re-processing, just copy top clips

---

### Step 8: Create Remotion Timeline

**File**: `firsttrial/steps/step8_create_timeline.py`

**Model**: `gpt-5-mini-2025-08-07` (Reasoning model)

**Purpose**: Map top 15 b-roll clips to avatar video timestamps based on narration

#### Multi-Video Support
- Uses clips from `outputs/top15/`
- References step 7 metadata for clip details

#### Input
- Step 1 transcription: `outputs/step1_transcription.json`
- Step 7 top15 metadata: `outputs/step7_top15.json`
- Avatar video URL

#### Output
- `outputs/final_timeline.json` (Remotion-compatible format)

```json
{
  "avatarVideo": "https://example.com/avatar.mp4",
  "scenes": [
    {
      "type": "hook",
      "startTime": 0.0,
      "endTime": 3.5,
      "text": "Create Amazing AI Videos",
      "broll": "rank01_video_001_clip_03_animation.mp4"
    },
    {
      "type": "speaking",
      "startTime": 3.5,
      "endTime": 8.2,
      "text": "JSON Prompt Structure",
      "broll": "rank02_video_001_clip_05_JSON_docs.mp4"
    },
    {
      "type": "tutorial",
      "startTime": 8.2,
      "endTime": 15.5,
      "text": "OpenArt Platform Demo",
      "broll": "rank03_video_002_clip_01_OpenArt_UI.mp4"
    }
  ]
}
```

#### Complete Prompt (System + User)
```python
SYSTEM_PROMPT = """You are an expert video editing AI specialized in creating
compelling timelines that match B-roll clips to avatar narration.

Your task is to create a Remotion-compatible timeline JSON that maps available
B-roll clips to the avatar video based on content relevance and narrative flow.

RULES:
1. Match b-roll clips to narration content semantically
2. Use EVERY available b-roll clip if possible (they're pre-ranked by quality)
3. Don't overlap clips - each clip should have its own time segment
4. Keep text overlays SHORT and impactful (3-5 words max)
5. Align timing with natural speech pauses
6. Scene types: "hook" (0-10s), "speaking" (middle), "tutorial" (demos), "cta" (end)

OUTPUT FORMAT:
{
  "avatarVideo": "url",
  "scenes": [
    {
      "type": "hook|speaking|tutorial|cta",
      "startTime": 0.0,
      "endTime": 3.5,
      "text": "SHORT OVERLAY TEXT",
      "broll": "rank01_video_001_clip.mp4"
    }
  ]
}
"""

USER_PROMPT = f"""AVATAR VIDEO: {avatar_url}

TRANSCRIPT (what the avatar says with timestamps):
{format_transcription(transcription)}

AVAILABLE B-ROLL CLIPS (ranked 1-15 by quality):
{format_clips(top15_clips)}

Each clip includes:
- Rank (1 = best)
- Video source
- Duration
- Clean timestamps (safe portions without humans)
- Description (what's shown)
- Reason (why it was selected)
- Quality scores (human visibility, animation, match, broll quality)

CREATE TIMELINE JSON:
- Map each b-roll clip to appropriate avatar timestamp
- Match clip content with what's being discussed
- Prioritize higher-ranked clips for important moments
- Use clip durations wisely (don't force fit)
- Add impactful text overlays
- Ensure smooth narrative flow

Output valid JSON only (no markdown).
"""
```

#### API Call (Responses API)
```python
from openai import OpenAI

client = OpenAI(api_key=config.OPENAI_API_KEY)

response = client.responses.create(
    model="gpt-5-mini-2025-08-07",
    input=f"{SYSTEM_PROMPT}\n\n{USER_PROMPT}",
    reasoning={
        "effort": config.GPT5_REASONING_EFFORT  # "medium"
    },
    text={
        "verbosity": "medium"  # Need more detail for timeline
    }
)

timeline_json = json.loads(clean_json(response.output_text))
```

#### Why GPT-5 for This Task
- **Semantic understanding**: Matches clips to narration meaning (not just keywords)
- **Reasoning capability**: Plans narrative flow across entire video
- **Context awareness**: Considers clip rankings, durations, and descriptions
- **Structured output**: Reliable JSON generation with complex nested structure

---

## SDK Integrations

### DashScope SDK (Alibaba Qwen)

**Package**: `dashscope`

**Installation**:
```bash
pip install dashscope
```

**Configuration**:
```python
import dashscope

# Set international endpoint
dashscope.base_http_api_url = 'https://dashscope-intl.aliyuncs.com/api/v1'
```

#### Pattern 1: MultiModalConversation.call() (Steps 2, 4, 6, 6.5)

**Usage**: Video analysis with vision-language models

```python
response = dashscope.MultiModalConversation.call(
    api_key=DASHSCOPE_API_KEY,
    model='qwen-vl-max-latest',
    messages=[{
        "role": "user",
        "content": [
            {"video": video_url},  # URL or file://path
            {"text": prompt_text}
        ]
    }]
)

# Extract response
result_text = response.output.choices[0].message.content[0]["text"]

# Extract reasoning (if thinking model)
reasoning = response.output.choices[0].message.reasoning_content
```

**Supported video sources**:
- Public URLs: `"https://example.com/video.mp4"`
- Local files: `"file:///absolute/path/to/video.mp4"`

#### Pattern 2: OpenAI-Compatible API (Step 1 - Streaming)

**Usage**: Audio transcription with streaming

```python
from openai import OpenAI

client = OpenAI(
    api_key=DASHSCOPE_API_KEY,
    base_url="https://dashscope-intl.aliyuncs.com/compatible-mode/v1"
)

completion = client.chat.completions.create(
    model="qwen3-omni-flash",
    messages=[{
        "role": "user",
        "content": [
            {"type": "video_url", "video_url": {"url": video_url}},
            {"type": "text", "text": prompt_text}
        ]
    }],
    modalities=["text"],  # Or ["text", "audio"]
    stream=True,
    stream_options={"include_usage": True}
)

# Stream response
result = ""
for chunk in completion:
    if chunk.choices and chunk.choices[0].delta.content:
        result += chunk.choices[0].delta.content
        print(chunk.choices[0].delta.content, end="", flush=True)

    # Usage stats in final chunk
    if chunk.usage:
        print(f"\nTokens used: {chunk.usage.total_tokens}")
```

#### Error Handling with Retries

```python
def call_with_retry(api_func, max_retries=3):
    for attempt in range(max_retries):
        try:
            return api_func()
        except Exception as e:
            if attempt < max_retries - 1:
                wait = 2 ** attempt  # Exponential backoff: 1s, 2s, 4s
                print(f"Retry {attempt + 1}/{max_retries} after {wait}s...")
                time.sleep(wait)
            else:
                raise

# Usage
result = call_with_retry(lambda: analyze_video(url, prompt))
```

---

### OpenAI SDK (GPT-5)

**Package**: `openai`

**Installation**:
```bash
pip install openai
```

#### Responses API (Steps 3, 8)

**Usage**: Extended reasoning tasks with controlled output

```python
from openai import OpenAI

client = OpenAI(api_key=OPENAI_API_KEY)

response = client.responses.create(
    model="gpt-5-mini-2025-08-07",
    input=prompt_text,
    reasoning={
        "effort": "medium"  # low / medium / high
    },
    text={
        "verbosity": "low"  # low / medium / high
    }
)

output = response.output_text
```

**Reasoning Effort Levels**:
- `"low"`: Quick, straightforward reasoning (faster, cheaper)
- `"medium"`: Balanced reasoning (default)
- `"high"`: Deep, thorough reasoning (slower, more expensive)

**Text Verbosity Levels**:
- `"low"`: Concise output (2-4 sentences)
- `"medium"`: Moderate detail (default)
- `"high"`: Comprehensive explanation

**Why Responses API?**
- Designed for reasoning tasks (not chat)
- Controlled output length
- More reliable structured output
- Better for prompt generation and timeline planning

#### Chat Completions API (Alternative)

**Usage**: Standard conversational interface

```python
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ],
    temperature=0.7
)

output = response.choices[0].message.content
```

---

### FFmpeg Integration

**Installation**:
```bash
# Ubuntu/Debian
sudo apt install ffmpeg

# macOS
brew install ffmpeg

# Verify
ffmpeg -version
ffprobe -version
```

#### Video Cutting (Step 5)

**Command Structure**:
```bash
ffmpeg -hide_banner -y \
  -i input.mp4 \
  -ss START_TIME \
  -to END_TIME \
  -c:v libx264 -preset ultrafast -crf 18 \
  -c:a aac \
  -movflags +faststart \
  output.mp4
```

**Parameter Explanation**:

| Parameter | Purpose |
|-----------|---------|
| `-hide_banner` | Clean output (no build info) |
| `-y` | Overwrite existing files |
| `-i input.mp4` | Input file |
| `-ss START` | Start time (AFTER -i for accuracy) |
| `-to END` | End time (absolute timestamp) |
| `-c:v libx264` | Video codec (H.264 re-encode) |
| `-preset ultrafast` | Encoding speed preset |
| `-crf 18` | Quality (18 = high quality, 0-51 range) |
| `-c:a aac` | Audio codec |
| `-movflags +faststart` | Web optimization (moov atom at start) |

**Why Placement Matters**:
```bash
# SLOW but ACCURATE (used in pipeline)
ffmpeg -i input.mp4 -ss 00:05 -to 00:12 output.mp4
# Decodes from start, then seeks to 00:05

# FAST but INACCURATE
ffmpeg -ss 00:05 -i input.mp4 -to 00:07 output.mp4
# Seeks first (fast), but imprecise due to keyframes
```

**Pipeline uses accurate method** to ensure pixel-perfect timestamps.

#### Duration Extraction

```bash
ffprobe -v error \
  -show_entries format=duration \
  -of default=noprint_wrappers=1:nokey=1 \
  video.mp4
```

**Python Wrapper**:
```python
import subprocess

def get_duration(video_path):
    result = subprocess.run([
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        str(video_path)
    ], capture_output=True, text=True, check=True)

    return float(result.stdout.strip())
```

---

## Prompt Engineering

### Technique 1: Structured Output Format

**Used in**: Step 1 (Transcription)

**Strategy**: Provide exact output format with clear constraints

```python
prompt = """Extract EVERY SENTENCE with exact timestamps.

Output ONLY valid JSON in this exact format:
{
  "sentences": [
    {"start": "MM:SS", "end": "MM:SS", "text": "..."},
    {"start": "MM:SS", "end": "MM:SS", "text": "..."}
  ]
}

Requirements:
- Each sentence = separate entry
- MM:SS format (e.g., "00:05", "02:30")
- Exact words spoken
- ALL sentences (start to end)
- Chronological order
- NO markdown formatting
"""
```

**Why it works**:
- Clear format reduces ambiguity
- Explicit constraints prevent common mistakes
- "ONLY valid JSON" prevents markdown wrapping
- Example format guides model output

---

### Technique 2: Complete Coverage Instruction

**Used in**: Step 2 (Screen Analysis)

**Strategy**: Emphasize ENTIRE timeline coverage (no gaps)

```python
prompt = """Analyze this ENTIRE video from start to finish.

IMPORTANT:
- Start from 00:00 and cover the ENTIRE video timeline to the end
- Include ALL segments (even those with humans)
- For each segment, describe what's SHOWN ON SCREEN
- Keep descriptions focused (under 15 words)
- Segment every 10-20 seconds
"""
```

**Why it works**:
- "ENTIRE video" repeated 3 times (emphasis)
- Explicit start point (00:00)
- Permission to include all content (filtering happens later)
- Length constraint (15 words) keeps output concise

---

### Technique 3: Constrained Generation with Examples

**Used in**: Step 3 (GPT-5 Prompt Crafting)

**Strategy**: Meta-prompt with strict constraints + concrete example

```python
system_prompt = """Create SHORT, FOCUSED prompt for VLM.

CRITICAL CONSTRAINTS:
- 2-4 sentences MAXIMUM
- NEVER mention: "speech", "audio", "narrator", "avatar"
- ONLY reference: visual elements
- VLM has NO ACCESS to audio
- MUST instruct: analyze ENTIRE video, rank, return TOP clips

EXAMPLE OUTPUT:
"Analyze COMPLETE video (00:00 to end). Find ALL: JSON documents,
OpenArt UI, animations (Labubu, Tom&Jerry), products (Apple, Ferrari).
Rank by quality. Select TOP 15-20 across timeline. Focus: 00:00-00:10,
01:20-02:00. NO HUMANS. JSON format."

Output ONLY the prompt.
"""
```

**Why it works**:
- Hard limit (2-4 sentences) prevents verbosity
- Forbidden words list prevents common mistake
- Concrete example shows desired style
- Explicit reminder (VLM can't hear) prevents audio references

---

### Technique 4: Conservative Safety Instruction

**Used in**: Step 6 (Human Detection)

**Strategy**: Strong bias toward safety with explicit trade-offs

```python
prompt = """BE EXTREMELY CONSERVATIVE. Find portions with ZERO humans.

IMPORTANT:
- Better to return SHORTER clips with NO humans than risk including one
- If you see ANY human face, body part, silhouette - EXCLUDE it
- Even brief appearances (1 frame) → exclude
- If uncertain whether something is human → exclude to be safe

Output safest continuous segment with 0.1s precision:
{"start": "MM:SS.S", "end": "MM:SS.S"}

Or if humans throughout:
{"unsaveable": true}
"""
```

**Why it works**:
- "EXTREMELY CONSERVATIVE" sets strong bias
- Explicit trade-off (shorter > risk) guides decisions
- Multiple examples of what counts as human
- "If uncertain" clause handles edge cases
- Structured output for easy parsing

---

### Technique 5: Detailed Rubric with Anchors

**Used in**: Step 6.5 (VLM Ranking)

**Strategy**: Provide detailed scoring rubric with 5 anchor points per criterion

```python
prompt = """Rank this clip on 4 criteria (0-100 each).

CRITERION 1: HUMAN VISIBILITY (higher = better)
- 100: Zero humans visible throughout entire clip
- 75:  Humans briefly visible (< 10%) but mostly clean
- 50:  Humans in significant portions (10-40%)
- 25:  Humans frequently visible (40-70%)
- 0:   Humans prominent throughout (> 70%)

[3 more detailed rubrics...]

WATCH THE VIDEO and output JSON:
{
  "human_visibility_score": 0-100,
  "human_reasoning": "1-2 sentence explanation",
  ...
}
"""
```

**Why it works**:
- 5 anchor points prevent arbitrary scoring
- Concrete descriptions at each level
- Percentages provide objective thresholds
- Reasoning required for each score (accountability)
- "WATCH THE VIDEO" emphasizes actual analysis

---

### Technique 6: Complete Context + Structured Output

**Used in**: Step 8 (Timeline Creation)

**Strategy**: Provide ALL context + clear rules + desired format

```python
prompt = f"""Create timeline mapping b-roll to avatar narration.

TRANSCRIPT:
{full_transcript}

AVAILABLE CLIPS (ranked 1-15):
{detailed_clip_info}

RULES:
1. Match clips to narration content semantically
2. Use EVERY clip if possible
3. Don't overlap clips
4. Short text overlays (3-5 words)
5. Align with speech pauses

OUTPUT:
{{
  "avatarVideo": "url",
  "scenes": [
    {{"type": "hook|speaking|tutorial|cta",
      "startTime": 0.0, "endTime": 3.5,
      "text": "OVERLAY", "broll": "rank01_clip.mp4"}}
  ]
}}
"""
```

**Why it works**:
- Complete context (transcript + clips) enables semantic matching
- Clear rules guide decisions
- Ranking info helps model prioritize
- Structured format ensures valid output
- Scene types provide narrative structure

---

## Data Schemas

All data models defined in `firsttrial/schemas/schemas.py` using Pydantic for validation.

### TranscriptionOutput
```python
class Sentence(BaseModel):
    start: str      # MM:SS format
    end: str        # MM:SS format
    text: str       # Transcribed sentence

class TranscriptionOutput(BaseModel):
    sentences: List[Sentence]
```

### ScreenAnalysisOutput
```python
class ScreenActivity(BaseModel):
    start: str             # MM:SS format
    end: str               # MM:SS format
    description: str       # What's on screen
    activity_type: str     # "demo", "ui", "animation", etc.

class ScreenAnalysisOutput(BaseModel):
    activities: List[ScreenActivity]
```

### TargetedAnalysisOutput
```python
class SceneSelection(BaseModel):
    start: str          # MM:SS format
    end: str            # MM:SS format
    description: str    # Scene description
    reason: str         # Why selected

class TargetedAnalysisOutput(BaseModel):
    scenes: List[SceneSelection]
```

### ClipsMetadataOutput
```python
class ClipMetadata(BaseModel):
    clip_number: int
    filename: str
    start: str           # MM:SS format
    end: str             # MM:SS format
    description: str
    reason: str
    video_id: str        # Source video identifier

class ClipsMetadataOutput(BaseModel):
    source_video: str
    clips: List[ClipMetadata]
```

### OptimizationOutput
```python
class HumanDetection(BaseModel):
    source_filename: str
    output_filename: Optional[str]
    status: Literal["clean", "unsaveable", "failed"]
    clean_start: Optional[str]  # MM:SS.S format
    clean_end: Optional[str]    # MM:SS.S format
    attempts: int
    final_result: Literal["none", "start", "end", "all"]
    video_id: str
    original_context: dict      # From step 5

class OptimizationOutput(BaseModel):
    clips: List[HumanDetection]
```

### RankingsOutput
```python
class ClipRankingCriteria(BaseModel):
    # Scores 0-100 each
    human_visibility_score: int
    animation_completeness_score: int
    reason_match_score: int
    broll_quality_score: int

    # Reasoning for each score
    human_reasoning: str
    animation_reasoning: str
    reason_reasoning: str
    broll_reasoning: str

class ClipRanking(BaseModel):
    video_id: str
    clip_filename: str
    clip_path: str
    criteria: ClipRankingCriteria
    total_score: int            # Sum of 4 scores (0-400)
    normalized_score: float     # 0-100
    rank: int                   # 1 = best
    original_context: dict      # From step 5
    optimization_result: dict   # From step 6

class RankingsOutput(BaseModel):
    total_clips: int
    rankings: List[ClipRanking]  # Sorted by total_score descending
```

### Top15Selection
```python
class Top15Clip(BaseModel):
    rank: int                    # 1-15
    video_id: str
    original_filename: str
    top15_filename: str
    final_path: str
    total_score: int             # 0-400
    normalized_score: float      # 0-100
    ranking_details: ClipRankingCriteria
    duration_seconds: float
    clean_start: str             # MM:SS.S format
    clean_end: str
    description: str
    reason: str

class Top15Selection(BaseModel):
    selection_timestamp: str
    total_candidates: int
    selected_clips: List[Top15Clip]
    selection_criteria: str
```

### VideosConfig
```python
class VideoConfig(BaseModel):
    id: str          # e.g., "video_001"
    name: str
    url: str         # For VLM API
    local_path: str  # For FFmpeg
    priority: int = 1

class VideosConfig(BaseModel):
    videos: List[VideoConfig]
```

---

## File Structure

```
firsttrial/
├── config.py                           # Central configuration
├── videos_config.json                  # Multi-video sources
├── .env                                # API keys (not in git)
│
├── schemas/
│   ├── __init__.py
│   └── schemas.py                      # Pydantic data models
│
├── steps/
│   ├── __init__.py
│   ├── step1_transcribe_avatar.py      # Audio → Sentences
│   ├── step2_analyze_screen.py         # Video → Activities
│   ├── step3_craft_prompt.py           # GPT-5 → Prompt
│   ├── step4_targeted_analysis.py      # VLM → Scenes
│   ├── step5_cut_clips.py              # FFmpeg → Clips
│   ├── step6_optimize_clips_omni.py    # VLM → Human Detection
│   ├── step6_5_rank_clips.py           # VLM → Rankings (NEW)
│   ├── step7_select_top15.py           # Logic → Top15 (NEW)
│   └── step8_create_timeline.py        # GPT-5 → Timeline
│
├── utils/
│   ├── api_clients.py                  # QwenClient, OpenAIClient
│   ├── json_utils.py                   # JSON parsing/cleaning
│   └── video_utils.py                  # FFmpeg wrappers
│
├── run.py                              # Interactive menu
├── run_remaining_steps.py              # Quick runner (steps 6.5-8)
│
└── outputs/
    ├── step1_transcription.json        # Avatar transcription
    │
    ├── video_001/                      # Per-video outputs
    │   ├── step2_screen_analysis.json
    │   ├── step2_screen_analysis_reasoning.txt
    │   ├── step3_generated_prompt.txt
    │   ├── step4_scene_selection.json
    │   └── clips_metadata.json
    │
    ├── video_002/                      # Another video
    │   └── ...
    │
    ├── clips_raw/                      # All raw clips
    │   ├── video_001_clip_01_description.mp4
    │   ├── video_001_clip_02_description.mp4
    │   ├── video_002_clip_01_description.mp4
    │   └── ...
    │
    ├── step6_all_clips_analysis.json   # Human detection (all clips)
    ├── step6_5_rankings.json            # VLM rankings (all clips)
    ├── step7_top15.json                 # Top 15 metadata
    │
    ├── top15/                           # Final selected clips
    │   ├── rank01_video_001_clip_03.mp4
    │   ├── rank02_video_003_clip_12.mp4
    │   └── ...
    │
    └── final_timeline.json              # Remotion timeline
```

---

## Execution Guide

### Setup

1. **Install dependencies**:
```bash
pip install dashscope openai pydantic python-dotenv
sudo apt install ffmpeg  # or brew install ffmpeg
```

2. **Configure API keys**:
```bash
cp .env.example .env
nano .env  # Add your keys
```

3. **Configure videos**:
```bash
nano videos_config.json  # Add your demo videos
```

### Running the Pipeline

#### Interactive Mode (Recommended)
```bash
cd firsttrial
python run.py
```

**Menu options**:
- `1-8`: Run individual steps
- `5.5`: Preprocess clips (if needed)
- `6.5`: Rank clips with VLM
- `7`: Select top 15
- `A`: Run all steps (complete pipeline)
- `M`: Run multi-video pipeline
- `C`: Show configuration
- `Q`: Quit

#### Multi-Video Pipeline
```bash
python run.py
# Select option: M
```

**What it does**:
1. Transcribe avatar (once)
2. Process each video (steps 2-5 per video)
3. Aggregate all clips
4. Rank all clips (step 6.5)
5. Select top 15 (step 7)
6. Generate timeline (step 8)

#### Quick Resume (Steps 6.5-8)
```bash
# After completing steps 1-6
python run_remaining_steps.py
```

**Use case**: You've processed all videos and cut all clips, now want to rank and select top 15.

### Output Files

**After step 1**:
- `outputs/step1_transcription.json` - Avatar sentences

**After steps 2-5** (per video):
- `outputs/video_001/step2_screen_analysis.json` - Screen activities
- `outputs/video_001/step3_generated_prompt.txt` - GPT-5 prompt
- `outputs/video_001/step4_scene_selection.json` - Selected scenes
- `outputs/video_001/clips_metadata.json` - Clip metadata
- `outputs/clips_raw/video_001_clip_*.mp4` - Raw clips

**After step 6**:
- `outputs/step6_all_clips_analysis.json` - Human detection (all clips)

**After step 6.5**:
- `outputs/step6_5_rankings.json` - VLM rankings (all clips)

**After step 7**:
- `outputs/step7_top15.json` - Top 15 metadata
- `outputs/top15/rank01_*.mp4` - Top 15 clips (copied)

**After step 8**:
- `outputs/final_timeline.json` - Remotion timeline

### Troubleshooting

**API errors**:
- Check API keys in `.env`
- Verify DashScope endpoint is accessible
- Check video URLs are publicly accessible

**FFmpeg errors**:
- Verify FFmpeg is installed: `ffmpeg -version`
- Check video file paths exist
- Ensure sufficient disk space

**JSON parsing errors**:
- Check `*_reasoning.txt` files for model thinking
- Enable verbose output in config
- Review prompts for clarity

**Poor clip selection**:
- Review step 3 generated prompt (manual checkpoint)
- Adjust GPT-5 reasoning effort (config)
- Check step 2 screen analysis coverage

---

## Summary

This pipeline combines multiple AI models (Qwen VL, GPT-5) with traditional tools (FFmpeg) to create an intelligent, multi-video B-roll extraction system. Key innovations:

1. **Multi-video processing**: Process multiple source videos in parallel
2. **VLM-based ranking**: Objective quality scores (4 criteria, 0-400 total)
3. **Two-stage prompting**: GPT-5 crafts optimal prompts for VLM
4. **Conservative safety**: Human detection with fine-grained timestamps
5. **Complete automation**: End-to-end pipeline with quality assurance

The system is designed for scalability (handle many videos), quality (VLM watches every clip), and maintainability (Pydantic schemas, centralized config, modular steps).

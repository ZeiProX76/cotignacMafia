# Video Clip Extraction Pipeline

## What We're Doing

Extract short, high-quality clips from a video showing screen demos/animations **without any visible humans**. Perfect for creating promotional content from tutorial videos.

## How It Works

### The Goal
Input: A video with someone talking (avatar) + screen content being shown
Output: Clean 10-30 second clips showing only screen activities, no humans

### The Process

---

## Step 1: Transcribe Avatar Audio
**What**: Listen to what the presenter is saying
**How**: Qwen3-Omni-Flash analyzes audio
**Output**: List of sentences with timestamps

```json
{
  "sentences": [
    {"start": "00:15", "end": "00:23", "text": "Now let me show you the dashboard"}
  ]
}
```

---

## Step 2: Analyze Screen Content
**What**: Identify what's shown on screen in 20-second segments
**How**: Qwen3-VL-32B scans video visually
**Output**: Screen activities with timestamps (excluding any human appearances)

```json
{
  "activities": [
    {"start": "00:20", "end": "00:40", "description": "Dashboard animation", "activity_type": "demo"}
  ]
}
```

---

## Step 3: Craft Smart Prompt
**What**: Combine transcription + screen data to create precise instructions
**How**: GPT-5 reasoning model writes a targeted prompt
**Output**: A prompt that tells the video AI exactly what clips to extract

```text
"Extract 6-10 product demo clips showing UI interactions and animations.
Focus on moments at 00:15-00:30, 01:05-01:20 where features are demonstrated.
NO HUMANS VISIBLE. Output JSON with timestamps."
```

**Note**: Pipeline pauses here for manual review/approval of the prompt.

---

## Step 4: Extract Scene Selections
**What**: Use the smart prompt to select the best clips
**How**: Qwen3-VL-32B analyzes video with the crafted prompt
**Output**: Precise scene selections

```json
{
  "scenes": [
    {
      "start": "00:15",
      "end": "00:30",
      "description": "Dashboard loading animation",
      "reason": "Shows key UI feature"
    }
  ]
}
```

---

## Step 5: Cut Video Clips
**What**: Extract the selected scenes from the video file
**How**: FFmpeg cuts clips based on timestamps
**Output**: Multiple .mp4 files in `clips_raw/`

```
clips_raw/
  ├── clip_01_dashboard_loading.mp4
  ├── clip_02_menu_interaction.mp4
  └── clip_03_animation_demo.mp4
```

---

## Step 6: Detect Humans
**What**: Check each clip for visible humans at start/end
**How**: Qwen3-VL-32B analyzes first/last few seconds of each clip
**Output**: Human detection results

```json
{
  "clips": [
    {"source_filename": "clip_01.mp4", "human_at": "none"},
    {"source_filename": "clip_02.mp4", "human_at": "start", "timestamp": "00:01"}
  ]
}
```

---

## Step 7: Filter Final Clips
**What**: Keep only clips with no humans visible
**How**: Copy clean clips to final directory
**Output**: Final clean clips in `clips_final/`

```
clips_final/
  ├── clip_01_clean.mp4  ✓ (no human)
  └── filtering_summary.json
```

---

## Quick Start

```bash
# Install dependencies
cd firsttrial
pip install -r requirements.txt

# Set up API keys in .env
DASHSCOPE_API_KEY=your_key
OPENAI_API_KEY=your_key

# Run interactive pipeline
python run.py
```

Choose option **A** to run the complete pipeline.

---

## Key Files

- `config.py` - All settings (video URLs, API keys, models)
- `run.py` - Interactive menu to run steps
- `steps/step*.py` - Individual pipeline steps
- `outputs/` - All generated files
- `clips_final/` - Your final clean clips

---

## The Models

| Step | Model | Purpose |
|------|-------|---------|
| 1 | Qwen3-Omni-Flash | Audio transcription (fast) |
| 2, 4, 6 | Qwen3-VL-32B-Thinking | Video understanding (accurate) |
| 3 | GPT-5 | Prompt engineering (smart) |
| 5, 7 | FFmpeg | Video cutting (standard) |

---

## Common Issues

**No clips in final output?**
- Check if humans were detected in all clips (step 6)
- Review optimization results in `step6_optimization.json`

**API errors?**
- Verify `.env` has correct API keys
- Check API quotas/limits

**FFmpeg errors?**
- Ensure FFmpeg is installed: `ffmpeg -version`
- Update `MAIN_VIDEO_LOCAL` path in config.py

---

## What Makes This Smart

1. **Two-pass analysis**: First understand the video broadly (steps 1-2), then target precisely (step 4)
2. **AI-crafted prompts**: GPT-5 writes better prompts than humans for video extraction
3. **Automatic filtering**: No manual review of clips - AI detects humans automatically
4. **Validation**: Every output is validated with Pydantic schemas for reliability

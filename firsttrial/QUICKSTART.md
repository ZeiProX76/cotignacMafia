# Quick Start Guide

Get up and running with the Video Analysis Pipeline in 5 minutes.

## Prerequisites

- Python 3.8+
- FFmpeg installed
- DashScope API key (Alibaba Cloud)
- OpenAI API key

## Installation

### 1. Install Python Dependencies

```bash
cd firsttrial
pip install -r requirements.txt
```

### 2. Install FFmpeg

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install ffmpeg
```

**macOS:**
```bash
brew install ffmpeg
```

**Verify:**
```bash
ffmpeg -version
```

### 3. Configure API Keys

The `.env` file should already exist. If not, create it:

```bash
# In firsttrial directory
cat > .env << EOF
DASHSCOPE_API_KEY=your_dashscope_key_here
OPENAI_API_KEY=your_openai_key_here
EOF
```

Replace `your_dashscope_key_here` and `your_openai_key_here` with your actual API keys.

## First Run

### Option 1: Interactive Mode (Recommended)

```bash
cd firsttrial
python run.py
```

You'll see a menu:
```
VIDEO ANALYSIS PIPELINE
============================================================

Available steps:

  1. Transcribe avatar audio (Step 1)
  2. Analyze screen activities (Step 2)
  3. Craft prompt with GPT-5 (Step 3)
  4. Run targeted analysis (Step 4)
  5. Cut video clips (Step 5)
  6. Optimize clips (detect humans) (Step 6)
  7. Apply optimization (filter clips) (Step 7)

  A. Run ALL steps (complete pipeline)
  C. Show configuration
  Q. Quit

Select option:
```

**For first run**: Type `A` and press Enter to run the complete pipeline.

### Option 2: Run Steps Individually

```bash
# Step 1: Transcribe avatar
python steps/step1_transcribe_avatar.py

# Step 2: Analyze screen
python steps/step2_analyze_screen.py

# Step 3: Generate prompt (will pause for review)
python steps/step3_craft_prompt.py

# Step 4: Extract scenes
python steps/step4_targeted_analysis.py

# Step 5: Cut clips
python steps/step5_cut_clips.py

# Step 6: Detect humans
python steps/step6_optimize_clips.py

# Step 7: Filter clips
python steps/step7_apply_optimization.py
```

## Understanding the Workflow

```
Avatar Video → [Step 1] → Transcription (sentences with timestamps)
                              ↓
Main Video → [Step 2] → Screen Analysis (activities, no humans)
                              ↓
          [Step 3] → GPT-5 crafts precise prompt ⚠️ REVIEW CHECKPOINT
                              ↓
Main Video → [Step 4] → Targeted scene selection
                              ↓
          [Step 5] → Cut clips from video
                              ↓
          [Step 6] → Detect humans in clips
                              ↓
          [Step 7] → Filter out clips with humans
                              ↓
                  Final clean clips in outputs/clips_final/
```

## Important Notes

### Step 3: Manual Review Checkpoint

When you reach Step 3, the pipeline will **pause** and show you the GPT-5 generated prompt:

```
============================================================
MANUAL REVIEW CHECKPOINT
============================================================
Please review the generated prompt above.
You can edit it at: /path/to/outputs/step3_generated_prompt.txt

Continue with this prompt? [y/N]:
```

- Review the prompt carefully
- If you want to edit it, open the file and make changes
- Type `y` to continue, or `N` to stop and edit manually

### Video Sources

By default, the pipeline uses these videos (configured in `config.py`):

- **Avatar video**: `https://efuozhjlnyrcyritksiy.supabase.co/storage/v1/object/public/cotignac/InfiniteTalk_00005-audio.mp4`
- **Main video**: `https://efuozhjlnyrcyritksiy.supabase.co/storage/v1/object/public/cotignac/videoplayback%20(3).mp4`

To use your own videos, edit `config.py`:

```python
AVATAR_VIDEO_URL = "https://your-avatar-video.mp4"
MAIN_VIDEO_URL = "https://your-main-video.mp4"
MAIN_VIDEO_LOCAL = "/path/to/your/local/video.mp4"
```

## Expected Output

After running the complete pipeline, you'll find:

```
outputs/
├── step1_transcription.json          # Sentence-level transcription
├── step2_screen_analysis.json        # Screen activities
├── step3_generated_prompt.txt        # GPT-5 crafted prompt
├── step4_scene_selection.json        # Selected scenes
├── step6_optimization.json           # Human detection results
├── clips_raw/                        # Raw cut clips
│   ├── clip_01_*.mp4
│   ├── clip_02_*.mp4
│   └── clips_metadata.json
└── clips_final/                      # 🎬 FINAL CLEAN CLIPS
    ├── clip_01_*_clean.mp4
    ├── clip_02_*_clean.mp4
    └── filtering_summary.json
```

## Troubleshooting

### "DASHSCOPE_API_KEY not found"

**Solution**: Make sure `.env` file exists in `firsttrial/` directory with your API keys.

```bash
cd firsttrial
cat .env  # Should show your keys
```

### "Video file not found"

**Solution**: Update the local video path in `config.py`:

```python
MAIN_VIDEO_LOCAL = "/correct/path/to/your/video.mp4"
```

### "FFmpeg not found"

**Solution**: Install FFmpeg (see Installation section above)

### API Rate Limits

If you hit rate limits, wait a few minutes and resume from the last completed step using the interactive menu.

## Next Steps

- Review the [README.md](README.md) for detailed documentation
- Explore individual step files in `steps/` directory
- Customize prompts and models in `config.py`
- Use as a library in your own scripts

## Support

For issues, check the full [README.md](README.md) or contact the development team.

# Video Analysis Pipeline

A sophisticated, multi-stage pipeline for analyzing videos, transcribing audio, and extracting high-quality clips automatically using AI models (Qwen VL, GPT-5).

## Features

- **Sentence-level audio transcription** with precise timestamps
- **Screen activity detection** (excluding visible humans)
- **AI-powered prompt generation** using GPT-5 reasoning
- **Targeted video clip extraction** based on crafted prompts
- **Automatic human presence detection** and filtering
- **Clean, modular architecture** with validation
- **Interactive CLI** with step-by-step control

## Architecture

```
firsttrial/
├── run.py                     # Interactive orchestrator
├── config.py                  # Centralized configuration
├── requirements.txt           # Python dependencies
├── .env                      # API keys (gitignored)
│
├── steps/                    # Pipeline steps (7 total)
│   ├── step1_transcribe_avatar.py
│   ├── step2_analyze_screen.py
│   ├── step3_craft_prompt.py
│   ├── step4_targeted_analysis.py
│   ├── step5_cut_clips.py
│   ├── step6_optimize_clips.py
│   └── step7_apply_optimization.py
│
├── utils/                    # Reusable utilities
│   ├── api_clients.py       # Qwen & OpenAI wrappers
│   ├── video_utils.py       # FFmpeg helpers
│   └── json_utils.py        # JSON parsing/validation
│
├── schemas/                  # Pydantic data models
│   └── schemas.py
│
└── outputs/                  # Generated files
    ├── step1_transcription.json
    ├── step2_screen_analysis.json
    ├── step3_generated_prompt.txt
    ├── step4_scene_selection.json
    ├── clips_raw/           # Cut clips
    ├── clips_optimized/     # (reserved)
    └── clips_final/         # Final filtered clips
```

## Pipeline Workflow

### Step 1: Transcribe Avatar Audio
- **Model**: Qwen3-Omni-Flash (audio-aware)
- **Input**: Avatar video URL
- **Output**: `step1_transcription.json`
- **Purpose**: Extract every sentence with start/end timestamps

### Step 2: Analyze Screen Activities
- **Model**: Qwen3-VL-32B-Thinking
- **Input**: Main video URL
- **Output**: `step2_screen_analysis.json`
- **Purpose**: Detect all screen activities (excluding visible humans)

### Step 3: Craft Prompt with GPT-5
- **Model**: GPT-5 with reasoning
- **Input**: Transcription + Screen analysis
- **Output**: `step3_generated_prompt.txt`
- **Purpose**: Generate ultra-precise prompt for clip selection
- **Note**: Pauses for manual review/approval

### Step 4: Targeted Analysis
- **Model**: Qwen3-VL-32B-Thinking
- **Input**: Main video + crafted prompt
- **Output**: `step4_scene_selection.json`
- **Purpose**: Extract precise scenes based on GPT-5 prompt

### Step 5: Cut Video Clips
- **Tool**: FFmpeg
- **Input**: Local video + scene selections
- **Output**: `clips_raw/*.mp4` + metadata
- **Purpose**: Cut selected clips from source video

### Step 6: Optimize Clips
- **Model**: Qwen3-VL-32B-Thinking
- **Input**: Cut clips
- **Output**: `step6_optimization.json`
- **Purpose**: Detect human presence in each clip

### Step 7: Apply Optimization
- **Tool**: Python file operations
- **Input**: Optimization results
- **Output**: `clips_final/*.mp4`
- **Purpose**: Filter out clips with visible humans

## Setup

### 1. Install Dependencies

```bash
cd firsttrial
pip install -r requirements.txt
```

### 2. Install FFmpeg

```bash
# Ubuntu/Debian
sudo apt-get install ffmpeg

# macOS
brew install ffmpeg

# Verify installation
ffmpeg -version
```

### 3. Configure API Keys

Create a `.env` file:

```bash
DASHSCOPE_API_KEY=your_dashscope_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
```

### 4. Update Video Paths (Optional)

Edit `config.py` to set your video URLs/paths:

```python
AVATAR_VIDEO_URL = "https://your-avatar-video-url.mp4"
MAIN_VIDEO_URL = "https://your-main-video-url.mp4"
MAIN_VIDEO_LOCAL = "/path/to/local/video.mp4"
```

## Usage

### Interactive Mode (Recommended)

```bash
cd firsttrial
python run.py
```

This opens an interactive menu where you can:
- Run individual steps (1-7)
- Run the complete pipeline (A)
- View configuration (C)
- Quit (Q)

### Run Individual Steps

```bash
# Step 1: Transcribe audio
python steps/step1_transcribe_avatar.py

# Step 2: Analyze screen
python steps/step2_analyze_screen.py

# Step 3: Craft prompt (with review)
python steps/step3_craft_prompt.py

# Step 4: Targeted analysis
python steps/step4_targeted_analysis.py

# Step 5: Cut clips
python steps/step5_cut_clips.py

# Step 6: Optimize clips
python steps/step6_optimize_clips.py

# Step 7: Apply optimization
python steps/step7_apply_optimization.py
```

### Run as Library

```python
from steps import (
    transcribe_avatar,
    analyze_screen,
    craft_prompt,
    targeted_analysis,
    cut_clips,
    optimize_clips,
    apply_optimization
)

# Run step 1
result = transcribe_avatar(verbose=True)

# Access validated data
for sentence in result.sentences:
    print(f"[{sentence.start}] {sentence.text}")
```

## Output Files

All outputs are saved to the `outputs/` directory:

| File | Description |
|------|-------------|
| `step1_transcription.json` | Sentence-level transcription with timestamps |
| `step2_screen_analysis.json` | Screen activities (no humans) |
| `step3_generated_prompt.txt` | GPT-5 crafted prompt |
| `step4_scene_selection.json` | Selected scenes for clipping |
| `step6_optimization.json` | Human detection results |
| `clips_raw/*.mp4` | Cut clips from source video |
| `clips_final/*.mp4` | Final filtered clips (no humans) |
| `clips_final/filtering_summary.json` | Summary of filtering process |

## Configuration

Key settings in `config.py`:

```python
# Models
QWEN_AUDIO_MODEL = "qwen3-omni-flash"
QWEN_VIDEO_MODEL = "qwen3-vl-32b-thinking"
GPT5_MODEL = "gpt-5"

# API settings
MAX_API_RETRIES = 3
GPT5_REASONING_EFFORT = "medium"  # low/medium/high
GPT5_TEXT_VERBOSITY = "low"       # low/medium/high

# Video processing
FFMPEG_FAST_MODE = True  # Fast copy vs accurate re-encode
```

## Best Practices

1. **Run steps sequentially** - Each step depends on previous outputs
2. **Review GPT-5 prompt** - Step 3 pauses for manual review/editing
3. **Check disk space** - Video clips can be large
4. **Monitor API usage** - Video analysis can consume significant tokens
5. **Validate outputs** - Each step validates JSON with Pydantic schemas

## Troubleshooting

### API Key Errors
```
ValueError: DASHSCOPE_API_KEY not found in environment
```
**Solution**: Create `.env` file with your API keys

### FFmpeg Not Found
```
FFmpeg/FFprobe not found. Please install FFmpeg.
```
**Solution**: Install FFmpeg (see Setup section)

### Step N Output Not Found
```
Step 3 output not found: .../step3_generated_prompt.txt
Run step 3 first!
```
**Solution**: Run previous steps in order (1 → 2 → 3 → ...)

### Video File Not Found
```
Video file not found: /path/to/video.mp4
```
**Solution**: Update `MAIN_VIDEO_LOCAL` in `config.py` with correct path

## Advanced Usage

### Custom Video Sources

```python
from steps import transcribe_avatar

# Use custom video URL
result = transcribe_avatar(
    video_url="https://example.com/my-video.mp4",
    output_path="custom_output.json",
    verbose=True
)
```

### Programmatic Pipeline

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from steps import *

# Run complete pipeline programmatically
try:
    transcription = transcribe_avatar(verbose=True)
    screen_analysis = analyze_screen(verbose=True)
    prompt = craft_prompt(verbose=True, pause_for_review=False)
    scenes = targeted_analysis(verbose=True)
    metadata = cut_clips(verbose=True)
    optimization = optimize_clips(verbose=True)
    summary = apply_optimization(verbose=True)

    print(f"✅ Pipeline complete! {summary['kept_clips']} final clips")

except Exception as e:
    print(f"❌ Pipeline failed: {e}")
```

## Data Models

All outputs are validated with Pydantic schemas:

```python
# Step 1: Transcription
{
  "sentences": [
    {"start": "00:00", "end": "00:05", "text": "Hello world"}
  ]
}

# Step 2: Screen Analysis
{
  "activities": [
    {
      "start": "00:10",
      "end": "00:20",
      "description": "UI animation",
      "activity_type": "animation"
    }
  ]
}

# Step 4: Scene Selection
{
  "scenes": [
    {
      "start": "00:15",
      "end": "00:30",
      "description": "Product demo",
      "reason": "Shows key feature"
    }
  ]
}

# Step 6: Optimization
{
  "clips": [
    {
      "source_filename": "clip_01.mp4",
      "output_filename": "clip_01_clean.mp4",
      "human_at": "none" | "start" | "end",
      "timestamp": "00:02"
    }
  ]
}
```

## License

Internal use only.

## Support

For issues or questions, contact the development team.

"""Centralized configuration for video analysis pipeline."""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Project root directory
PROJECT_ROOT = Path(__file__).parent

# API Configuration
DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Model Configuration
QWEN_AUDIO_MODEL = "qwen3-omni-flash"  # Audio-aware model for transcription
QWEN_VIDEO_MODEL = "qwen-vl-max-latest"  # Video analysis model
GPT5_MODEL = "gpt-5-mini-2025-08-07"  # GPT-5 Mini for prompt crafting

# Video URLs (can be updated by user)
AVATAR_VIDEO_URL = "https://efuozhjlnyrcyritksiy.supabase.co/storage/v1/object/public/cotignac/InfiniteTalk_00005-audio.mp4"
MAIN_VIDEO_URL = "https://efuozhjlnyrcyritksiy.supabase.co/storage/v1/object/public/cotignac/videoplayback%20(3).mp4"
MAIN_VIDEO_LOCAL = "/home/hugues/clipping/frontend/public/image/videoplayback (3).mp4"

# Output directories
OUTPUTS_DIR = PROJECT_ROOT / "outputs"
CLIPS_RAW_DIR = OUTPUTS_DIR / "clips_raw"
CLIPS_OPTIMIZED_DIR = OUTPUTS_DIR / "clips_optimized"
CLIPS_FINAL_DIR = OUTPUTS_DIR / "clips_final"

# Output files
STEP1_OUTPUT = OUTPUTS_DIR / "step1_transcription.json"
STEP2_OUTPUT = OUTPUTS_DIR / "step2_screen_analysis.json"
STEP3_OUTPUT = OUTPUTS_DIR / "step3_generated_prompt.txt"
STEP4_OUTPUT = OUTPUTS_DIR / "step4_scene_selection.json"
STEP5_METADATA = CLIPS_RAW_DIR / "clips_metadata.json"
STEP6_OUTPUT = OUTPUTS_DIR / "step6_optimization.json"

# Pipeline settings
FFMPEG_FAST_MODE = False  # Use accurate re-encode mode (prevents corruption)
MAX_API_RETRIES = 3  # Number of retries for API calls
GPT5_REASONING_EFFORT = "medium"  # low/medium/high
GPT5_TEXT_VERBOSITY = "low"  # low/medium/high

# Validation
def validate_config():
    """Validate that required configuration is present."""
    errors = []

    if not DASHSCOPE_API_KEY:
        errors.append("DASHSCOPE_API_KEY not found in .env file")

    if not OPENAI_API_KEY:
        errors.append("OPENAI_API_KEY not found in .env file")

    # Create output directories
    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
    CLIPS_RAW_DIR.mkdir(parents=True, exist_ok=True)
    CLIPS_OPTIMIZED_DIR.mkdir(parents=True, exist_ok=True)
    CLIPS_FINAL_DIR.mkdir(parents=True, exist_ok=True)

    if errors:
        raise ValueError(f"Configuration errors:\n" + "\n".join(f"  - {e}" for e in errors))


# Display configuration
def display_config():
    """Display current configuration."""
    print("=" * 60)
    print("PIPELINE CONFIGURATION")
    print("=" * 60)
    print(f"Project Root:     {PROJECT_ROOT}")
    print(f"Outputs Dir:      {OUTPUTS_DIR}")
    print(f"\nModels:")
    print(f"  Audio Model:    {QWEN_AUDIO_MODEL}")
    print(f"  Video Model:    {QWEN_VIDEO_MODEL}")
    print(f"  GPT-5 Model:    {GPT5_MODEL}")
    print(f"\nVideo Sources:")
    print(f"  Avatar:         {AVATAR_VIDEO_URL[:60]}...")
    print(f"  Main:           {MAIN_VIDEO_URL[:60]}...")
    print(f"\nAPI Keys:")
    print(f"  DashScope:      {'✓ Set' if DASHSCOPE_API_KEY else '✗ Missing'}")
    print(f"  OpenAI:         {'✓ Set' if OPENAI_API_KEY else '✗ Missing'}")
    print("=" * 60)


if __name__ == "__main__":
    validate_config()
    display_config()

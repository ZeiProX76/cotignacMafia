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

# Video URLs (legacy single-video support - for avatar video only)
AVATAR_VIDEO_URL = "https://efuozhjlnyrcyritksiy.supabase.co/storage/v1/object/public/cotignac/InfiniteTalk_00005-audio.mp4"

# Multi-video configuration (NEW: for processing multiple demo videos)
VIDEOS_CONFIG_PATH = PROJECT_ROOT / "videos_config.json"

# Output directories
OUTPUTS_DIR = PROJECT_ROOT / "outputs"
CLIPS_RAW_DIR = OUTPUTS_DIR / "clips_raw"
CLIPS_OPTIMIZED_DIR = OUTPUTS_DIR / "clips_optimized"
CLIPS_FINAL_DIR = OUTPUTS_DIR / "clips_final"
TOP15_DIR = OUTPUTS_DIR / "top15"  # Top 15 clips selected for timeline

# Output files (Single-video mode - legacy)
STEP1_OUTPUT = OUTPUTS_DIR / "step1_transcription.json"
STEP2_OUTPUT = OUTPUTS_DIR / "step2_screen_analysis.json"  # Legacy single-video
STEP3_OUTPUT = OUTPUTS_DIR / "step3_generated_prompt.txt"  # Legacy single-video
STEP4_OUTPUT = OUTPUTS_DIR / "step4_scene_selection.json"  # Legacy single-video
STEP5_METADATA = CLIPS_RAW_DIR / "clips_metadata.json"  # Legacy single-video
STEP6_OUTPUT = OUTPUTS_DIR / "step6_all_clips_analysis.json"  # Aggregated from all videos
STEP6_5_OUTPUT = OUTPUTS_DIR / "step6_5_rankings.json"  # NEW: Clip rankings
STEP7_OUTPUT = OUTPUTS_DIR / "step7_top15.json"  # NEW: Top 15 selection
STEP8_OUTPUT = OUTPUTS_DIR / "final_timeline.json"  # Timeline JSON for Remotion

# Pipeline settings
FFMPEG_FAST_MODE = False  # Use accurate re-encode mode (prevents corruption)
MAX_API_RETRIES = 3  # Number of retries for API calls
GPT5_REASONING_EFFORT = "medium"  # low/medium/high
GPT5_TEXT_VERBOSITY = "low"  # low/medium/high


# ==============================================================================
# MULTI-VIDEO HELPER FUNCTIONS
# ==============================================================================

def load_videos_config():
    """Load videos configuration from JSON file.

    Returns:
        VideosConfig: Parsed and validated videos configuration

    Raises:
        FileNotFoundError: If videos_config.json doesn't exist
        ValueError: If JSON is invalid or doesn't match schema
    """
    import json
    from schemas import VideosConfig

    if not VIDEOS_CONFIG_PATH.exists():
        raise FileNotFoundError(
            f"Videos config not found: {VIDEOS_CONFIG_PATH}\n"
            "Create videos_config.json with your video sources"
        )

    with open(VIDEOS_CONFIG_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)

    return VideosConfig(**data)


def get_video_output_dir(video_id: str) -> Path:
    """Get output directory for a specific video.

    Args:
        video_id: Video identifier (e.g., 'video_001')

    Returns:
        Path to video-specific output directory
    """
    return OUTPUTS_DIR / video_id


def get_video_step_output(video_id: str, step: int, extension: str = ".json") -> Path:
    """Get output path for a specific step and video.

    Args:
        video_id: Video identifier
        step: Step number (2, 3, 4, 5)
        extension: File extension (default: .json)

    Returns:
        Path to step output file

    Example:
        get_video_step_output("video_001", 2) -> outputs/video_001/step2_screen_analysis.json
        get_video_step_output("video_002", 3, ".txt") -> outputs/video_002/step3_generated_prompt.txt
    """
    video_dir = get_video_output_dir(video_id)

    step_names = {
        2: f"step2_screen_analysis{extension}",
        3: f"step3_generated_prompt{extension}",
        4: f"step4_scene_selection{extension}",
        5: f"clips_metadata{extension}"
    }

    if step not in step_names:
        raise ValueError(f"Invalid step number: {step}. Must be 2, 3, 4, or 5.")

    return video_dir / step_names[step]


def create_video_directories(video_id: str):
    """Create output directories for a specific video.

    Args:
        video_id: Video identifier
    """
    video_dir = get_video_output_dir(video_id)
    video_dir.mkdir(parents=True, exist_ok=True)


# ==============================================================================
# VALIDATION
# ==============================================================================

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
    TOP15_DIR.mkdir(parents=True, exist_ok=True)

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
    print(f"  Videos Config:  {VIDEOS_CONFIG_PATH}")

    # Try to load and display videos config
    try:
        videos_cfg = load_videos_config()
        print(f"  Demo Videos:    {len(videos_cfg.videos)} configured")
        for video in videos_cfg.videos:
            print(f"    - {video.id}: {video.name}")
    except Exception as e:
        print(f"  Demo Videos:    ✗ Not loaded ({str(e)[:30]}...)")

    print(f"\nAPI Keys:")
    print(f"  DashScope:      {'✓ Set' if DASHSCOPE_API_KEY else '✗ Missing'}")
    print(f"  OpenAI:         {'✓ Set' if OPENAI_API_KEY else '✗ Missing'}")
    print("=" * 60)


if __name__ == "__main__":
    validate_config()
    display_config()

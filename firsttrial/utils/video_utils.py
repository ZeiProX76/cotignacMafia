"""Video processing utilities using FFmpeg."""

import subprocess
import re
from pathlib import Path
from typing import Union


def get_duration(video_path: Union[str, Path]) -> float:
    """
    Get video duration in seconds using ffprobe.

    Args:
        video_path: Path to video file

    Returns:
        Duration in seconds

    Raises:
        subprocess.CalledProcessError: If ffprobe fails
    """
    result = subprocess.run(
        [
            "ffprobe", "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            str(video_path)
        ],
        capture_output=True,
        text=True,
        check=True
    )
    return float(result.stdout.strip())


def mmss_to_seconds(timestamp: str) -> float:
    """
    Convert MM:SS or MM:SS.ms timestamp to seconds.

    Args:
        timestamp: Timestamp string (e.g., "01:30" or "01:30.5")

    Returns:
        Time in seconds

    Examples:
        >>> mmss_to_seconds("01:30")
        90.0
        >>> mmss_to_seconds("00:45.5")
        45.5
    """
    parts = timestamp.split(":")
    minutes = int(parts[0])
    seconds = float(parts[1])
    return minutes * 60 + seconds


def seconds_to_mmss(seconds: float, include_ms: bool = False) -> str:
    """
    Convert seconds to MM:SS or MM:SS.ms format.

    Args:
        seconds: Time in seconds
        include_ms: Include milliseconds in output

    Returns:
        Formatted timestamp string
    """
    minutes = int(seconds // 60)
    secs = seconds % 60

    if include_ms:
        return f"{minutes:02d}:{secs:06.3f}"
    else:
        return f"{minutes:02d}:{int(secs):02d}"


def sanitize_filename(name: str) -> str:
    """
    Remove unsafe characters from filename, keep readable names.

    Args:
        name: Original filename or description

    Returns:
        Sanitized filename safe for filesystem
    """
    name = name.strip()
    name = re.sub(r"[^\w\-\. ]+", "_", name, flags=re.UNICODE)
    name = re.sub(r"\s+", "_", name)
    return name or "clip"


def cut_clip(
    input_path: Union[str, Path],
    start: str,
    end: str,
    output_path: Union[str, Path],
    fast_mode: bool = False,
    start_buffer: float = 0.2
) -> None:
    """
    Cut a clip from video using ffmpeg.

    Args:
        input_path: Source video path
        start: Start timestamp (MM:SS format)
        end: End timestamp (MM:SS format)
        output_path: Output video path
        fast_mode: Use fast copy mode (may corrupt) vs accurate re-encode (recommended)
        start_buffer: Seconds to subtract from start time for safety (default: 0.2)

    Raises:
        subprocess.CalledProcessError: If ffmpeg fails
    """
    # Calculate duration from start and end
    start_seconds = mmss_to_seconds(start)
    end_seconds = mmss_to_seconds(end)

    # Apply start buffer (start 0.2s earlier for safety)
    start_seconds = max(0, start_seconds - start_buffer)

    duration = end_seconds - start_seconds

    # Convert adjusted times back to timestamp format for ffmpeg
    adjusted_start = seconds_to_mmss(start_seconds, include_ms=True)
    adjusted_end = seconds_to_mmss(end_seconds, include_ms=True)

    # Put -ss AFTER -i for accurate timestamps
    cmd = [
        "ffmpeg",
        "-hide_banner", "-y",
        "-i", str(input_path),
        "-ss", adjusted_start,
        "-to", adjusted_end,
        "-c:v", "libx264",
        "-preset", "ultrafast",
        "-crf", "18",
        "-c:a", "aac",
        "-strict", "experimental",
        "-movflags", "+faststart",
        str(output_path),
    ]

    proc = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )

    if proc.returncode != 0:
        print("FFmpeg error:")
        print(proc.stdout)
        raise subprocess.CalledProcessError(
            proc.returncode,
            cmd,
            output=proc.stdout
        )


def verify_ffmpeg_installed() -> bool:
    """
    Check if ffmpeg and ffprobe are installed.

    Returns:
        True if both are available, False otherwise
    """
    try:
        subprocess.run(
            ["ffmpeg", "-version"],
            capture_output=True,
            check=True
        )
        subprocess.run(
            ["ffprobe", "-version"],
            capture_output=True,
            check=True
        )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

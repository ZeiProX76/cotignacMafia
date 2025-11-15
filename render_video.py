#!/usr/bin/env python3
"""
Programmatic video rendering with Remotion
No UI, just code -> video output
"""
import json
import subprocess
import os
from pathlib import Path

def add_video_overlay(src, start_seconds, duration_seconds, position, animation, width=400, height=400):
    """
    Create a video overlay configuration

    Args:
        src: Video URL or path
        start_seconds: When to show overlay (float)
        duration_seconds: How long to show (float)
        position: 'top-left', 'top-right', 'bottom-left', 'bottom-right', 'center'
        animation: 'slide-left', 'slide-right', 'slide-top'
        width: Overlay width in pixels
        height: Overlay height in pixels
    """
    return {
        "type": "video",
        "src": src,
        "startSeconds": start_seconds,
        "durationSeconds": duration_seconds,
        "position": position,
        "animation": animation,
        "width": width,
        "height": height,
        "borderRadius": 24
    }

def add_text_overlay(text, start_seconds, duration_seconds, position, font_size=48, color="#ffffff", bg_color="rgba(0, 0, 0, 0.7)"):
    """
    Create a text overlay configuration

    Args:
        text: Text to display
        start_seconds: When to show text (float)
        duration_seconds: How long to show (float)
        position: 'top-left', 'top-right', 'bottom-left', 'bottom-right', 'center'
        font_size: Font size in pixels
        color: Text color (hex or rgba)
        bg_color: Background color (hex or rgba)
    """
    return {
        "type": "text",
        "text": text,
        "startSeconds": start_seconds,
        "durationSeconds": duration_seconds,
        "position": position,
        "fontSize": font_size,
        "color": color,
        "backgroundColor": bg_color
    }

def render_video(main_video_url, overlays, output_path="out/final.mp4", duration_seconds=30, fps=60, width=1920, height=1080):
    """
    Render a video with overlays programmatically

    Args:
        main_video_url: URL or path to main video
        overlays: List of overlay configs (from add_video_overlay or add_text_overlay)
        output_path: Where to save the final video
        duration_seconds: Total video duration
        fps: Frame rate (default 60)
        width: Video width (default 1920)
        height: Video height (default 1080)
    """
    timeline = {
        "mainVideo": main_video_url,
        "fps": fps,
        "width": width,
        "height": height,
        "durationInSeconds": duration_seconds,
        "overlays": overlays
    }

    # Save timeline to temporary JSON
    timeline_path = "temp_timeline.json"
    with open(timeline_path, 'w') as f:
        json.dump(timeline, f, indent=2)

    print(f"📝 Timeline created: {timeline_path}")
    print(f"🎬 Main video: {main_video_url}")
    print(f"📊 {len(overlays)} overlays defined")
    print(f"⏱️  Duration: {duration_seconds}s @ {fps}fps")
    print(f"\n🎥 Rendering video...")
    print(f"⏳ This may take a few minutes...\n")

    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)

    # Run render command
    try:
        result = subprocess.run(
            ['npm', 'run', 'render', '--', f'--json={timeline_path}', f'--output={output_path}'],
            check=True,
            capture_output=False
        )
        print(f"\n✅ Video rendered successfully!")
        print(f"📹 Output: {output_path}")
        print(f"\nTo watch: vlc {output_path}")
        return output_path
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Error rendering video: {e}")
        raise

if __name__ == "__main__":
    # Example usage
    main_video = "https://efuozhjlnyrcyritksiy.supabase.co/storage/v1/object/public/cotignac/videoplayback%20(2).mp4"

    overlays = [
        # First video overlay - slides in from right at 3 seconds
        add_video_overlay(
            src="https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4",
            start_seconds=3.0,
            duration_seconds=5.0,
            position="top-right",
            animation="slide-left",
            width=400,
            height=400
        ),

        # Second video overlay - slides in from left at 10 seconds
        add_video_overlay(
            src="https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerEscapes.mp4",
            start_seconds=10.0,
            duration_seconds=5.0,
            position="bottom-left",
            animation="slide-right",
            width=350,
            height=350
        ),

        # Text overlay for first video
        add_text_overlay(
            text="First Overlay!",
            start_seconds=3.5,
            duration_seconds=2.5,
            position="top-left",
            font_size=48,
            color="#ffeb3b"
        ),

        # Text overlay for second video
        add_text_overlay(
            text="Second Moment",
            start_seconds=10.5,
            duration_seconds=3.0,
            position="bottom-right",
            font_size=42,
            color="#ffffff",
            bg_color="rgba(255, 0, 0, 0.8)"
        )
    ]

    # Render the video
    render_video(
        main_video_url=main_video,
        overlays=overlays,
        output_path="out/my-video.mp4",
        duration_seconds=20,
        fps=60
    )

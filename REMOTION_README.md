# Remotion Programmatic Video Editing System

A powerful TypeScript-based system for programmatically compositing video overlays and text onto main videos using [Remotion](https://www.remotion.dev/).

## Features

- **JSON-Driven Timeline**: Define your entire video composition in a JSON configuration file
- **Video Overlays**: Add multiple video clips as overlays at precise timeframes
- **Text Overlays**: Dynamic text overlays with customizable styling
- **3 Animation Types**:
  - `slide-left`: Slides in from right, exits to left
  - `slide-right`: Slides in from left, exits to right
  - `slide-top`: Slides in from bottom, exits to top
- **60 FPS Support**: High frame rate for smooth playback
- **Precise Positioning**: 5 position presets (top-left, top-right, bottom-left, bottom-right, center)
- **CLI Rendering**: Command-line tool to render videos from JSON

## Installation

```bash
npm install
```

## Quick Start

### 1. Preview in Remotion Studio

Launch the interactive preview:

```bash
npm start
```

This opens the Remotion Studio where you can see the default composition and make live edits.

### 2. Render from JSON

Render a video using a timeline configuration:

```bash
npm run render -- --json=example-timeline.json --output=out/final.mp4
```

## JSON Timeline Configuration

### Complete Example

```json
{
  "mainVideo": "path/to/main-video.mp4",
  "fps": 60,
  "width": 1920,
  "height": 1080,
  "durationInSeconds": 30,
  "overlays": [
    {
      "type": "video",
      "src": "clips_out/best-clip-1.mp4",
      "startSeconds": 5.0,
      "durationSeconds": 8.0,
      "position": "top-right",
      "animation": "slide-left",
      "width": 400,
      "height": 400,
      "borderRadius": 24
    },
    {
      "type": "text",
      "text": "Amazing moment!",
      "startSeconds": 5.5,
      "durationSeconds": 3.0,
      "position": "bottom-left",
      "fontSize": 48,
      "fontWeight": "bold",
      "color": "#ffffff",
      "backgroundColor": "rgba(0, 0, 0, 0.7)"
    }
  ]
}
```

### Configuration Reference

#### Root Level

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `mainVideo` | string | ✅ | Path or URL to the main background video |
| `fps` | number | ✅ | Frame rate (recommended: 60) |
| `width` | number | ❌ | Video width in pixels (default: 1920) |
| `height` | number | ❌ | Video height in pixels (default: 1080) |
| `durationInSeconds` | number | ❌ | Total video duration in seconds |
| `overlays` | array | ✅ | Array of overlay configurations |

#### Video Overlay Object

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `type` | "video" | ✅ | Overlay type |
| `src` | string | ✅ | Path or URL to the overlay video |
| `startSeconds` | number | ✅ | When to start showing the overlay |
| `durationSeconds` | number | ✅ | How long to show the overlay |
| `position` | string | ✅ | Position: `top-left`, `top-right`, `bottom-left`, `bottom-right`, `center` |
| `animation` | string | ✅ | Animation: `slide-left`, `slide-right`, `slide-top` |
| `width` | number | ❌ | Overlay width (default: 400) |
| `height` | number | ❌ | Overlay height (default: 400) |
| `borderRadius` | number | ❌ | Corner radius (default: 24) |

#### Text Overlay Object

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `type` | "text" | ✅ | Overlay type |
| `text` | string | ✅ | Text content to display |
| `startSeconds` | number | ✅ | When to start showing the text |
| `durationSeconds` | number | ✅ | How long to show the text |
| `position` | string | ✅ | Position: `top-left`, `top-right`, `bottom-left`, `bottom-right`, `center` |
| `fontSize` | number | ❌ | Font size in pixels (default: 48) |
| `fontWeight` | string/number | ❌ | Font weight (default: "bold") |
| `color` | string | ❌ | Text color (default: "#ffffff") |
| `backgroundColor` | string | ❌ | Background color (default: "rgba(0, 0, 0, 0.7)") |
| `padding` | number | ❌ | Padding in pixels (default: 20) |
| `borderRadius` | number | ❌ | Corner radius (default: 12) |

## Animation Details

All animations include:
- **0.5 second entrance**: Fade in + slide in
- **0.5 second exit**: Fade out + slide out
- Smooth interpolation using Remotion's built-in functions

### Animation Types

- **`slide-left`**: Enters from the right (200px offset), exits to the left
- **`slide-right`**: Enters from the left (-200px offset), exits to the right
- **`slide-top`**: Enters from the bottom (200px offset), exits to the top

Text overlays have a subtle scale animation (0.95 → 1.0) combined with fade.

## Programmatic Usage

You can also use the components directly in TypeScript:

```typescript
import { Composition } from './remotion/src/Composition';
import { TimelineConfig } from './remotion/src/types';

const myTimeline: TimelineConfig = {
  mainVideo: 'video.mp4',
  fps: 60,
  overlays: [
    {
      type: 'video',
      src: 'overlay.mp4',
      startSeconds: 2,
      durationSeconds: 5,
      position: 'top-right',
      animation: 'slide-left',
    }
  ]
};

// Use in a Remotion composition
<Composition timeline={myTimeline} />
```

## CLI Options

### Render Command

```bash
npm run render -- --json=<timeline.json> --output=<output.mp4>
```

- `--json`: Path to timeline JSON configuration (required)
- `--output`: Output video path (default: `out/video.mp4`)

### Examples

```bash
# Basic render
npm run render -- --json=timeline.json

# Custom output location
npm run render -- --json=my-config.json --output=videos/final.mp4

# Using local video files
npm run render -- --json=local-timeline.json --output=result.mp4
```

## Use Case: AI-Selected Best Clips

This system is designed to work with your existing Python video analysis pipeline:

1. **Python Script Analyzes Video**: Your `test_video_description.py` uses Qwen VL to identify best clips
2. **Extract Clips**: `cut_clips.py` extracts the selected clips to `clips_out/`
3. **Create Timeline JSON**: Generate a JSON file that places these clips as overlays on a main video
4. **Render with Remotion**: Use this system to create the final composite video

### Example Workflow

```json
{
  "mainVideo": "original-video.mp4",
  "fps": 60,
  "durationInSeconds": 60,
  "overlays": [
    {
      "type": "video",
      "src": "clips_out/best-moment-1.mp4",
      "startSeconds": 10,
      "durationSeconds": 5,
      "position": "top-right",
      "animation": "slide-left"
    },
    {
      "type": "text",
      "text": "Best Moment #1",
      "startSeconds": 10.5,
      "durationSeconds": 2,
      "position": "top-left"
    }
  ]
}
```

## Project Structure

```
/remotion/
  /src/
    index.ts              # Entry point
    Root.tsx              # Remotion root component
    Composition.tsx       # Main composition renderer
    VideoOverlay.tsx      # Video overlay component
    TextOverlay.tsx       # Text overlay component
    types.ts              # TypeScript type definitions
    animations.ts         # Animation calculation utilities
    positioning.ts        # Position calculation utilities
remotion.config.ts        # Remotion configuration
render.ts                 # CLI rendering script
example-timeline.json     # Example timeline configuration
```

## Tips & Best Practices

1. **Frame Precision**: At 60fps, each frame is ~16.67ms. Use decimal seconds for precise timing (e.g., `5.5` seconds)

2. **Video Paths**: Can use:
   - Local files: `clips_out/clip1.mp4`
   - Absolute paths: `/home/user/videos/video.mp4`
   - URLs: `https://example.com/video.mp4`

3. **Overlay Sizing**: Keep overlays proportional to your main video:
   - For 1920x1080: 300-400px overlays work well
   - For 3840x2160 (4K): 600-800px overlays

4. **Animation Timing**: Default 0.5s animations work well at 60fps. Adjust by modifying `animationDurationSeconds` in the code.

5. **Text Readability**: Use high contrast colors and semi-transparent backgrounds for readability

## Troubleshooting

### Videos not loading
- Check file paths are correct
- Ensure video files are accessible
- Try using absolute paths instead of relative

### Rendering too slow
- Reduce video resolution in timeline config
- Lower fps to 30 if 60fps not needed
- Use shorter test clips during development

### Out of memory
- Render shorter segments
- Reduce overlay video quality/resolution
- Close other applications during rendering

## Next Steps

- Integrate with your Python pipeline to auto-generate timeline JSON
- Add more animation types (zoom, rotate, etc.)
- Create presets for common overlay patterns
- Add audio support for overlay videos
- Implement transition effects between overlays

## Resources

- [Remotion Documentation](https://www.remotion.dev/docs)
- [Remotion Examples](https://github.com/remotion-dev/remotion)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)

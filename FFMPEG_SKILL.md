# FFmpeg Skill Documentation

## Overview

The **FFmpeg skill** provides video/audio processing capabilities through the FFmpeg command-line tool. This skill handles all video file operations: cutting clips, quality conversion, format changes, metadata extraction, and stream manipulation.

**Key Capabilities:**
- **Clip cutting** with pixel-perfect accuracy (slow but reliable re-encode method)
- **Quality conversion** (high → low bitrate for web optimization)
- **Format conversion** (MP4, WebM, MOV, etc.)
- **Metadata extraction** (duration, resolution, codec info)
- **Stream manipulation** (audio extraction, codec changes, resolution changes)
- **Advanced operations** (concatenation, overlays, filters)

**When to Use This Skill:**
- Need to cut specific segments from video with precise timestamps
- Converting high-quality video to web-optimized formats
- Extracting video metadata (duration, dimensions, codec)
- Changing video resolution, bitrate, or codec
- Extracting or replacing audio streams
- Concatenating multiple video clips
- Any video file transformation or analysis

**Technology:**
- FFmpeg 6.x+ (video/audio processing)
- FFprobe 6.x+ (metadata extraction)
- Shell command execution (bash/zsh)

---

## Core Workflows

### Workflow 1: Cut Video Clips (Accurate Method)

**Use Case:** Extract specific time segments from video with frame-perfect accuracy

**Method:** Slow but reliable re-encode (prevents corruption and keyframe issues)

**Command Pattern:**
```bash
ffmpeg -hide_banner -y \
  -i INPUT_VIDEO \
  -ss START_TIME \
  -to END_TIME \
  -c:v libx264 -preset ultrafast -crf 18 \
  -c:a aac \
  -movflags +faststart \
  OUTPUT_VIDEO
```

**Parameters Explained:**
- `-hide_banner -y`: Clean output, overwrite existing files
- `-i INPUT_VIDEO`: Input file (place -ss/-to AFTER -i for accuracy)
- `-ss START_TIME`: Start timestamp (MM:SS or HH:MM:SS or seconds)
- `-to END_TIME`: End timestamp (absolute, not duration)
- `-c:v libx264`: Video codec (H.264 re-encode)
- `-preset ultrafast`: Encoding speed (ultrafast, fast, medium, slow)
- `-crf 18`: Quality (0-51, lower=better, 18=high quality)
- `-c:a aac`: Audio codec
- `-movflags +faststart`: Web optimization (moov atom at beginning)

**Example:**
```bash
# Cut 5 seconds to 12 seconds from video
ffmpeg -hide_banner -y \
  -i demo.mp4 \
  -ss 00:05 \
  -to 00:12 \
  -c:v libx264 -preset ultrafast -crf 18 \
  -c:a aac \
  -movflags +faststart \
  clip_001.mp4
```

**Why This Method (Not Stream Copy):**
- `-ss` AFTER `-i`: Accurate frame positioning (decodes from start)
- Re-encode (not `-c copy`): Prevents keyframe alignment issues
- No corrupt clips, no missing frames, no timeline drift
- Tradeoff: Slower but 100% reliable

**Fast but Inaccurate Alternative (NOT RECOMMENDED):**
```bash
# This is FAST but can produce corrupt clips
ffmpeg -ss 00:05 -i demo.mp4 -to 00:07 -c copy clip.mp4
```

---

### Workflow 2: Convert High Quality to Low (Web Optimization)

**Use Case:** Reduce file size for web delivery while maintaining acceptable quality

**Command Pattern:**
```bash
ffmpeg -hide_banner -y \
  -i HIGH_QUALITY_VIDEO \
  -c:v libx264 \
  -preset medium \
  -crf 23 \
  -maxrate 2M \
  -bufsize 4M \
  -vf "scale=-2:720" \
  -c:a aac -b:a 128k \
  -movflags +faststart \
  LOW_QUALITY_VIDEO
```

**Parameters Explained:**
- `-c:v libx264`: H.264 codec (best compatibility)
- `-preset medium`: Balance speed/compression (fast, medium, slow, slower)
- `-crf 23`: Quality (23=good for web, 28=acceptable, 18=high)
- `-maxrate 2M`: Max bitrate 2 Mbps (prevents spikes)
- `-bufsize 4M`: Buffer size (2x maxrate recommended)
- `-vf "scale=-2:720"`: Scale to 720p height (keep aspect ratio)
- `-c:a aac -b:a 128k`: Audio codec + 128kbps bitrate
- `-movflags +faststart`: Streaming optimization

**Quality Presets:**

**High Quality (4K/1080p source → 1080p web):**
```bash
ffmpeg -i input.mp4 \
  -c:v libx264 -preset medium -crf 20 \
  -vf "scale=-2:1080" \
  -c:a aac -b:a 192k \
  -movflags +faststart \
  output_1080p.mp4
```

**Medium Quality (1080p → 720p web):**
```bash
ffmpeg -i input.mp4 \
  -c:v libx264 -preset medium -crf 23 \
  -vf "scale=-2:720" \
  -c:a aac -b:a 128k \
  -movflags +faststart \
  output_720p.mp4
```

**Low Quality (720p → 480p mobile):**
```bash
ffmpeg -i input.mp4 \
  -c:v libx264 -preset fast -crf 28 \
  -vf "scale=-2:480" \
  -c:a aac -b:a 96k \
  -movflags +faststart \
  output_480p.mp4
```

**File Size Comparison (10-minute video):**
- 4K original: ~2-5 GB
- 1080p high (CRF 20): ~500-800 MB
- 720p medium (CRF 23): ~200-350 MB
- 480p low (CRF 28): ~80-150 MB

---

### Workflow 3: Extract Video Metadata

**Use Case:** Get video properties (duration, resolution, codec, bitrate)

**Command Pattern (Duration):**
```bash
ffprobe -v error \
  -show_entries format=duration \
  -of default=noprint_wrappers=1:nokey=1 \
  VIDEO_FILE
```

**Output:** `123.456` (seconds as float)

**Command Pattern (Resolution):**
```bash
ffprobe -v error \
  -select_streams v:0 \
  -show_entries stream=width,height \
  -of csv=p=0 \
  VIDEO_FILE
```

**Output:** `1920,1080` (width,height)

**Command Pattern (Full Video Info):**
```bash
ffprobe -v error \
  -show_format \
  -show_streams \
  -print_format json \
  VIDEO_FILE
```

**Output:** Complete JSON with all metadata

**Common Metadata Queries:**

```bash
# Duration in seconds
ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 video.mp4

# Resolution (width x height)
ffprobe -v error -select_streams v:0 -show_entries stream=width,height -of csv=p=0 video.mp4

# Video codec
ffprobe -v error -select_streams v:0 -show_entries stream=codec_name -of default=noprint_wrappers=1:nokey=1 video.mp4

# Audio codec
ffprobe -v error -select_streams a:0 -show_entries stream=codec_name -of default=noprint_wrappers=1:nokey=1 video.mp4

# Bitrate (kb/s)
ffprobe -v error -show_entries format=bit_rate -of default=noprint_wrappers=1:nokey=1 video.mp4

# Frame rate (fps)
ffprobe -v error -select_streams v:0 -show_entries stream=r_frame_rate -of default=noprint_wrappers=1:nokey=1 video.mp4
```

---

### Workflow 4: Format Conversion

**Use Case:** Convert between video formats (MP4, WebM, MOV, etc.)

**MP4 to WebM (for web):**
```bash
ffmpeg -i input.mp4 \
  -c:v libvpx-vp9 -crf 30 -b:v 0 \
  -c:a libopus -b:a 128k \
  output.webm
```

**MOV to MP4 (for compatibility):**
```bash
ffmpeg -i input.mov \
  -c:v libx264 -preset medium -crf 23 \
  -c:a aac -b:a 128k \
  -movflags +faststart \
  output.mp4
```

**AVI to MP4:**
```bash
ffmpeg -i input.avi \
  -c:v libx264 -preset medium -crf 23 \
  -c:a aac -b:a 128k \
  output.mp4
```

**Any format to MP4 (universal converter):**
```bash
ffmpeg -i input.* \
  -c:v libx264 -preset medium -crf 23 \
  -c:a aac \
  -movflags +faststart \
  output.mp4
```

---

### Workflow 5: Change Resolution/Aspect Ratio

**Use Case:** Resize video or change aspect ratio for different platforms

**Scale to Specific Height (Keep Aspect Ratio):**
```bash
# 720p
ffmpeg -i input.mp4 \
  -vf "scale=-2:720" \
  -c:a copy \
  output_720p.mp4

# 1080p
ffmpeg -i input.mp4 \
  -vf "scale=-2:1080" \
  -c:a copy \
  output_1080p.mp4
```

**Scale to Specific Width (Keep Aspect Ratio):**
```bash
ffmpeg -i input.mp4 \
  -vf "scale=1280:-2" \
  -c:a copy \
  output_1280w.mp4
```

**Force Exact Resolution (May Distort):**
```bash
ffmpeg -i input.mp4 \
  -vf "scale=1920:1080" \
  -c:a copy \
  output_1920x1080.mp4
```

**Convert to Instagram Vertical (9:16):**
```bash
ffmpeg -i input.mp4 \
  -vf "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2" \
  -c:a copy \
  instagram_vertical.mp4
```

**Convert to TikTok/Reels (9:16):**
```bash
ffmpeg -i input.mp4 \
  -vf "crop=ih*9/16:ih" \
  -c:a copy \
  tiktok_vertical.mp4
```

---

### Workflow 6: Audio Operations

**Extract Audio Only:**
```bash
ffmpeg -i video.mp4 \
  -vn \
  -c:a copy \
  audio.aac
```

**Remove Audio (Silent Video):**
```bash
ffmpeg -i video.mp4 \
  -an \
  -c:v copy \
  silent_video.mp4
```

**Replace Audio Track:**
```bash
ffmpeg -i video.mp4 -i new_audio.mp3 \
  -c:v copy \
  -c:a aac \
  -map 0:v:0 -map 1:a:0 \
  video_new_audio.mp4
```

**Adjust Audio Volume:**
```bash
# Increase volume by 10dB
ffmpeg -i input.mp4 \
  -af "volume=10dB" \
  -c:v copy \
  louder.mp4

# Decrease volume to 50%
ffmpeg -i input.mp4 \
  -af "volume=0.5" \
  -c:v copy \
  quieter.mp4
```

**Normalize Audio Levels:**
```bash
# Two-pass normalization
ffmpeg -i input.mp4 -af loudnorm=print_format=json -f null -
# (use measured values)
ffmpeg -i input.mp4 \
  -af loudnorm=measured_I=-16:measured_LRA=11:measured_TP=-1.5 \
  -c:v copy \
  normalized.mp4
```

---

### Workflow 7: Concatenate Multiple Videos

**Use Case:** Merge multiple clips into single video

**Method 1: Concat Demuxer (Same Codec/Resolution - Fast):**
```bash
# Create list file
echo "file 'clip1.mp4'" > filelist.txt
echo "file 'clip2.mp4'" >> filelist.txt
echo "file 'clip3.mp4'" >> filelist.txt

# Concatenate
ffmpeg -f concat -safe 0 -i filelist.txt \
  -c copy \
  merged.mp4
```

**Method 2: Concat Filter (Different Codecs/Resolutions - Reliable):**
```bash
ffmpeg \
  -i clip1.mp4 \
  -i clip2.mp4 \
  -i clip3.mp4 \
  -filter_complex "[0:v][0:a][1:v][1:a][2:v][2:a]concat=n=3:v=1:a=1[vout][aout]" \
  -map "[vout]" -map "[aout]" \
  merged.mp4
```

**Method 3: Simple Sequential Merge (Same Format):**
```bash
ffmpeg -i "concat:clip1.mp4|clip2.mp4|clip3.mp4" \
  -c copy \
  merged.mp4
```

---

### Workflow 8: Speed Up/Slow Down Video

**Speed Up (2x faster):**
```bash
ffmpeg -i input.mp4 \
  -filter:v "setpts=0.5*PTS" \
  -filter:a "atempo=2.0" \
  output_2x.mp4
```

**Slow Down (0.5x slower):**
```bash
ffmpeg -i input.mp4 \
  -filter:v "setpts=2.0*PTS" \
  -filter:a "atempo=0.5" \
  output_half.mp4
```

**Speed Multipliers:**
- `setpts=0.5*PTS` + `atempo=2.0` = 2x faster
- `setpts=0.25*PTS` + `atempo=4.0` = 4x faster
- `setpts=2.0*PTS` + `atempo=0.5` = 2x slower
- `setpts=4.0*PTS` + `atempo=0.25` = 4x slower

**Note:** Audio tempo must be between 0.5-2.0. For larger changes, chain multiple atempo filters:
```bash
# 4x faster audio
-filter:a "atempo=2.0,atempo=2.0"
```

---

### Workflow 9: Extract Frames/Thumbnails

**Extract Single Frame at Timestamp:**
```bash
ffmpeg -ss 00:05.000 -i input.mp4 \
  -frames:v 1 \
  thumbnail.jpg
```

**Extract Multiple Frames (Every N Seconds):**
```bash
# Extract 1 frame per second
ffmpeg -i input.mp4 \
  -vf fps=1 \
  frames/frame_%04d.jpg

# Extract 1 frame every 5 seconds
ffmpeg -i input.mp4 \
  -vf fps=1/5 \
  frames/frame_%04d.jpg
```

**Extract All Frames:**
```bash
ffmpeg -i input.mp4 \
  frames/frame_%06d.png
```

**Create Video from Image Sequence:**
```bash
ffmpeg -framerate 30 -i frames/frame_%04d.jpg \
  -c:v libx264 -pix_fmt yuv420p \
  output.mp4
```

---

## Command Pattern Reference

### Timestamp Formats

FFmpeg accepts multiple timestamp formats:

```bash
# Seconds
-ss 45.5

# MM:SS
-ss 01:30

# HH:MM:SS
-ss 00:01:30

# HH:MM:SS.mmm (millisecond precision)
-ss 00:01:30.500
```

**Start vs End Time:**
- `-ss`: Start time
- `-to`: End time (absolute timestamp)
- `-t`: Duration (how long to record)

```bash
# Method 1: Start + End (recommended)
ffmpeg -i input.mp4 -ss 00:05 -to 00:12 output.mp4

# Method 2: Start + Duration
ffmpeg -i input.mp4 -ss 00:05 -t 7 output.mp4
```

---

### Quality Settings

**CRF (Constant Rate Factor) - Best for Most Use Cases:**
```bash
-crf 18   # High quality, large file
-crf 20   # Very good quality (1080p web)
-crf 23   # Good quality (720p web)
-crf 28   # Acceptable quality (480p mobile)
-crf 32   # Low quality (preview/draft)
```

**Bitrate (CBR/VBR) - For Specific File Size Targets:**
```bash
# Constant bitrate
-b:v 2M

# Variable bitrate with max
-b:v 2M -maxrate 2.5M -bufsize 5M

# Two-pass encoding (best quality for target size)
# Pass 1
ffmpeg -i input.mp4 -c:v libx264 -b:v 2M -pass 1 -f null /dev/null
# Pass 2
ffmpeg -i input.mp4 -c:v libx264 -b:v 2M -pass 2 output.mp4
```

---

### Preset Settings (Speed vs Compression)

```bash
-preset ultrafast  # Fastest encoding, largest files
-preset superfast
-preset veryfast
-preset faster
-preset fast
-preset medium     # Default, balanced
-preset slow       # Better compression (2-3x slower)
-preset slower     # Best compression (5-10x slower)
-preset veryslow   # Maximum compression (extremely slow)
```

**Recommendation:**
- **Development/testing**: `ultrafast` (speed matters)
- **Production web**: `medium` (good balance)
- **Final delivery**: `slow` (quality matters)

---

### Stream Selection

```bash
# Video only (no audio)
-an

# Audio only (no video)
-vn

# Specific stream
-map 0:v:0   # First video stream
-map 0:a:0   # First audio stream
-map 0:a:1   # Second audio stream

# Multiple inputs
-i video.mp4 -i audio.mp3
-map 0:v:0   # Video from first input
-map 1:a:0   # Audio from second input
```

---

## Best Practices

### 1. Accuracy vs Speed Trade-offs

**Accurate Cutting (Use for Production):**
```bash
# SLOW but ACCURATE
ffmpeg -i input.mp4 -ss START -to END -c:v libx264 output.mp4
```
- Place `-ss`/`-to` AFTER `-i`
- Re-encode video (not stream copy)
- Frame-perfect timestamps
- No keyframe issues

**Fast Cutting (Use for Previews Only):**
```bash
# FAST but INACCURATE
ffmpeg -ss START -i input.mp4 -to END -c copy output.mp4
```
- Place `-ss` BEFORE `-i`
- Stream copy (no re-encode)
- May miss frames or have slight time drift
- Can produce corrupt clips

---

### 2. File Size Optimization

**Web Optimization Checklist:**
1. ✅ Use H.264 codec (`libx264`)
2. ✅ Set reasonable CRF (20-23 for 1080p, 23-28 for 720p)
3. ✅ Add `-movflags +faststart` (streaming)
4. ✅ Scale resolution if oversized (`-vf scale=-2:720`)
5. ✅ Use AAC audio at 128kbps
6. ✅ Consider two-pass encoding for target size

**Example:**
```bash
ffmpeg -i large.mp4 \
  -c:v libx264 -preset medium -crf 23 \
  -vf "scale=-2:720" \
  -c:a aac -b:a 128k \
  -movflags +faststart \
  optimized.mp4
```

---

### 3. Batch Processing

**Process All MP4 Files in Directory:**
```bash
for file in *.mp4; do
  ffmpeg -i "$file" \
    -c:v libx264 -crf 23 \
    -c:a aac \
    "converted_${file}"
done
```

**Parallel Processing (GNU Parallel):**
```bash
find . -name "*.mp4" | parallel -j 4 \
  ffmpeg -i {} -c:v libx264 -crf 23 {.}_converted.mp4
```

---

### 4. Error Handling

**Check FFmpeg Installation:**
```bash
ffmpeg -version
ffprobe -version
```

**Verify Input File:**
```bash
ffprobe -v error input.mp4
# No output = file OK
# Error messages = file corrupted
```

**Test Command Without Encoding:**
```bash
# Dry run (no output file)
ffmpeg -i input.mp4 -ss 00:05 -to 00:12 -f null -
```

---

### 5. Logging and Debugging

**Minimal Output:**
```bash
ffmpeg -hide_banner -loglevel error -i input.mp4 output.mp4
```

**Detailed Progress:**
```bash
ffmpeg -hide_banner -loglevel info -i input.mp4 output.mp4
```

**Full Debug Info:**
```bash
ffmpeg -hide_banner -loglevel debug -i input.mp4 output.mp4 2> debug.log
```

**Log Levels:**
- `quiet`: No output
- `panic`: Only critical errors
- `fatal`: Fatal errors only
- `error`: Errors only
- `warning`: Warnings + errors
- `info`: Info + warnings + errors (default)
- `verbose`: Verbose info
- `debug`: Debug info

---

## Common Recipes

### Recipe 1: Instagram Reel (9:16 vertical, 1080x1920)
```bash
ffmpeg -i input.mp4 \
  -vf "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2,setsar=1" \
  -c:v libx264 -preset medium -crf 23 \
  -c:a aac -b:a 128k \
  -movflags +faststart \
  instagram_reel.mp4
```

### Recipe 2: YouTube Video (16:9, 1080p optimized)
```bash
ffmpeg -i input.mp4 \
  -vf "scale=-2:1080" \
  -c:v libx264 -preset slow -crf 18 \
  -c:a aac -b:a 192k \
  -movflags +faststart \
  youtube_1080p.mp4
```

### Recipe 3: Twitter/X Video (< 512MB, max 2:20)
```bash
ffmpeg -i input.mp4 -t 140 \
  -vf "scale=-2:720" \
  -c:v libx264 -preset medium -crf 23 -maxrate 2M -bufsize 4M \
  -c:a aac -b:a 128k \
  -movflags +faststart \
  twitter.mp4
```

### Recipe 4: GIF from Video
```bash
ffmpeg -i input.mp4 -ss 00:05 -to 00:10 \
  -vf "fps=10,scale=480:-1:flags=lanczos,split[s0][s1];[s0]palettegen[p];[s1][p]paletteuse" \
  output.gif
```

### Recipe 5: Silent B-Roll Clip (No Audio)
```bash
ffmpeg -i input.mp4 -ss 00:05 -to 00:12 \
  -an \
  -c:v libx264 -preset ultrafast -crf 18 \
  -movflags +faststart \
  broll_silent.mp4
```

### Recipe 6: Extract 10-Second Clips Every Minute
```bash
#!/bin/bash
DURATION=$(ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 input.mp4)
for (( i=0; i<${DURATION%.*}; i+=60 )); do
  END=$((i+10))
  ffmpeg -i input.mp4 -ss $i -to $END \
    -c:v libx264 -preset ultrafast -crf 18 \
    -c:a aac \
    clip_$(printf "%03d" $((i/60+1))).mp4
done
```

---

## Skill Integration Pattern

### Directory Structure

```
.claude/skills/ffmpeg/
├── SKILL.md                    # This file
├── resources/
│   ├── quality-presets.md      # CRF/bitrate recommendations
│   ├── platform-specs.md       # Instagram, YouTube, TikTok specs
│   └── troubleshooting.md      # Common errors and fixes
└── servers/
    └── ffmpeg-wrapper.sh       # Bash script wrapper (optional)
```

### Usage by Agent

**1. Load Skill (Manual for MVP):**
```
Agent: "Load FFmpeg skill"
→ Reads .claude/skills/ffmpeg/SKILL.md
```

**2. Execute FFmpeg Commands:**
```typescript
// Agent writes TypeScript code that executes FFmpeg
import { exec } from 'child_process';
import { promisify } from 'util';

const execAsync = promisify(exec);

// Cut clip with accurate method
await execAsync(`ffmpeg -hide_banner -y -i input.mp4 -ss 00:05 -to 00:12 -c:v libx264 -preset ultrafast -crf 18 -c:a aac -movflags +faststart output.mp4`);

// Get duration
const { stdout } = await execAsync(`ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 video.mp4`);
const duration = parseFloat(stdout);
```

**3. Capture Output:**
```typescript
// Execute and capture result
const { stdout, stderr } = await execAsync(ffmpegCommand);

// Parse metadata
const duration = parseFloat(stdout.trim());
const [width, height] = stdout.trim().split(',').map(Number);
```

---

## Performance Considerations

**Encoding Speed Hierarchy (Fastest → Slowest):**
1. Stream copy (`-c copy`) - No re-encoding
2. Hardware encoding (`h264_nvenc`, `h264_videotoolbox`) - GPU acceleration
3. Software encoding with ultrafast preset - Minimal compression
4. Software encoding with medium preset - Balanced
5. Software encoding with slow/slower preset - Maximum compression

**File Size Hierarchy (Smallest → Largest):**
1. High CRF + slow preset + low resolution
2. Low CRF + slow preset + low resolution
3. High CRF + fast preset + high resolution
4. Low CRF + slow preset + high resolution

**Typical Processing Times (1-minute 1080p video on modern CPU):**
- Stream copy: ~2 seconds
- Ultrafast preset + CRF 23: ~10-15 seconds
- Medium preset + CRF 23: ~30-45 seconds
- Slow preset + CRF 18: ~90-120 seconds

---

## Troubleshooting

### Issue: "No such file or directory"
**Solution:** Check file path, use quotes for spaces
```bash
ffmpeg -i "path with spaces/video.mp4" output.mp4
```

### Issue: "Invalid argument" for timestamps
**Solution:** Use proper timestamp format (MM:SS not M:S)
```bash
# Wrong
-ss 1:5

# Correct
-ss 01:05
```

### Issue: "Codec not supported"
**Solution:** Check available codecs
```bash
ffmpeg -codecs | grep h264
ffmpeg -codecs | grep aac
```

### Issue: Output file too large
**Solution:** Increase CRF, decrease resolution, or use two-pass
```bash
# Higher CRF (lower quality, smaller file)
-crf 28

# Lower resolution
-vf "scale=-2:480"

# Two-pass for target size
-b:v 1M -pass 1
```

### Issue: Audio out of sync
**Solution:** Use accurate cutting method (re-encode, not stream copy)
```bash
# Re-encode instead of copy
-c:v libx264 -c:a aac
```

### Issue: Green screen or corruption
**Solution:** Don't use stream copy for cutting, always re-encode
```bash
# Wrong (can corrupt)
ffmpeg -ss 00:05 -i input.mp4 -to 00:12 -c copy output.mp4

# Correct (reliable)
ffmpeg -i input.mp4 -ss 00:05 -to 00:12 -c:v libx264 -c:a aac output.mp4
```

---

## References

**Official Documentation:**
- FFmpeg: https://ffmpeg.org/documentation.html
- FFprobe: https://ffmpeg.org/ffprobe.html

**Key Guides:**
- H.264 Encoding: https://trac.ffmpeg.org/wiki/Encode/H.264
- VP9 Encoding: https://trac.ffmpeg.org/wiki/Encode/VP9
- Filtering Guide: https://ffmpeg.org/ffmpeg-filters.html

**Useful Tools:**
- FFmpeg Command Builder: https://evanhahn.github.io/ffmpeg-buddy/
- Video Format Comparison: https://caniuse.com/mpeg4

---

## Summary

This skill provides comprehensive FFmpeg capabilities for video processing. The core workflows cover the most common operations:

1. **Accurate clip cutting** (slow re-encode method) - Production quality
2. **Quality conversion** (high → low for web) - File size optimization
3. **Metadata extraction** (duration, resolution, codec) - Video analysis
4. **Format conversion** (MP4, WebM, MOV) - Universal compatibility
5. **Resolution changes** (scale, crop, aspect ratio) - Platform optimization
6. **Audio operations** (extract, remove, replace, normalize) - Audio control
7. **Concatenation** (merge clips) - Video assembly
8. **Speed adjustments** (fast/slow motion) - Pacing control
9. **Frame extraction** (thumbnails, sequences) - Still image generation

**Key Principle:** Use accurate re-encode method for production, fast stream copy only for previews.

**Integration:** Agent loads SKILL.md, executes FFmpeg commands via bash, captures stdout for results.

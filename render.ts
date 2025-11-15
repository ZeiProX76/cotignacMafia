#!/usr/bin/env node
import { bundle } from '@remotion/bundler';
import { renderMedia, selectComposition } from '@remotion/renderer';
import path from 'path';
import fs from 'fs';
import { TimelineConfig } from './remotion/src/types';

/**
 * CLI tool to render videos from JSON timeline configuration
 * Usage: npm run render -- --json=timeline.json --output=final.mp4
 */
async function renderVideo() {
  // Parse command line arguments
  const args = process.argv.slice(2);
  const jsonArg = args.find((arg) => arg.startsWith('--json='));
  const outputArg = args.find((arg) => arg.startsWith('--output='));

  if (!jsonArg) {
    console.error('❌ Error: --json parameter is required');
    console.log('Usage: npm run render -- --json=timeline.json --output=final.mp4');
    process.exit(1);
  }

  const jsonPath = jsonArg.split('=')[1];
  const outputPath = outputArg ? outputArg.split('=')[1] : 'out/video.mp4';

  // Check if JSON file exists
  if (!fs.existsSync(jsonPath)) {
    console.error(`❌ Error: JSON file not found: ${jsonPath}`);
    process.exit(1);
  }

  // Read and parse timeline configuration
  console.log(`📖 Reading timeline configuration from ${jsonPath}...`);
  const timelineConfig: TimelineConfig = JSON.parse(
    fs.readFileSync(jsonPath, 'utf-8')
  );

  // Validate required fields
  if (!timelineConfig.mainVideo) {
    console.error('❌ Error: mainVideo is required in timeline configuration');
    process.exit(1);
  }

  if (!timelineConfig.fps) {
    console.error('❌ Error: fps is required in timeline configuration');
    process.exit(1);
  }

  console.log('✅ Timeline configuration loaded successfully');
  console.log(`   Main video: ${timelineConfig.mainVideo}`);
  console.log(`   FPS: ${timelineConfig.fps}`);
  console.log(`   Overlays: ${timelineConfig.overlays.length}`);

  try {
    // Bundle the Remotion project
    console.log('\n📦 Bundling Remotion project...');
    const bundleLocation = await bundle({
      entryPoint: path.resolve('./remotion/src/index.ts'),
      webpackOverride: (config) => config,
    });
    console.log('✅ Bundle created');

    // Get composition
    console.log('\n🎬 Loading composition...');
    const composition = await selectComposition({
      serveUrl: bundleLocation,
      id: 'VideoComposition',
      inputProps: {
        timeline: timelineConfig,
      },
    });

    // Override composition settings with timeline config
    const fps = timelineConfig.fps;
    const width = timelineConfig.width || composition.width;
    const height = timelineConfig.height || composition.height;
    const durationInSeconds = timelineConfig.durationInSeconds || composition.durationInFrames / fps;
    const durationInFrames = Math.round(durationInSeconds * fps);

    console.log(`✅ Composition loaded`);
    console.log(`   Resolution: ${width}x${height}`);
    console.log(`   Duration: ${durationInSeconds}s (${durationInFrames} frames)`);

    // Ensure output directory exists
    const outputDir = path.dirname(outputPath);
    if (!fs.existsSync(outputDir)) {
      fs.mkdirSync(outputDir, { recursive: true });
    }

    // Render video
    console.log(`\n🎥 Rendering video to ${outputPath}...`);
    console.log('⏳ This may take a few minutes...\n');

    await renderMedia({
      composition: {
        ...composition,
        fps,
        width,
        height,
        durationInFrames,
      },
      serveUrl: bundleLocation,
      codec: 'h264',
      outputLocation: outputPath,
      inputProps: {
        timeline: timelineConfig,
      },
      onProgress: ({ progress, renderedFrames, encodedFrames }) => {
        const percent = (progress * 100).toFixed(1);
        process.stdout.write(
          `\r   Progress: ${percent}% | Rendered: ${renderedFrames}/${durationInFrames} | Encoded: ${encodedFrames}/${durationInFrames}`
        );
      },
    });

    console.log('\n\n✅ Video rendered successfully!');
    console.log(`📹 Output: ${outputPath}`);
  } catch (error) {
    console.error('\n❌ Error during rendering:', error);
    process.exit(1);
  }
}

renderVideo();

import React from 'react';
import { Composition as RemotionComposition } from 'remotion';
import { Composition } from './Composition';
import { TimelineConfig } from './types';

// Default timeline for preview
const defaultTimeline: TimelineConfig = {
  mainVideo: 'https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4',
  fps: 60,
  width: 1920,
  height: 1080,
  durationInSeconds: 10,
  overlays: [
    {
      type: 'video',
      src: 'https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4',
      startSeconds: 2,
      durationSeconds: 5,
      position: 'top-right',
      animation: 'slide-left',
      width: 400,
      height: 400,
    },
    {
      type: 'text',
      text: 'Welcome to Remotion!',
      startSeconds: 1,
      durationSeconds: 3,
      position: 'bottom-left',
      fontSize: 48,
      color: '#ffffff',
    },
  ],
};

export const Root: React.FC = () => {
  return (
    <>
      <RemotionComposition
        id="VideoComposition"
        component={() => <Composition timeline={defaultTimeline} />}
        durationInFrames={Math.round((defaultTimeline.durationInSeconds || 30) * defaultTimeline.fps)}
        fps={defaultTimeline.fps}
        width={defaultTimeline.width || 1920}
        height={defaultTimeline.height || 1080}
      />
    </>
  );
};

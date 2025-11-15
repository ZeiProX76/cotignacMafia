import React from 'react';
import {
  AbsoluteFill,
  Video,
  Sequence,
  useCurrentFrame,
  useVideoConfig,
} from 'remotion';
import { VideoOverlayConfig } from './types';
import { getSlideAnimation } from './animations';
import { getPositionStyles } from './positioning';

interface VideoOverlayProps {
  config: VideoOverlayConfig;
}

/**
 * Renders a video overlay with animations
 */
export const VideoOverlay: React.FC<VideoOverlayProps> = ({ config }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const startFrame = Math.round(config.startSeconds * fps);
  const durationInFrames = Math.round(config.durationSeconds * fps);
  const endFrame = startFrame + durationInFrames;

  const width = config.width || 400;
  const height = config.height || 400;
  const borderRadius = config.borderRadius || 24;

  const animation = getSlideAnimation({
    frame,
    startFrame,
    endFrame,
    fps,
    animationType: config.animation,
    animationDurationSeconds: 0.5,
  });

  const positionStyles = getPositionStyles(config.position, width, height);

  return (
    <Sequence from={startFrame} durationInFrames={durationInFrames}>
      <AbsoluteFill
        style={{
          ...positionStyles,
          width,
          height,
          opacity: animation.opacity,
          transform: `${positionStyles.transform || ''} translateX(${animation.translateX}px) translateY(${animation.translateY}px)`,
          borderRadius,
          overflow: 'hidden',
          boxShadow: '0 10px 40px rgba(0, 0, 0, 0.3)',
        }}
      >
        <Video src={config.src} />
      </AbsoluteFill>
    </Sequence>
  );
};

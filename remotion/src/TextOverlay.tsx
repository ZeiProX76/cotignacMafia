import React from 'react';
import {
  AbsoluteFill,
  Sequence,
  useCurrentFrame,
  useVideoConfig,
  interpolate,
} from 'remotion';
import { TextOverlayConfig } from './types';
import { getPositionStyles } from './positioning';

interface TextOverlayProps {
  config: TextOverlayConfig;
}

/**
 * Renders a text overlay with fade-in/out animations
 */
export const TextOverlay: React.FC<TextOverlayProps> = ({ config }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const startFrame = Math.round(config.startSeconds * fps);
  const durationInFrames = Math.round(config.durationSeconds * fps);
  const endFrame = startFrame + durationInFrames;

  const fontSize = config.fontSize || 48;
  const fontWeight = config.fontWeight || 'bold';
  const color = config.color || '#ffffff';
  const backgroundColor = config.backgroundColor || 'rgba(0, 0, 0, 0.7)';
  const padding = config.padding || 20;
  const borderRadius = config.borderRadius || 12;

  // Fade in/out animation (0.3s each)
  const fadeFrames = Math.round(0.3 * fps);
  const entranceEnd = startFrame + fadeFrames;
  const exitStart = endFrame - fadeFrames;

  const opacity = interpolate(
    frame,
    [startFrame, entranceEnd, exitStart, endFrame],
    [0, 1, 1, 0],
    {
      extrapolateLeft: 'clamp',
      extrapolateRight: 'clamp',
    }
  );

  const scale = interpolate(
    frame,
    [startFrame, entranceEnd, exitStart, endFrame],
    [0.95, 1, 1, 0.95],
    {
      extrapolateLeft: 'clamp',
      extrapolateRight: 'clamp',
    }
  );

  // For text, we don't use exact pixel positioning, just use the position as a guide
  const positionStyles = getPositionStyles(config.position, 0, 0);

  return (
    <Sequence from={startFrame} durationInFrames={durationInFrames}>
      <AbsoluteFill
        style={{
          ...positionStyles,
          display: 'flex',
          alignItems: 'flex-start',
          justifyContent: 'flex-start',
          pointerEvents: 'none',
        }}
      >
        <div
          style={{
            fontSize,
            fontWeight,
            color,
            backgroundColor,
            padding,
            borderRadius,
            opacity,
            transform: `scale(${scale})`,
            boxShadow: '0 4px 20px rgba(0, 0, 0, 0.4)',
            maxWidth: '80%',
            wordWrap: 'break-word',
          }}
        >
          {config.text}
        </div>
      </AbsoluteFill>
    </Sequence>
  );
};

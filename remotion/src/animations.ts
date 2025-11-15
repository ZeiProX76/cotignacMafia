import { interpolate } from 'remotion';
import { AnimationType } from './types';

export interface AnimationConfig {
  frame: number;
  startFrame: number;
  endFrame: number;
  fps: number;
  animationType: AnimationType;
  animationDurationSeconds?: number;
}

export interface AnimationResult {
  opacity: number;
  translateX: number;
  translateY: number;
}

/**
 * Calculate animation values for slide animations
 * @param config Animation configuration
 * @returns Animation values (opacity, translateX, translateY)
 */
export function getSlideAnimation(config: AnimationConfig): AnimationResult {
  const {
    frame,
    startFrame,
    endFrame,
    fps,
    animationType,
    animationDurationSeconds = 0.5,
  } = config;

  const animationDurationFrames = Math.round(animationDurationSeconds * fps);
  const entranceEnd = startFrame + animationDurationFrames;
  const exitStart = endFrame - animationDurationFrames;

  // Entrance animation (fade + slide in)
  const opacity = interpolate(
    frame,
    [startFrame, entranceEnd, exitStart, endFrame],
    [0, 1, 1, 0],
    {
      extrapolateLeft: 'clamp',
      extrapolateRight: 'clamp',
    }
  );

  let translateX = 0;
  let translateY = 0;

  switch (animationType) {
    case 'slide-left':
      // Slide in from the right, exit to the left
      translateX = interpolate(
        frame,
        [startFrame, entranceEnd, exitStart, endFrame],
        [200, 0, 0, -200],
        {
          extrapolateLeft: 'clamp',
          extrapolateRight: 'clamp',
        }
      );
      break;

    case 'slide-right':
      // Slide in from the left, exit to the right
      translateX = interpolate(
        frame,
        [startFrame, entranceEnd, exitStart, endFrame],
        [-200, 0, 0, 200],
        {
          extrapolateLeft: 'clamp',
          extrapolateRight: 'clamp',
        }
      );
      break;

    case 'slide-top':
      // Slide in from the bottom, exit to the top
      translateY = interpolate(
        frame,
        [startFrame, entranceEnd, exitStart, endFrame],
        [200, 0, 0, -200],
        {
          extrapolateLeft: 'clamp',
          extrapolateRight: 'clamp',
        }
      );
      break;
  }

  return { opacity, translateX, translateY };
}

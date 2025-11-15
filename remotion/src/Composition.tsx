import React from 'react';
import { AbsoluteFill, Video, staticFile } from 'remotion';
import { TimelineConfig } from './types';
import { VideoOverlay } from './VideoOverlay';
import { TextOverlay } from './TextOverlay';

interface CompositionProps {
  timeline: TimelineConfig;
}

/**
 * Main video composition component
 * Renders the main video with all overlays according to timeline configuration
 */
export const Composition: React.FC<CompositionProps> = ({ timeline }) => {
  return (
    <AbsoluteFill style={{ backgroundColor: '#000' }}>
      {/* Main video layer */}
      <Video src={timeline.mainVideo} />

      {/* Render all overlays */}
      {timeline.overlays.map((overlay, index) => {
        if (overlay.type === 'video') {
          return <VideoOverlay key={`video-${index}`} config={overlay} />;
        } else if (overlay.type === 'text') {
          return <TextOverlay key={`text-${index}`} config={overlay} />;
        }
        return null;
      })}
    </AbsoluteFill>
  );
};

export type AnimationType = 'slide-left' | 'slide-right' | 'slide-top';

export type Position =
  | 'top-left'
  | 'top-right'
  | 'bottom-left'
  | 'bottom-right'
  | 'center';

export interface VideoOverlayConfig {
  type: 'video';
  src: string;
  startSeconds: number;
  durationSeconds: number;
  position: Position;
  animation: AnimationType;
  width?: number;
  height?: number;
  borderRadius?: number;
}

export interface TextOverlayConfig {
  type: 'text';
  text: string;
  startSeconds: number;
  durationSeconds: number;
  position: Position;
  fontSize?: number;
  fontWeight?: string | number;
  color?: string;
  backgroundColor?: string;
  padding?: number;
  borderRadius?: number;
}

export interface TimelineConfig {
  mainVideo: string;
  fps: number;
  durationInSeconds?: number;
  width?: number;
  height?: number;
  overlays: (VideoOverlayConfig | TextOverlayConfig)[];
}

export interface PositionStyle {
  top?: number;
  bottom?: number;
  left?: number;
  right?: number;
  transform?: string;
}

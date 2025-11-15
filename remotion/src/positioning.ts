import { Position, PositionStyle } from './types';

/**
 * Get CSS positioning styles based on position preset
 * @param position Position preset
 * @param width Width of the element
 * @param height Height of the element
 * @param margin Margin from edges (default: 60px)
 * @returns CSS positioning styles
 */
export function getPositionStyles(
  position: Position,
  width: number,
  height: number,
  margin: number = 60
): PositionStyle {
  const styles: PositionStyle = {};

  switch (position) {
    case 'top-left':
      styles.top = margin;
      styles.left = margin;
      break;

    case 'top-right':
      styles.top = margin;
      styles.right = margin;
      break;

    case 'bottom-left':
      styles.bottom = margin;
      styles.left = margin;
      break;

    case 'bottom-right':
      styles.bottom = margin;
      styles.right = margin;
      break;

    case 'center':
      styles.top = 0;
      styles.left = 0;
      styles.right = 0;
      styles.bottom = 0;
      styles.transform = 'translate(-50%, -50%)';
      // For centered items, we need to position them at 50% with transform
      styles.top = '50%' as any;
      styles.left = '50%' as any;
      delete styles.right;
      delete styles.bottom;
      break;
  }

  return styles;
}

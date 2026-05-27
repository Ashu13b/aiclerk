import React from 'react';
import Svg, { Circle } from 'react-native-svg';

type Props = { pct: number; size?: number; stroke?: number; color: string; bg: string };

export function ProgressRing({ pct, size = 56, stroke = 5, color, bg }: Props) {
  const r = (size - stroke * 2) / 2;
  const circ = 2 * Math.PI * r;
  const dash = (pct / 100) * circ;
  const cx = size / 2;
  return (
    <Svg width={size} height={size} style={{ transform: [{ rotate: '-90deg' }] }}>
      <Circle cx={cx} cy={cx} r={r} fill="none" stroke={bg} strokeWidth={stroke} />
      <Circle
        cx={cx} cy={cx} r={r} fill="none"
        stroke={color} strokeWidth={stroke}
        strokeDasharray={`${dash} ${circ}`}
        strokeLinecap="round"
      />
    </Svg>
  );
}

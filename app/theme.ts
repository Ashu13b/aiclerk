export const MED = {
  bg0:    '#04060f',
  bg1:    '#080d1a',
  bg2:    '#0d1425',
  green:  '#00e5a0',
  cyan:   '#00cfff',
  red:    '#ff3d5a',
  amber:  '#ffb020',
  violet: '#a78bfa',
  textHi:  '#e8f4f0',
  textMid: '#7eb8a4',
  textLow: '#3a5a50',
  border:  '#1a3d30',
} as const;

export type Theme = ReturnType<typeof getTheme>;

export function getTheme(accent: string, dark: boolean) {
  return {
    bg:          dark ? MED.bg0     : '#f0faf6',
    card:        dark ? MED.bg1     : '#ffffff',
    card2:       dark ? MED.bg2     : '#e4f7ef',
    text:        dark ? MED.textHi  : '#0a2018',
    muted:       dark ? MED.textMid : '#3d7a62',
    border:      dark ? MED.border  : '#b8e8d0',
    accent:      dark ? accent      : '#00a870',
    accentMuted: dark ? accent + '28' : '#00a87018',
    success:     MED.green,
    danger:      dark ? MED.red     : '#d42b47',
    warning:     dark ? MED.amber   : '#c47800',
    cyan:        dark ? MED.cyan    : '#0099cc',
    violet:      dark ? MED.violet  : '#7c5cbf',
    dark,
  };
}

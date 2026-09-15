/** Единый источник дизайн-токенов TrafficMaster Pro. */

export const theme = {
  colors: {
    bg:           '#F5EFE6',
    bgElevated:   '#FDFBF7',
    bgSunken:     '#EDE4D3',
    textPrimary:  '#2D1B0E',
    textBody:     '#3D2B1F',
    textMuted:    '#7A6652',
    textInverse:  '#FDFBF7',
    accent:       '#C0603A',
    accentHover:  '#A34A28',
    accentSoft:   '#F2DDD3',
    success:      '#6B8E5A',
    successSoft:  '#E4EDDD',
    warning:      '#D49A3E',
    error:        '#B54A3A',
    errorSoft:    '#F2D9D3',
    border:       '#E8DFD2',
    borderStrong: '#D4C8B5',
  },
  fonts: {
    sans: 'system-ui, -apple-system, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif',
    mono: 'ui-monospace, "SF Mono", Menlo, Consolas, monospace',
  },
  sizes: {
    h1: 'clamp(40px, 6vw, 72px)',
    h2: 'clamp(28px, 4vw, 40px)',
    h3: '24px',
    bodyLg: '20px',
    body: '18px',
    bodySm: '16px',
    caption: '14px',
    micro: '13px',
    xs: '8px', sm: '16px', md: '24px',
    lg: '40px', xl: '64px', xxl: '96px', xxxl: '128px',
  },
  radii: { sm: '6px', md: '12px', lg: '20px', full: '999px' },
  shadows: {
    card:  '0 2px 8px rgba(45, 27, 14, 0.06), 0 1px 2px rgba(45, 27, 14, 0.04)',
    hover: '0 6px 20px rgba(45, 27, 14, 0.10)',
  },
  layout: {
    maxContent: '1200px',
    maxText:    '680px',
  },
  transitions: {
    fast:   '150ms ease-out',
    normal: '200ms ease-out',
    slow:   '300ms ease-out',
  },
}

export default theme

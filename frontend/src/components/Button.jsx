/** Кнопка дизайн-системы: primary, secondary и ghost. */

import { useState } from 'react'

import theme from '../styles/theme'

function Button({
  variant = 'primary',
  size = 'md',
  fullWidth = false,
  children,
  onClick,
  type = 'button',
  disabled = false,
}) {
  const [hovered, setHovered] = useState(false)

  const sizeStyles =
    size === 'lg'
      ? { padding: '16px 32px', fontSize: theme.sizes.body }
      : { padding: '12px 24px', fontSize: theme.sizes.bodySm }

  const variants = {
    primary: {
      background: hovered && !disabled ? theme.colors.accentHover : theme.colors.accent,
      color: theme.colors.textInverse,
      border: 'none',
    },
    secondary: {
      background: hovered && !disabled ? theme.colors.accentSoft : 'transparent',
      color: theme.colors.accent,
      border: `1px solid ${theme.colors.accent}`,
    },
    ghost: {
      background: 'transparent',
      color: theme.colors.textBody,
      border: 'none',
    },
  }

  return (
    <button
      type={type}
      onClick={onClick}
      disabled={disabled}
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
      style={{
        ...sizeStyles,
        ...variants[variant],
        borderRadius: theme.radii.full,
        transition: theme.transitions.fast,
        width: fullWidth ? '100%' : 'auto',
        opacity: disabled ? 0.5 : 1,
        cursor: disabled ? 'not-allowed' : 'pointer',
        fontWeight: 700,
      }}
    >
      {children}
    </button>
  )
}

export default Button

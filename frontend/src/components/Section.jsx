/** Секция лендинга с ограничением ширины и вариантами фона. */

import theme from '../styles/theme'

const BACKGROUNDS = {
  default: 'transparent',
  elevated: theme.colors.bgElevated,
  sunken: theme.colors.bgSunken,
}

function Section({ id, children, background = 'default' }) {
  return (
    <section
      id={id}
      style={{
        padding: `${theme.sizes.xxl} ${theme.sizes.md}`,
        background: BACKGROUNDS[background],
        scrollMarginTop: '80px',
      }}
    >
      <div style={{ maxWidth: theme.layout.maxContent, margin: '0 auto' }}>{children}</div>
    </section>
  )
}

export default Section

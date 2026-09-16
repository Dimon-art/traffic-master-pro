/** Подвал сайта со ссылками и копирайтом. */

import { Link } from 'react-router-dom'

import theme from '../styles/theme'

function Footer() {
  return (
    <footer
      style={{
        background: theme.colors.bgSunken,
        padding: `${theme.sizes.xl} ${theme.sizes.md}`,
        textAlign: 'center',
      }}
    >
      <p
        style={{
          margin: 0,
          color: theme.colors.textPrimary,
          fontSize: theme.sizes.bodySm,
        }}
      >
        TrafficMaster Pro · © 2026
      </p>
      <p
        style={{
          margin: `${theme.sizes.sm} 0`,
          fontSize: theme.sizes.bodySm,
          color: theme.colors.textMuted,
        }}
      >
        <Link to="/lead">Оставить заявку</Link>
        {' · '}
        <Link to="/admin">Техническая панель</Link>
        {' · '}
        <a href="#">GitHub</a>
        {' · '}
        <a href="#">Telegram</a>
        {' · '}
        <a href="mailto:support@trafficmaster.pro">support@trafficmaster.pro</a>
      </p>
      <p
        style={{
          margin: 0,
          color: theme.colors.textMuted,
          fontSize: theme.sizes.caption,
        }}
      >
        Нейро-тренер для экспертов по продвижению в Telegram
      </p>
    </footer>
  )
}

export default Footer

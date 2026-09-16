/** Фиксированная шапка с якорной навигацией и кнопкой входа или выхода. */

import { useEffect, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'

import { useAuth } from '../context/AuthContext'
import theme from '../styles/theme'
import Button from './Button'

function Navbar() {
  const { user, isAdmin, logout } = useAuth()
  const navigate = useNavigate()
  const [scrolled, setScrolled] = useState(false)
  const [isMobile, setIsMobile] = useState(false)

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 20)
    const onResize = () => setIsMobile(window.innerWidth < 768)
    onScroll()
    onResize()
    window.addEventListener('scroll', onScroll, { passive: true })
    window.addEventListener('resize', onResize)
    return () => {
      window.removeEventListener('scroll', onScroll)
      window.removeEventListener('resize', onResize)
    }
  }, [])

  const handleLogout = () => {
    logout()
    navigate('/')
  }

  return (
    <header
      style={{
        position: 'fixed',
        top: 0,
        width: '100%',
        zIndex: 100,
        height: '72px',
        background: scrolled ? theme.colors.bgElevated : 'transparent',
        boxShadow: scrolled ? theme.shadows.card : 'none',
        transition: theme.transitions.normal,
      }}
    >
      <nav
        style={{
          maxWidth: theme.layout.maxContent,
          margin: '0 auto',
          height: '100%',
          padding: `0 ${theme.sizes.md}`,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          gap: theme.sizes.sm,
        }}
      >
        <Link
          to="/"
          style={{
            color: theme.colors.textPrimary,
            fontWeight: 800,
            fontSize: theme.sizes.bodySm,
            whiteSpace: 'nowrap',
          }}
        >
          TrafficMaster Pro
        </Link>
        {!isMobile && (
          <div style={{ display: 'flex', gap: theme.sizes.md }}>
            <a href="/#about" style={{ color: theme.colors.textBody }}>
              О тренере
            </a>
            <a href="/#modes" style={{ color: theme.colors.textBody }}>
              Режимы
            </a>
            <a href="/#how" style={{ color: theme.colors.textBody }}>
              Как работает
            </a>
          </div>
        )}
        <div style={{ display: 'flex', alignItems: 'center', gap: theme.sizes.sm, flexWrap: 'wrap' }}>
          {user ? (
            <>
              {isAdmin ? (
                <>
                  <Link to="/trainings" style={{ color: theme.colors.textBody, fontSize: theme.sizes.bodySm }}>
                    Мои тренировки
                  </Link>
                  <Link to="/leads" style={{ color: theme.colors.textBody, fontSize: theme.sizes.bodySm }}>
                    Заявки
                  </Link>
                  <Link
                    to="/admin/users"
                    style={{ color: theme.colors.textBody, fontSize: theme.sizes.bodySm }}
                  >
                    Пользователи
                  </Link>
                </>
              ) : (
                <>
                  <Link to="/trainings" style={{ color: theme.colors.textBody, fontSize: theme.sizes.bodySm }}>
                    Мои тренировки
                  </Link>
                  <Link to="/leads" style={{ color: theme.colors.textBody, fontSize: theme.sizes.bodySm }}>
                    Мои заявки
                  </Link>
                </>
              )}
              <span
                title={user.name ? `${user.name} (${user.email})` : user.email}
                style={{
                  color: theme.colors.textBody,
                  fontSize: theme.sizes.bodySm,
                  maxWidth: isMobile ? '140px' : '300px',
                  overflow: 'hidden',
                  textOverflow: 'ellipsis',
                  whiteSpace: 'nowrap',
                }}
              >
                {user.name ? `${user.name} (${user.email})` : user.email}
              </span>
              <Button variant="secondary" size="md" onClick={handleLogout}>
                Выйти
              </Button>
            </>
          ) : (
            <Button variant="primary" size="md" onClick={() => navigate('/login')}>
              Войти
            </Button>
          )}
        </div>
      </nav>
    </header>
  )
}

export default Navbar

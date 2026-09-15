/** Страница входа: форма-заглушка до появления авторизации. */

import { useState } from 'react'

import Footer from '../components/Footer'
import Navbar from '../components/Navbar'
import Section from '../components/Section'
import Button from '../components/Button'
import theme from '../styles/theme'

function Login() {
  const [submitting, setSubmitting] = useState(false)

  const handleSubmit = (event) => {
    event.preventDefault()
    setSubmitting(true)
    window.setTimeout(() => {
      setSubmitting(false)
      window.alert('Функция входа появится на следующем шаге')
    }, 800)
  }

  const fieldStyle = {
    padding: '12px',
    borderRadius: theme.radii.md,
    border: `1px solid ${theme.colors.border}`,
    fontSize: theme.sizes.bodySm,
    width: '100%',
    marginBottom: theme.sizes.sm,
    background: theme.colors.bg,
    color: theme.colors.textBody,
    fontFamily: theme.fonts.sans,
  }

  const labelStyle = {
    display: 'block',
    marginBottom: theme.sizes.xs,
    fontSize: theme.sizes.bodySm,
    color: theme.colors.textPrimary,
    fontWeight: 600,
  }

  return (
    <>
      <Navbar />
      <main>
        <Section>
          <div
            style={{
              maxWidth: '440px',
              margin: '120px auto',
              padding: '48px',
              background: theme.colors.bgElevated,
              borderRadius: theme.radii.lg,
              boxShadow: theme.shadows.card,
            }}
          >
            <h1 style={{ fontSize: '32px', textAlign: 'center' }}>Вход в аккаунт</h1>
            <p
              style={{
                color: theme.colors.textMuted,
                textAlign: 'center',
                marginBottom: '32px',
              }}
            >
              Войдите, чтобы начать тренировку
            </p>
            <form onSubmit={handleSubmit}>
              <label htmlFor="email" style={labelStyle}>
                Email
              </label>
              <input id="email" name="email" type="email" required autoComplete="email" style={fieldStyle} />
              <label htmlFor="password" style={labelStyle}>
                Пароль
              </label>
              <input
                id="password"
                name="password"
                type="password"
                required
                autoComplete="current-password"
                style={fieldStyle}
              />
              <label
                htmlFor="remember"
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: theme.sizes.xs,
                  marginBottom: theme.sizes.md,
                  fontSize: theme.sizes.bodySm,
                  color: theme.colors.textBody,
                }}
              >
                <input id="remember" name="remember" type="checkbox" />
                Запомнить меня
              </label>
              <Button type="submit" variant="primary" fullWidth disabled={submitting}>
                {submitting ? 'Отправляю...' : 'Войти'}
              </Button>
            </form>
            <p
              style={{
                color: theme.colors.textMuted,
                fontSize: theme.sizes.caption,
                textAlign: 'center',
                margin: `${theme.sizes.md} 0 0`,
              }}
            >
              <a href="#" style={{ color: theme.colors.textMuted }}>
                Забыли пароль?
              </a>
              {' · '}
              <a href="#" style={{ color: theme.colors.textMuted }}>
                Зарегистрироваться
              </a>
            </p>
          </div>
        </Section>
      </main>
      <Footer />
    </>
  )
}

export default Login

/** Страница регистрации нового пользователя. */

import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'

import Footer from '../components/Footer'
import Navbar from '../components/Navbar'
import Section from '../components/Section'
import Button from '../components/Button'
import { useAuth } from '../context/AuthContext'
import theme from '../styles/theme'

function Register() {
  const navigate = useNavigate()
  const { register } = useAuth()
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [passwordConfirm, setPasswordConfirm] = useState('')
  const [error, setError] = useState('')
  const [submitting, setSubmitting] = useState(false)

  const handleSubmit = async (event) => {
    event.preventDefault()
    setError('')
    if (password.length < 8) {
      setError('Пароль должен содержать не менее 8 символов')
      return
    }
    if (password !== passwordConfirm) {
      setError('Пароли не совпадают')
      return
    }
    setSubmitting(true)
    try {
      await register(name.trim() || null, email, password)
      navigate('/')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Не удалось зарегистрироваться')
    } finally {
      setSubmitting(false)
    }
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
            <h1 style={{ fontSize: '32px', textAlign: 'center' }}>Регистрация</h1>
            <p
              style={{
                color: theme.colors.textMuted,
                textAlign: 'center',
                marginBottom: '32px',
              }}
            >
              Создайте аккаунт, чтобы начать тренировку
            </p>
            {error ? (
              <div
                style={{
                  background: theme.colors.errorSoft,
                  color: theme.colors.error,
                  borderRadius: theme.radii.md,
                  padding: '12px 16px',
                  marginBottom: theme.sizes.sm,
                  fontSize: theme.sizes.bodySm,
                }}
              >
                {error}
              </div>
            ) : null}
            <form onSubmit={handleSubmit}>
              <label htmlFor="name" style={labelStyle}>
                Имя
              </label>
              <input
                id="name"
                name="name"
                type="text"
                autoComplete="name"
                placeholder="Например, Иван"
                value={name}
                onChange={(event) => setName(event.target.value)}
                style={fieldStyle}
              />
              <label htmlFor="email" style={labelStyle}>
                Email
              </label>
              <input
                id="email"
                name="email"
                type="email"
                required
                autoComplete="email"
                value={email}
                onChange={(event) => setEmail(event.target.value)}
                style={fieldStyle}
              />
              <label htmlFor="password" style={labelStyle}>
                Пароль
              </label>
              <input
                id="password"
                name="password"
                type="password"
                required
                minLength={8}
                autoComplete="new-password"
                value={password}
                onChange={(event) => setPassword(event.target.value)}
                style={fieldStyle}
              />
              <label htmlFor="passwordConfirm" style={labelStyle}>
                Повторите пароль
              </label>
              <input
                id="passwordConfirm"
                name="passwordConfirm"
                type="password"
                required
                minLength={8}
                autoComplete="new-password"
                value={passwordConfirm}
                onChange={(event) => setPasswordConfirm(event.target.value)}
                style={{ ...fieldStyle, marginBottom: theme.sizes.md }}
              />
              <Button type="submit" variant="primary" fullWidth disabled={submitting}>
                {submitting ? 'Отправляю...' : 'Зарегистрироваться'}
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
              <Link to="/login" style={{ color: theme.colors.textMuted }}>
                Уже есть аккаунт? Войти
              </Link>
            </p>
          </div>
        </Section>
      </main>
      <Footer />
    </>
  )
}

export default Register

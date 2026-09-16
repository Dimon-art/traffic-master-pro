/** Страница создания заявки на консультацию. */

import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'

import { apiFetch } from '../api/client'
import Footer from '../components/Footer'
import Navbar from '../components/Navbar'
import Section from '../components/Section'
import Button from '../components/Button'
import theme from '../styles/theme'

function Lead() {
  const navigate = useNavigate()
  const [name, setName] = useState('')
  const [phone, setPhone] = useState('')
  const [email, setEmail] = useState('')
  const [comment, setComment] = useState('')
  const [error, setError] = useState('')
  const [success, setSuccess] = useState(false)
  const [submitting, setSubmitting] = useState(false)

  useEffect(() => {
    if (!success) {
      return undefined
    }
    const timer = window.setTimeout(() => navigate('/'), 2000)
    return () => window.clearTimeout(timer)
  }, [success, navigate])

  const handleSubmit = async (event) => {
    event.preventDefault()
    setError('')
    if (!phone.trim() && !email.trim()) {
      setError('Укажите телефон или email')
      return
    }
    setSubmitting(true)
    try {
      await apiFetch('/leads/', {
        method: 'POST',
        body: JSON.stringify({
          name: name.trim(),
          phone: phone.trim() || null,
          email: email.trim() || null,
          comment: comment.trim() || null,
        }),
      })
      setSuccess(true)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Не удалось отправить заявку')
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
            <h1 style={{ fontSize: theme.sizes.h2, textAlign: 'center' }}>Оставить заявку</h1>
            <p
              style={{
                color: theme.colors.textMuted,
                textAlign: 'center',
                marginBottom: '32px',
              }}
            >
              Оставьте контакты — мы свяжемся и расскажем подробнее
            </p>
            {success ? (
              <div
                style={{
                  background: theme.colors.successSoft,
                  color: theme.colors.success,
                  borderRadius: theme.radii.md,
                  padding: '12px 16px',
                  fontSize: theme.sizes.bodySm,
                  textAlign: 'center',
                }}
              >
                Заявка принята, мы свяжемся с вами
              </div>
            ) : (
              <>
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
                    Имя *
                  </label>
                  <input
                    id="name"
                    name="name"
                    type="text"
                    required
                    minLength={2}
                    maxLength={100}
                    placeholder="Например, Иван"
                    value={name}
                    onChange={(event) => setName(event.target.value)}
                    style={fieldStyle}
                  />
                  <label htmlFor="phone" style={labelStyle}>
                    Телефон
                  </label>
                  <input
                    id="phone"
                    name="phone"
                    type="tel"
                    maxLength={30}
                    value={phone}
                    onChange={(event) => setPhone(event.target.value)}
                    style={fieldStyle}
                  />
                  <label htmlFor="email" style={labelStyle}>
                    Email
                  </label>
                  <input
                    id="email"
                    name="email"
                    type="email"
                    value={email}
                    onChange={(event) => setEmail(event.target.value)}
                    style={fieldStyle}
                  />
                  <label htmlFor="comment" style={labelStyle}>
                    Комментарий
                  </label>
                  <textarea
                    id="comment"
                    name="comment"
                    maxLength={2000}
                    rows={4}
                    placeholder="Что вас интересует?"
                    value={comment}
                    onChange={(event) => setComment(event.target.value)}
                    style={{ ...fieldStyle, marginBottom: theme.sizes.md, resize: 'vertical' }}
                  />
                  <Button type="submit" variant="primary" fullWidth disabled={submitting}>
                    {submitting ? 'Отправляю...' : 'Отправить заявку'}
                  </Button>
                </form>
              </>
            )}
          </div>
        </Section>
      </main>
      <Footer />
    </>
  )
}

export default Lead

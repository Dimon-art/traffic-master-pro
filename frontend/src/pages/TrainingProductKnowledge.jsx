/** Диалог режима «Знание продукта». */

import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'

import { getTraining, startTraining, submitAnswer } from '../api/trainings'
import Footer from '../components/Footer'
import Navbar from '../components/Navbar'
import Section from '../components/Section'
import Button from '../components/Button'
import theme from '../styles/theme'

function TrainingProductKnowledge() {
  const navigate = useNavigate()
  const [training, setTraining] = useState(null)
  const [messages, setMessages] = useState([])
  const [answer, setAnswer] = useState('')
  const [feedback, setFeedback] = useState(null)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(true)
  const [submitting, setSubmitting] = useState(false)

  useEffect(() => {
    let cancelled = false
    async function start() {
      try {
        const data = await startTraining('product_knowledge')
        if (cancelled) {
          return
        }
        setTraining(data)
        setMessages(data.messages || [])
      } catch (err) {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : 'Не удалось начать тренировку')
        }
      } finally {
        if (!cancelled) {
          setLoading(false)
        }
      }
    }
    start()
    return () => {
      cancelled = true
    }
  }, [])

  const completed = training?.status === 'completed'

  const handleSubmit = async (event) => {
    event.preventDefault()
    if (!training || !answer.trim()) {
      return
    }
    setSubmitting(true)
    setError('')
    try {
      const result = await submitAnswer(training.id, answer.trim())
      setFeedback(result)
      setAnswer('')
      const detail = await getTraining(training.id)
      setTraining(detail)
      setMessages(detail.messages || [])
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Не удалось отправить ответ')
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
    background: theme.colors.bg,
    color: theme.colors.textBody,
    fontFamily: theme.fonts.sans,
    resize: 'vertical',
  }

  return (
    <>
      <Navbar />
      <main style={{ paddingTop: '72px', minHeight: '100vh' }}>
        <Section>
          <h1 style={{ fontSize: theme.sizes.h2 }}>Знание продукта</h1>
          <p style={{ color: theme.colors.textMuted, marginBottom: theme.sizes.md }}>
            Отвечайте своими словами. Система ищет ключевые моменты и сразу даёт разбор.
          </p>
          {loading ? <p style={{ color: theme.colors.textMuted }}>Загрузка...</p> : null}
          {error ? (
            <div
              style={{
                background: theme.colors.errorSoft,
                color: theme.colors.error,
                borderRadius: theme.radii.md,
                padding: '12px 16px',
                marginBottom: theme.sizes.md,
              }}
            >
              {error}
            </div>
          ) : null}
          <div style={{ display: 'flex', flexDirection: 'column', gap: theme.sizes.sm }}>
            {messages.map((message) => (
              <div
                key={message.id}
                style={{
                  alignSelf: message.role === 'user' ? 'flex-end' : 'flex-start',
                  maxWidth: '85%',
                  padding: theme.sizes.sm,
                  borderRadius: theme.radii.md,
                  background: message.role === 'user' ? theme.colors.accentSoft : theme.colors.bgElevated,
                  border: `1px solid ${theme.colors.border}`,
                  color: theme.colors.textBody,
                }}
              >
                <div style={{ fontSize: theme.sizes.caption, color: theme.colors.textMuted, marginBottom: theme.sizes.xs }}>
                  {message.role === 'user' ? 'Вы' : 'Тренер'}
                  {message.score != null ? ` · ${message.score}/10` : ''}
                </div>
                {message.content}
              </div>
            ))}
          </div>
          {feedback ? (
            <div
              style={{
                marginTop: theme.sizes.md,
                padding: theme.sizes.md,
                background: theme.colors.successSoft,
                borderRadius: theme.radii.md,
                color: theme.colors.textBody,
              }}
            >
              <strong>Оценка: {feedback.score}/10</strong>
              <p style={{ margin: `${theme.sizes.xs} 0 0` }}>{feedback.feedback}</p>
            </div>
          ) : null}
          {completed ? (
            <div style={{ marginTop: theme.sizes.lg, textAlign: 'center' }}>
              <h2 style={{ fontSize: theme.sizes.h3 }}>Тренировка завершена</h2>
              <p style={{ color: theme.colors.textMuted }}>Итог: {training.score} из 100</p>
              <Button variant="primary" onClick={() => navigate('/trainings')}>
                К моим тренировкам
              </Button>
            </div>
          ) : (
            !loading && (
              <form onSubmit={handleSubmit} style={{ marginTop: theme.sizes.md }}>
                <textarea
                  value={answer}
                  onChange={(event) => setAnswer(event.target.value)}
                  rows={4}
                  required
                  placeholder="Ваш ответ"
                  style={fieldStyle}
                />
                <div style={{ marginTop: theme.sizes.sm }}>
                  <Button type="submit" variant="primary" disabled={submitting}>
                    {submitting ? 'Проверяю...' : 'Ответить'}
                  </Button>
                </div>
              </form>
            )
          )}
        </Section>
      </main>
      <Footer />
    </>
  )
}

export default TrainingProductKnowledge

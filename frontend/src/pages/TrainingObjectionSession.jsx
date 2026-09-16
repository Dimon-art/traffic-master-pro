/** Диалог сценария «Работа с возражениями». */

import { useEffect, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'

import { deleteTraining, getTraining, startTraining, submitAnswer } from '../api/trainings'
import Footer from '../components/Footer'
import Navbar from '../components/Navbar'
import Section from '../components/Section'
import Button from '../components/Button'
import theme from '../styles/theme'

function TrainingObjectionSession() {
  const { topic } = useParams()
  const navigate = useNavigate()
  const [training, setTraining] = useState(null)
  const [answer, setAnswer] = useState('')
  const [error, setError] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const [lastFeedback, setLastFeedback] = useState(null)
  const [loading, setLoading] = useState(true)
  const [aborting, setAborting] = useState(false)

  useEffect(() => {
    let cancelled = false
    async function start() {
      if (!topic) {
        setError('Сценарий не выбран')
        setLoading(false)
        return
      }
      try {
        const data = await startTraining('objections', topic)
        if (cancelled) {
          return
        }
        setTraining(data)
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
  }, [topic])

  const messages = training?.messages || []
  const completed = training?.status === 'completed'
  const roundNumber = Math.min((training?.current_question_index || 0) + 1, 5)
  const lastUserMessage = [...messages].reverse().find((message) => message.role === 'user')

  const handleSubmit = async (event) => {
    event.preventDefault()
    if (!training || !answer.trim()) {
      return
    }
    setSubmitting(true)
    setError('')
    try {
      const result = await submitAnswer(training.id, answer.trim())
      setLastFeedback(result)
      setAnswer('')
      const detail = await getTraining(training.id)
      setTraining(detail)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Не удалось отправить ответ')
    } finally {
      setSubmitting(false)
    }
  }

  const handleAbort = async () => {
    setAborting(true)
    try {
      if (training?.id) {
        await deleteTraining(training.id)
      }
    } catch {
      // всё равно возвращаемся к выбору сценария
    } finally {
      navigate('/training/objections')
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
          <div
            style={{
              display: 'flex',
              justifyContent: 'space-between',
              gap: theme.sizes.sm,
              flexWrap: 'wrap',
              alignItems: 'center',
              marginBottom: theme.sizes.md,
            }}
          >
            <div>
              <h1 style={{ fontSize: theme.sizes.h2 }}>Работа с возражениями</h1>
              {!completed && !loading ? (
                <p style={{ color: theme.colors.textMuted, margin: `${theme.sizes.xs} 0 0` }}>
                  Раунд {roundNumber} из 5
                </p>
              ) : null}
            </div>
            {!completed ? (
              <Button variant="ghost" onClick={handleAbort} disabled={aborting}>
                {aborting ? 'Выхожу...' : 'Прервать'}
              </Button>
            ) : null}
          </div>
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
            {messages.map((message) => {
              const isUser = message.role === 'user'
              const showFeedback = isUser && lastUserMessage?.id === message.id && lastFeedback
              return (
                <div
                  key={message.id}
                  style={{
                    alignSelf: isUser ? 'flex-end' : 'flex-start',
                    maxWidth: '85%',
                  }}
                >
                  <div
                    style={{
                      padding: theme.sizes.sm,
                      borderRadius: theme.radii.md,
                      background: isUser ? theme.colors.accentSoft : theme.colors.bgElevated,
                      border: `1px solid ${theme.colors.border}`,
                      color: theme.colors.textBody,
                    }}
                  >
                    <div
                      style={{
                        fontSize: theme.sizes.caption,
                        color: theme.colors.textMuted,
                        marginBottom: theme.sizes.xs,
                        display: 'flex',
                        alignItems: 'center',
                        gap: theme.sizes.xs,
                        flexWrap: 'wrap',
                      }}
                    >
                      <span>{isUser ? 'Вы' : 'Клиент'}</span>
                      {isUser && message.score != null ? (
                        <span
                          style={{
                            background: theme.colors.bgSunken,
                            borderRadius: theme.radii.full,
                            padding: '2px 10px',
                            fontSize: theme.sizes.micro,
                            color: theme.colors.textBody,
                          }}
                        >
                          {message.score}/10
                        </span>
                      ) : null}
                    </div>
                    {message.content}
                  </div>
                  {showFeedback ? (
                    <p
                      style={{
                        margin: `${theme.sizes.xs} 0 0`,
                        fontSize: theme.sizes.caption,
                        color: theme.colors.textMuted,
                      }}
                    >
                      {lastFeedback.feedback}
                    </p>
                  ) : null}
                </div>
              )
            })}
          </div>
          {completed ? (
            <div
              style={{
                marginTop: theme.sizes.lg,
                padding: theme.sizes.lg,
                background: theme.colors.bgElevated,
                border: `1px solid ${theme.colors.border}`,
                borderRadius: theme.radii.lg,
                textAlign: 'center',
              }}
            >
              <h2 style={{ fontSize: theme.sizes.h3 }}>Диалог завершён</h2>
              <p style={{ color: theme.colors.textMuted, margin: `${theme.sizes.sm} 0 ${theme.sizes.md}` }}>
                Итог: {training.score} из 100
              </p>
              <div style={{ display: 'flex', gap: theme.sizes.sm, justifyContent: 'center', flexWrap: 'wrap' }}>
                <Button variant="primary" onClick={() => navigate('/trainings')}>
                  Мои тренировки
                </Button>
                <Button variant="secondary" onClick={() => navigate('/training/objections')}>
                  Другой сценарий
                </Button>
              </div>
            </div>
          ) : (
            !loading &&
            training && (
              <form onSubmit={handleSubmit} style={{ marginTop: theme.sizes.md }}>
                <textarea
                  value={answer}
                  onChange={(event) => setAnswer(event.target.value)}
                  rows={4}
                  required
                  placeholder="Ваш ответ клиенту"
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

export default TrainingObjectionSession

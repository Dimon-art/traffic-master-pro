/** Просмотр истории одной тренировки. */

import { useEffect, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'

import { getTraining } from '../api/trainings'
import Footer from '../components/Footer'
import Navbar from '../components/Navbar'
import Section from '../components/Section'
import Button from '../components/Button'
import theme from '../styles/theme'

const MODE_LABELS = {
  product_knowledge: 'Знание продукта',
  objections: 'Возражения',
  needs: 'Потребности',
  sales_call: 'Созвон',
  proposal: 'КП',
}

function TrainingDetail() {
  const { trainingId } = useParams()
  const navigate = useNavigate()
  const [training, setTraining] = useState(null)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function load() {
      try {
        const data = await getTraining(trainingId)
        setTraining(data)
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Не удалось загрузить тренировку')
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [trainingId])

  return (
    <>
      <Navbar />
      <main style={{ paddingTop: '72px', minHeight: '100vh' }}>
        <Section>
          <Button variant="ghost" onClick={() => navigate('/trainings')}>
            Назад к списку
          </Button>
          {loading ? <p style={{ color: theme.colors.textMuted }}>Загрузка...</p> : null}
          {error ? (
            <div
              style={{
                background: theme.colors.errorSoft,
                color: theme.colors.error,
                borderRadius: theme.radii.md,
                padding: '12px 16px',
                marginTop: theme.sizes.sm,
              }}
            >
              {error}
            </div>
          ) : null}
          {training ? (
            <>
              <h1 style={{ fontSize: theme.sizes.h2, marginTop: theme.sizes.md }}>
                {MODE_LABELS[training.mode] || training.mode}
              </h1>
              <p style={{ color: theme.colors.textMuted }}>
                Статус: {training.status}
                {training.score != null ? ` · Итог ${training.score}/100` : ''}
              </p>
              <div style={{ display: 'flex', flexDirection: 'column', gap: theme.sizes.sm }}>
                {(training.messages || []).map((message) => (
                  <div
                    key={message.id}
                    style={{
                      padding: theme.sizes.sm,
                      borderRadius: theme.radii.md,
                      background:
                        message.role === 'user' ? theme.colors.accentSoft : theme.colors.bgElevated,
                      border: `1px solid ${theme.colors.border}`,
                    }}
                  >
                    <div style={{ fontSize: theme.sizes.caption, color: theme.colors.textMuted }}>
                      {message.role === 'user' ? 'Вы' : 'Тренер'}
                      {message.score != null ? ` · ${message.score}/10` : ''}
                    </div>
                    <p style={{ margin: `${theme.sizes.xs} 0 0` }}>{message.content}</p>
                  </div>
                ))}
              </div>
            </>
          ) : null}
        </Section>
      </main>
      <Footer />
    </>
  )
}

export default TrainingDetail

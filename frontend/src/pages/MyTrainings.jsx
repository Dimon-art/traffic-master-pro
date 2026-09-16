/** Список сессий тренировки текущего пользователя. */

import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'

import { listTrainings } from '../api/trainings'
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

const STATUS_LABELS = {
  started: 'Начата',
  in_progress: 'В процессе',
  completed: 'Завершена',
}

function formatDate(value) {
  if (!value) {
    return '—'
  }
  return new Date(value).toLocaleString('ru-RU')
}

function MyTrainings() {
  const navigate = useNavigate()
  const [items, setItems] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    async function load() {
      try {
        const data = await listTrainings()
        setItems(data)
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Не удалось загрузить тренировки')
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [])

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
              marginBottom: theme.sizes.lg,
            }}
          >
            <h1 style={{ fontSize: theme.sizes.h2 }}>Мои тренировки</h1>
            <Button variant="primary" onClick={() => navigate('/training')}>
              Новая тренировка
            </Button>
          </div>
          {error ? (
            <div
              style={{
                background: theme.colors.errorSoft,
                color: theme.colors.error,
                borderRadius: theme.radii.md,
                padding: '12px 16px',
              }}
            >
              {error}
            </div>
          ) : null}
          {loading ? (
            <p style={{ color: theme.colors.textMuted }}>Загрузка...</p>
          ) : items.length === 0 ? (
            <p style={{ color: theme.colors.textMuted }}>Тренировок пока нет</p>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: theme.sizes.sm }}>
              {items.map((item) => (
                <article
                  key={item.id}
                  style={{
                    background: theme.colors.bgElevated,
                    border: `1px solid ${theme.colors.border}`,
                    borderRadius: theme.radii.lg,
                    padding: theme.sizes.md,
                    display: 'flex',
                    justifyContent: 'space-between',
                    gap: theme.sizes.sm,
                    flexWrap: 'wrap',
                    alignItems: 'center',
                  }}
                >
                  <div>
                    <h2 style={{ fontSize: theme.sizes.h3 }}>
                      {MODE_LABELS[item.mode] || item.mode}
                    </h2>
                    <p style={{ margin: 0, color: theme.colors.textMuted, fontSize: theme.sizes.caption }}>
                      {STATUS_LABELS[item.status] || item.status} · {formatDate(item.created_at)}
                      {item.score != null ? ` · ${item.score}/100` : ''}
                    </p>
                  </div>
                  <Button variant="secondary" onClick={() => navigate(`/trainings/${item.id}`)}>
                    Открыть
                  </Button>
                </article>
              ))}
            </div>
          )}
        </Section>
      </main>
      <Footer />
    </>
  )
}

export default MyTrainings

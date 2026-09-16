/** Список сессий тренировки текущего пользователя. */

import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'

import { listTrainings } from '../api/trainings'
import Footer from '../components/Footer'
import Navbar from '../components/Navbar'
import Section from '../components/Section'
import Button from '../components/Button'
import { useAuth } from '../context/AuthContext'
import theme from '../styles/theme'

const MODE_LABELS = {
  product_knowledge: 'Знание продукта',
  objections: 'Работа с возражениями',
  needs: 'Выявление потребностей',
  sales_call: 'Продающий созвон',
  proposal: 'Мастер коммерческого предложения',
}

const FILTERS = [
  { id: 'all', label: 'Все' },
  { id: 'product_knowledge', label: 'Знание продукта' },
  { id: 'objections', label: 'Возражения' },
]

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
  const { isAdmin } = useAuth()
  const title = isAdmin ? 'Все тренировки' : 'Мои тренировки'
  const [items, setItems] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [filter, setFilter] = useState('all')

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
            <h1 style={{ fontSize: theme.sizes.h2 }}>{title}</h1>
            <Button variant="primary" onClick={() => navigate('/training')}>
              Новая тренировка
            </Button>
          </div>
          <div
            style={{
              display: 'flex',
              gap: theme.sizes.xs,
              flexWrap: 'wrap',
              marginBottom: theme.sizes.md,
            }}
          >
            {FILTERS.map((item) => {
              const active = filter === item.id
              return (
                <button
                  key={item.id}
                  type="button"
                  onClick={() => setFilter(item.id)}
                  style={{
                    padding: '8px 16px',
                    borderRadius: theme.radii.full,
                    border: `1px solid ${active ? theme.colors.accent : theme.colors.border}`,
                    background: active ? theme.colors.accentSoft : theme.colors.bgElevated,
                    color: active ? theme.colors.accent : theme.colors.textBody,
                    cursor: 'pointer',
                    fontSize: theme.sizes.caption,
                    fontFamily: theme.fonts.sans,
                    outline: 'none',
                  }}
                  onFocus={(event) => {
                    event.currentTarget.style.boxShadow = `0 0 0 2px ${theme.colors.accent}`
                  }}
                  onBlur={(event) => {
                    event.currentTarget.style.boxShadow = 'none'
                  }}
                >
                  {item.label}
                </button>
              )
            })}
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
          ) : items.filter((item) => filter === 'all' || item.mode === filter).length === 0 ? (
            <p style={{ color: theme.colors.textMuted }}>Тренировок пока нет</p>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: theme.sizes.sm }}>
              {items
                .filter((item) => filter === 'all' || item.mode === filter)
                .map((item) => (
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

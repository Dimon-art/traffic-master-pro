/** Техническая панель: проверка backend, PostgreSQL и Redis. */

import { useCallback, useEffect, useState } from 'react'

import Footer from '../components/Footer'
import Navbar from '../components/Navbar'
import Button from '../components/Button'
import theme from '../styles/theme'

const API_URL = (import.meta.env.VITE_API_URL || 'http://localhost:8000/api').replace(/\/$/, '')

const ENDPOINTS = [
  { key: 'backend', label: 'Backend', path: '/health' },
  { key: 'db', label: 'PostgreSQL', path: '/health/db' },
  { key: 'redis', label: 'Redis', path: '/health/redis' },
]

function HealthPanel() {
  const [statuses, setStatuses] = useState({
    backend: null,
    db: null,
    redis: null,
  })
  const [loading, setLoading] = useState(false)

  const checkAll = useCallback(async () => {
    setLoading(true)
    const results = await Promise.all(
      ENDPOINTS.map(async ({ key, path }) => {
        try {
          const response = await fetch(`${API_URL}${path}`)
          const data = await response.json()
          return [key, { ok: data.status === 'ok' }]
        } catch {
          return [key, { ok: false }]
        }
      }),
    )
    setStatuses(Object.fromEntries(results))
    setLoading(false)
  }, [])

  useEffect(() => {
    checkAll()
  }, [checkAll])

  const statusBackground = (ok) => {
    if (ok === null) return theme.colors.bgSunken
    return ok ? theme.colors.successSoft : theme.colors.errorSoft
  }

  return (
    <>
      <Navbar />
      <main
        style={{
          minHeight: '100vh',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          padding: `120px ${theme.sizes.md} ${theme.sizes.lg}`,
        }}
      >
        <div
          style={{
            width: '100%',
            maxWidth: '520px',
            background: theme.colors.bgElevated,
            borderRadius: theme.radii.lg,
            boxShadow: theme.shadows.card,
            padding: `${theme.sizes.lg} 32px ${theme.sizes.md}`,
            textAlign: 'center',
          }}
        >
          <h1 style={{ fontSize: '32px' }}>TrafficMaster Pro</h1>
          <p
            style={{
              margin: `${theme.sizes.sm} 0 ${theme.sizes.md}`,
              fontSize: theme.sizes.bodySm,
              color: theme.colors.textMuted,
            }}
          >
            Нейро-тренер для экспертов по продвижению в Telegram
          </p>
          <div
            style={{
              display: 'flex',
              flexDirection: 'column',
              gap: '12px',
              marginBottom: theme.sizes.md,
            }}
          >
            {ENDPOINTS.map(({ key, label }) => {
              const status = statuses[key]
              const ok = status === null ? null : status.ok
              return (
                <div
                  key={key}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    padding: '14px 18px',
                    borderRadius: theme.radii.md,
                    background: statusBackground(ok),
                    color: theme.colors.textPrimary,
                    fontWeight: 600,
                    fontSize: theme.sizes.bodySm,
                  }}
                >
                  <span>{label}</span>
                  <span aria-label={ok === null ? 'Ожидание' : ok ? 'Доступен' : 'Ошибка'}>
                    {ok === null ? '…' : ok ? '✅' : '❌'}
                  </span>
                </div>
              )
            })}
          </div>
          <Button variant="primary" onClick={checkAll} disabled={loading}>
            🔄 Проверить снова
          </Button>
          <div
            style={{
              marginTop: '14px',
              fontSize: theme.sizes.caption,
              color: theme.colors.accent,
              minHeight: '20px',
            }}
          >
            {loading ? 'Проверяю...' : '\u00a0'}
          </div>
          <div
            style={{
              marginTop: theme.sizes.md,
              fontSize: theme.sizes.micro,
              color: theme.colors.textMuted,
            }}
          >
            v0.1.0 · Шаг 1: инфраструктура готова
          </div>
        </div>
      </main>
      <Footer />
    </>
  )
}

export default HealthPanel

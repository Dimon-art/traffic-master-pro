import { useCallback, useEffect, useState } from 'react'

const PALETTE = {
  sun: '#FFB627',
  green: '#2ECC71',
  blue: '#3498DB',
  orange: '#FF6B35',
  dark: '#1A2B45',
  light: '#F5F7FA',
}

const ENDPOINTS = [
  { key: 'backend', label: 'Backend', url: 'http://localhost:8000/api/health' },
  { key: 'db', label: 'PostgreSQL', url: 'http://localhost:8000/api/health/db' },
  { key: 'redis', label: 'Redis', url: 'http://localhost:8000/api/health/redis' },
]

function App() {
  const [statuses, setStatuses] = useState({
    backend: null,
    db: null,
    redis: null,
  })
  const [loading, setLoading] = useState(false)

  const checkAll = useCallback(async () => {
    setLoading(true)
    const results = await Promise.all(
      ENDPOINTS.map(async ({ key, url }) => {
        try {
          const response = await fetch(url)
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

  const styles = {
    page: {
      minHeight: '100vh',
      margin: 0,
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      fontFamily: 'Segoe UI, system-ui, sans-serif',
      background: `linear-gradient(160deg, ${PALETTE.light} 0%, #ffffff 45%, ${PALETTE.sun}22 100%)`,
      color: PALETTE.dark,
      padding: '24px',
      boxSizing: 'border-box',
    },
    card: {
      width: '100%',
      maxWidth: '520px',
      background: '#ffffff',
      borderRadius: '20px',
      boxShadow: '0 18px 50px rgba(26, 43, 69, 0.16)',
      padding: '40px 32px 28px',
      textAlign: 'center',
    },
    title: {
      margin: 0,
      fontSize: '32px',
      fontWeight: 800,
      background: `linear-gradient(90deg, ${PALETTE.green}, ${PALETTE.blue}, ${PALETTE.orange})`,
      WebkitBackgroundClip: 'text',
      backgroundClip: 'text',
      color: 'transparent',
    },
    subtitle: {
      margin: '12px 0 28px',
      fontSize: '15px',
      lineHeight: 1.5,
      color: `${PALETTE.dark}cc`,
    },
    statusList: {
      display: 'flex',
      flexDirection: 'column',
      gap: '12px',
      marginBottom: '24px',
    },
    statusItem: (ok) => ({
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      padding: '14px 18px',
      borderRadius: '12px',
      background: ok === null ? `${PALETTE.light}` : ok ? `${PALETTE.green}33` : '#e74c3c33',
      color: PALETTE.dark,
      fontWeight: 600,
      fontSize: '15px',
    }),
    button: {
      border: 'none',
      borderRadius: '12px',
      padding: '12px 22px',
      fontSize: '15px',
      fontWeight: 700,
      color: '#ffffff',
      cursor: loading ? 'wait' : 'pointer',
      background: `linear-gradient(90deg, ${PALETTE.green}, ${PALETTE.blue})`,
      opacity: loading ? 0.7 : 1,
    },
    loading: {
      marginTop: '14px',
      fontSize: '14px',
      color: PALETTE.blue,
      minHeight: '20px',
    },
    footer: {
      marginTop: '24px',
      fontSize: '12px',
      color: `${PALETTE.dark}99`,
    },
  }

  return (
    <div style={styles.page}>
      <div style={styles.card}>
        <h1 style={styles.title}>TrafficMaster Pro</h1>
        <p style={styles.subtitle}>
          Нейро-тренер для экспертов по продвижению в Telegram
        </p>
        <div style={styles.statusList}>
          {ENDPOINTS.map(({ key, label }) => {
            const status = statuses[key]
            const ok = status === null ? null : status.ok
            return (
              <div key={key} style={styles.statusItem(ok)}>
                <span>{label}</span>
                <span>{ok === null ? '…' : ok ? '✅' : '❌'}</span>
              </div>
            )
          })}
        </div>
        <button type="button" style={styles.button} onClick={checkAll} disabled={loading}>
          🔄 Проверить снова
        </button>
        <div style={styles.loading}>{loading ? 'Проверяю...' : '\u00a0'}</div>
        <div style={styles.footer}>v0.1.0 · Шаг 1: инфраструктура готова</div>
      </div>
    </div>
  )
}

export default App

/** Админ-список пользователей с редактированием роли и статуса. */

import { useCallback, useEffect, useState } from 'react'

import { apiFetch } from '../api/client'
import Footer from '../components/Footer'
import Navbar from '../components/Navbar'
import Section from '../components/Section'
import Button from '../components/Button'
import theme from '../styles/theme'

function formatDate(value) {
  if (!value) {
    return '—'
  }
  return new Date(value).toLocaleString('ru-RU')
}

function AdminUsers() {
  const [users, setUsers] = useState([])
  const [drafts, setDrafts] = useState({})
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [savingId, setSavingId] = useState(null)
  const [isMobile, setIsMobile] = useState(false)

  useEffect(() => {
    const onResize = () => setIsMobile(window.innerWidth < 768)
    onResize()
    window.addEventListener('resize', onResize)
    return () => window.removeEventListener('resize', onResize)
  }, [])

  const loadUsers = useCallback(async () => {
    setLoading(true)
    setError('')
    try {
      const data = await apiFetch('/users/')
      setUsers(data)
      setDrafts(
        Object.fromEntries(
          data.map((item) => [
            item.id,
            { name: item.name || '', role: item.role, is_active: item.is_active },
          ]),
        ),
      )
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Не удалось загрузить пользователей')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    loadUsers()
  }, [loadUsers])

  const updateDraft = (userId, patch) => {
    setDrafts((current) => ({
      ...current,
      [userId]: { ...current[userId], ...patch },
    }))
  }

  const saveUser = async (userId) => {
    const draft = drafts[userId]
    if (!draft) {
      return
    }
    setSavingId(userId)
    setError('')
    try {
      await apiFetch(`/users/${userId}`, {
        method: 'PATCH',
        body: JSON.stringify({
          name: draft.name.trim() || null,
          role: draft.role,
          is_active: draft.is_active,
        }),
      })
      await loadUsers()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Не удалось сохранить пользователя')
    } finally {
      setSavingId(null)
    }
  }

  const inputStyle = {
    padding: theme.sizes.xs,
    borderRadius: theme.radii.sm,
    border: `1px solid ${theme.colors.border}`,
    fontSize: theme.sizes.caption,
    background: theme.colors.bg,
    color: theme.colors.textBody,
    fontFamily: theme.fonts.sans,
    width: '100%',
  }

  const thStyle = {
    textAlign: 'left',
    padding: theme.sizes.sm,
    borderBottom: `1px solid ${theme.colors.border}`,
    color: theme.colors.textMuted,
    fontSize: theme.sizes.caption,
    fontWeight: 600,
  }

  const tdStyle = {
    padding: theme.sizes.sm,
    borderBottom: `1px solid ${theme.colors.border}`,
    fontSize: theme.sizes.caption,
    color: theme.colors.textBody,
    verticalAlign: 'middle',
  }

  const renderEditor = (user) => {
    const draft = drafts[user.id] || { name: '', role: 'user', is_active: true }
    return (
      <>
        <input
          value={draft.name}
          onChange={(event) => updateDraft(user.id, { name: event.target.value })}
          style={inputStyle}
          aria-label="Имя"
        />
        <select
          value={draft.role}
          onChange={(event) => updateDraft(user.id, { role: event.target.value })}
          style={inputStyle}
          aria-label="Роль"
        >
          <option value="user">user</option>
          <option value="admin">admin</option>
        </select>
        <label style={{ display: 'flex', alignItems: 'center', gap: theme.sizes.xs, fontSize: theme.sizes.caption }}>
          <input
            type="checkbox"
            checked={Boolean(draft.is_active)}
            onChange={(event) => updateDraft(user.id, { is_active: event.target.checked })}
          />
          Активен
        </label>
        <Button
          variant="primary"
          size="md"
          onClick={() => saveUser(user.id)}
          disabled={savingId === user.id}
        >
          {savingId === user.id ? 'Сохраняю...' : 'Сохранить'}
        </Button>
      </>
    )
  }

  return (
    <>
      <Navbar />
      <main style={{ paddingTop: '72px', minHeight: '100vh' }}>
        <Section>
          <h1 style={{ fontSize: theme.sizes.h2, marginBottom: theme.sizes.lg }}>Пользователи</h1>
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
          {loading ? (
            <p style={{ color: theme.colors.textMuted }}>Загрузка...</p>
          ) : isMobile ? (
            <div style={{ display: 'flex', flexDirection: 'column', gap: theme.sizes.sm }}>
              {users.map((user) => (
                <article
                  key={user.id}
                  style={{
                    background: theme.colors.bgElevated,
                    border: `1px solid ${theme.colors.border}`,
                    borderRadius: theme.radii.lg,
                    padding: theme.sizes.md,
                    display: 'flex',
                    flexDirection: 'column',
                    gap: theme.sizes.sm,
                  }}
                >
                  <strong>{user.email}</strong>
                  <span style={{ color: theme.colors.textMuted, fontSize: theme.sizes.caption }}>
                    {formatDate(user.created_at)}
                  </span>
                  {renderEditor(user)}
                </article>
              ))}
            </div>
          ) : (
            <div
              style={{
                overflowX: 'auto',
                background: theme.colors.bgElevated,
                borderRadius: theme.radii.lg,
                border: `1px solid ${theme.colors.border}`,
                boxShadow: theme.shadows.card,
              }}
            >
              <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                <thead>
                  <tr>
                    <th style={thStyle}>Email</th>
                    <th style={thStyle}>Имя</th>
                    <th style={thStyle}>Роль</th>
                    <th style={thStyle}>Активен</th>
                    <th style={thStyle}>Создан</th>
                    <th style={thStyle}> </th>
                  </tr>
                </thead>
                <tbody>
                  {users.map((user) => {
                    const draft = drafts[user.id] || { name: '', role: 'user', is_active: true }
                    return (
                      <tr key={user.id}>
                        <td style={tdStyle}>{user.email}</td>
                        <td style={tdStyle}>
                          <input
                            value={draft.name}
                            onChange={(event) => updateDraft(user.id, { name: event.target.value })}
                            style={inputStyle}
                            aria-label="Имя"
                          />
                        </td>
                        <td style={tdStyle}>
                          <select
                            value={draft.role}
                            onChange={(event) => updateDraft(user.id, { role: event.target.value })}
                            style={inputStyle}
                            aria-label="Роль"
                          >
                            <option value="user">user</option>
                            <option value="admin">admin</option>
                          </select>
                        </td>
                        <td style={tdStyle}>
                          <input
                            type="checkbox"
                            checked={Boolean(draft.is_active)}
                            onChange={(event) =>
                              updateDraft(user.id, { is_active: event.target.checked })
                            }
                            aria-label="Активен"
                          />
                        </td>
                        <td style={tdStyle}>{formatDate(user.created_at)}</td>
                        <td style={tdStyle}>
                          <Button
                            variant="primary"
                            size="md"
                            onClick={() => saveUser(user.id)}
                            disabled={savingId === user.id}
                          >
                            {savingId === user.id ? 'Сохраняю...' : 'Сохранить'}
                          </Button>
                        </td>
                      </tr>
                    )
                  })}
                </tbody>
              </table>
            </div>
          )}
        </Section>
      </main>
      <Footer />
    </>
  )
}

export default AdminUsers

/** Список заявок: свои для пользователя, все — для администратора. */

import { useCallback, useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'

import { apiFetch } from '../api/client'
import Footer from '../components/Footer'
import Navbar from '../components/Navbar'
import Section from '../components/Section'
import Button from '../components/Button'
import { useAuth } from '../context/AuthContext'
import theme from '../styles/theme'

const STATUS_LABELS = {
  new: 'Новая',
  in_progress: 'В работе',
  done: 'Готово',
  rejected: 'Отклонена',
}

function formatDate(value) {
  if (!value) {
    return '—'
  }
  return new Date(value).toLocaleString('ru-RU')
}

function Leads() {
  const navigate = useNavigate()
  const { isAdmin } = useAuth()
  const [leads, setLeads] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [isMobile, setIsMobile] = useState(false)
  const [editing, setEditing] = useState(null)
  const [saving, setSaving] = useState(false)

  useEffect(() => {
    const onResize = () => setIsMobile(window.innerWidth < 768)
    onResize()
    window.addEventListener('resize', onResize)
    return () => window.removeEventListener('resize', onResize)
  }, [])

  const loadLeads = useCallback(async () => {
    setLoading(true)
    setError('')
    try {
      const data = await apiFetch('/leads/')
      setLeads(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Не удалось загрузить заявки')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    loadLeads()
  }, [loadLeads])

  const rejectLead = async (leadId) => {
    try {
      await apiFetch(`/leads/${leadId}`, {
        method: 'PATCH',
        body: JSON.stringify({ status: 'rejected' }),
      })
      await loadLeads()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Не удалось обновить заявку')
    }
  }

  const deleteLead = async (leadId) => {
    if (!window.confirm('Удалить заявку?')) {
      return
    }
    try {
      await apiFetch(`/leads/${leadId}`, { method: 'DELETE' })
      await loadLeads()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Не удалось удалить заявку')
    }
  }

  const saveEdit = async (event) => {
    event.preventDefault()
    if (!editing) {
      return
    }
    setSaving(true)
    setError('')
    try {
      await apiFetch(`/leads/${editing.id}`, {
        method: 'PATCH',
        body: JSON.stringify({
          name: editing.name,
          phone: editing.phone || null,
          email: editing.email || null,
          comment: editing.comment || null,
          status: editing.status,
        }),
      })
      setEditing(null)
      await loadLeads()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Не удалось сохранить заявку')
    } finally {
      setSaving(false)
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
    verticalAlign: 'top',
  }

  const renderActions = (lead) =>
    isAdmin ? (
      <div style={{ display: 'flex', gap: theme.sizes.xs, flexWrap: 'wrap' }}>
        <Button variant="secondary" size="md" onClick={() => setEditing({ ...lead })}>
          Редактировать
        </Button>
        <Button variant="ghost" size="md" onClick={() => deleteLead(lead.id)}>
          Удалить
        </Button>
      </div>
    ) : (
      lead.status !== 'rejected' && (
        <Button variant="secondary" size="md" onClick={() => rejectLead(lead.id)}>
          Отменить
        </Button>
      )
    )

  return (
    <>
      <Navbar />
      <main style={{ paddingTop: '72px', minHeight: '100vh' }}>
        <Section>
          <div
            style={{
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              gap: theme.sizes.sm,
              flexWrap: 'wrap',
              marginBottom: theme.sizes.lg,
            }}
          >
            <h1 style={{ fontSize: theme.sizes.h2 }}>{isAdmin ? 'Все заявки' : 'Мои заявки'}</h1>
            <Button variant="primary" size="md" onClick={() => navigate('/lead')}>
              + Новая заявка
            </Button>
          </div>
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
          ) : leads.length === 0 ? (
            <p style={{ color: theme.colors.textMuted }}>Заявок пока нет</p>
          ) : isMobile ? (
            <div style={{ display: 'flex', flexDirection: 'column', gap: theme.sizes.sm }}>
              {leads.map((lead) => (
                <article
                  key={lead.id}
                  style={{
                    background: theme.colors.bgElevated,
                    border: `1px solid ${theme.colors.border}`,
                    borderRadius: theme.radii.lg,
                    padding: theme.sizes.md,
                    boxShadow: theme.shadows.card,
                  }}
                >
                  <h2 style={{ fontSize: theme.sizes.h3, marginBottom: theme.sizes.xs }}>{lead.name}</h2>
                  <p style={{ margin: 0, color: theme.colors.textMuted, fontSize: theme.sizes.caption }}>
                    {lead.phone || '—'} · {lead.email || '—'}
                  </p>
                  <p style={{ margin: `${theme.sizes.xs} 0`, color: theme.colors.textBody }}>
                    {lead.comment || 'Без комментария'}
                  </p>
                  <p style={{ margin: `0 0 ${theme.sizes.sm}`, color: theme.colors.textMuted, fontSize: theme.sizes.caption }}>
                    {STATUS_LABELS[lead.status] || lead.status} · {formatDate(lead.created_at)}
                  </p>
                  {renderActions(lead)}
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
                    <th style={thStyle}>Имя</th>
                    <th style={thStyle}>Телефон</th>
                    <th style={thStyle}>Email</th>
                    <th style={thStyle}>Комментарий</th>
                    <th style={thStyle}>Статус</th>
                    <th style={thStyle}>Дата</th>
                    <th style={thStyle}> </th>
                  </tr>
                </thead>
                <tbody>
                  {leads.map((lead) => (
                    <tr key={lead.id}>
                      <td style={tdStyle}>{lead.name}</td>
                      <td style={tdStyle}>{lead.phone || '—'}</td>
                      <td style={tdStyle}>{lead.email || '—'}</td>
                      <td style={tdStyle}>{lead.comment || '—'}</td>
                      <td style={tdStyle}>{STATUS_LABELS[lead.status] || lead.status}</td>
                      <td style={tdStyle}>{formatDate(lead.created_at)}</td>
                      <td style={tdStyle}>{renderActions(lead)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </Section>
      </main>
      {editing ? (
        <div
          style={{
            position: 'fixed',
            inset: 0,
            background: `${theme.colors.textPrimary}59`,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            padding: theme.sizes.md,
            zIndex: 200,
          }}
        >
          <form
            onSubmit={saveEdit}
            style={{
              width: '100%',
              maxWidth: '480px',
              background: theme.colors.bgElevated,
              borderRadius: theme.radii.lg,
              padding: theme.sizes.lg,
              boxShadow: theme.shadows.hover,
            }}
          >
            <h2 style={{ fontSize: theme.sizes.h3, marginBottom: theme.sizes.md }}>Редактировать заявку</h2>
            <input
              value={editing.name}
              onChange={(event) => setEditing({ ...editing, name: event.target.value })}
              style={fieldStyle}
              required
            />
            <input
              value={editing.phone || ''}
              onChange={(event) => setEditing({ ...editing, phone: event.target.value })}
              style={fieldStyle}
              placeholder="Телефон"
            />
            <input
              value={editing.email || ''}
              onChange={(event) => setEditing({ ...editing, email: event.target.value })}
              style={fieldStyle}
              placeholder="Email"
            />
            <textarea
              value={editing.comment || ''}
              onChange={(event) => setEditing({ ...editing, comment: event.target.value })}
              style={{ ...fieldStyle, resize: 'vertical' }}
              rows={3}
              placeholder="Комментарий"
            />
            <select
              value={editing.status}
              onChange={(event) => setEditing({ ...editing, status: event.target.value })}
              style={fieldStyle}
            >
              {Object.entries(STATUS_LABELS).map(([value, label]) => (
                <option key={value} value={value}>
                  {label}
                </option>
              ))}
            </select>
            <div style={{ display: 'flex', gap: theme.sizes.sm }}>
              <Button type="submit" variant="primary" disabled={saving}>
                {saving ? 'Сохраняю...' : 'Сохранить'}
              </Button>
              <Button type="button" variant="ghost" onClick={() => setEditing(null)}>
                Отмена
              </Button>
            </div>
          </form>
        </div>
      ) : null}
      <Footer />
    </>
  )
}

export default Leads

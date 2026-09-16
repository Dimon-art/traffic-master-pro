/** Каталог сценариев режима «Выявление потребностей». */

import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'

import { listNeedsScenarios } from '../api/trainings'
import Footer from '../components/Footer'
import Navbar from '../components/Navbar'
import Section from '../components/Section'
import Button from '../components/Button'
import theme from '../styles/theme'

function TrainingNeeds() {
  const navigate = useNavigate()
  const [scenarios, setScenarios] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [hoveredId, setHoveredId] = useState(null)

  useEffect(() => {
    let cancelled = false
    async function load() {
      try {
        const data = await listNeedsScenarios()
        if (!cancelled) {
          setScenarios(data)
        }
      } catch (err) {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : 'Не удалось загрузить сценарии')
        }
      } finally {
        if (!cancelled) {
          setLoading(false)
        }
      }
    }
    load()
    return () => {
      cancelled = true
    }
  }, [])

  const openScenario = (scenarioId) => {
    navigate(`/training/needs/${scenarioId}`)
  }

  return (
    <>
      <Navbar />
      <main style={{ paddingTop: '72px', minHeight: '100vh' }}>
        <Section>
          <h1 style={{ fontSize: theme.sizes.h2, textAlign: 'center' }}>Выявление потребностей</h1>
          <p
            style={{
              textAlign: 'center',
              color: theme.colors.textMuted,
              margin: `${theme.sizes.sm} auto ${theme.sizes.lg}`,
              maxWidth: theme.layout.maxText,
            }}
          >
            Клиент задаёт расплывчатый запрос. Ваша задача — открытыми вопросами выяснить потребность.
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
          <div
            style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
              gap: theme.sizes.sm,
            }}
          >
            {scenarios.map((scenario) => {
              const hovered = hoveredId === scenario.id
              return (
                <article
                  key={scenario.id}
                  onMouseEnter={() => setHoveredId(scenario.id)}
                  onMouseLeave={() => setHoveredId(null)}
                  onClick={() => openScenario(scenario.id)}
                  style={{
                    borderRadius: theme.radii.lg,
                    padding: theme.sizes.md,
                    background: theme.colors.bgElevated,
                    border: `1px solid ${theme.colors.border}`,
                    boxShadow: hovered ? theme.shadows.hover : theme.shadows.card,
                    cursor: 'pointer',
                    transition: theme.transitions.fast,
                  }}
                >
                  <h2 style={{ fontSize: theme.sizes.h3 }}>{scenario.title}</h2>
                  <p
                    style={{
                      color: theme.colors.textMuted,
                      margin: `${theme.sizes.xs} 0 ${theme.sizes.sm}`,
                    }}
                  >
                    {scenario.description}
                  </p>
                  <Button
                    variant="primary"
                    onClick={(event) => {
                      event.stopPropagation()
                      openScenario(scenario.id)
                    }}
                  >
                    Начать
                  </Button>
                </article>
              )
            })}
          </div>
        </Section>
      </main>
      <Footer />
    </>
  )
}

export default TrainingNeeds

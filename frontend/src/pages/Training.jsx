/** Каталог режимов тренировки. */

import { useNavigate } from 'react-router-dom'

import Footer from '../components/Footer'
import Navbar from '../components/Navbar'
import Section from '../components/Section'
import Button from '../components/Button'
import { useAuth } from '../context/AuthContext'
import theme from '../styles/theme'

const MODES = [
  {
    id: 'product_knowledge',
    title: 'Знание продукта',
    description: 'Проверка курсов, тарифов и особенностей Университета.',
    available: true,
    href: '/training/product-knowledge',
  },
  {
    id: 'objections',
    title: 'Работа с возражениями',
    description: 'Диалог с ИИ-клиентом: «дорого», «нет времени», «сомневаюсь».',
    available: false,
  },
  {
    id: 'needs',
    title: 'Выявление потребностей',
    description: 'ИИ играет роль клиента — вы учитесь задавать правильные вопросы.',
    available: false,
  },
  {
    id: 'sales_call',
    title: 'Продающий созвон',
    description: 'Симуляция брифинга от знакомства до точки Б.',
    available: false,
  },
  {
    id: 'proposal',
    title: 'Мастер коммерческого предложения',
    description: 'ИИ проверяет структуру КП, кейсы и прогноз окупаемости.',
    available: false,
  },
]

function Training() {
  const navigate = useNavigate()
  const { user } = useAuth()

  const openMode = (mode) => {
    if (!mode.available) {
      return
    }
    if (!user) {
      navigate('/login')
      return
    }
    navigate(mode.href)
  }

  return (
    <>
      <Navbar />
      <main style={{ paddingTop: '72px', minHeight: '100vh' }}>
        <Section>
          <h1 style={{ fontSize: theme.sizes.h2, textAlign: 'center' }}>Режимы тренировки</h1>
          <p
            style={{
              textAlign: 'center',
              color: theme.colors.textMuted,
              margin: `${theme.sizes.sm} auto ${theme.sizes.lg}`,
              maxWidth: theme.layout.maxText,
            }}
          >
            Сейчас доступен режим «Знание продукта». Остальные появятся следующими шагами.
          </p>
          <div style={{ display: 'flex', flexDirection: 'column', gap: theme.sizes.sm }}>
            {MODES.map((mode) => (
              <article
                key={mode.id}
                style={{
                  borderRadius: theme.radii.lg,
                  padding: theme.sizes.md,
                  background: theme.colors.bgElevated,
                  border: `1px solid ${theme.colors.border}`,
                  opacity: mode.available ? 1 : 0.7,
                }}
              >
                <h2 style={{ fontSize: theme.sizes.h3 }}>{mode.title}</h2>
                <p style={{ color: theme.colors.textMuted, margin: `${theme.sizes.xs} 0 ${theme.sizes.sm}` }}>
                  {mode.description}
                </p>
                {mode.available ? (
                  <Button variant="primary" onClick={() => openMode(mode)}>
                    Начать
                  </Button>
                ) : (
                  <span style={{ color: theme.colors.textMuted, fontSize: theme.sizes.caption }}>Скоро</span>
                )}
              </article>
            ))}
          </div>
          <div
            style={{
              marginTop: theme.sizes.xl,
              padding: theme.sizes.lg,
              background: theme.colors.bgElevated,
              border: `1px solid ${theme.colors.border}`,
              borderRadius: theme.radii.lg,
              boxShadow: theme.shadows.card,
              textAlign: 'center',
            }}
          >
            <h2 style={{ fontSize: theme.sizes.h3, marginBottom: theme.sizes.sm }}>Хотите консультацию?</h2>
            <p style={{ margin: `0 0 ${theme.sizes.md}`, color: theme.colors.textMuted }}>
              Оставьте заявку — расскажем о тренировках и подберём программу под ваш отдел.
            </p>
            <Button variant="secondary" size="lg" onClick={() => navigate('/lead')}>
              Оставить заявку
            </Button>
          </div>
        </Section>
      </main>
      <Footer />
    </>
  )
}

export default Training

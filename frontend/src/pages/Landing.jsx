/** Главная посадочная страница с hero, режимами и шагами. */

import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'

import Footer from '../components/Footer'
import Navbar from '../components/Navbar'
import Section from '../components/Section'
import Button from '../components/Button'
import theme from '../styles/theme'

const MODES = [
  {
    title: 'Знание продукта',
    description:
      'Проверка того, насколько уверенно менеджер знает курсы, тарифы и особенности Университета.',
  },
  {
    title: 'Работа с возражениями',
    description:
      'Диалог с ИИ-клиентом: «дорого», «нет времени», «сомневаюсь в гарантиях» — и рекомендации, как закрыть.',
  },
  {
    title: 'Выявление потребностей',
    description: 'ИИ играет роль реального клиента — менеджер учится задавать правильные вопросы.',
  },
  {
    title: 'Продающий созвон',
    description:
      'Симуляция брифинга: от знакомства до точки Б. ИИ оценивает, все ли ключевые вопросы заданы.',
  },
  {
    title: 'Мастер коммерческого предложения',
    description: 'Менеджер пишет КП — ИИ проверяет структуру, кейсы и прогноз окупаемости.',
  },
]

const STEPS = [
  { number: '1', text: 'Выбираете режим и тему' },
  { number: '2', text: 'Отвечаете текстом или голосом' },
  { number: '3', text: 'Получаете оценку, разбор и рекомендации' },
]

function Landing() {
  const navigate = useNavigate()
  const [isMobile, setIsMobile] = useState(false)
  const [hoveredMode, setHoveredMode] = useState(null)

  useEffect(() => {
    const onResize = () => setIsMobile(window.innerWidth < 768)
    onResize()
    window.addEventListener('resize', onResize)
    return () => window.removeEventListener('resize', onResize)
  }, [])

  return (
    <>
      <Navbar />
      <main style={{ paddingTop: '72px' }}>
        <Section id="hero">
          <div style={{ textAlign: 'center' }}>
            <h1 style={{ fontSize: theme.sizes.h1 }}>
              <span style={{ display: 'block' }}>НЕЙРО-ТРЕНЕР</span>
              <span style={{ display: 'block' }}>ОТДЕЛА ПРОДАЖ</span>
              <span style={{ display: 'block' }}>РЕКЛАМЫ</span>
            </h1>
            <p
              style={{
                maxWidth: theme.layout.maxText,
                margin: `${theme.sizes.md} auto 0`,
                fontSize: theme.sizes.bodyLg,
                color: theme.colors.textMuted,
                textAlign: 'center',
              }}
            >
              Пять режимов тренировки. Один ИИ-наставник. Ваш отдел учится говорить с клиентом — без
              запинок, без «дорого», без потерь.
            </p>
            <div
              style={{
                display: 'flex',
                gap: theme.sizes.sm,
                marginTop: theme.sizes.lg,
                justifyContent: 'center',
                flexWrap: 'wrap',
                flexDirection: isMobile ? 'column' : 'row',
                alignItems: 'center',
              }}
            >
              <Button variant="primary" size="lg" onClick={() => navigate('/training')}>
                Начать тренировку
              </Button>
              <Button variant="secondary" size="lg" onClick={() => navigate('/login')}>
                Войти в аккаунт
              </Button>
            </div>
          </div>
        </Section>

        <div id="about" style={{ scrollMarginTop: '80px' }} />

        <Section id="screenshots">
          <h2 style={{ fontSize: theme.sizes.h2, textAlign: 'center', marginBottom: theme.sizes.lg }}>
            Как это выглядит
          </h2>
          <div
            style={{
              display: 'grid',
              gridTemplateColumns: isMobile ? '1fr' : 'repeat(3, 1fr)',
              gap: theme.sizes.md,
            }}
          >
            {[1, 2, 3].map((item) => (
              <div
                key={item}
                style={{
                  aspectRatio: '16 / 10',
                  background: theme.colors.bgSunken,
                  border: `1px solid ${theme.colors.border}`,
                  borderRadius: theme.radii.lg,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  color: theme.colors.textMuted,
                  fontSize: theme.sizes.caption,
                  padding: theme.sizes.md,
                  textAlign: 'center',
                }}
              >
                Интерфейс появится после первого запуска тренировки
              </div>
            ))}
          </div>
        </Section>

        <Section id="modes">
          <h2 style={{ fontSize: theme.sizes.h2, textAlign: 'center' }}>
            Пять навыков, которые тренирует система
          </h2>
          <p
            style={{
              textAlign: 'center',
              color: theme.colors.textMuted,
              margin: `${theme.sizes.sm} 0 ${theme.sizes.lg}`,
            }}
          >
            Каждый — отдельный режим с разбором от ИИ
          </p>
          {MODES.map((mode, index) => (
            <article
              key={mode.title}
              onMouseEnter={() => setHoveredMode(index)}
              onMouseLeave={() => setHoveredMode(null)}
              style={{
                borderRadius: theme.radii.lg,
                padding: '32px',
                background: theme.colors.bgElevated,
                border: `1px solid ${theme.colors.border}`,
                marginBottom: theme.sizes.sm,
                transition: theme.transitions.normal,
                transform: hoveredMode === index ? 'translateY(-2px)' : 'none',
                boxShadow: hoveredMode === index ? theme.shadows.hover : 'none',
              }}
            >
              <h3 style={{ fontSize: theme.sizes.h3, marginBottom: theme.sizes.xs }}>{mode.title}</h3>
              <p style={{ margin: 0, color: theme.colors.textMuted }}>{mode.description}</p>
            </article>
          ))}
        </Section>

        <Section id="how" background="elevated">
          <h2
            style={{
              fontSize: theme.sizes.h2,
              textAlign: 'center',
              marginBottom: theme.sizes.lg,
            }}
          >
            Три шага — одна тренировка
          </h2>
          <div
            style={{
              display: 'grid',
              gridTemplateColumns: isMobile ? '1fr' : 'repeat(3, 1fr)',
              gap: theme.sizes.md,
              textAlign: 'center',
            }}
          >
            {STEPS.map((step) => (
              <div key={step.number}>
                <div
                  style={{
                    fontSize: '48px',
                    fontWeight: 800,
                    color: theme.colors.accent,
                    lineHeight: 1.15,
                  }}
                >
                  {step.number}
                </div>
                <p style={{ margin: `${theme.sizes.sm} 0 0`, color: theme.colors.textBody }}>
                  {step.text}
                </p>
              </div>
            ))}
          </div>
        </Section>
      </main>
      <Footer />
    </>
  )
}

export default Landing

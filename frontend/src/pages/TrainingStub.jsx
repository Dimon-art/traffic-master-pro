/** Заглушка страницы режимов тренировки. */

import { useNavigate } from 'react-router-dom'

import Footer from '../components/Footer'
import Navbar from '../components/Navbar'
import Button from '../components/Button'
import theme from '../styles/theme'

function TrainingStub() {
  const navigate = useNavigate()

  return (
    <>
      <Navbar />
      <main
        style={{
          minHeight: '100vh',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          textAlign: 'center',
          padding: `72px ${theme.sizes.md} ${theme.sizes.lg}`,
          gap: theme.sizes.md,
        }}
      >
        <h1 style={{ fontSize: theme.sizes.h2 }}>
          Режимы тренировки появятся на следующем шаге
        </h1>
        <Button variant="primary" onClick={() => navigate('/')}>
          Вернуться на главную
        </Button>
        <div
          style={{
            maxWidth: theme.layout.maxText,
            width: '100%',
            marginTop: theme.sizes.lg,
            padding: theme.sizes.lg,
            background: theme.colors.bgElevated,
            border: `1px solid ${theme.colors.border}`,
            borderRadius: theme.radii.lg,
            boxShadow: theme.shadows.card,
          }}
        >
          <h2 style={{ fontSize: theme.sizes.h3, marginBottom: theme.sizes.sm }}>
            Хотите консультацию?
          </h2>
          <p style={{ margin: `0 0 ${theme.sizes.md}`, color: theme.colors.textMuted }}>
            Оставьте заявку — расскажем о тренировках и подберём программу под ваш отдел.
          </p>
          <Button variant="secondary" size="lg" onClick={() => navigate('/lead')}>
            Оставить заявку
          </Button>
        </div>
      </main>
      <Footer />
    </>
  )
}

export default TrainingStub

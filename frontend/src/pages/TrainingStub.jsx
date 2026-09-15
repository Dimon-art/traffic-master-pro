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
      </main>
      <Footer />
    </>
  )
}

export default TrainingStub

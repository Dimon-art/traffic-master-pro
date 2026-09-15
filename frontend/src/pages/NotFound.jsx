/** Страница 404. */

import { useNavigate } from 'react-router-dom'

import Footer from '../components/Footer'
import Navbar from '../components/Navbar'
import Button from '../components/Button'
import theme from '../styles/theme'

function NotFound() {
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
        }}
      >
        <p
          style={{
            margin: 0,
            fontSize: '120px',
            fontWeight: 800,
            color: theme.colors.accent,
            lineHeight: 1,
          }}
        >
          404
        </p>
        <h1 style={{ fontSize: theme.sizes.h2, margin: `${theme.sizes.md} 0` }}>Страница не найдена</h1>
        <Button variant="primary" onClick={() => navigate('/')}>
          На главную
        </Button>
      </main>
      <Footer />
    </>
  )
}

export default NotFound

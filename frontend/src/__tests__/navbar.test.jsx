/** Проверяет ссылки Navbar в зависимости от роли. */

import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import Navbar from '../components/Navbar.jsx'
import { useAuth } from '../context/AuthContext'

vi.mock('../context/AuthContext', () => ({
  useAuth: vi.fn(),
}))

function renderNavbar() {
  return render(
    <MemoryRouter>
      <Navbar />
    </MemoryRouter>,
  )
}

describe('Navbar — ссылки по ролям', () => {
  beforeEach(() => {
    useAuth.mockReset()
  })

  it('гость: видит кнопку «Войти», не видит «Мои тренировки»', () => {
    useAuth.mockReturnValue({ user: null, isAdmin: false, loading: false, logout: vi.fn() })
    renderNavbar()
    expect(screen.getByText(/Войти/i)).toBeInTheDocument()
    expect(screen.queryByText(/Мои тренировки/i)).not.toBeInTheDocument()
  })

  it('юзер: видит «Мои тренировки» → /trainings', () => {
    useAuth.mockReturnValue({
      user: { name: 'Иван', email: 'u@e.com', role: 'user' },
      isAdmin: false,
      loading: false,
      logout: vi.fn(),
    })
    renderNavbar()
    const link = screen.getByText(/Мои тренировки/i)
    expect(link).toBeInTheDocument()
    expect(link.closest('a')?.getAttribute('href')).toBe('/trainings')
  })

  it('админ: видит «Тренировки» и «Пользователи»', () => {
    useAuth.mockReturnValue({
      user: { name: 'Admin', email: 'a@e.com', role: 'admin' },
      isAdmin: true,
      loading: false,
      logout: vi.fn(),
    })
    renderNavbar()
    expect(screen.getByText(/^Тренировки$/i)).toBeInTheDocument()
    expect(screen.getByText(/Пользователи/i)).toBeInTheDocument()
  })
})

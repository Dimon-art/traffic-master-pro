/** Проверяет, что на /training видны все пять режимов. */

import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { describe, expect, it, vi } from 'vitest'

import Training from '../pages/Training.jsx'

vi.mock('../context/AuthContext', () => ({
  useAuth: () => ({ user: null, isAdmin: false, loading: false, logout: vi.fn() }),
}))

describe('/training — список режимов', () => {
  it('показывает 5 режимов', () => {
    render(
      <MemoryRouter>
        <Training />
      </MemoryRouter>,
    )
    expect(screen.getByRole('heading', { name: /Знание продукта/i })).toBeInTheDocument()
    expect(screen.getByRole('heading', { name: /Работа с возражениями/i })).toBeInTheDocument()
    expect(screen.getByRole('heading', { name: /Выявление потребностей/i })).toBeInTheDocument()
    expect(screen.getByRole('heading', { name: /Продающий созвон/i })).toBeInTheDocument()
    expect(screen.getByRole('heading', { name: /коммерческого предложения/i })).toBeInTheDocument()
    expect(screen.getAllByRole('heading', { level: 2 }).filter((el) =>
      [
        'Знание продукта',
        'Работа с возражениями',
        'Выявление потребностей',
        'Продающий созвон',
        'Мастер коммерческого предложения',
      ].includes(el.textContent),
    )).toHaveLength(5)
  })
})

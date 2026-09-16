/** Статическая проверка, что в App.jsx объявлены все маршруты. */

import { readFileSync } from 'node:fs'
import { dirname, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

import { describe, expect, it } from 'vitest'

const EXPECTED_ROUTES = [
  '/',
  '/login',
  '/register',
  '/training',
  '/training/product-knowledge',
  '/training/objections',
  '/training/objections/:topic',
  '/trainings',
  '/trainings/:trainingId',
  '/lead',
  '/leads',
  '/admin/users',
  '/admin',
  '*',
]

describe('App.jsx — маршруты', () => {
  const appSource = readFileSync(
    resolve(dirname(fileURLToPath(import.meta.url)), '../App.jsx'),
    'utf-8',
  )

  it.each(EXPECTED_ROUTES)('должен содержать маршрут %s', (route) => {
    const pattern = `path="${route}"`
    expect(
      appSource.includes(pattern),
      `Маршрут "${route}" отсутствует в App.jsx. Проверь, не удалён ли он.`,
    ).toBe(true)
  })

  it('должен содержать <Routes> и <BrowserRouter>', () => {
    expect(appSource).toContain('<Routes>')
    expect(appSource).toContain('<BrowserRouter>')
  })
})

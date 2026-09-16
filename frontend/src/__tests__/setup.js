/** Общая подготовка Vitest: jest-dom, очистка и моки. */

import '@testing-library/jest-dom'
import { cleanup } from '@testing-library/react'
import { afterEach, vi } from 'vitest'

const localStorageMock = (() => {
  let store = {}
  return {
    getItem: (key) => store[key] || null,
    setItem: (key, value) => {
      store[key] = value.toString()
    },
    removeItem: (key) => {
      delete store[key]
    },
    clear: () => {
      store = {}
    },
  }
})()

global.localStorage = localStorageMock
global.fetch = vi.fn()

afterEach(() => {
  cleanup()
  localStorage.clear()
})

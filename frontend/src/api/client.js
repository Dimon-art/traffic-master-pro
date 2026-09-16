/** HTTP-клиент API с JWT из localStorage. */

const API_URL = (import.meta.env.VITE_API_URL || 'http://localhost:8031/api').replace(
  /\/$/,
  '',
)
const TOKEN_KEY = 'token'

export function getToken() {
  return window.localStorage.getItem(TOKEN_KEY)
}

export function setToken(token) {
  window.localStorage.setItem(TOKEN_KEY, token)
}

export function clearToken() {
  window.localStorage.removeItem(TOKEN_KEY)
}

function parseDetail(data) {
  const detail = data?.detail
  if (!detail) {
    return 'Ошибка запроса'
  }
  if (typeof detail === 'string') {
    return detail
  }
  if (Array.isArray(detail)) {
    return detail.map((item) => item.msg || String(item)).join(' ')
  }
  return 'Ошибка запроса'
}

export async function apiFetch(path, options = {}) {
  const headers = {
    'Content-Type': 'application/json',
    ...(options.headers || {}),
  }
  const token = getToken()
  if (token) {
    headers.Authorization = `Bearer ${token}`
  }

  const response = await fetch(`${API_URL}${path}`, { ...options, headers })

  if (response.status === 401) {
    clearToken()
    let message = 'Недействительный токен'
    try {
      const data = await response.json()
      message = parseDetail(data)
    } catch {
      // тело ответа может быть пустым
    }
    throw new Error(message)
  }

  if (!response.ok) {
    let message = 'Ошибка запроса'
    try {
      const data = await response.json()
      message = parseDetail(data)
    } catch {
      // тело ответа может быть пустым
    }
    throw new Error(message)
  }

  return response.json()
}

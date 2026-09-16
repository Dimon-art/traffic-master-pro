/** Контекст авторизации: сессия, вход, регистрация и выход. */

import { createContext, useContext, useEffect, useMemo, useState } from 'react'

import { apiFetch, clearToken, getToken, setToken } from '../api/client'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function loadUser() {
      if (!getToken()) {
        setLoading(false)
        return
      }
      try {
        const data = await apiFetch('/auth/me')
        setUser(data)
      } catch {
        clearToken()
        setUser(null)
      } finally {
        setLoading(false)
      }
    }
    loadUser()
  }, [])

  const value = useMemo(
    () => ({
      user,
      loading,
      isAdmin: user?.role === 'admin',
      role: user?.role || null,
      async login(email, password) {
        const data = await apiFetch('/auth/login', {
          method: 'POST',
          body: JSON.stringify({ email, password }),
        })
        setToken(data.access_token)
        setUser(data.user)
        return data
      },
      async register(name, email, password) {
        const data = await apiFetch('/auth/register', {
          method: 'POST',
          body: JSON.stringify({ name, email, password }),
        })
        setToken(data.access_token)
        setUser(data.user)
        return data
      },
      logout() {
        clearToken()
        setUser(null)
      },
    }),
    [user, loading],
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (context === null) {
    throw new Error('useAuth должен вызываться внутри AuthProvider')
  }
  return context
}

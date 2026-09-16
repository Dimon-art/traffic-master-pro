/** Защита маршрутов: редирект гостей, пользователей и не-админов. */

import { Navigate } from 'react-router-dom'

import { useAuth } from '../context/AuthContext'

function ProtectedRoute({ children, requireAuth = true, requireAdmin = false }) {
  const { loading, user, isAdmin } = useAuth()

  if (loading) {
    return <div>Загрузка...</div>
  }
  if (!user && requireAuth) {
    return <Navigate to="/login" replace />
  }
  if (user && requireAdmin && !isAdmin) {
    return <Navigate to="/" replace />
  }
  if (user && !requireAuth) {
    return <Navigate to="/" replace />
  }
  return children
}

export default ProtectedRoute

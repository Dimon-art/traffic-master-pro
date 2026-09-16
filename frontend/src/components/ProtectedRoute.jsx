/** Защита маршрутов: редирект гостей и авторизованных пользователей. */

import { Navigate } from 'react-router-dom'

import { useAuth } from '../context/AuthContext'

function ProtectedRoute({ children, requireAuth = true }) {
  const { loading, user } = useAuth()

  if (loading) {
    return <div>Загрузка...</div>
  }
  if (requireAuth && !user) {
    return <Navigate to="/login" replace />
  }
  if (!requireAuth && user) {
    return <Navigate to="/" replace />
  }
  return children
}

export default ProtectedRoute

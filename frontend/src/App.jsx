/** Корневой роутер приложения TrafficMaster Pro. */

import { BrowserRouter, Route, Routes } from 'react-router-dom'

import ProtectedRoute from './components/ProtectedRoute.jsx'
import { AuthProvider } from './context/AuthContext.jsx'
import AdminUsers from './pages/AdminUsers.jsx'
import HealthPanel from './pages/HealthPanel.jsx'
import Landing from './pages/Landing.jsx'
import Lead from './pages/Lead.jsx'
import Leads from './pages/Leads.jsx'
import Login from './pages/Login.jsx'
import MyTrainings from './pages/MyTrainings.jsx'
import NotFound from './pages/NotFound.jsx'
import Register from './pages/Register.jsx'
import Training from './pages/Training.jsx'
import TrainingDetail from './pages/TrainingDetail.jsx'
import TrainingObjectionSession from './pages/TrainingObjectionSession.jsx'
import TrainingObjections from './pages/TrainingObjections.jsx'
import TrainingProductKnowledge from './pages/TrainingProductKnowledge.jsx'

function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          <Route path="/" element={<Landing />} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="/training" element={<Training />} />
          <Route
            path="/training/product-knowledge"
            element={
              <ProtectedRoute>
                <TrainingProductKnowledge />
              </ProtectedRoute>
            }
          />
          <Route
            path="/training/objections"
            element={
              <ProtectedRoute>
                <TrainingObjections />
              </ProtectedRoute>
            }
          />
          <Route
            path="/training/objections/:topic"
            element={
              <ProtectedRoute>
                <TrainingObjectionSession />
              </ProtectedRoute>
            }
          />
          <Route
            path="/trainings"
            element={
              <ProtectedRoute>
                <MyTrainings />
              </ProtectedRoute>
            }
          />
          <Route
            path="/trainings/:trainingId"
            element={
              <ProtectedRoute>
                <TrainingDetail />
              </ProtectedRoute>
            }
          />
          <Route
            path="/lead"
            element={
              <ProtectedRoute>
                <Lead />
              </ProtectedRoute>
            }
          />
          <Route
            path="/leads"
            element={
              <ProtectedRoute>
                <Leads />
              </ProtectedRoute>
            }
          />
          <Route
            path="/admin/users"
            element={
              <ProtectedRoute requireAdmin>
                <AdminUsers />
              </ProtectedRoute>
            }
          />
          <Route
            path="/admin"
            element={
              <ProtectedRoute>
                <HealthPanel />
              </ProtectedRoute>
            }
          />
          <Route path="*" element={<NotFound />} />
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  )
}

export default App

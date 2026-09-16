/** Корневой роутер приложения TrafficMaster Pro. */

import { BrowserRouter, Route, Routes } from 'react-router-dom'

import ProtectedRoute from './components/ProtectedRoute.jsx'
import { AuthProvider } from './context/AuthContext.jsx'
import HealthPanel from './pages/HealthPanel.jsx'
import Landing from './pages/Landing.jsx'
import Login from './pages/Login.jsx'
import NotFound from './pages/NotFound.jsx'
import Register from './pages/Register.jsx'
import TrainingStub from './pages/TrainingStub.jsx'

function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          <Route path="/" element={<Landing />} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="/training" element={<TrainingStub />} />
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

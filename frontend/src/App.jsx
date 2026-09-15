/** Корневой роутер приложения TrafficMaster Pro. */

import { BrowserRouter, Route, Routes } from 'react-router-dom'

import HealthPanel from './pages/HealthPanel.jsx'
import Landing from './pages/Landing.jsx'
import Login from './pages/Login.jsx'
import NotFound from './pages/NotFound.jsx'
import TrainingStub from './pages/TrainingStub.jsx'

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Landing />} />
        <Route path="/login" element={<Login />} />
        <Route path="/training" element={<TrainingStub />} />
        <Route path="/admin" element={<HealthPanel />} />
        <Route path="*" element={<NotFound />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App

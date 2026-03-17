import { Routes, Route } from 'react-router-dom'
import Layout from './components/layout/Layout'
import Dashboard from './pages/Dashboard'
import RealTimeDetection from './pages/RealTimeDetection'
import ModelComparison from './pages/ModelComparison'
import Performance from './pages/Performance'
import Alerts from './pages/Alerts'
import About from './pages/About'

function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route path="/" element={<Dashboard />} />
        <Route path="/detection" element={<RealTimeDetection />} />
        <Route path="/models" element={<ModelComparison />} />
        <Route path="/performance" element={<Performance />} />
        <Route path="/alerts" element={<Alerts />} />
        <Route path="/about" element={<About />} />
      </Route>
    </Routes>
  )
}

export default App

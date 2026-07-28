import { Routes, Route, Navigate } from 'react-router-dom'
import LandingPage from './pages/LandingPage'
import ConfigPage from './pages/ConfigPage'
import AnnotationPage from './pages/AnnotationPage'
import ReviewPage from './pages/ReviewPage'

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<LandingPage />} />
      <Route path="/config" element={<ConfigPage />} />
      <Route path="/annotate" element={<AnnotationPage />} />
      <Route path="/review" element={<ReviewPage />} />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}

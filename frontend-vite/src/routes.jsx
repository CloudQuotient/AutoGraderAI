import { Routes, Route, Navigate } from 'react-router-dom'
import Login from './pages/Login'
import StudentDashboard from './pages/student/StudentDashboard'
import StudentClassView from './pages/student/StudentClassView'
import StudentQuestionAttempt from './pages/student/StudentQuestionAttempt'
import InstructorDashboard from './pages/instructor/InstructorDashboard'
import InstructorClassView from './pages/instructor/InstructorClassView'
import InstructorQuestionView from './pages/instructor/InstructorQuestionView'

function RequireAuth({ children }) {
  const token = typeof window !== 'undefined' ? localStorage.getItem('token') : null
  if (!token) {
    return <Navigate to="/login" replace />
  }
  return children
}

function AppRoutes() {
  return (
    <Routes>
      <Route path="/" element={<Navigate to="/login" replace />} />
      <Route path="/login" element={<Login />} />
      <Route path="/student/dashboard" element={<RequireAuth><StudentDashboard /></RequireAuth>} />
      <Route path="/student/class/:classId" element={<RequireAuth><StudentClassView /></RequireAuth>} />
      <Route path="/student/class/:classId/question/:questionId" element={<RequireAuth><StudentQuestionAttempt /></RequireAuth>} />
      <Route path="/instructor/dashboard" element={<RequireAuth><InstructorDashboard /></RequireAuth>} />
      <Route path="/instructor/class/:classId" element={<RequireAuth><InstructorClassView /></RequireAuth>} />
      <Route path="/instructor/class/:classId/question/:questionId" element={<RequireAuth><InstructorQuestionView /></RequireAuth>} />
    </Routes>
  )
}

export default AppRoutes


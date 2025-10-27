import { Routes, Route, Navigate } from 'react-router-dom'
import Login from './pages/Login'
import StudentDashboard from './pages/student/StudentDashboard'
import StudentClassView from './pages/student/StudentClassView'
import StudentQuestionAttempt from './pages/student/StudentQuestionAttempt'
import InstructorDashboard from './pages/instructor/InstructorDashboard'
import InstructorClassView from './pages/instructor/InstructorClassView'
import InstructorQuestionView from './pages/instructor/InstructorQuestionView'

function AppRoutes() {
  return (
    <Routes>
      <Route path="/" element={<Navigate to="/login" replace />} />
      <Route path="/login" element={<Login />} />
      
      {/* Student Routes */}
      <Route path="/student/dashboard" element={<StudentDashboard />} />
      <Route path="/student/class/:classId" element={<StudentClassView />} />
      <Route path="/student/class/:classId/question/:questionId" element={<StudentQuestionAttempt />} />
      
      {/* Instructor Routes */}
      <Route path="/instructor/dashboard" element={<InstructorDashboard />} />
      <Route path="/instructor/class/:classId" element={<InstructorClassView />} />
      <Route path="/instructor/class/:classId/question/:questionId" element={<InstructorQuestionView />} />
    </Routes>
  )
}

export default AppRoutes

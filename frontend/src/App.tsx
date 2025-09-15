import { Routes, Route, Navigate } from 'react-router-dom';
import Login from './pages/Login';
import SubmitAssignment from './pages/SubmitAssignment';
import StudentDashboard from './pages/StudentDashboard';
import InstructorDashboard from './pages/InstructorDashboard';

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/submit" element={<SubmitAssignment />} />
      <Route path="/student" element={<StudentDashboard />} />
      <Route path="/instructor" element={<InstructorDashboard />} />
      <Route path="*" element={<Navigate to="/login" />} />
    </Routes>
  );
}

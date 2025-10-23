import { BrowserRouter, Routes, Route } from "react-router-dom";
import StudentClasses from "./components/StudentClasses";
import StudentClassQuestions from "./components/StudentClassQuestions";
import StudentQuestionAttempt from "./components/StudentQuestionAttempt";
import InstructorClasses from "./components/InstructorClasses";
import InstructorClassQuestions from "./components/InstructorClassQuestions";
import InstructorAddQuestion from "./components/InstructorAddQuestion";

export default function AppRoutes() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Student Routes */}
        <Route path="/student/classes" element={<StudentClasses />} />
        <Route path="/student/class/:id" element={<StudentClassQuestions />} />
        <Route path="/student/class/:classId/:questionId" element={<StudentQuestionAttempt />} />

        {/* Instructor Routes */}
        <Route path="/instructor/classes" element={<InstructorClasses />} />
        <Route path="/instructor/class/:id" element={<InstructorClassQuestions />} />
        <Route path="/instructor/class/:id/question" element={<InstructorAddQuestion />} />

        <Route path="*" element={<h2>404 Not Found</h2>} />
      </Routes>
    </BrowserRouter>
  );
}

import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import API from "../api/api";

export default function InstructorClassQuestions() {
  const { id } = useParams();
  const [questions, setQuestions] = useState([]);

  useEffect(() => {
    API.get(`/api/instructor/class/${id}`)
      .then(res => setQuestions(res.data.questions))
      .catch(err => console.error(err));
  }, [id]);

  return (
    <div>
      <h2>Questions for Class #{id}</h2>
      <Link to={`/instructor/class/${id}/question`}>+ Add Question</Link>
      <ul>
        {questions.map(q => (
          <li key={q.QuestionID}>
            Question #{q.QuestionID} — Status: {q.Status}
          </li>
        ))}
      </ul>
    </div>
  );
}

import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import API from "../api/api";

export default function StudentClassQuestions() {
  const { id } = useParams();
  const [questions, setQuestions] = useState([]);

  useEffect(() => {
    API.get(`/api/student/class/${id}`)
      .then(res => setQuestions(res.data.questions))
      .catch(err => console.error(err));
  }, [id]);

  return (
    <div>
      <h2>Questions for Class #{id}</h2>
      {questions.length ? (
        <ul>
          {questions.map(q => (
            <li key={q.QuestionID}>
              <Link to={`/student/class/${id}/${q.QuestionID}`}>
                Question #{q.QuestionID} — Status: {q.Status}
              </Link>
            </li>
          ))}
        </ul>
      ) : (
        <p>No questions found.</p>
      )}
    </div>
  );
}

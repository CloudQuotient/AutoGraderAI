import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import API from "../api/api";

export default function StudentQuestionAttempt() {
  const { classId, questionId } = useParams();
  const [question, setQuestion] = useState(null);

  useEffect(() => {
    API.get(`/api/student/class/${classId}/${questionId}`)
      .then(res => setQuestion(res.data))
      .catch(err => console.error(err));
  }, [classId, questionId]);

  if (!question) return <p>Loading question...</p>;

  return (
    <div>
      <h2>Question #{questionId}</h2>
      <p>{question.QuestionText}</p>
      <pre>{JSON.stringify(question.TestCases, null, 2)}</pre>

      {question.Status === "open" && (
        <div>
          <textarea rows="10" cols="50" placeholder="Write your code here..." />
          <br />
          <button>Run</button>
          <button>Submit</button>
        </div>
      )}

      {question.Status === "closed" && question.Submission && (
        <div>
          <p><strong>Score:</strong> {question.Submission.Score}</p>
          <p><strong>Feedback:</strong> {question.Submission.Feedback}</p>
        </div>
      )}
    </div>
  );
}

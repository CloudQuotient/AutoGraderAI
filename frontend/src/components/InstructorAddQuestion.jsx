import { useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import API from "../api/api";

export default function InstructorAddQuestion() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [form, setForm] = useState({ QuestionText: "", TestCases: [] });
  const [input, setInput] = useState({ input: "", output: "" });

  const addTestCase = () => {
    if (!input.input || !input.output) return;
    setForm({ ...form, TestCases: [...form.TestCases, input] });
    setInput({ input: "", output: "" });
  };

  const handleSubmit = async () => {
    try {
      await API.post(`/api/instructor/class/${id}/question`, form);
      navigate(`/instructor/class/${id}`);
    } catch (err) {
      console.error(err);
      alert("Error adding question");
    }
  };

  return (
    <div>
      <h2>Add Question for Class #{id}</h2>

      <textarea
        placeholder="Question text"
        value={form.QuestionText}
        onChange={e => setForm({ ...form, QuestionText: e.target.value })}
      />
      <h3>Add Test Case</h3>
      <input
        placeholder="Input"
        value={input.input}
        onChange={e => setInput({ ...input, input: e.target.value })}
      />
      <input
        placeholder="Expected Output"
        value={input.output}
        onChange={e => setInput({ ...input, output: e.target.value })}
      />
      <button onClick={addTestCase}>Add Test Case</button>

      <pre>{JSON.stringify(form.TestCases, null, 2)}</pre>

      <button onClick={handleSubmit}>Save Question</button>
    </div>
  );
}

import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import API from "../api/api";

export default function InstructorClasses() {
  const [data, setData] = useState(null);

  useEffect(() => {
    API.get("/api/instructor/classes")
      .then(res => setData(res.data))
      .catch(err => console.error(err));
  }, []);

  if (!data) return <p>Loading...</p>;

  return (
    <div>
      <h2>Instructor: {data.instructor.Name}</h2>
      <h3>Classes</h3>
      <ul>
        {data.classes.map(cls => (
          <li key={cls.ClassID}>
            <Link to={`/instructor/class/${cls.ClassID}`}>Class #{cls.ClassID}</Link>
          </li>
        ))}
      </ul>
    </div>
  );
}

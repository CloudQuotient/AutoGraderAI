import { useEffect, useState } from "react";
import API from "../api/api";
import { Link } from "react-router-dom";

export default function StudentClasses() {
  const [classes, setClasses] = useState([]);

  useEffect(() => {
    API.get("/api/student/classes")
      .then(res => setClasses(res.data.classes))
      .catch(err => console.error(err));
  }, []);

  return (
    <div>
      <h2>Student Classes</h2>
      {classes.length ? (
        <ul>
          {classes.map(cls => (
            <li key={cls.ClassID}>
              <Link to={`/student/class/${cls.ClassID}`}>
                Class #{cls.ClassID} — Instructor: {cls.InstructorName}
              </Link>
            </li>
          ))}
        </ul>
      ) : (
        <p>No classes found.</p>
      )}
    </div>
  );
}

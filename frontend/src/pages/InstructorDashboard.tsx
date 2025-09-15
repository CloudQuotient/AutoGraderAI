import React, { useEffect, useState } from 'react';
import { getInstructorStats, getSubmissions } from '../lib/api';

export default function InstructorDashboard() {
  const [stats, setStats] = useState<any>({});
  const [submissions, setSubmissions] = useState([]);
  const [filter, setFilter] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    Promise.all([
      getInstructorStats(),
      getSubmissions(filter)
    ])
      .then(([statsData, subsData]) => {
        setStats(statsData);
        setSubmissions(subsData);
        setLoading(false);
      })
      .catch(() => {
        setError('Failed to load dashboard');
        setLoading(false);
      });
  }, [filter]);

  return (
    <div className="p-6">
      <h2 className="text-xl mb-4">Instructor Dashboard</h2>
      {loading ? (
        <div>Loading...</div>
      ) : error ? (
        <div className="text-red-500">{error}</div>
      ) : (
        <>
          <div className="mb-4">
            <div>Students: {stats.studentCount ?? '-'}</div>
            <div>Average Score: {stats.avgScore ?? '-'}</div>
            <div>Flagged Plagiarism: {stats.plagiarismCount ?? '-'}</div>
          </div>
          <div className="mb-2">
            <input
              type="text"
              placeholder="Filter by assignment or student"
              value={filter}
              onChange={e => setFilter(e.target.value)}
              className="border p-2"
            />
          </div>
          <table className="min-w-full border">
            <thead>
              <tr>
                <th className="border px-2">Student</th>
                <th className="border px-2">Assignment</th>
                <th className="border px-2">Score</th>
                <th className="border px-2">Plagiarism</th>
                <th className="border px-2">Submitted At</th>
              </tr>
            </thead>
            <tbody>
              {submissions.map((sub: any) => (
                <tr key={sub.id}>
                  <td className="border px-2">{sub.studentName}</td>
                  <td className="border px-2">{sub.assignmentTitle}</td>
                  <td className="border px-2">{sub.score ?? '-'}</td>
                  <td className="border px-2">{sub.plagiarismFlag ? 'Yes' : 'No'}</td>
                  <td className="border px-2">{sub.submittedAt}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </>
      )}
    </div>
  );
}

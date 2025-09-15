import React, { useEffect, useState } from 'react';
import { getStudentSubmissions } from '../lib/api';

export default function StudentDashboard() {
  const [submissions, setSubmissions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    getStudentSubmissions()
      .then(data => {
        setSubmissions(data);
        setLoading(false);
      })
      .catch(err => {
        setError('Failed to load submissions');
        setLoading(false);
      });
  }, []);

  return (
    <div className="p-6">
      <h2 className="text-xl mb-4">Student Dashboard</h2>
      {loading ? (
        <div>Loading...</div>
      ) : error ? (
        <div className="text-red-500">{error}</div>
      ) : (
        <table className="min-w-full border">
          <thead>
            <tr>
              <th className="border px-2">Assignment</th>
              <th className="border px-2">Score</th>
              <th className="border px-2">Feedback</th>
              <th className="border px-2">Version</th>
              <th className="border px-2">Actions</th>
            </tr>
          </thead>
          <tbody>
            {submissions.map((sub: any) => (
              <tr key={sub.id}>
                <td className="border px-2">{sub.assignmentTitle}</td>
                <td className="border px-2">{sub.score ?? '-'}</td>
                <td className="border px-2">{sub.feedback ?? '-'}</td>
                <td className="border px-2">{sub.version}</td>
                <td className="border px-2">
                  <button className="bg-blue-500 text-white px-2 py-1 rounded" onClick={() => window.location.href = '/submit'}>Resubmit</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}

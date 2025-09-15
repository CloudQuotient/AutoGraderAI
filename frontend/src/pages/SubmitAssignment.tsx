import React, { useState } from 'react';
import FileUploader from '../components/FileUploader';
import { getPresignedUploadUrl, submitMetadata } from '../lib/api';

const MOCK_ASSIGNMENTS = [
  { id: 'a1', name: 'Assignment 1' },
  { id: 'a2', name: 'Assignment 2' },
];

const DEMO_MODE = typeof import.meta.env !== 'undefined' && import.meta.env.VITE_DEMO_MODE === 'true';

export default function SubmitAssignment() {
  const [assignmentId, setAssignmentId] = useState('');
  const [file, setFile] = useState<File | null>(null);
  const [status, setStatus] = useState('');
  const [error, setError] = useState('');

  const handleFileChange = (f: File | null) => setFile(f);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setStatus('');
    if (!assignmentId || !file) {
      setError('Please select assignment and file.');
      return;
    }
    try {
      let presignRes;
      let s3Key;
      if (DEMO_MODE) {
        presignRes = { url: 'https://demo-url', key: 'demo-key' };
        s3Key = 'demo-key';
      } else {
        presignRes = await getPresignedUploadUrl(assignmentId, file.name);
        s3Key = presignRes.key;
        await FileUploader.uploadFile(file, presignRes.url);
      }
      const userId = DEMO_MODE ? 'demo-user' : localStorage.getItem('userId') || '';
      await submitMetadata({ assignmentId, s3Key, filename: file.name, userId });
      setStatus('Submission successful!');
    } catch (err: any) {
      setError(err.message || 'Submission failed');
    }
  };

  return (
    <div className="max-w-md mx-auto mt-10 p-6 bg-white rounded shadow">
      <h2 className="text-xl mb-4">Submit Assignment</h2>
      <form onSubmit={handleSubmit}>
        <select
          value={assignmentId}
          onChange={e => setAssignmentId(e.target.value)}
          className="border p-2 mb-4 w-full"
        >
          <option value="">Select Assignment</option>
          {MOCK_ASSIGNMENTS.map(a => (
            <option key={a.id} value={a.id}>{a.name}</option>
          ))}
        </select>
        <FileUploader onFileChange={handleFileChange} />
        {error && <div className="text-red-500 mt-2">{error}</div>}
        {status && <div className="text-green-500 mt-2">{status}</div>}
        <button type="submit" className="bg-blue-500 text-white px-4 py-2 rounded w-full mt-4">Submit</button>
      </form>
      {DEMO_MODE && <div className="mt-4 text-sm text-gray-500">Demo mode enabled. No real upload.</div>}
    </div>
  );
}

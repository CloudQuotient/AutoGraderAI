import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

export async function getPresignedUploadUrl(assignmentId: string, filename: string) {
  const token = localStorage.getItem('jwt');
  const res = await axios.get(`${API_BASE_URL}/api/v1/presign`, {
    params: { assignmentId, filename },
    headers: { Authorization: `Bearer ${token}` },
  });
  return res.data;
}

export async function submitMetadata({ assignmentId, s3Key, filename, userId }: { assignmentId: string; s3Key: string; filename: string; userId: string; }) {
  const token = localStorage.getItem('jwt');
  await axios.post(`${API_BASE_URL}/api/v1/submissions`, {
    assignmentId, s3Key, filename, userId
  }, {
    headers: { Authorization: `Bearer ${token}` },
  });
}

export async function getStudentSubmissions() {
  // TODO: Replace with real API call
  return [
    { id: 'sub1', assignmentTitle: 'Assignment 1', score: 95, feedback: 'Great job!', version: 1 },
    { id: 'sub2', assignmentTitle: 'Assignment 2', score: 88, feedback: 'Needs improvement.', version: 2 }
  ];
}

export async function getInstructorStats() {
  // TODO: Replace with real API call
  return { studentCount: 20, avgScore: 82, plagiarismCount: 1 };
}

export async function getSubmissions(filter: string) {
  // TODO: Replace with real API call
  return [
    { id: 'sub1', studentName: 'Alice', assignmentTitle: 'Assignment 1', score: 95, plagiarismFlag: false, submittedAt: '2025-09-10' },
    { id: 'sub2', studentName: 'Bob', assignmentTitle: 'Assignment 2', score: 88, plagiarismFlag: true, submittedAt: '2025-09-12' }
  ];
}

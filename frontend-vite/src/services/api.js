import axios from 'axios';

const API = axios.create({
  baseURL: 'http://localhost:5000',
});

// Interceptor to add auth token if needed in the future
API.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export default API;

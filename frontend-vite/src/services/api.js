
import axios from 'axios'
import { BACKEND_URL } from '../config'

const API = axios.create({
  baseURL: BACKEND_URL,
  withCredentials: true,
})

API.interceptors.request.use((config) => {
  const token = typeof window !== 'undefined' ? localStorage.getItem('token') : null
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

API.interceptors.response.use(
  (response) => response,
  (error) => {
    const status = error?.response?.status
    if (status === 401 || status === 403) {
      try { localStorage.clear() } catch {}
      if (typeof window !== 'undefined') {
        window.location.href = '/login'
      }
    }
    return Promise.reject(error)
  }
)

export default API


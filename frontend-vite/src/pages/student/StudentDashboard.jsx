import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import toast from 'react-hot-toast'
import API from '../../services/api'

function StudentDashboard() {
  const [classes, setClasses] = useState([])
  const [loading, setLoading] = useState(true)
  const navigate = useNavigate()

  useEffect(() => {
    fetchClasses()
  }, [])

  const fetchClasses = async () => {
    try {
      setLoading(true)
      console.log('[StudentDashboard] Fetching classes...')
      const response = await API.get('/api/student/classes')
      console.log('[StudentDashboard] Response:', response.data)
      
      const classes = response.data.classes || []
      console.log(`[StudentDashboard] Found ${classes.length} classes`)
      
      if (classes.length === 0 && response.data.message) {
        console.warn('[StudentDashboard] No classes:', response.data.message)
        toast.error(response.data.message || 'No classes available')
      }
      
      setClasses(classes)
    } catch (error) {
      console.error('[StudentDashboard] Error fetching classes:', error)
      console.error('[StudentDashboard] Error details:', {
        message: error.message,
        response: error.response?.data,
        status: error.response?.status
      })
      
      const errorMsg = error.response?.data?.message || error.message || 'Failed to load classes'
      toast.error(errorMsg)
      setClasses([])
    } finally {
      setLoading(false)
    }
  }

  const handleClassClick = (classId) => {
    navigate(`/student/class/${classId}`)
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex justify-between items-center">
            <h1 className="text-2xl font-bold text-gray-900">My Classes</h1>
            <button
              onClick={() => {
                localStorage.clear()
                navigate('/login')
              }}
              className="text-sm text-gray-600 hover:text-gray-900"
            >
              Logout
            </button>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {loading ? (
          <div className="flex justify-center items-center h-64">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
          </div>
        ) : classes.length === 0 ? (
          <div className="text-center py-12">
            <p className="text-gray-500 mb-4">No classes enrolled yet.</p>
            <p className="text-sm text-gray-400">
              Check browser console (F12) for details
            </p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {classes.map((cls) => (
              <div
                key={cls.ClassID}
                onClick={() => handleClassClick(cls.ClassID)}
                className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow cursor-pointer border border-gray-200 hover:border-indigo-500"
              >
                <div className="flex items-center justify-between mb-4">
                  <span className="text-sm font-medium text-indigo-600 bg-indigo-50 px-3 py-1 rounded-full">
                    Class ID: {cls.ClassID}
                  </span>
                </div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">
                  Instructor: {cls.InstructorName}
                </h3>
                <p className="text-sm text-gray-500">
                  Click to view questions
                </p>
              </div>
            ))}
          </div>
        )}
      </main>
    </div>
  )
}

export default StudentDashboard

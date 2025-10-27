import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import toast from 'react-hot-toast'
import API from '../../services/api'

function InstructorDashboard() {
  const [classes, setClasses] = useState([])
  const [instructor, setInstructor] = useState(null)
  const [loading, setLoading] = useState(true)
  const navigate = useNavigate()

  useEffect(() => {
    fetchClasses()
  }, [])

  const fetchClasses = async () => {
    try {
      setLoading(true)
      const response = await API.get('/api/instructor/classes')
      setInstructor(response.data.instructor)
      setClasses(response.data.classes || [])
    } catch (error) {
      console.error('Error fetching classes:', error)
      toast.error('Failed to load classes')
      setClasses([])
    } finally {
      setLoading(false)
    }
  }

  const handleClassClick = (classId) => {
    navigate(`/instructor/class/${classId}`)
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Instructor Portal</h1>
              {instructor && (
                <p className="text-sm text-gray-600">Welcome, {instructor.Name}</p>
              )}
            </div>
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
            <p className="text-gray-500">No classes available.</p>
          </div>
        ) : (
          <div>
            <h2 className="text-xl font-semibold text-gray-900 mb-6">My Classes</h2>
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
                    Class {cls.ClassID}
                  </h3>
                  <p className="text-sm text-gray-500">
                    Click to view questions
                  </p>
                </div>
              ))}
            </div>
          </div>
        )}
      </main>
    </div>
  )
}

export default InstructorDashboard

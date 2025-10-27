import { useState, useEffect } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import toast from 'react-hot-toast'
import API from '../../services/api'
import AddNewQuestion from '../../components/instructor/AddNewQuestion'

function InstructorClassView() {
  const { classId } = useParams()
  const [questions, setQuestions] = useState([])
  const [loading, setLoading] = useState(true)
  const [showAddModal, setShowAddModal] = useState(false)
  const navigate = useNavigate()

  useEffect(() => {
    fetchQuestions()
  }, [classId])

  const fetchQuestions = async () => {
    try {
      setLoading(true)
      const response = await API.get(`/api/instructor/class/${classId}`)
      setQuestions(response.data.questions || [])
    } catch (error) {
      console.error('Error fetching questions:', error)
      toast.error('Failed to load questions')
      setQuestions([])
    } finally {
      setLoading(false)
    }
  }

  const handleViewResults = (questionId) => {
    navigate(`/instructor/class/${classId}/question/${questionId}`)
  }

  const handleAddQuestionSuccess = () => {
    setShowAddModal(false)
    fetchQuestions()
  }

  const getStatusColor = (status) => {
    return status === 'open' ? 'text-green-600 bg-green-100' : 'text-red-600 bg-red-100'
  }

  const getStatusIcon = (status) => {
    return status === 'open' ? '🟢' : '🔴'
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <button
                onClick={() => navigate('/instructor/dashboard')}
                className="text-gray-600 hover:text-gray-900"
              >
                ← Back
              </button>
              <h1 className="text-2xl font-bold text-gray-900">Class {classId}</h1>
            </div>
            <button
              onClick={() => setShowAddModal(true)}
              className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 flex items-center space-x-2"
            >
              <span>+</span>
              <span>Add New Question</span>
            </button>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {loading ? (
          <div className="flex justify-center items-center h-64">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
          </div>
        ) : questions.length === 0 ? (
          <div className="text-center py-12">
            <p className="text-gray-500 mb-4">No questions available for this class.</p>
            <button
              onClick={() => setShowAddModal(true)}
              className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700"
            >
              Add First Question
            </button>
          </div>
        ) : (
          <div className="bg-white shadow-sm rounded-lg overflow-hidden">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Question ID
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Status
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Action
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {questions.map((question) => (
                  <tr key={question.QuestionID} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      {question.QuestionID}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`px-3 py-1 rounded-full text-xs font-medium ${getStatusColor(question.Status)}`}>
                        {getStatusIcon(question.Status)} {question.Status.toUpperCase()}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                      <button
                        onClick={() => handleViewResults(question.QuestionID)}
                        className="text-indigo-600 hover:text-indigo-900 font-medium"
                      >
                        View Results
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </main>

      {showAddModal && (
        <AddNewQuestion
          classId={classId}
          onClose={() => setShowAddModal(false)}
          onSuccess={handleAddQuestionSuccess}
        />
      )}
    </div>
  )
}

export default InstructorClassView

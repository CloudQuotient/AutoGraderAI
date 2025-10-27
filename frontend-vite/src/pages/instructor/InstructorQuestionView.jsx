import { useState, useEffect } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import toast from 'react-hot-toast'
import API from '../../services/api'

function InstructorQuestionView() {
  const { classId, questionId } = useParams()
  const [questionData, setQuestionData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [evaluating, setEvaluating] = useState(false)
  const navigate = useNavigate()

  useEffect(() => {
    fetchQuestionData()
  }, [classId, questionId])

  const fetchQuestionData = async () => {
    try {
      setLoading(true)
      const response = await API.get(`/api/instructor/class/${classId}/${questionId}`)
      setQuestionData(response.data)
    } catch (error) {
      console.error('Error fetching question data:', error)
      toast.error('Failed to load question')
    } finally {
      setLoading(false)
    }
  }

  const handleEvaluate = async () => {
    if (!confirm('Are you sure you want to evaluate and close submissions for this question? This action cannot be undone.')) {
      return
    }

    try {
      setEvaluating(true)
      await API.post(`/api/instructor/evaluate/${questionId}`)
      toast.success('Question evaluated successfully!')
      fetchQuestionData()
    } catch (error) {
      console.error('Error evaluating question:', error)
      toast.error('Failed to evaluate question')
    } finally {
      setEvaluating(false)
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex justify-center items-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
      </div>
    )
  }

  if (!questionData) {
    return (
      <div className="min-h-screen bg-gray-50 flex justify-center items-center">
        <p className="text-gray-500">Question not found</p>
      </div>
    )
  }

  const isOpen = questionData.status === 'open'

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center space-x-4">
            <button
              onClick={() => navigate(`/instructor/class/${classId}`)}
              className="text-gray-600 hover:text-gray-900"
            >
              ← Back
            </button>
            <h1 className="text-2xl font-bold text-gray-900">
              Question {questionId}
            </h1>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* State A: Question is open */}
        {isOpen && (
          <div className="bg-white rounded-lg shadow-sm p-8 text-center">
            <div className="max-w-2xl mx-auto space-y-6">
              <div className="text-6xl mb-4">📝</div>
              <p className="text-lg text-gray-700">
                {questionData.msg || 'Click on Evaluate Button For Results'}
              </p>
              <p className="text-sm text-gray-500 mb-8">
                This will evaluate all student submissions and close the question for further submissions.
              </p>
              <button
                onClick={handleEvaluate}
                disabled={evaluating}
                className="px-8 py-4 bg-indigo-600 text-white text-lg font-semibold rounded-lg hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors shadow-lg"
              >
                {evaluating ? (
                  <span className="flex items-center justify-center space-x-2">
                    <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                    <span>Evaluating...</span>
                  </span>
                ) : (
                  'Evaluate & Close Submissions'
                )}
              </button>
            </div>
          </div>
        )}

        {/* State B: Question is closed */}
        {!isOpen && questionData.results && (
          <div className="bg-white rounded-lg shadow-sm p-8">
            <h2 className="text-2xl font-bold text-gray-900 mb-6">Results</h2>
            
            <div className="bg-gray-900 text-green-400 font-mono text-sm rounded-lg p-6 overflow-auto max-h-96">
              <pre className="whitespace-pre-wrap">
                {typeof questionData.results === 'string' 
                  ? questionData.results 
                  : JSON.stringify(questionData.results, null, 2)}
              </pre>
            </div>

            <div className="mt-6 p-4 bg-blue-50 rounded-lg">
              <p className="text-sm text-blue-800">
                <strong>Note:</strong> This shows the plagiarism report and evaluation results for all student submissions.
              </p>
            </div>
          </div>
        )}

        {/* State B: Question is closed but no results yet */}
        {!isOpen && !questionData.results && (
          <div className="bg-white rounded-lg shadow-sm p-8 text-center">
            <div className="text-6xl mb-4">📊</div>
            <p className="text-lg text-gray-700">
              No results available yet.
            </p>
          </div>
        )}
      </main>
    </div>
  )
}

export default InstructorQuestionView

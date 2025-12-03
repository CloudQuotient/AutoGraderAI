import { useState, useEffect } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import toast from 'react-hot-toast'
import API from '../../services/api'

function InstructorQuestionView() {
  const { classId, questionId } = useParams()
  const [questionData, setQuestionData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [evaluating, setEvaluating] = useState(false)
  const [showOthers, setShowOthers] = useState(false)
  const [showAll, setShowAll] = useState(false)
  const navigate = useNavigate()

  useEffect(() => {
    fetchQuestionData()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [classId, questionId])

  const fetchQuestionData = async () => {
    try {
      setLoading(true)
      const response = await API.get(`/api/instructor/class/${classId}/${questionId}`)
      console.log('Fetched question data:', response.data)
      setQuestionData(response.data)
    } catch (error) {
      console.error('Error fetching question data:', error)
      toast.error('Failed to load question')
      setQuestionData(null)
    } finally {
      setLoading(false)
    }
  }

  const handleEvaluate = async () => {
    if (!window.confirm('Are you sure you want to evaluate and close submissions for this question? This action cannot be undone.')) {
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

  const extractStudentNumber = (filename) => {
    const match = filename.match(/student_(\d+)_/i)
    return match ? `Student ${match[1]}` : filename
  }

  // Loading state
  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex justify-center items-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
      </div>
    )
  }

  // No data
  if (!questionData) {
    return (
      <div className="min-h-screen bg-gray-50 flex justify-center items-center">
        <p className="text-gray-500">Question not found</p>
      </div>
    )
  }

  const isOpen = questionData.status === 'open'
  const results = questionData.results

  return (
    <div className="min-h-screen bg-gray-50">
      {/* HEADER */}
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

      {/* MAIN CONTENT */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">

        {/* OPEN STATE */}
        {isOpen && (
          <div className="bg-white rounded-lg shadow-sm p-8 text-center">
            <div className="max-w-2xl mx-auto space-y-6">
              <div className="text-6xl mb-4">📝</div>
              <p className="text-lg text-gray-700">
                {questionData.msg || 'Click the button below to evaluate all submissions.'}
              </p>
              <p className="text-sm text-gray-500 mb-8">
                This will evaluate all student submissions and close the question for further submissions.
              </p>
              <button
                onClick={handleEvaluate}
                disabled={evaluating}
                className="px-8 py-4 bg-indigo-600 text-white text-lg font-semibold rounded-lg hover:bg-indigo-700 disabled:opacity-50 transition-colors shadow-lg"
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

        {/* CLOSED STATE WITH RESULTS */}
        {!isOpen && results && (
          <div className="bg-white rounded-lg shadow-sm p-8">
            <h2 className="text-2xl font-bold text-gray-900 mb-6">📊 Plagiarism Report</h2>

            {(() => {
              const plagiarised = results.results.filter(r => r.plagiarism_flag)
              const others = results.results.filter(r => !r.plagiarism_flag)
              const all = results.results

              return (
                <div className="space-y-10">

                  {/* SUMMARY */}
                  <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
                    <div className="bg-blue-50 rounded-lg p-4 text-blue-800 shadow-sm border border-blue-100">
                      <p className="text-sm font-medium">Similarity Threshold</p>
                      <p className="text-xl font-bold">{(results.threshold * 100).toFixed(2)}%</p>
                    </div>
                    <div className="bg-green-50 rounded-lg p-4 text-green-800 shadow-sm border border-green-100">
                      <p className="text-sm font-medium">Storage Bucket</p>
                      <p className="text-sm font-mono truncate">{results.bucket}</p>
                    </div>
                    <div className="bg-gray-50 rounded-lg p-4 text-gray-700 shadow-sm border border-gray-100">
                      <p className="text-sm font-medium">Total Comparisons</p>
                      <p className="text-xl font-bold">{results.results.length}</p>
                    </div>
                  </div>

                  {/* BUTTONS */}
                  <div className="flex flex-wrap gap-3">
                    <button
                      onClick={() => setShowAll(false)}
                      className={`px-4 py-2 rounded-lg font-medium transition-colors ${!showAll ? 'bg-red-600 text-white' : 'bg-gray-100 text-gray-700 hover:bg-gray-200'}`}
                    >
                      Plagiarised Only
                    </button>
                    <button
                      onClick={() => setShowAll(true)}
                      className={`px-4 py-2 rounded-lg font-medium transition-colors ${showAll ? 'bg-indigo-600 text-white' : 'bg-gray-100 text-gray-700 hover:bg-gray-200'}`}
                    >
                      Show All Comparisons
                    </button>
                  </div>

                  {/* PLAGIARISED / ALL RESULTS */}
                  <div>
                    <div className="overflow-x-auto rounded-lg border border-gray-200 shadow-sm">
                      <table className="min-w-full text-sm">
                        <thead className="bg-gray-100 text-gray-700 uppercase tracking-wide">
                          <tr>
                            <th className="px-4 py-2 text-left">Student 1</th>
                            <th className="px-4 py-2 text-left">Student 2</th>
                            <th className="px-4 py-2 text-center">Similarity</th>
                            <th className="px-4 py-2 text-center">Plagiarised</th>
                          </tr>
                        </thead>
                        <tbody>
                          {(showAll ? all : plagiarised).map((row, idx) => (
                            <tr
                              key={idx}
                              className={`border-b ${row.plagiarism_flag ? 'bg-red-50 hover:bg-red-100' : 'hover:bg-gray-50'} transition-colors`}
                            >
                              <td className="px-4 py-2 font-mono text-sm text-gray-800">
                                {extractStudentNumber(row.file1)}
                              </td>
                              <td className="px-4 py-2 font-mono text-sm text-gray-800">
                                {extractStudentNumber(row.file2)}
                              </td>
                              <td className="px-4 py-2 text-center font-semibold text-gray-800">
                                {(row.similarity * 100).toFixed(2)}%
                              </td>
                              <td className="px-4 py-2 text-center">
                                {row.plagiarism_flag ? (
                                  <span className="text-red-600 font-semibold">Yes</span>
                                ) : (
                                  <span className="text-green-600 font-semibold">No</span>
                                )}
                              </td>
                            </tr>
                          ))}
                          {(!showAll && plagiarised.length === 0) && (
                            <tr>
                              <td colSpan={4} className="text-center py-4 text-gray-400">
                                No plagiarised pairs found 🎉
                              </td>
                            </tr>
                          )}
                        </tbody>
                      </table>
                    </div>
                  </div>
                </div>
              )
            })()}
          </div>
        )}

        {/* CLOSED STATE, NO RESULTS */}
        {!isOpen && !results && (
          <div className="bg-white rounded-lg shadow-sm p-8 text-center">
            <div className="text-6xl mb-4">📊</div>
            <p className="text-lg text-gray-700">No results available yet.</p>
          </div>
        )}
      </main>
    </div>
  )
}

export default InstructorQuestionView

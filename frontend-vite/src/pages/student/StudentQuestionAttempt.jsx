import { useState, useEffect } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import toast from 'react-hot-toast'
import Editor from '@monaco-editor/react'
import API from '../../services/api'

function StudentQuestionAttempt() {
  const { classId, questionId } = useParams()
  const [questionData, setQuestionData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [code, setCode] = useState('# Write your code here\n')
  const [testRunResults, setTestRunResults] = useState(null)
  const [submitting, setSubmitting] = useState(false)
  const [testing, setTesting] = useState(false)
  const [language, setLanguage] = useState('Python')
  const [prevLanguage, setPrevLanguage] = useState('Python')

  const languageExtensions = {
    'C': 'c',
    'C++': 'cpp',
    'Java': 'java',
    'Python': 'py'
  }

  const monacoLanguages = {
    'C': 'c',
    'C++': 'cpp',
    'Java': 'java',
    'Python': 'python'
  }
  const navigate = useNavigate()

  useEffect(() => {
    fetchQuestionData()
  }, [classId, questionId])

  const fetchQuestionData = async () => {
    try {
      setLoading(true)
      const response = await API.get(`/api/student/class/${classId}/${questionId}`)
      setQuestionData(response.data)
    } catch (error) {
      console.error('Error fetching question data:', error)
      toast.error('Failed to load question')
    } finally {
      setLoading(false)
    }
  }

  const handleTestRun = async () => {
    try {
      setTesting(true)
      
      const ext = languageExtensions[language]
      const filename = `Main.${ext}`
      const blob = new Blob([code], { type: 'text/plain' })
      const file = new File([blob], filename, { type: 'text/plain' })
      
      const formData = new FormData()
      formData.append('file', file)

      if (prevLanguage !== language && prevLanguage) {
        const oldExt = languageExtensions[prevLanguage];
        const oldFilename = `Main.${oldExt}`;
        formData.append('old_filename', oldFilename);
      }

      const response = await API.post(`/api/student/run/${questionId}`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      })

      setTestRunResults(response.data.Results)
      toast.success('Test run completed successfully')
      setPrevLanguage(language);
    } catch (error) {
      console.error('Error running test:', error)
      toast.error('Test run failed')
    } finally {
      setTesting(false)
    }
  }

  const handleFinalSubmit = async () => {
    try {
      setSubmitting(true)
      
      const ext = languageExtensions[language]
      const filename = `Main.${ext}`
      const blob = new Blob([code], { type: 'text/plain' })
      const file = new File([blob], filename, { type: 'text/plain' })
      
      const formData = new FormData()
      formData.append('file', file)

      if (prevLanguage !== language && prevLanguage) {
        const oldExt = languageExtensions[prevLanguage];
        const oldFilename = `Main.${oldExt}`;
        formData.append('old_filename', oldFilename);
      }

      await API.post(`/api/student/submission/${questionId}`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      })

      toast.success('Submission successful!')
      navigate(`/student/class/${classId}`)
      setPrevLanguage(language);
    } catch (error) {
      console.error('Error submitting:', error)
      toast.error('Submission failed')
    } finally {
      setSubmitting(false)
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

  const isQuestionOpen = questionData.Status === 'open'
  const isSubmitted = !!questionData.message
  const isClosed = questionData.Status === 'closed'

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center space-x-4">
            <button
              onClick={() => navigate(`/student/class/${classId}`)}
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
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Left Column - Problem Description */}
          <div className="bg-white rounded-lg shadow-sm p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">
              Problem Description
            </h2>
            <div className="prose prose-sm max-w-none mb-6">
              <p className="text-gray-700 whitespace-pre-wrap">
                {questionData.QuestionText}
              </p>
            </div>

            <h3 className="text-lg font-semibold text-gray-900 mb-3">
              Test Cases
            </h3>
            <div className="space-y-3">
              {Array.isArray(questionData.TestCases) ? (
                questionData.TestCases.map((testCase, idx) => (
                  <div key={idx} className="border border-gray-200 rounded p-3">
                    <div className="flex items-start space-x-2">
                      <span className="font-medium text-indigo-600">Test {idx + 1}:</span>
                      <div className="flex-1">
                        {typeof testCase === 'object' ? (
                          <>
                            {testCase.input && (
                              <p className="text-sm text-gray-600">
                                <span className="font-medium">Input:</span> {testCase.input}
                              </p>
                            )}
                            {testCase.output && (
                              <p className="text-sm text-gray-600">
                                <span className="font-medium">Expected Output:</span> {testCase.output}
                              </p>
                            )}
                          </>
                        ) : (
                          <p className="text-sm text-gray-600">{testCase}</p>
                        )}
                      </div>
                    </div>
                  </div>
                ))
              ) : (
                <div className="border border-gray-200 rounded p-3">
                  <p className="text-sm text-gray-600">{JSON.stringify(questionData.TestCases)}</p>
                </div>
              )}
            </div>
          </div>

          {/* Right Column - Code Editor / Results */}
          <div className="space-y-6">
            {/* State A: Open and not submitted */}
            {isQuestionOpen && !isSubmitted && (
              <div className="bg-white rounded-lg shadow-sm">
                <div className="p-4 border-b border-gray-200">
                  <h2 className="text-xl font-semibold text-gray-900">Code Editor</h2>
                </div>
                <div className="flex items-center px-4 py-2 space-x-4">
                  <label className="text-sm font-bold text-gray-700 whitespace-nowrap">Select Code Language:</label>
                  <select
                    value={language}
                    onChange={(e) => {
                      setPrevLanguage(language);
                      setLanguage(e.target.value);
                    }}
                    className="flex-1 block rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 py-2 px-3"
                  >
                    <option>C</option>
                    <option>C++</option>
                    <option>Java</option>
                    <option>Python</option>
                  </select>
                </div>
                <div className="h-96">
                  <Editor
                    height="100%"
                    language={monacoLanguages[language]}
                    value={code}
                    onChange={setCode}
                    theme="vs-light"
                    options={{
                      minimap: { enabled: false },
                      fontSize: 14,
                      lineNumbers: 'on',
                      scrollBeyondLastLine: false,
                    }}
                  />
                </div>
                <div className="p-4 border-t border-gray-200 space-x-4 flex">
                  <button
                    onClick={handleTestRun}
                    disabled={testing}
                    className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {testing ? 'Running...' : 'Test Run'}
                  </button>
                  <button
                    onClick={handleFinalSubmit}
                    disabled={submitting}
                    className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {submitting ? 'Submitting...' : 'Final Submit'}
                  </button>
                </div>
              </div>
            )}

            {/* State B: Open and submitted */}
            {isQuestionOpen && isSubmitted && (
              <div className="bg-white rounded-lg shadow-sm p-6">
                <div className="text-center py-8">
                  <div className="text-6xl mb-4">⏳</div>
                  <p className="text-lg text-gray-700">
                    {questionData.message || 'Already submitted. Please wait for results.'}
                  </p>
                </div>
              </div>
            )}

            {/* State C: Closed */}
            {isClosed && (
              <div className="bg-white rounded-lg shadow-sm p-6">
                <h2 className="text-xl font-semibold text-gray-900 mb-4">Results</h2>
                {questionData.Submission && (
                  <div className="space-y-4">
                    <div className="border border-gray-200 rounded-lg p-4">
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-sm font-medium text-gray-700">Score:</span>
                        <span className={`text-lg font-bold ${
                          questionData.Submission.Score !== null && questionData.Submission.Score !== undefined
                            ? 'text-green-600'
                            : 'text-gray-600'
                        }`}>
                          {questionData.Submission.Score !== null && questionData.Submission.Score !== undefined
                            ? `${questionData.Submission.Score}%`
                            : 'N/A'}
                        </span>
                      </div>
                    </div>
                    <div className="border border-gray-200 rounded-lg p-4">
                      <span className="text-sm font-medium text-gray-700 block mb-2">
                        Feedback:
                      </span>
                      <p className="text-gray-600 whitespace-pre-wrap">
                        {questionData.Submission.Feedback || 'No feedback available'}
                      </p>
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* Test Run Results */}
            {testRunResults && isQuestionOpen && !isSubmitted && (
              <div className="bg-white rounded-lg shadow-sm">
                <div className="p-4 border-b border-gray-200">
                  <h2 className="text-xl font-semibold text-gray-900">Test Run Results</h2>
                </div>
                <div className="p-4 bg-gray-900 text-green-400 font-mono text-sm rounded-b-lg overflow-auto max-h-64">
                  <pre>{JSON.stringify(testRunResults, null, 2)}</pre>
                </div>
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  )
}

export default StudentQuestionAttempt

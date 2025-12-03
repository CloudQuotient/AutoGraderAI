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
      navigate(`api/student/class/${classId}`)
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
                        <span className="text-sm font-medium text-gray-700">Score: </span>
                        <span className={`text-lg font-bold ${
                          questionData.Submission.Score !== null && questionData.Submission.Score !== undefined
                            ? 'text-green-600'
                            : 'text-gray-600'
                        }`}>
                          {(() => {
                            const scoreArr = Array.isArray(questionData.Submission.Score?.results)
                              ? questionData.Submission.Score.results
                              : Array.isArray(questionData.Submission.Score)
                                ? questionData.Submission.Score
                                : null;
                            if (scoreArr) {
                              return (
                                <div className="overflow-x-auto">
                                  <table className="min-w-full text-sm border border-gray-200 rounded">
                                    <thead>
                                      <tr className="bg-gray-100">
                                        <th className="px-2 py-1 border">Test Case</th>
                                        <th className="px-2 py-1 border">Input</th>
                                        <th className="px-2 py-1 border">Expected</th>
                                        <th className="px-2 py-1 border">Actual</th>
                                        <th className="px-2 py-1 border">Status</th>
                                      </tr>
                                    </thead>
                                    <tbody>
                                      {scoreArr.map((res, idx) => (
                                        <tr key={idx}>
                                          <td className="px-2 py-1 border text-center">{res.test_case || idx + 1}</td>
                                          <td className="px-2 py-1 border">{String(res.input)}</td>
                                          <td className="px-2 py-1 border">{String(res.expected)}</td>
                                          <td className="px-2 py-1 border">{String(res.actual)}</td>
                                          <td className={`px-2 py-1 border text-center font-semibold ${
                                            res.status === 'Passed' ? 'text-green-600' :
                                            res.status === 'Failed' ? 'text-yellow-600' :
                                            'text-red-600'
                                          }`}>
                                            {res.status}
                                          </td>
                                        </tr>
                                      ))}
                                    </tbody>
                                  </table>
                                </div>
                              );
                            } else if (typeof questionData.Submission.Score === 'object' && questionData.Submission.Score !== null) {
                              return <span className="text-xs text-gray-500">{JSON.stringify(questionData.Submission.Score)}</span>;
                            } else {
                              return questionData.Submission.Score !== null && questionData.Submission.Score !== undefined
                                ? questionData.Submission.Score
                                : 'N/A';
                            }
                          })()}
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
                <div className="p-4 space-y-4">
                  {(() => {
                    const resultArray = Array.isArray(testRunResults)
                      ? testRunResults
                      : (testRunResults.results || []);

                    const passed = resultArray.filter(r => r.status === 'Passed').length;
                    const failed = resultArray.filter(r => r.status === 'Failed').length;
                    const errors = resultArray.filter(r => r.status === 'Error' || r.status === 'Compile Error').length;

                    return (
                      <>
                        <div className="flex items-center gap-2 text-sm">
                          <span className="px-2 py-1 rounded-full bg-green-100 text-green-700 font-medium">Passed: {passed}</span>
                          <span className="px-2 py-1 rounded-full bg-yellow-100 text-yellow-700 font-medium">Failed: {failed}</span>
                          <span className="px-2 py-1 rounded-full bg-red-100 text-red-700 font-medium">Errors: {errors}</span>
                          <span className="ml-auto text-gray-500">Total: {resultArray.length}</span>
                        </div>

                        <div className="divide-y divide-gray-200 border border-gray-200 rounded-lg overflow-hidden">
                          {resultArray.map((res, idx) => (
                            <div key={idx} className="p-4 bg-white">
                              <div className="flex items-center justify-between mb-2">
                                <div className="flex items-center gap-3">
                                  <span className="text-sm text-gray-500">Test {res.test_case || idx + 1}</span>
                                  <span
                                    className={
                                      `text-xs font-semibold px-2 py-1 rounded-full ` +
                                      (res.status === 'Passed' ? 'bg-green-100 text-green-700' :
                                       res.status === 'Failed' ? 'bg-yellow-100 text-yellow-700' :
                                       'bg-red-100 text-red-700')
                                    }
                                  >
                                    {res.status}
                                  </span>
                                </div>
                              </div>

                              <div className="grid grid-cols-1 md:grid-cols-3 gap-3 text-sm">
                                {res.input !== undefined && (
                                  <div className="bg-gray-50 rounded p-3">
                                    <div className="text-gray-500 font-medium mb-1">Input</div>
                                    <pre className="whitespace-pre-wrap text-gray-800">{String(res.input)}</pre>
                                  </div>
                                )}
                                {res.expected !== undefined && (
                                  <div className="bg-gray-50 rounded p-3">
                                    <div className="text-gray-500 font-medium mb-1">Expected</div>
                                    <pre className="whitespace-pre-wrap text-gray-800">{String(res.expected)}</pre>
                                  </div>
                                )}
                                {(res.actual !== undefined || res.error) && (
                                  <div className={`rounded p-3 ${res.error ? 'bg-red-50' : 'bg-gray-50'}`}>
                                    <div className="text-gray-500 font-medium mb-1">{res.error ? 'Error' : 'Actual'}</div>
                                    <pre className={`whitespace-pre-wrap ${res.error ? 'text-red-700' : 'text-gray-800'}`}>
                                      {String(res.error || res.actual)}
                                    </pre>
                                  </div>
                                )}
                              </div>
                            </div>
                          ))}
                          {resultArray.length === 0 && (
                            <div className="p-4 text-sm text-gray-500">No test results returned.</div>
                          )}
                        </div>

                        {/* Raw JSON (collapsed) for debugging when needed */}
                        <details className="mt-2">
                          <summary className="text-sm text-gray-500 cursor-pointer">Show raw JSON</summary>
                          <div className="mt-2 bg-gray-900 text-green-400 font-mono text-xs rounded p-3 overflow-auto max-h-64">
                            <pre>{JSON.stringify(testRunResults, null, 2)}</pre>
                          </div>
                        </details>
                      </>
                    );
                  })()}
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
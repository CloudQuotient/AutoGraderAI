import { useState } from 'react'
import toast from 'react-hot-toast'
import API from '../../services/api'

function AddNewQuestion({ classId, onClose, onSuccess }) {
  const [questionText, setQuestionText] = useState('')
  const [testCases, setTestCases] = useState([
    { input: '', output: '' }
  ])
  const [submitting, setSubmitting] = useState(false)

  const handleAddTestCase = () => {
    setTestCases([...testCases, { input: '', output: '' }])
  }

  const handleRemoveTestCase = (index) => {
    if (testCases.length > 1) {
      setTestCases(testCases.filter((_, i) => i !== index))
    }
  }

  const handleTestCaseChange = (index, field, value) => {
    const updated = [...testCases]
    updated[index][field] = value
    setTestCases(updated)
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    
    if (!questionText.trim()) {
      toast.error('Please enter question text')
      return
    }

    // Validate test cases
    const validTestCases = testCases.filter(tc => tc.input.trim() && tc.output.trim())
    if (validTestCases.length === 0) {
      toast.error('Please add at least one valid test case')
      return
    }

    try {
      setSubmitting(true)
      const payload = {
        QuestionText: questionText,
        TestCases: validTestCases
      }

      const response = await API.post(`/api/instructor/class/${classId}/question`, payload)
      
      toast.success('Question added successfully!')
      onSuccess()
    } catch (error) {
      console.error('Error adding question:', error)
      toast.error('Failed to add question')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
        <div className="sticky top-0 bg-white border-b border-gray-200 px-6 py-4">
          <div className="flex justify-between items-center">
            <h2 className="text-2xl font-bold text-gray-900">Add New Question</h2>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600 text-2xl"
            >
              ×
            </button>
          </div>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-6">
          <div>
            <label htmlFor="questionText" className="block text-sm font-medium text-gray-700 mb-2">
              Question Text
            </label>
            <textarea
              id="questionText"
              value={questionText}
              onChange={(e) => setQuestionText(e.target.value)}
              required
              rows={6}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none"
              placeholder="Enter the question description..."
            />
          </div>

          <div>
            <div className="flex justify-between items-center mb-4">
              <label className="block text-sm font-medium text-gray-700">
                Test Cases
              </label>
              <button
                type="button"
                onClick={handleAddTestCase}
                className="px-3 py-1 bg-indigo-600 text-white text-sm rounded-lg hover:bg-indigo-700"
              >
                + Add Test Case
              </button>
            </div>

            <div className="space-y-4">
              {testCases.map((testCase, index) => (
                <div key={index} className="border border-gray-200 rounded-lg p-4">
                  <div className="flex justify-between items-center mb-3">
                    <span className="text-sm font-medium text-gray-700">
                      Test Case {index + 1}
                    </span>
                    {testCases.length > 1 && (
                      <button
                        type="button"
                        onClick={() => handleRemoveTestCase(index)}
                        className="text-red-600 hover:text-red-800 text-sm"
                      >
                        Remove
                      </button>
                    )}
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-xs font-medium text-gray-600 mb-1">
                        Input
                      </label>
                      <input
                        type="text"
                        value={testCase.input}
                        onChange={(e) => handleTestCaseChange(index, 'input', e.target.value)}
                        className="w-full px-3 py-2 border border-gray-300 rounded focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none text-sm"
                        placeholder="e.g., [1,2,3,4,5]"
                      />
                    </div>
                    <div>
                      <label className="block text-xs font-medium text-gray-600 mb-1">
                        Expected Output
                      </label>
                      <input
                        type="text"
                        value={testCase.output}
                        onChange={(e) => handleTestCaseChange(index, 'output', e.target.value)}
                        className="w-full px-3 py-2 border border-gray-300 rounded focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none text-sm"
                        placeholder="e.g., [1,2,3,4,5]"
                      />
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="flex justify-end space-x-4 pt-4 border-t border-gray-200">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={submitting}
              className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {submitting ? 'Submitting...' : 'Submit'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

export default AddNewQuestion

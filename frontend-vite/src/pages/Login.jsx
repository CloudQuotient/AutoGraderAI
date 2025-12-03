import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import toast from 'react-hot-toast'
import API from '../services/api'

// --- ADD THESE IMPORTS ---
import { AuthenticationDetails, CognitoUser } from 'amazon-cognito-identity-js'
import { userPool } from '../cognitoConfig' // Adjusted path to src/cognitoConfig.js

function Login() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate()

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)

    try {
      // --- START: NEW COGNITO LOGIC ---

      // 1. Set up Cognito auth objects
      const cognitoUser = new CognitoUser({
        Username: email,
        Pool: userPool,
      })

      const authDetails = new AuthenticationDetails({
        Username: email,
        Password: password,
      })

      // 2. Create a Promise wrapper for the Cognito login
      const loginToCognito = () => {
        return new Promise((resolve, reject) => {
          cognitoUser.authenticateUser(authDetails, {
            onSuccess: (session) => {
              // 3. Get the *Cognito ID Token* on success
              const cognitoIdToken = session.getIdToken().getJwtToken()
              resolve(cognitoIdToken)
            },
            onFailure: (err) => {
              reject(err)
            },
            // 4. This handles the 'FORCE_CHANGE_PASSWORD' state for imported users
            newPasswordRequired: () => {
              // We'll just re-use the temporary password as the new permanent one.
              // A real app might show a modal asking for a new password.
              cognitoUser.completeNewPasswordChallenge(password, {}, {
                onSuccess: (session) => {
                  const cognitoIdToken = session.getIdToken().getJwtToken()
                  resolve(cognitoIdToken)
                },
                onFailure: (err) => {
                  reject(err)
                },
              })
            },
          })
        })
      }

      // 5. Authenticate with Cognito first
      const cognitoIdToken = await loginToCognito()

      // --- END: NEW COGNITO LOGIC ---


      // 6. Call YOUR backend with the Cognito token (this line is modified)
      const response = await API.post('/api/login', {
        token: cognitoIdToken, // Send the token, not email/pass
      })

      // 7. This part is THE SAME! It handles the response from your backend.
      const { access_token, role, user_id } = response.data

      // Store user info in localStorage
      localStorage.setItem('role', role)
      localStorage.setItem('userId', user_id.toString())
      localStorage.setItem('token', access_token)

      toast.success(`Logged in as ${role}`)

      // Redirect based on role
      if (role === 'student') {
        navigate('/student/dashboard')
      } else if (role === 'instructor') {
        navigate('/instructor/dashboard')
      } else {
        navigate('/login')
      }
    } catch (error) {
      // This error handling is now smarter
      let errorMsg

      if (error.code) {
        // This is a Cognito error (e.g., 'UserNotFoundException')
        if (error.code === 'UserNotFoundException') {
          errorMsg = 'User does not exist.'
        } else if (error.code === 'NotAuthorizedException') {
          errorMsg = 'Incorrect email or password.'
        } else {
          errorMsg = error.message || 'Login failed. Please try again.'
        }
      } else {
        // This is an error from your backend (axios)
        errorMsg = error.response?.data?.message || 'Login failed. Please try again.'
      }

      toast.error(errorMsg)
      console.error('Login error:', error)
    } finally {
      setLoading(false)
    }
  }

  return (
    // NO CHANGES NEEDED TO YOUR UI!
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="bg-white p-8 rounded-lg shadow-xl w-full max-w-md">
        <h2 className="text-3xl font-bold text-center text-gray-800 mb-6">
          Autograder Login
        </h2>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-2">
              Email
            </label>
            <input
              id="email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none"
              placeholder="Enter your email"
            />
          </div>
          <div>
            <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-2">
              Password
            </label>
            <input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none"
              placeholder="Enter your password"
            />
          </div>
          <button
            type="submit"
            disabled={loading}
            className="w-full bg-indigo-600 text-white py-2 px-4 rounded-lg hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {loading ? 'Logging in...' : 'Login'}
          </button>
        </form>
      </div>
    </div>
  )
}

export default Login
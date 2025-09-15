import React, { useState } from 'react';
import { signIn } from 'aws-amplify/auth';
// Removed duplicate import of Amplify
import { Amplify } from 'aws-amplify';

Amplify.configure({
  Auth: {
    Cognito: {
      userPoolId: import.meta.env.VITE_COGNITO_POOL_ID,
      userPoolClientId: import.meta.env.VITE_COGNITO_CLIENT_ID,
      // region is not a valid key for Cognito config in Amplify v6
    }
  }
});

export default function Login() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    try {
      const result = await signIn({ username, password });
      if (result.isSignedIn && result.nextStep?.signInStep === 'DONE') {
        // Amplify v6 returns tokens in result.tokens if available
        const idToken = (result as any).tokens?.idToken;
        if (idToken) {
          localStorage.setItem('jwt', idToken);
          // Decode JWT to get role
          const payload = JSON.parse(atob(idToken.split('.')[1]));
          localStorage.setItem('userRole', payload['custom:role'] || 'student');
          if (payload['custom:role'] === 'instructor') {
            window.location.href = '/instructor';
          } else {
            window.location.href = '/student';
          }
        } else {
          setError('Login succeeded but no token returned.');
        }
      } else {
        setError('Login failed: ' + (result.nextStep?.signInStep || 'Unknown error'));
      }
    } catch (err: any) {
      setError(err.message || 'Login failed');
    }
  };

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-gray-100">
      <form onSubmit={handleLogin} className="bg-white p-6 rounded shadow w-80">
        <h2 className="text-xl mb-4">Login</h2>
        <input
          type="text"
          placeholder="Username"
          value={username}
          onChange={e => setUsername(e.target.value)}
          className="border p-2 mb-2 w-full"
          required
        />
        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={e => setPassword(e.target.value)}
          className="border p-2 mb-2 w-full"
          required
        />
        {error && <div className="text-red-500 mb-2">{error}</div>}
        <button type="submit" className="bg-blue-500 text-white px-4 py-2 rounded w-full">Login</button>
      </form>
    </div>
  );
}

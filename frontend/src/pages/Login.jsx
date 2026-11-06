import { useState } from 'react'
import { Link, Navigate, useLocation, useNavigate } from 'react-router-dom'
import Layout from '../components/Layout'
import { useAuth } from '../auth/AuthContext'

export default function Login() {
  const { user, login } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [submitting, setSubmitting] = useState(false)

  if (user) {
    return <Navigate to="/dashboard" replace />
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')

    if (!username.trim()) {
      setError('Username is required.')
      return
    }
    if (!password) {
      setError('Password is required.')
      return
    }

    setSubmitting(true)
    try {
      const result = await login(username, password)
      if (result.error) {
        setError(result.error)
        return
      }
      const next = location.state?.from || '/dashboard'
      navigate(next)
    } catch {
      setError('Unable to log in. Please try again.')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <Layout>
      <div className="mx-auto max-w-sm px-4 py-16">
        <h1 className="text-2xl font-semibold text-white">Log In</h1>
        <form onSubmit={handleSubmit} className="mt-8 space-y-4">
          <div>
            <label className="block text-sm text-neutral-400">Username</label>
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              autoComplete="username"
              className="mt-1 w-full rounded border border-echo-border bg-echo-card px-3 py-2 text-white outline-none focus:border-neutral-500"
            />
          </div>
          <div>
            <label className="block text-sm text-neutral-400">Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              autoComplete="current-password"
              className="mt-1 w-full rounded border border-echo-border bg-echo-card px-3 py-2 text-white outline-none focus:border-neutral-500"
            />
          </div>
          {error && <p className="text-sm text-red-400">{error}</p>}
          <button
            type="submit"
            disabled={submitting}
            className="w-full rounded bg-echo-gold py-2.5 text-sm font-medium text-echo-bg hover:bg-echo-gold-dim disabled:opacity-60"
          >
            {submitting ? 'Logging in…' : 'Log In'}
          </button>
        </form>
        <p className="mt-6 text-sm text-neutral-500">
          No account?{' '}
          <Link to="/register" className="text-white hover:underline">
            Create Account
          </Link>
        </p>
      </div>
    </Layout>
  )
}

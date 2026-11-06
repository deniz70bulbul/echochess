import { Link } from 'react-router-dom'
import Layout from '../components/Layout'
import { useAuth } from '../auth/AuthContext'
import Logo from '../brand/Logo'

export default function Landing() {
  const { user } = useAuth()

  return (
    <Layout>
      <div className="mx-auto max-w-2xl px-4 py-24 text-center">
        <h1>
          <Logo className="text-4xl font-semibold tracking-tight text-white" />
        </h1>
        <p className="mt-4 text-neutral-400">
          Create an Echo from your chess games and play against it.
        </p>
        <div className="mt-10 flex justify-center gap-3">
          {user ? (
            <Link
              to="/dashboard"
              className="bg-echo-gold px-5 py-2.5 text-sm font-medium text-echo-bg hover:bg-echo-gold-dim"
            >
              Dashboard
            </Link>
          ) : (
            <>
              <Link
                to="/login"
                className="border border-echo-border px-5 py-2.5 text-sm text-white hover:bg-echo-card"
              >
                Log In
              </Link>
              <Link
                to="/register"
                className="bg-echo-gold px-5 py-2.5 text-sm font-medium text-echo-bg hover:bg-echo-gold-dim"
              >
                Create Account
              </Link>
            </>
          )}
        </div>
        <p className="mt-16 text-xs text-neutral-600">Private beta</p>
      </div>
    </Layout>
  )
}

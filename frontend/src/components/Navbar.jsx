import { Link, useLocation, useNavigate } from 'react-router-dom'
import { useAuth } from '../auth/AuthContext'
import Logo from '../brand/Logo'

export default function Navbar() {
  const location = useLocation()
  const navigate = useNavigate()
  const { user, logout } = useAuth()

  const authLinks = [
    { to: '/dashboard', label: 'Dashboard' },
    { to: '/create', label: 'Create Echo' },
    { to: user ? `/play/${user.username}` : '/dashboard', label: 'Play' },
    { to: user ? `/profile/${user.username}` : '/dashboard', label: 'Profile' },
  ]
  if (user?.role === 'admin') {
    authLinks.push({ to: '/admin', label: 'Admin' })
  }

  const handleLogout = async () => {
    await logout()
    navigate('/')
  }

  return (
    <nav className="border-b border-echo-border bg-echo-surface">
      <div className="mx-auto flex h-14 max-w-6xl items-center justify-between px-4">
        <Link to={user ? '/dashboard' : '/'}>
          <Logo />
        </Link>

        {user ? (
          <div className="flex items-center gap-1">
            {authLinks.map(({ to, label }) => (
              <Link
                key={label}
                to={to}
                className={`hidden rounded px-3 py-1.5 text-sm sm:inline ${
                  location.pathname === to
                    ? 'bg-echo-card text-white'
                    : 'text-neutral-400 hover:text-white'
                }`}
              >
                {label}
              </Link>
            ))}
            <span className="ml-2 hidden text-sm text-neutral-500 md:inline">
              {user.username}
            </span>
            <button
              type="button"
              onClick={handleLogout}
              className="ml-2 rounded px-3 py-1.5 text-sm text-neutral-300 hover:bg-echo-card hover:text-white"
            >
              Logout
            </button>
          </div>
        ) : (
          <div className="flex items-center gap-2">
            <Link
              to="/login"
              className="rounded px-3 py-1.5 text-sm text-neutral-300 hover:text-white"
            >
              Log In
            </Link>
            <Link
              to="/register"
              className="rounded bg-echo-gold px-3 py-1.5 text-sm font-medium text-echo-bg hover:bg-echo-gold-dim"
            >
              Create Account
            </Link>
          </div>
        )}
      </div>
    </nav>
  )
}

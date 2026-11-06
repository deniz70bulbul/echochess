import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import Layout from '../components/Layout'
import { api } from '../api/client'
import { useAuth } from '../auth/AuthContext'

export default function Dashboard() {
  const { user } = useAuth()
  const [profiles, setProfiles] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api.getProfiles()
      .then((data) => setProfiles(data.profiles || []))
      .finally(() => setLoading(false))
  }, [])

  return (
    <Layout>
      <div className="mx-auto max-w-3xl px-4 py-10">
        <div className="flex items-center justify-between">
          <h1 className="text-2xl font-semibold text-white">Dashboard</h1>
          <Link
            to="/create"
            className="bg-echo-gold px-4 py-2 text-sm font-medium text-echo-bg hover:bg-echo-gold-dim"
          >
            Create Echo
          </Link>
        </div>

        {loading ? (
          <p className="mt-12 text-sm text-neutral-500">Loading…</p>
        ) : profiles.length === 0 ? (
          <div className="mt-12 border border-echo-border bg-echo-card px-6 py-10 text-center">
            <p className="text-neutral-400">No Echo yet.</p>
            <Link to="/create" className="mt-3 inline-block text-sm text-white underline">
              Create Echo
            </Link>
          </div>
        ) : (
          <ul className="mt-8 divide-y divide-echo-border border border-echo-border bg-echo-card">
            {profiles.map(({ username, personality }) => (
              <li key={username} className="flex items-center justify-between gap-4 px-4 py-4">
                <div>
                  <p className="font-medium capitalize text-white">{username}</p>
                  {(personality?.personality || []).length > 0 && (
                    <p className="mt-1 text-sm text-neutral-500">
                      {personality.personality.join(', ')}
                    </p>
                  )}
                </div>
                <div className="flex gap-2">
                  <Link
                    to={`/profile/${username}`}
                    className="border border-echo-border px-3 py-1.5 text-sm text-neutral-300 hover:bg-echo-surface"
                  >
                    View Profile
                  </Link>
                  <Link
                    to={`/play/${username}`}
                    className="bg-echo-gold px-3 py-1.5 text-sm font-medium text-echo-bg hover:bg-echo-gold-dim"
                  >
                    Play
                  </Link>
                </div>
              </li>
            ))}
          </ul>
        )}

        {user && (
          <p className="mt-6 text-xs text-neutral-600">Signed in as {user.username}</p>
        )}
      </div>
    </Layout>
  )
}

import { useEffect, useState } from 'react'
import { Navigate } from 'react-router-dom'
import Layout from '../components/Layout'
import { useAuth } from '../auth/AuthContext'
import { api } from '../api/client'

export default function Admin() {
  const { user } = useAuth()
  const [users, setUsers] = useState([])
  const [invites, setInvites] = useState([])
  const [createdCode, setCreatedCode] = useState('')
  const [error, setError] = useState('')
  const [maxUses, setMaxUses] = useState(1)
  const [days, setDays] = useState(14)
  const [label, setLabel] = useState('')

  const load = async () => {
    const [u, i] = await Promise.all([api.adminUsers(), api.adminInvites()])
    if (u.error || i.error) {
      setError(u.error || i.error)
      return
    }
    setUsers(u.users || [])
    setInvites(i.invites || [])
  }

  useEffect(() => {
    load()
  }, [])

  if (user?.role !== 'admin') {
    return <Navigate to="/dashboard" replace />
  }

  return (
    <Layout>
      <div className="mx-auto max-w-4xl px-4 py-8">
        <h1 className="text-2xl font-semibold text-white">Admin</h1>
        {error && <p className="mt-3 text-sm text-red-400">{error}</p>}
        {createdCode && (
          <p className="mt-3 break-all border border-echo-border bg-echo-card px-3 py-2 text-sm text-white">
            New invite (shown once): {createdCode}
          </p>
        )}

        <form
          className="mt-6 flex flex-wrap items-end gap-2"
          onSubmit={async (e) => {
            e.preventDefault()
            setError('')
            const result = await api.adminCreateInvite({
              max_uses: Number(maxUses),
              days: Number(days),
              label,
            })
            if (result.error) {
              setError(result.error)
              return
            }
            setCreatedCode(result.code)
            setLabel('')
            load()
          }}
        >
          <label className="text-sm text-neutral-400">
            Label
            <input
              value={label}
              onChange={(e) => setLabel(e.target.value)}
              className="mt-1 block w-40 border border-echo-border bg-echo-card px-2 py-1.5 text-white"
            />
          </label>
          <label className="text-sm text-neutral-400">
            Max uses
            <input
              type="number"
              min="1"
              value={maxUses}
              onChange={(e) => setMaxUses(e.target.value)}
              className="mt-1 block w-24 border border-echo-border bg-echo-card px-2 py-1.5 text-white"
            />
          </label>
          <label className="text-sm text-neutral-400">
            Days
            <input
              type="number"
              min="1"
              value={days}
              onChange={(e) => setDays(e.target.value)}
              className="mt-1 block w-24 border border-echo-border bg-echo-card px-2 py-1.5 text-white"
            />
          </label>
          <button type="submit" className="bg-echo-gold px-3 py-2 text-sm text-echo-bg">
            Create invite
          </button>
        </form>

        <h2 className="mt-8 text-sm font-semibold uppercase text-neutral-500">Invites</h2>
        <ul className="mt-2 divide-y divide-echo-border border border-echo-border">
          {invites.map((invite) => (
            <li key={invite.id} className="flex items-center justify-between px-3 py-2 text-sm">
              <span className="text-neutral-300">
                {invite.label || invite.id} · {invite.used_count}/{invite.max_uses}
                {invite.revoked ? ' · revoked' : ''}
              </span>
              {!invite.revoked && (
                <button
                  type="button"
                  className="text-red-400"
                  onClick={async () => {
                    await api.adminRevokeInvite(invite.id)
                    load()
                  }}
                >
                  Revoke
                </button>
              )}
            </li>
          ))}
        </ul>

        <h2 className="mt-8 text-sm font-semibold uppercase text-neutral-500">Users</h2>
        <ul className="mt-2 divide-y divide-echo-border border border-echo-border">
          {users.map((row) => (
            <li key={row.username} className="flex items-center justify-between px-3 py-2 text-sm">
              <span className="text-neutral-300">
                {row.username} · {row.role}
                {row.banned ? ' · banned' : ''}
              </span>
              {row.role !== 'admin' && (
                <button
                  type="button"
                  className="text-neutral-300 underline"
                  onClick={async () => {
                    if (row.banned) {
                      await api.adminUnban(row.username)
                    } else {
                      await api.adminBan(row.username)
                    }
                    load()
                  }}
                >
                  {row.banned ? 'Unban' : 'Ban'}
                </button>
              )}
            </li>
          ))}
        </ul>
      </div>
    </Layout>
  )
}

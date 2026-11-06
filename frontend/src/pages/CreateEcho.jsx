import { useState, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import Layout from '../components/Layout'
import { api } from '../api/client'
import { useAuth } from '../auth/AuthContext'

export default function CreateEcho() {
  const { user } = useAuth()
  const navigate = useNavigate()
  const fileRef = useRef(null)

  const [files, setFiles] = useState([])
  const [phase, setPhase] = useState('form')
  const [error, setError] = useState('')
  const [result, setResult] = useState(null)

  const handleFiles = (e) => {
    setFiles(Array.from(e.target.files || []))
  }

  const runAnalysis = async () => {
    if (!user?.username) {
      setError('Please log in.')
      return
    }

    if (files.length === 0) {
      setError('Upload at least one PGN file.')
      return
    }

    setError('')
    setPhase('analyzing')

    try {
      const upload = await api.uploadPgns(user.username, files)
      if (upload.error) {
        setError(upload.error)
        setPhase('form')
        return
      }

      if (!upload.count) {
        setError('No PGN files were saved. Use .pgn files.')
        setPhase('form')
        return
      }

      const data = await api.createEcho('lichess')

      if (data.error) {
        setError(data.message || data.error)
        setPhase('form')
        return
      }

      setResult(data)
      setPhase('complete')
    } catch {
      setError('Could not create Echo. Please try again.')
      setPhase('form')
    }
  }

  return (
    <Layout>
      <div className="mx-auto max-w-lg px-4 py-10">
        <h1 className="text-2xl font-semibold text-white">Create Echo</h1>
        <p className="mt-2 text-sm text-neutral-400">
          Upload PGN files for {user?.username}. EchoChess will analyze those games.
        </p>

        {phase === 'form' && (
          <div className="mt-8 border border-echo-border bg-echo-card p-5">
            <label className="block text-sm text-neutral-400">Username</label>
            <input
              type="text"
              value={user?.username || ''}
              readOnly
              className="mt-1 w-full border border-echo-border bg-echo-bg px-3 py-2 text-neutral-300"
            />

            <label className="mt-5 block text-sm text-neutral-400">PGN files</label>
            <button
              type="button"
              onClick={() => fileRef.current?.click()}
              className="mt-1 w-full border border-dashed border-echo-border px-4 py-8 text-sm text-neutral-400 hover:border-neutral-500 hover:text-white"
            >
              {files.length > 0
                ? `${files.length} file(s) selected`
                : 'Choose .pgn files'}
            </button>
            <input
              ref={fileRef}
              type="file"
              accept=".pgn"
              multiple
              onChange={handleFiles}
              className="hidden"
            />

            {error && <p className="mt-4 text-sm text-red-400">{error}</p>}

            <button
              type="button"
              onClick={runAnalysis}
              className="mt-6 w-full bg-echo-gold py-2.5 text-sm font-medium text-echo-bg hover:bg-echo-gold-dim"
            >
              Create
            </button>
          </div>
        )}

        {phase === 'analyzing' && (
          <div className="mt-8 border border-echo-border bg-echo-card px-5 py-10 text-center">
            <p className="text-white">Analyzing games…</p>
            <p className="mt-2 text-sm text-neutral-500">
              This can take a while. The Echo is ready when this step finishes.
            </p>
          </div>
        )}

        {phase === 'complete' && result && (
          <div className="mt-8 border border-echo-border bg-echo-card px-5 py-8 text-center">
            <h2 className="text-xl font-semibold text-white">Echo created</h2>
            <p className="mt-2 text-sm text-neutral-400">{result.username}</p>

            {result.profile?.personality?.personality?.length > 0 && (
              <p className="mt-4 text-sm text-neutral-300">
                {result.profile.personality.personality.join(', ')}
              </p>
            )}

            <div className="mt-6 flex justify-center gap-3">
              <button
                type="button"
                onClick={() => navigate(`/profile/${result.username}`)}
                className="border border-echo-border px-4 py-2 text-sm text-white hover:bg-echo-surface"
              >
                View Profile
              </button>
              <button
                type="button"
                onClick={() => navigate(`/play/${result.username}`)}
                className="bg-echo-gold px-4 py-2 text-sm font-medium text-echo-bg hover:bg-echo-gold-dim"
              >
                Play
              </button>
            </div>
          </div>
        )}
      </div>
    </Layout>
  )
}

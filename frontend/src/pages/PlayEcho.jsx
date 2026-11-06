import { useCallback, useEffect, useRef, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { Chessboard } from 'react-chessboard'
import { Chess } from 'chess.js'
import { Loader2 } from 'lucide-react'
import Layout from '../components/Layout'
import StatCard from '../components/StatCard'
import { api } from '../api/client'

const PIECE_VALUES = { p: 1, n: 3, b: 3, r: 5, q: 9 }

function CapturedPieces({ pieces, color }) {
  const sorted = [...pieces].sort(
    (a, b) => (PIECE_VALUES[b.toLowerCase()] || 0) - (PIECE_VALUES[a.toLowerCase()] || 0)
  )

  return (
    <div className="flex flex-wrap gap-1">
      {sorted.map((p, i) => (
        <span
          key={i}
          className={`text-lg ${color === 'white' ? 'text-neutral-200' : 'text-neutral-500'}`}
        >
          {p}
        </span>
      ))}
    </div>
  )
}

export default function PlayEcho() {
  const { username } = useParams()
  const [game, setGame] = useState(null)
  const [chess] = useState(() => new Chess())
  const [fen, setFen] = useState('start')
  const [orientation, setOrientation] = useState('white')
  const [loading, setLoading] = useState(true)
  const [thinking, setThinking] = useState(false)
  const [error, setError] = useState('')
  const [sessionId, setSessionId] = useState(null)
  const [profile, setProfile] = useState(null)
  const [moveHistory, setMoveHistory] = useState([])
  const [captured, setCaptured] = useState({ white: [], black: [] })
  const [gameOver, setGameOver] = useState(null)
  const [playerColor, setPlayerColor] = useState('white')
  const startRequestRef = useRef(0)

  const syncFromServer = useCallback((state) => {
    if (state.error) {
      setError(state.error)
      return
    }

    chess.load(state.fen)
    setFen(state.fen)
    setMoveHistory(state.move_history || [])
    setCaptured(state.captured || { white: [], black: [] })

    if (state.is_game_over) {
      setGameOver(state.result)
    } else {
      setGameOver(null)
    }

    if (state.profile) {
      setProfile(state.profile)
    }
  }, [chess])

  const startGame = useCallback(async (color) => {
    const requestId = ++startRequestRef.current
    setLoading(true)
    setError('')
    setGameOver(null)

    try {
      const state = await api.newGame(username, color)
      if (requestId !== startRequestRef.current) {
        return
      }

      if (state.error) {
        setError(state.message || state.error)
        setGame(null)
        return
      }

      setSessionId(state.session_id)
      setPlayerColor(color)
      setOrientation(color)
      syncFromServer(state)
      setGame(state)
    } catch (err) {
      if (requestId === startRequestRef.current) {
        setError(err.message)
      }
    } finally {
      if (requestId === startRequestRef.current) {
        setLoading(false)
      }
    }
  }, [username, syncFromServer])

  useEffect(() => {
    startGame('white')
  }, [startGame])

  const onDrop = async (sourceSquare, targetSquare) => {
    if (thinking || gameOver || !sessionId) return false

    const turn = chess.turn()
    const expected = playerColor === 'white' ? 'w' : 'b'
    if (turn !== expected) return false

    const move = chess.move({ from: sourceSquare, to: targetSquare, promotion: 'q' })
    if (!move) return false

    setThinking(true)
    setFen(chess.fen())

    try {
      const state = await api.makeMove(sessionId, move.from + move.to + (move.promotion || ''))

      if (state.error) {
        chess.undo()
        setFen(chess.fen())
        setError(state.error)
        return false
      }

      syncFromServer(state)
    } catch (err) {
      chess.undo()
      setFen(chess.fen())
      setError(err.message)
      return false
    } finally {
      setThinking(false)
    }

    return true
  }

  const handleResign = async () => {
    if (!sessionId) return
    const result = await api.resign(sessionId)
    if (result.result) setGameOver(result.result)
  }

  const handleDraw = async () => {
    if (!sessionId) return
    const result = await api.offerDraw(sessionId)
    if (result.result) setGameOver(result.result)
  }

  const handleUndo = async () => {
    if (!sessionId || thinking) return
    setThinking(true)
    setError('')
    try {
      const state = await api.undo(sessionId)
      if (state.error) {
        setError(state.error)
        return
      }
      syncFromServer(state)
    } finally {
      setThinking(false)
    }
  }

  const handleNewGame = () => startGame(playerColor)

  if (loading && !game) {
    return (
      <Layout>
        <div className="flex min-h-[60vh] items-center justify-center text-sm text-neutral-400">
          Loading game…
        </div>
      </Layout>
    )
  }

  if (!loading && !game && !sessionId) {
    return (
      <Layout>
        <div className="mx-auto max-w-lg px-4 py-20 text-center">
          <p className="text-red-400">{error || 'Could not start game'}</p>
          <Link to="/create" className="mt-4 inline-block text-sm text-white underline">
            Create Echo
          </Link>
        </div>
      </Layout>
    )
  }

  const formattedMoves = []
  for (let i = 0; i < moveHistory.length; i += 2) {
    formattedMoves.push({
      num: Math.floor(i / 2) + 1,
      white: moveHistory[i]?.san,
      black: moveHistory[i + 1]?.san,
    })
  }

  return (
    <Layout>
      <div className="mx-auto max-w-7xl px-4 py-4 lg:px-6">
        {error && (
          <div className="mb-3 border border-red-900/60 bg-red-950/40 px-3 py-2 text-sm text-red-400">
            {error}
            {error.includes('profile not found') && (
              <Link to="/create" className="ml-2 underline">Create Echo</Link>
            )}
          </div>
        )}

        <div className="grid gap-4 lg:grid-cols-[220px_minmax(0,1fr)_240px]">
          <div className="order-2 border border-echo-border bg-echo-card p-3 lg:order-1">
            <h3 className="mb-2 text-xs font-semibold uppercase tracking-wide text-neutral-500">
              Game
            </h3>
            <p className="mb-3 text-sm capitalize text-white">{username}</p>

            <p className="mb-1 text-xs text-neutral-500">Captured by Echo</p>
            <CapturedPieces pieces={captured[playerColor] || []} color="white" />
            <p className="mb-1 mt-3 text-xs text-neutral-500">Captured by You</p>
            <CapturedPieces
              pieces={captured[playerColor === 'white' ? 'black' : 'white'] || []}
              color="black"
            />

            <h3 className="mb-2 mt-4 text-xs font-semibold uppercase tracking-wide text-neutral-500">
              Moves
            </h3>
            <div className="max-h-80 overflow-y-auto font-mono text-sm">
              <table className="w-full">
                <tbody>
                  {formattedMoves.map(({ num, white, black }) => (
                    <tr key={num} className="text-neutral-300">
                      <td className="w-8 py-0.5 text-neutral-500">{num}.</td>
                      <td className="py-0.5 pr-3">{white}</td>
                      <td className="py-0.5">{black}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          <div className="order-1 lg:order-2">
            <div className="mb-2 flex items-center justify-between">
              <p className="text-sm text-neutral-400">
                You play {playerColor}
              </p>
              {thinking && (
                <span className="flex items-center gap-2 text-sm text-neutral-300">
                  <Loader2 className="h-4 w-4 animate-spin" />
                  Echo is thinking…
                </span>
              )}
            </div>

            <div className="relative mx-auto max-w-[560px]">
              <Chessboard
                options={{
                  position: fen,
                  onPieceDrop: ({ sourceSquare, targetSquare }) =>
                    onDrop(sourceSquare, targetSquare),
                  boardOrientation: orientation,
                  allowDragging: !thinking && !gameOver,
                  darkSquareStyle: { backgroundColor: '#4a5568' },
                  lightSquareStyle: { backgroundColor: '#718096' },
                }}
              />
            </div>

            {gameOver && (
              <div className="mt-3 border border-echo-border bg-echo-card px-3 py-2 text-center text-sm text-white">
                {gameOver}
              </div>
            )}
          </div>

          <div className="order-3 border border-echo-border bg-echo-card p-3">
            <h3 className="mb-3 text-xs font-semibold uppercase tracking-wide text-neutral-500">
              Echo
            </h3>

            {profile ? (
              <>
                <p className="font-medium capitalize text-white">{username}</p>
                {(profile.personality?.personality || []).length > 0 && (
                  <p className="mt-1 text-sm text-neutral-400">
                    {profile.personality.personality.join(', ')}
                  </p>
                )}

                <div className="mt-3 space-y-2">
                  <StatCard
                    label="Clone accuracy"
                    value={profile.clone_accuracy}
                    unit="%"
                  />
                  <StatCard
                    label="Aggression"
                    value={profile.advanced_dna?.aggression ?? profile.dna?.aggression}
                  />
                  <StatCard
                    label="Opening loyalty"
                    value={profile.opening_loyalty?.loyalty_score}
                  />
                </div>

                <Link
                  to={`/profile/${username}`}
                  className="mt-3 block text-sm text-neutral-300 underline hover:text-white"
                >
                  View profile
                </Link>
              </>
            ) : (
              <p className="text-sm text-neutral-500">Loading profile…</p>
            )}

            <div className="mt-6 space-y-2">
              <button
                type="button"
                onClick={handleNewGame}
                className="w-full border border-echo-border px-3 py-2 text-sm text-white hover:bg-echo-surface"
              >
                New Game
              </button>
              <button
                type="button"
                onClick={handleUndo}
                disabled={thinking || !!gameOver}
                className="w-full border border-echo-border px-3 py-2 text-sm text-white hover:bg-echo-surface disabled:opacity-40"
              >
                Undo
              </button>
              <button
                type="button"
                onClick={handleDraw}
                disabled={!!gameOver}
                className="w-full border border-echo-border px-3 py-2 text-sm text-white hover:bg-echo-surface disabled:opacity-40"
              >
                Offer Draw
              </button>
              <button
                type="button"
                onClick={handleResign}
                disabled={!!gameOver}
                className="w-full border border-red-900/50 px-3 py-2 text-sm text-red-400 hover:bg-red-950/40 disabled:opacity-40"
              >
                Resign
              </button>
            </div>

            <div className="mt-3 flex gap-2">
              {['white', 'black'].map((color) => (
                <button
                  key={color}
                  type="button"
                  onClick={() => startGame(color)}
                  className={`flex-1 px-2 py-1.5 text-xs capitalize ${
                    playerColor === color
                      ? 'bg-echo-gold text-echo-bg'
                      : 'border border-echo-border text-neutral-400 hover:text-white'
                  }`}
                >
                  Play as {color}
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>
    </Layout>
  )
}

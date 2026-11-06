import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import Layout from '../components/Layout'
import PersonalityRadar from '../components/PersonalityRadar'
import { api } from '../api/client'

function hasValue(value) {
  return value !== undefined && value !== null && value !== ''
}

function Row({ label, value }) {
  if (!hasValue(value)) return null
  return (
    <div className="flex justify-between gap-4 py-1.5 text-sm">
      <span className="text-neutral-400">{label}</span>
      <span className="text-white">{value}</span>
    </div>
  )
}

function Section({ title, children }) {
  if (!children) return null
  return (
    <section className="border border-echo-border bg-echo-card p-5">
      <h2 className="mb-3 text-sm font-semibold uppercase tracking-wide text-neutral-500">
        {title}
      </h2>
      {children}
    </section>
  )
}

export default function EchoProfile() {
  const { username } = useParams()
  const [profile, setProfile] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    api.getProfile(username)
      .then((data) => {
        if (data.error) {
          setError(data.error)
        } else {
          setProfile(data)
        }
      })
      .catch(() => setError('Could not load profile.'))
      .finally(() => setLoading(false))
  }, [username])

  if (loading) {
    return (
      <Layout>
        <div className="flex min-h-[50vh] items-center justify-center text-sm text-neutral-400">
          Loading…
        </div>
      </Layout>
    )
  }

  if (error || !profile) {
    return (
      <Layout>
        <div className="mx-auto max-w-lg px-4 py-20 text-center">
          <p className="text-red-400">{error || 'Profile not found'}</p>
          <Link to="/create" className="mt-4 inline-block text-sm text-white underline">
            Create Echo
          </Link>
        </div>
      </Layout>
    )
  }

  const personality = profile.personality || {}
  const dna = profile.dna || {}
  const advanced = profile.advanced_dna || {}
  const loyalty = profile.opening_loyalty || {}
  const signature = profile.move_signature || {}
  const endgame = profile.endgame_personality || {}
  const sacrifice = profile.sacrifice_profile || {}
  const gambit = profile.gambit_preference || {}
  const tags = personality.personality || []

  const showEndgame =
    endgame &&
    endgame.endgame_style &&
    endgame.endgame_style !== 'unknown'
  const showSacrifice = sacrifice && (sacrifice.games > 0 || sacrifice.sacrifice_moves > 0)
  const showGambit = gambit && gambit.total_games > 0
  const showSignature = signature && signature.games > 0
  const openings = Array.isArray(profile.opening_dna) ? profile.opening_dna : []

  return (
    <Layout>
      <div className="mx-auto max-w-5xl px-4 py-8">
        <Link to="/dashboard" className="text-sm text-neutral-400 hover:text-white">
          Back to Dashboard
        </Link>

        <div className="mt-4 flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
          <div>
            <h1 className="text-2xl font-semibold capitalize text-white">{username}</h1>
            {tags.length > 0 && (
              <p className="mt-2 text-sm text-neutral-400">{tags.join(', ')}</p>
            )}
          </div>
          <Link
            to={`/play/${username}`}
            className="bg-echo-gold px-4 py-2 text-sm font-medium text-echo-bg hover:bg-echo-gold-dim"
          >
            Play
          </Link>
        </div>

        <div className="mt-8 grid gap-4 lg:grid-cols-2">
          <Section title="Personality">
            <PersonalityRadar profile={profile} />
          </Section>

          <div className="space-y-4">
            <Section title="DNA">
              <Row label="Aggression" value={dna.aggression} />
              <Row label="Risk" value={dna.risk} />
              <Row label="Opening loyalty" value={dna.opening_loyalty} />
            </Section>

            <Section title="Advanced DNA">
              <Row label="Aggression" value={advanced.aggression} />
              <Row label="Risk" value={advanced.risk} />
              <Row label="Tactical" value={advanced.tactical} />
              <Row label="Positional" value={advanced.positional} />
              <Row label="Development" value={advanced.development_style} />
              <Row label="Opening loyalty" value={advanced.opening_loyalty} />
            </Section>
          </div>
        </div>

        <div className="mt-4 grid gap-4 md:grid-cols-2">
          <Section title="Opening Loyalty">
            <Row label="Favorite opening" value={loyalty.favorite_opening} />
            <Row label="Loyalty score" value={loyalty.loyalty_score} />
          </Section>

          <Section title="Clone">
            <Row label="Clone accuracy" value={hasValue(profile.clone_accuracy) ? `${profile.clone_accuracy}%` : null} />
            <Row label="PGN games" value={profile.pgn_count} />
          </Section>
        </div>

        {openings.length > 0 && (
          <div className="mt-4">
            <Section title="Openings">
              <ul className="space-y-1 text-sm text-neutral-300">
                {openings.slice(0, 8).map((opening, i) => (
                  <li key={i}>
                    {typeof opening === 'string'
                      ? opening
                      : opening.opening || opening.name}
                    {typeof opening === 'object' && hasValue(opening.weight)
                      ? ` (${opening.weight}%)`
                      : ''}
                  </li>
                ))}
              </ul>
            </Section>
          </div>
        )}

        <div className="mt-4 grid gap-4 md:grid-cols-3">
          {showSignature && (
            <Section title="Move Signature">
              <Row label="Checks" value={signature.checks} />
              <Row label="Captures" value={signature.captures} />
              <Row label="Center pawn push" value={signature.center_pawn_push} />
              <Row label="Early queen" value={signature.early_queen} />
            </Section>
          )}

          {showEndgame && (
            <Section title="Endgame">
              <Row label="Style" value={endgame.endgame_style} />
              <Row label="Simplification" value={endgame.simplification} />
              <Row label="Fighting" value={endgame.fighting} />
            </Section>
          )}

          {showGambit && (
            <Section title="Gambit">
              <Row label="Gambit games" value={gambit.gambit_games} />
              <Row label="Total games" value={gambit.total_games} />
              <Row label="Gambit rate" value={gambit.gambit_rate} />
            </Section>
          )}

          {showSacrifice && (
            <Section title="Sacrifices">
              <Row label="Style" value={sacrifice.sacrifice_style} />
              <Row label="Sacrifice rate" value={sacrifice.sacrifice_rate} />
            </Section>
          )}
        </div>
      </div>
    </Layout>
  )
}

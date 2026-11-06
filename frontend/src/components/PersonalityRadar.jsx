import {
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  Radar,
  ResponsiveContainer,
} from 'recharts'

function point(trait, value) {
  if (value === undefined || value === null) return null
  return { trait, value }
}

export default function PersonalityRadar({ profile }) {
  const dna = profile?.advanced_dna || profile?.dna || {}
  const loyalty = profile?.opening_loyalty || {}
  const gambit = profile?.gambit_preference || {}

  const data = [
    point('Aggression', dna.aggression),
    point('Tactical', dna.tactical),
    point('Positional', dna.positional),
    point('Risk', dna.risk),
    point('Loyalty', loyalty.loyalty_score),
    point('Gambit', gambit.gambit_rate),
  ].filter(Boolean)

  if (data.length < 3) {
    return <p className="text-sm text-neutral-500">Not enough data to chart.</p>
  }

  return (
    <div className="h-64 w-full">
      <ResponsiveContainer width="100%" height="100%">
        <RadarChart data={data} cx="50%" cy="50%" outerRadius="70%">
          <PolarGrid stroke="#3d3b38" />
          <PolarAngleAxis
            dataKey="trait"
            tick={{ fill: '#a8a29e', fontSize: 12 }}
          />
          <Radar
            name="DNA"
            dataKey="value"
            stroke="#c9a227"
            fill="#c9a227"
            fillOpacity={0.2}
            strokeWidth={1.5}
          />
        </RadarChart>
      </ResponsiveContainer>
    </div>
  )
}

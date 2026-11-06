export default function StatCard({ label, value, unit = '' }) {
  if (value === undefined || value === null || value === '') {
    return null
  }

  return (
    <div className="border border-echo-border bg-echo-bg px-3 py-2">
      <p className="text-xs text-neutral-500">{label}</p>
      <p className="mt-0.5 text-lg text-white">
        {value}
        {unit}
      </p>
    </div>
  )
}

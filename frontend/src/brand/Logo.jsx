/**
 * Central EchoChess mark.
 *
 * Temporary: text wordmark only.
 * When a logo file is provided, import it below as `mark` and the
 * same component will feed the navbar and any other logo slots.
 * Also replace public/favicon.svg with that file (or a square crop).
 */
const mark = null

export default function Logo({ className = 'text-base font-semibold tracking-tight text-white' }) {
  if (mark) {
    return <img src={mark} alt="EchoChess" className={className} />
  }

  return <span className={className}>EchoChess</span>
}

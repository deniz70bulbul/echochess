import Navbar from './Navbar'

export default function Layout({ children, hideNav = false }) {
  return (
    <div className="min-h-screen">
      {!hideNav && <Navbar />}
      <main>{children}</main>
    </div>
  )
}

import { createContext, useContext, useEffect, useState } from 'react'
import { api } from '../api/client'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [ready, setReady] = useState(false)

  useEffect(() => {
    api.me()
      .then((data) => setUser(data.user || null))
      .catch(() => setUser(null))
      .finally(() => setReady(true))
  }, [])

  const login = async (username, password) => {
    const data = await api.login(username, password)
    if (data.error) {
      return data
    }
    setUser(data.user)
    return data
  }

  const register = async (username, password, confirmPassword, inviteCode) => {
    const data = await api.register(username, password, confirmPassword, inviteCode)
    if (data.error) {
      return data
    }
    setUser(data.user)
    return data
  }

  const logout = async () => {
    await api.logout()
    setUser(null)
  }

  return (
    <AuthContext.Provider value={{ user, ready, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  return useContext(AuthContext) || {
    user: null,
    ready: false,
    login: async () => ({ error: 'Not ready.' }),
    register: async () => ({ error: 'Not ready.' }),
    logout: async () => {},
  }
}

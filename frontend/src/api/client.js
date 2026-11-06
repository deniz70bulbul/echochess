const API_BASE = import.meta.env.VITE_API_URL ?? (import.meta.env.DEV ? '/api' : '')

async function request(path, options = {}) {
  const headers = { ...options.headers }
  const isForm = options.body instanceof FormData

  if (!isForm && !headers['Content-Type']) {
    headers['Content-Type'] = 'application/json'
  }

  const res = await fetch(`${API_BASE}${path}`, {
    credentials: 'include',
    ...options,
    headers,
  })

  const data = await res.json().catch(() => ({}))

  if (res.status === 401 && data.error) {
    return data
  }

  if (!res.ok && !data.error) {
    throw new Error('Something went wrong. Please try again.')
  }

  return data
}

export const api = {
  me: () => request('/auth/me'),

  login: (username, password) =>
    request('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ username, password }),
    }),

  register: (username, password, confirmPassword, inviteCode) =>
    request('/auth/register', {
      method: 'POST',
      body: JSON.stringify({
        username,
        password,
        confirm_password: confirmPassword,
        invite_code: inviteCode,
      }),
    }),

  logout: () => request('/auth/logout', { method: 'POST' }),

  getProfiles: () => request('/profiles'),

  getProfile: (username) => request(`/profile/${username}`),

  createEcho: (platform = 'lichess') =>
    request('/echo/create', {
      method: 'POST',
      body: JSON.stringify({ platform }),
    }),

  getAccuracy: (username) => request(`/echo/${username}/accuracy`),

  uploadPgns: async (username, files) => {
    const form = new FormData()
    for (const file of files) {
      form.append('files', file)
    }

    const res = await fetch(`${API_BASE}/pgn/upload/${username}`, {
      method: 'POST',
      credentials: 'include',
      body: form,
    })

    return res.json()
  },

  newGame: (username, playerColor = 'white') =>
    request('/game/new', {
      method: 'POST',
      body: JSON.stringify({ username, player_color: playerColor }),
    }),

  getGame: (sessionId) => request(`/game/${sessionId}`),

  makeMove: (sessionId, move) =>
    request(`/game/${sessionId}/move`, {
      method: 'POST',
      body: JSON.stringify({ move }),
    }),

  resign: (sessionId) =>
    request(`/game/${sessionId}/resign`, { method: 'POST' }),

  offerDraw: (sessionId) =>
    request(`/game/${sessionId}/draw`, { method: 'POST' }),

  undo: (sessionId) =>
    request(`/game/${sessionId}/undo`, { method: 'POST' }),

  adminUsers: () => request('/admin/users'),
  adminInvites: () => request('/admin/invites'),
  adminCreateInvite: (payload) =>
    request('/admin/invites', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),
  adminRevokeInvite: (id) =>
    request(`/admin/invites/${id}/revoke`, { method: 'POST' }),
  adminBan: (username) =>
    request('/admin/users/ban', {
      method: 'POST',
      body: JSON.stringify({ username }),
    }),
  adminUnban: (username) =>
    request('/admin/users/unban', {
      method: 'POST',
      body: JSON.stringify({ username }),
    }),
}

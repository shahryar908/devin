// API client with token handling and automatic refresh
const API_BASE = '' // Uses Vite proxy in development

export function getToken() {
  return localStorage.getItem('access_token')
}

export function getRefreshToken() {
  return localStorage.getItem('refresh_token')
}

export function setTokens(accessToken, refreshToken) {
  if (accessToken) localStorage.setItem('access_token', accessToken)
  if (refreshToken) localStorage.setItem('refresh_token', refreshToken)
}

export function clearTokens() {
  localStorage.removeItem('access_token')
  localStorage.removeItem('refresh_token')
}

export async function apiRequest(endpoint, options = {}) {
  const token = getToken()
  const headers = {
    ...options.headers,
  }

  if (token && !headers['Authorization']) {
    headers['Authorization'] = `Bearer ${token}`
  }

  let res = await fetch(`${API_BASE}${endpoint}`, {
    ...options,
    headers,
  })

  // Try token refresh if 401
  if (res.status === 401 && getRefreshToken() && !endpoint.includes('/auth/refresh')) {
    try {
      const refreshRes = await fetch(`${API_BASE}/auth/refresh`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ refresh_token: getRefreshToken() }),
      })
      if (refreshRes.ok) {
        const data = await refreshRes.json()
        setTokens(data.access_token, data.refresh_token)
        headers['Authorization'] = `Bearer ${data.access_token}`
        res = await fetch(`${API_BASE}${endpoint}`, {
          ...options,
          headers,
        })
      } else {
        clearTokens()
      }
    } catch {
      clearTokens()
    }
  }

  return res
}

export async function register(username, email, password) {
  const res = await fetch(`${API_BASE}/auth/register`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, email, password }),
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({}))
    throw new Error(err.detail || 'Registration failed')
  }
  const data = await res.json()
  setTokens(data.access_token, data.refresh_token)
  return data
}

export async function login(username, password) {
  const formData = new URLSearchParams()
  formData.append('username', username)
  formData.append('password', password)

  const res = await fetch(`${API_BASE}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: formData.toString(),
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({}))
    throw new Error(err.detail || 'Invalid username or password')
  }
  const data = await res.json()
  setTokens(data.access_token, data.refresh_token)
  return data
}

export async function getMe() {
  const res = await apiRequest('/auth/me')
  if (!res.ok) {
    throw new Error('Failed to load user profile')
  }
  return res.json()
}

export async function getRoom(code) {
  const res = await apiRequest(`/rooms/${code}`)
  if (!res.ok) {
    throw new Error('Room not found')
  }
  return res.json()
}

export async function getLeaderboard(limit = 50) {
  const res = await apiRequest(`/leaderboard?limit=${limit}`)
  if (!res.ok) {
    throw new Error('Failed to load leaderboard')
  }
  return res.json()
}

export async function getUserStats(userId) {
  const res = await apiRequest(`/users/${userId}/stats`)
  if (!res.ok) {
    throw new Error('Failed to load user statistics')
  }
  return res.json()
}

export async function getUserMatches(userId) {
  const res = await apiRequest(`/users/${userId}/matches`)
  if (!res.ok) {
    throw new Error('Failed to load user match history')
  }
  return res.json()
}

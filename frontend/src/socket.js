import { io } from 'socket.io-client'
import { getToken } from './api'

let socket = null

export function getSocket() {
  if (!socket) {
    const token = getToken()
    socket = io('/', {
      autoConnect: false,
      auth: { token },
      transports: ['websocket', 'polling'],
    })
  }
  return socket
}

export function connectSocket() {
  const s = getSocket()
  const token = getToken()
  if (s && token) {
    s.auth = { token }
    if (!s.connected) {
      s.connect()
    }
  }
  return s
}

export function disconnectSocket() {
  if (socket) {
    socket.disconnect()
    socket = null
  }
}

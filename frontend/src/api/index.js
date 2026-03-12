import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 60000,
  headers: { 'Content-Type': 'application/json' },
})

export async function parseMessage(message, history = []) {
  const { data } = await api.post('/parse', { message, history })
  return data
}

export async function executeWithPassword(sessionId, password) {
  const { data } = await api.post('/execute', { session_id: sessionId, password })
  return data
}

export default api

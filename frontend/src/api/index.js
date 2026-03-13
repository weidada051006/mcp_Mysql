import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 90000, // LLM 可能较慢，90 秒
  headers: { 'Content-Type': 'application/json' },
})

/** 健康检查：先走代理 /api/health，失败则直连 8000（兼容代理未生效的情况） */
export async function checkHealth() {
  const opts = { timeout: 5000 }
  try {
    const { data } = await axios.get('/api/health', opts)
    return data
  } catch (e) {
    try {
      const { data } = await axios.get('http://127.0.0.1:8000/api/health', opts)
      return data
    } catch (_) {
      throw e
    }
  }
}

export async function parseMessage(message, history = []) {
  const { data } = await api.post('/parse', { message, history })
  return data
}

export async function executeWithPassword(sessionId, password) {
  const { data } = await api.post('/execute', { session_id: sessionId, password })
  return data
}

export default api

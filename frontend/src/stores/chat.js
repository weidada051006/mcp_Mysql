import { defineStore } from 'pinia'
import { parseMessage, executeWithPassword } from '../api'

const STORAGE_KEY = 'nlp2mysql_sessions'

function loadSessions() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    if (!raw) return []
    const list = JSON.parse(raw)
    return Array.isArray(list) ? list : []
  } catch {
    return []
  }
}

function saveSessions(sessions) {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(sessions))
  } catch (_) {}
}

export const useChatStore = defineStore('chat', {
  state: () => ({
    // 历史会话列表 { id, title, messages, createdAt }
    sessions: loadSessions(),
    // 当前会话 id，null 表示“新对话”
    currentSessionId: null,
    messages: [],
    loading: false,
    error: null,
    passwordModal: {
      visible: false,
      sessionId: null,
      operation: null,
      arguments: null,
      error: null,
    },
    conversationHistory: [],
  }),

  getters: {
    currentSession(state) {
      if (!state.currentSessionId) return null
      return state.sessions.find((s) => s.id === state.currentSessionId)
    },
    sortedSessions(state) {
      return [...state.sessions].sort((a, b) => (b.createdAt || 0) - (a.createdAt || 0))
    },
  },

  actions: {
    _persist() {
      saveSessions(this.sessions)
    },

    addUserMessage(content) {
      this.messages.push({
        id: crypto.randomUUID(),
        role: 'user',
        content,
        timestamp: Date.now(),
      })
      this.conversationHistory.push({ role: 'user', content })
    },

    addAssistantMessage(content) {
      this.messages.push({
        id: crypto.randomUUID(),
        role: 'assistant',
        content,
        timestamp: Date.now(),
      })
      this.conversationHistory.push({ role: 'assistant', content })
    },

    setLoading(v) {
      this.loading = v
    },
    setError(e) {
      this.error = e
    },

    openPasswordModal(sessionId, operation, args) {
      this.passwordModal.visible = true
      this.passwordModal.sessionId = sessionId
      this.passwordModal.operation = operation
      this.passwordModal.arguments = args
      this.passwordModal.error = null
    },

    closePasswordModal() {
      this.passwordModal.visible = false
      this.passwordModal.sessionId = null
      this.passwordModal.operation = null
      this.passwordModal.arguments = null
      this.passwordModal.error = null
    },

    setPasswordError(msg) {
      this.passwordModal.error = msg
    },

    /** 切换到“新对话”：清空当前展示的消息，不选任何历史会话 */
    startNewSession() {
      this.currentSessionId = null
      this.messages = []
      this.conversationHistory = []
    },

    /** 选中某条历史会话：加载其 messages 并设为当前会话 */
    selectSession(sessionId) {
      const session = this.sessions.find((s) => s.id === sessionId)
      if (!session) return
      this.currentSessionId = sessionId
      this.messages = session.messages || []
      this.conversationHistory = (session.messages || []).map((m) => ({
        role: m.role,
        content: m.content,
      }))
    },

    /** 删除某条历史会话；若删除的是当前会话则切换到新对话 */
    deleteSession(sessionId) {
      this.sessions = this.sessions.filter((s) => s.id !== sessionId)
      this._persist()
      if (this.currentSessionId === sessionId) {
        this.startNewSession()
      }
    },

    /** 发送后把本轮 user + assistant 消息写入当前会话（或新建会话） */
    _saveToCurrentSession() {
      const lastUser = this.messages.filter((m) => m.role === 'user').pop()
      const lastAssistant = this.messages.filter((m) => m.role === 'assistant').pop()
      if (!lastUser || !lastAssistant) return
      const title = lastUser.content.slice(0, 20) + (lastUser.content.length > 20 ? '…' : '')
      if (this.currentSessionId) {
        const session = this.sessions.find((s) => s.id === this.currentSessionId)
        if (session) {
          session.messages = [...this.messages]
          session.updatedAt = Date.now()
          if (!session.title || session.title === '新会话') session.title = title
          this._persist()
        }
      } else {
        const id = crypto.randomUUID()
        this.sessions.unshift({
          id,
          title,
          messages: [...this.messages],
          createdAt: Date.now(),
          updatedAt: Date.now(),
        })
        this.currentSessionId = id
        this._persist()
      }
    },

    async sendMessage(content) {
      if (!content?.trim()) return
      this.addUserMessage(content.trim())
      this.setLoading(true)
      this.setError(null)
      try {
        const res = await parseMessage(content.trim(), this.conversationHistory.slice(0, -1))
        if (res.status === 'direct_result') {
          this.addAssistantMessage(res.result)
          this._saveToCurrentSession()
        } else if (res.status === 'need_password') {
          this.openPasswordModal(res.session_id, res.operation, res.arguments)
        } else {
          this.addAssistantMessage(res.message || '请求失败，请重试。')
          this._saveToCurrentSession()
        }
      } catch (err) {
        const msg = err.response?.data?.message || err.message || '网络错误'
        this.addAssistantMessage(`错误：${msg}`)
        this.setError(msg)
        this._saveToCurrentSession()
      } finally {
        this.setLoading(false)
      }
    },

    async submitPassword(password) {
      const { sessionId } = this.passwordModal
      if (!sessionId || !password?.trim()) {
        this.setPasswordError('请输入密码')
        return
      }
      this.setPasswordError(null)
      try {
        const res = await executeWithPassword(sessionId, password.trim())
        if (res.status === 'success') {
          this.addAssistantMessage(res.result)
          this._saveToCurrentSession()
          this.closePasswordModal()
        } else {
          this.setPasswordError(res.message || '密码错误')
        }
      } catch (err) {
        this.setPasswordError(err.response?.data?.message || err.message || '请求失败')
      }
    },

    cancelPassword() {
      this.addAssistantMessage('操作已取消。')
      this._saveToCurrentSession()
      this.closePasswordModal()
    },
  },
})

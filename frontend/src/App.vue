<template>
  <div class="flex h-screen max-h-screen bg-[#f5f5f7]">
    <!-- 左侧历史会话 -->
    <SessionSidebar
      :sessions="chat.sortedSessions"
      :current-session-id="chat.currentSessionId"
      @new-session="chat.startNewSession()"
      @select="chat.selectSession($event)"
      @delete="chat.deleteSession($event)"
    />

    <!-- 右侧：顶栏 + 对话 + 输入 -->
    <div class="flex-1 flex flex-col min-w-0">
      <header class="flex-shrink-0 flex items-center justify-between h-14 px-6 bg-white/90 backdrop-blur border-b border-gray-100">
        <h1 class="text-lg font-semibold text-[#1d1d1f]">
          NL2SQL · 自然语言数据库问答
        </h1>
      </header>

      <main ref="messagesEndRef" class="flex-1 overflow-y-auto px-4 py-6 space-y-4">
        <div v-if="chat.messages.length === 0" class="flex flex-col items-center justify-center h-full text-center text-[#86868b]">
          <p class="text-sm">输入自然语言指令与数据库交互</p>
          <p class="text-xs mt-2">例如：查询所有商品、添加商品、删除草莓、价格在 2～8 元的商品有几个？</p>
        </div>
        <template v-else>
          <ChatMessage
            v-for="msg in chat.messages"
            :key="msg.id"
            :message="msg"
          />
        </template>
        <div v-if="chat.loading" class="flex justify-start">
          <div class="flex gap-1.5 px-4 py-3 rounded-2xl bg-white border border-gray-100 shadow-soft">
            <span class="w-2 h-2 rounded-full bg-[#0071e3] animate-bounce" style="animation-delay: 0ms" />
            <span class="w-2 h-2 rounded-full bg-[#0071e3] animate-bounce" style="animation-delay: 150ms" />
            <span class="w-2 h-2 rounded-full bg-[#0071e3] animate-bounce" style="animation-delay: 300ms" />
          </div>
        </div>
      </main>

      <ChatInput
        :disabled="chat.loading"
        @send="chat.sendMessage"
      />
    </div>

    <PasswordModal
      :visible="chat.passwordModal.visible"
      :error="chat.passwordModal.error"
      @confirm="chat.submitPassword"
      @cancel="chat.cancelPassword"
    />
  </div>
</template>

<script setup>
import { ref, watch, nextTick, onMounted } from 'vue'
import { useChatStore } from './stores/chat'
import ChatMessage from './components/ChatMessage.vue'
import ChatInput from './components/ChatInput.vue'
import PasswordModal from './components/PasswordModal.vue'
import SessionSidebar from './components/SessionSidebar.vue'

const chat = useChatStore()
const messagesEndRef = ref(null)

onMounted(() => {
  chat.startNewSession()
})

watch(
  () => chat.messages.length,
  () => {
    nextTick(() => {
      messagesEndRef.value?.scrollTo({ top: messagesEndRef.value.scrollHeight, behavior: 'smooth' })
    })
  }
)
</script>

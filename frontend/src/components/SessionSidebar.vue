<template>
  <aside class="w-56 flex-shrink-0 flex flex-col bg-white border-r border-gray-100">
    <div class="p-3 border-b border-gray-100">
      <button
        type="button"
        class="w-full flex items-center gap-2 px-3 py-2 rounded-xl text-sm font-medium text-[#1d1d1f] hover:bg-gray-100 transition-colors"
        @click="$emit('new-session')"
      >
        <PlusIcon class="w-4 h-4" />
        新会话
      </button>
    </div>
    <div class="flex-1 overflow-y-auto py-2">
      <p v-if="sessions.length === 0" class="px-3 py-2 text-xs text-[#a1a1a6]">暂无历史会话</p>
      <div
        v-for="s in sessions"
        :key="s.id"
        :class="[
          'group flex items-center gap-1 mx-2 rounded-xl text-sm transition-colors',
          isActive(s.id) ? 'bg-[#0071e3]/10' : 'hover:bg-gray-100',
        ]"
      >
        <button
          type="button"
          :class="[
            'flex-1 min-w-0 text-left px-3 py-2.5 truncate',
            isActive(s.id) ? 'text-[#0071e3]' : 'text-[#1d1d1f]',
          ]"
          :title="s.title"
          @click="$emit('select', s.id)"
        >
          {{ s.title || '未命名' }}
        </button>
        <button
          type="button"
          class="flex-shrink-0 p-1.5 rounded-lg text-[#86868b] hover:text-red-500 hover:bg-red-50 opacity-0 group-hover:opacity-100 transition-opacity"
          title="删除会话"
          @click.stop="$emit('delete', s.id)"
        >
          <TrashIcon class="w-4 h-4" />
        </button>
      </div>
    </div>
  </aside>
</template>

<script setup>
import { PlusIcon, TrashIcon } from '@heroicons/vue/24/outline'

const props = defineProps({
  sessions: { type: Array, default: () => [] },
  currentSessionId: { type: String, default: null },
})

defineEmits(['new-session', 'select', 'delete'])

function isActive(id) {
  return id === props.currentSessionId
}
</script>

<template>
  <div class="flex items-end gap-3 p-4 bg-white/80 backdrop-blur border-t border-gray-100">
    <div class="flex-1 relative">
      <!-- 提示语：未聚焦且无内容时显示，强制黑色 -->
      <div
        v-show="!focused && !text.trim()"
        class="input-placeholder-hint absolute inset-0 flex items-center pointer-events-none px-4 py-3 rounded-2xl text-[15px]"
        aria-hidden="true"
      >
        输入自然语言指令，如：查询所有商品、添加商品草莓 6元 188库存…
      </div>
      <textarea
        ref="inputRef"
        v-model="text"
        class="w-full min-h-[48px] max-h-32 px-4 py-3 rounded-2xl border border-gray-200 bg-gray-50/80 focus:outline-none focus:ring-2 focus:ring-[#0071e3]/30 focus:border-[#0071e3] resize-none transition-all relative z-10"
        style="color: #000000"
        rows="1"
        :disabled="disabled"
        @focus="handleFocus"
        @blur="handleBlur"
        @keydown.enter.exact.prevent="onSubmit"
        @keydown.ctrl.enter="handleMultilineEnter"
        @keydown.meta.enter="handleMultilineEnter"
        @input="autoResize"
      />
    </div>
    <button
      type="button"
      :disabled="disabled || !text.trim()"
      class="flex-shrink-0 w-12 h-12 rounded-full bg-gradient-to-br from-[#0071e3] to-[#42a5f5] text-white shadow-soft hover:shadow-soft-lg hover:scale-105 active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100 flex items-center justify-center transition-all"
      @click="onSubmit"
    >
      <PaperAirplaneIcon class="w-5 h-5" />
    </button>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import { PaperAirplaneIcon } from '@heroicons/vue/24/solid'

const emit = defineEmits(['send'])
const props = defineProps({
  disabled: { type: Boolean, default: false },
})

const text = ref('')
const focused = ref(false)
const inputRef = ref(null)

const handleFocus = () => {
  focused.value = true
}

const handleBlur = () => {
  focused.value = false
}

const handleMultilineEnter = () => {
  text.value += '\n'
  nextTick(() => {
    inputRef.value?.focus()
  })
}

const autoResize = () => {
  if (!inputRef.value) return
  inputRef.value.style.height = 'auto'
  const maxHeight = 112
  const scrollHeight = inputRef.value.scrollHeight
  inputRef.value.style.height = `${Math.min(scrollHeight, maxHeight)}px`
}

const onSubmit = () => {
  const t = text.value.trim()
  if (!t || props.disabled) return
  emit('send', t)
  text.value = ''
  autoResize()
}

onMounted(() => {
  inputRef.value?.focus()
  autoResize()
})
</script>

<style scoped>
.input-placeholder-hint {
  color: #000000 !important;
}
.shadow-soft {
  box-shadow: 0 2px 8px rgba(0, 113, 227, 0.15);
}
.shadow-soft-lg {
  box-shadow: 0 4px 12px rgba(0, 113, 227, 0.2);
}
</style>
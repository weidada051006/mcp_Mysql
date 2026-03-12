<template>
  <Transition name="modal">
    <div
      v-if="visible"
      class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/40 backdrop-blur-sm"
      @click.self="onCancel"
    >
      <div
        class="w-full max-w-md rounded-2xl bg-white shadow-soft-lg p-6 transform transition-all"
        role="dialog"
        aria-modal="true"
        aria-labelledby="modal-title"
      >
        <div class="flex items-center gap-3 mb-4">
          <div class="flex items-center justify-center w-10 h-10 rounded-full bg-[#0071e3]/10">
            <LockClosedIcon class="w-5 h-5 text-[#0071e3]" />
          </div>
          <h2 id="modal-title" class="text-lg font-semibold text-[#1d1d1f]">
            需要验证数据库密码
          </h2>
        </div>
        <p class="text-sm text-[#86868b] mb-4">
          当前操作需要输入数据库密码以继续执行。
        </p>
        <input
          v-model="password"
          type="password"
          placeholder="请输入数据库密码"
          class="w-full px-4 py-3 rounded-xl border border-gray-200 bg-gray-50 text-[#1d1d1f] placeholder:text-[#86868b] focus:outline-none focus:ring-2 focus:ring-[#0071e3]/30 focus:border-[#0071e3]"
          autofocus
          @keydown.enter.prevent="onConfirm"
        />
        <p v-if="error" class="mt-2 text-sm text-red-500">{{ error }}</p>
        <div class="flex gap-3 mt-6">
          <button
            type="button"
            class="flex-1 py-2.5 rounded-xl border border-gray-200 text-[#1d1d1f] hover:bg-gray-50 transition-colors"
            @click="onCancel"
          >
            取消
          </button>
          <button
            type="button"
            class="flex-1 py-2.5 rounded-xl bg-gradient-to-r from-[#0071e3] to-[#42a5f5] text-white hover:opacity-95 active:scale-[0.98] transition-all"
            @click="onConfirm"
          >
            确认
          </button>
        </div>
      </div>
    </div>
  </Transition>
</template>

<script setup>
import { ref, watch } from 'vue'
import { LockClosedIcon } from '@heroicons/vue/24/solid'

const props = defineProps({
  visible: Boolean,
  error: { type: String, default: null },
})

const emit = defineEmits(['confirm', 'cancel'])

const password = ref('')

watch(
  () => props.visible,
  (v) => {
    if (v) password.value = ''
  }
)

function onConfirm() {
  emit('confirm', password.value)
}

function onCancel() {
  emit('cancel')
}
</script>

<style scoped>
.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.2s ease;
}
.modal-enter-active .rounded-2xl,
.modal-leave-active .rounded-2xl {
  transition: transform 0.2s ease;
}
.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}
.modal-enter-from .rounded-2xl,
.modal-leave-to .rounded-2xl {
  transform: scale(0.96);
}
</style>

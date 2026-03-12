<template>
  <Transition name="message">
    <div
      :class="[
        'flex w-full',
        message.role === 'user' ? 'justify-end' : 'justify-start',
      ]"
    >
      <div
        :class="[
          'max-w-[85%] rounded-2xl px-4 py-3 shadow-soft',
          message.role === 'user'
            ? 'bg-gradient-to-br from-[#0071e3] to-[#42a5f5] text-white'
            : 'bg-white text-[#1d1d1f] border border-gray-100',
        ]"
      >
        <p class="text-sm whitespace-pre-wrap break-words">{{ message.content }}</p>
      </div>
    </div>
  </Transition>
</template>

<script setup>
defineProps({
  message: {
    type: Object,
    required: true,
  },
})
</script>

<style scoped>
.message-enter-active,
.message-leave-active {
  transition: opacity 0.2s ease, transform 0.2s ease;
}
.message-enter-from,
.message-leave-to {
  opacity: 0;
  transform: translateY(8px);
}
</style>

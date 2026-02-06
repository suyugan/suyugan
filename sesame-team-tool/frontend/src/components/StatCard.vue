<template>
  <div class="stat-card">
    <span class="text-[28px] font-bold text-black">{{ formattedValue }}</span>
    <span class="text-[14px] text-textGray mt-1">{{ label }}</span>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  value: {
    type: Number,
    required: true
  },
  label: {
    type: String,
    required: true
  }
})

const formattedValue = computed(() => {
  return props.value.toLocaleString()
})
</script>

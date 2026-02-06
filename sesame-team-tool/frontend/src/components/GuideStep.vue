<template>
  <div class="step-item">
    <div class="step-num">{{ num }}</div>
    <p class="text-[15px] text-black leading-relaxed">{{ stepText }}</p>
  </div>
</template>

<script setup>
defineProps({
  num: {
    type: Number,
    required: true
  },
  text: {
    type: String,
    required: true
  }
})

const stepText = computed(() => props.text)
</script>

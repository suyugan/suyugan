<template>
  <div class="px-4 mt-5">
    <div class="bg-white rounded-lg overflow-hidden shadow-sm relative">
      <div class="absolute top-2 left-2 bg-black/70 text-white text-[12px] px-1.5 rounded">广告</div>
      <div class="flex items-center p-3">
        <div class="flex-1">
          <p class="text-[15px] font-semibold text-black">{{ title }}</p>
          <p class="text-[12px] text-textGray mt-1">{{ subtitle }}</p>
        </div>
        <div class="bg-orange-100 rounded flex items-center justify-center overflow-hidden ml-2" :style="{ width: width + 'px', height: height + 'px' }">
          <img :src="imageUrl" class="w-full h-full object-cover" />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  title: {
    type: String,
    required: true
  },
  subtitle: {
    type: String,
    required: true
  },
  imageUrl: {
    type: String,
    required: true
  },
  width: {
    type: Number,
    default: 100
  },
  height: {
    type: Number,
    default: 70
  }
})
</script>

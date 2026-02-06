<template>
  <div class="body">
    <!-- 顶部状态栏 -->
    <StatusBar />

    <!-- 标题栏 -->
    <div class="flex items-center justify-between px-4 py-3">
      <h1 class="nav-title">匹配池</h1>
    </div>

    <!-- 匹配状态 -->
    <div class="px-4 mt-6">
      <div class="bg-white rounded-lg shadow-sm p-6">
        <div v-if="isWaiting">
          <p class="text-center text-[15px] text-black mb-4">等待匹配中...</p>
          <div class="flex justify-center">
            <i class="fa-solid fa-spinner fa-spin text-[40px] text-primary"></i>
          </div>
        </div>

        <div v-if="isMatched">
          <p class="text-center text-[15px] text-black mb-4">匹配成功！</p>
          <div class="space-y-3">
            <div v-for="member in currentMatch.members" :key="member.id" class="flex items-center gap-3 p-3 bg-gray-50 rounded-lg">
              <img :src="member.avatar" class="w-[50px] h-[50px] rounded-full object-cover">
              <div class="flex-1">
                <p class="text-[15px] font-semibold text-black">{{ member.username }}</p>
                <p class="text-[12px] text-textGray">分数: {{ member.score }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 底部导航栏 -->
    <TabBar activeTab="match" />
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useMatchStore } from '@/stores/match'
import StatusBar from '@/components/StatusBar.vue'
import TabBar from '@/components/TabBar.vue'

const matchStore = useMatchStore()
const isWaiting = ref(false)
const isMatched = ref(false)
const pollInterval = ref(null)

onMounted(() => {
  if (matchStore.isWaiting) {
    isWaiting.value = true
    // 轮询匹配状态
    pollInterval.value = setInterval(async () => {
      const status = await matchStore.checkMatchStatus()
      if (status && status.status === 'completed') {
        isWaiting.value = false
        isMatched.value = true
        clearInterval(pollInterval.value)
      }
    }, 5000)
  } else if (matchStore.isInMatch) {
    isMatched.value = true
  }
})

onUnmounted(() => {
  if (pollInterval.value) {
    clearInterval(pollInterval.value)
  }
})
</script>

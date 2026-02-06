<template>
  <div class="body">
    <!-- 顶部状态栏 -->
    <StatusBar />

    <!-- 标题栏 -->
    <div class="flex items-center justify-between px-4 py-3">
      <h1 class="nav-title">找分数</h1>
    </div>

    <!-- 输入口令区域 -->
    <div class="px-4 mt-6">
      <p class="text-[14px] text-black mb-2">输入口令</p>
      <input
        v-model="tokenInput"
        type="text"
        placeholder="请粘贴完整的支付宝口令（包含分数和乱码）"
        class="input-box"
        @input="parseToken"
      />

      <!-- 解析结果 -->
      <div v-if="parsedData" class="bg-white rounded-lg shadow-sm p-4 mt-4">
        <p class="text-[15px] font-semibold text-black mb-2">解析结果</p>
        <div class="space-y-2">
          <p class="text-[14px] text-black">分数: <span class="font-bold">{{ parsedData.score }}</span></p>
          <p class="text-[14px] text-black">用户: <span class="font-bold">{{ parsedData.username }}</span></p>
        </div>
      </div>
    </div>

    <!-- 底部导航栏 -->
    <TabBar activeTab="find" />
  </div>
</template>

<script setup>
import { ref } from 'vue'
import StatusBar from '@/components/StatusBar.vue'
import TabBar from '@/components/TabBar.vue'
import api from '@/api'

const tokenInput = ref('')
const parsedData = ref(null)

// 模拟解析口令
const parseToken = async () => {
  if (!tokenInput.value) return

  try {
    const response = await api.post('/token/parse', {
      token: tokenInput.value
    })

    if (response.data.success) {
      parsedData.value = response.data.data
    }
  } catch (error) {
    console.error('解析口令失败:', error)
  }
}
</script>

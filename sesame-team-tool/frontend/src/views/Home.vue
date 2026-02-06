<template>
  <div class="body">
    <!-- 顶部状态栏 -->
    <StatusBar />

    <!-- 标题栏 -->
    <div class="flex items-center justify-between px-4 py-3">
      <h1 class="nav-title">芝麻组队工具</h1>
      <div class="flex items-center gap-3">
        <i class="fa-solid fa-ellipsis text-black text-lg"></i>
        <div class="w-7 h-7 rounded-full bg-gray-200 flex items-center justify-center">
          <i class="fa-solid fa-circle text-textGray text-xs"></i>
        </div>
      </div>
    </div>

    <!-- 数据统计卡片 -->
    <div class="grid grid-cols-2 gap-4 px-4 mt-2">
      <StatCard :value="stats.totalTeams" label="成功组队" />
      <StatCard :value="stats.totalTokens" label="参与口令" />
    </div>

    <!-- 输入口令区域 -->
    <div class="px-4 mt-6">
      <p class="text-[14px] text-black mb-2">{{ t.inputLabel }}</p>
      <input
        v-model="tokenInput"
        type="text"
        :placeholder="t.inputPlaceholder"
        class="input-box"
      />
    </div>

    <!-- 广告位1 -->
    <AdBanner
      :title="ad1.title"
      :subtitle="ad1.subtitle"
      :imageUrl="ad1.imageUrl"
      :width="120"
      :height="80"
    />

    <!-- 广告位2 -->
    <AdBanner
      :title="ad2.title"
      :subtitle="ad2.subtitle"
      :imageUrl="ad2.imageUrl"
      :width="100"
      :height="70"
    />

    <!-- 功能按钮区 -->
    <div class="px-4 mt-6 space-y-3">
      <button class="btn-disabled">{{ t.btnMatch }}</button>
      <button class="btn-blue">{{ t.btnInvite }}</button>
      <button class="btn-green">{{ t.btnGroup }}</button>
    </div>

    <!-- 使用指南 -->
    <div class="px-4 mt-8">
      <p class="text-[14px] text-textGray mb-4">{{ t.guideTitle }}</p>
      <div class="space-y-3">
        <GuideStep :num="1" :text="t.step1" />
        <GuideStep :num="2" :text="t.step2" />
        <GuideStep :num="3" :text="t.step3" />
        <GuideStep :num="4" :text="t.step4" />
      </div>
    </div>

    <!-- 底部导航栏 -->
    <TabBar activeTab="home" />
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import StatusBar from '@/components/StatusBar.vue'
import StatCard from '@/components/StatCard.vue'
import AdBanner from '@/components/AdBanner.vue'
import TabBar from '@/components/TabBar.vue'
import GuideStep from '@/components/GuideStep.vue'
import api from '@/api'

// 翻译文本
const t = computed(() => ({
  inputLabel: '输入口令',
  inputPlaceholder: '请粘贴完整的支付宝口令（包含分数和乱码）',
  btnMatch: '加入匹配池',
  btnInvite: '邀请好友一起来玩',
  btnGroup: '进群互助：解决春节各类APP分享任务',
  guideTitle: '使用指南',
  step1: '打开支付宝，进入"芝麻信用"页面',
  step2: '点击去凑分页面的"分享吱口令"',
  step3: '粘贴到上方输入框，点击"加入匹配池"',
  step4: '等待系统自动凑齐三人 (总分2026)'
}))

// 状态
const tokenInput = ref('')
const stats = ref({
  totalTeams: 1057,
  totalTokens: 1480
})

const ad1 = ref({
  title: 'HR赫莲娜京东自营旗舰店',
  subtitle: '黑白绷带王牌套组，日护夜修精准抗老，新年',
  imageUrl: 'https://via.placeholder.com/120x80/CC0033/FFFFFF?text=HR赫莲娜',
  width: 120,
  height: 80
})

const ad2 = ref({
  title: '今日推荐,去哪儿旅行精',
  subtitle: '去哪儿旅行-订酒店机票...',
  imageUrl: 'https://via.placeholder.com/100x70/FF7A2F/FFFFFF?text=去哪儿',
  width: 100,
  height: 70
})

// 获取统计数据
const fetchStats = async () => {
  try {
    const response = await api.get('/stats')
    if (response.data.success) {
      stats.value = response.data.data
    }
  } catch (error) {
    console.error('获取统计数据失败:', error)
  }
}

onMounted(() => {
  fetchStats()
})
</script>

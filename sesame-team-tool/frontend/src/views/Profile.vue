<template>
  <div class="body">
    <!-- 顶部状态栏 -->
    <StatusBar />

    <!-- 标题栏 -->
    <div class="flex items-center justify-between px-4 py-3">
      <h1 class="nav-title">我的</h1>
      <div class="flex items-center gap-2">
        <button @click="logout" class="text-[14px] text-textGray">退出</button>
      </div>
    </div>

    <!-- 用户信息 -->
    <div class="px-4 mt-6">
      <div class="bg-white rounded-lg shadow-sm p-4 flex items-center gap-4">
        <div class="w-[60px] h-[60px] rounded-full bg-gray-200 flex items-center justify-center">
          <i class="fa-solid fa-user text-[24px] text-textGray"></i>
        </div>
        <div>
          <p class="text-[18px] font-semibold text-black">{{ userName }}</p>
          <p class="text-[14px] text-textGray">ID: {{ userId || '未登录' }}</p>
        </div>
      </div>
    </div>

    <!-- 我的组队 -->
    <div class="px-4 mt-6">
      <p class="text-[14px] text-black mb-2">我的组队</p>
      <div v-if="userTeams.length === 0" class="bg-white rounded-lg shadow-sm p-6 text-center">
        <p class="text-[14px] text-textGray">暂无组队记录</p>
      </div>
      <div v-else class="space-y-3">
        <div v-for="team in userTeams" :key="team.id" class="bg-white rounded-lg shadow-sm p-4">
          <p class="text-[15px] font-semibold text-black mb-1">{{ team.matchId }}</p>
          <p class="text-[12px] text-textGray">{{ team.status }} - 总分: {{ team.totalScore }}</p>
        </div>
      </div>
    </div>

    <!-- 底部导航栏 -->
    <TabBar activeTab="profile" />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import StatusBar from '@/components/StatusBar.vue'
import TabBar from '@/components/TabBar.vue'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()
const userId = computed(() => userStore.currentUser?.id || '')
const userName = computed(() => userStore.currentUser?.username || '游客')
const userTeams = ref([])

const logout = () => {
  userStore.logout()
  router.push('/')
}

onMounted(async () => {
  // TODO: 加载用户组队历史
  // 模拟数据
  userTeams.value = [
    { id: '1', matchId: 'TEAM001', status: 'completed', totalScore: 2026 },
    { id: '2', matchId: 'TEAM002', status: 'completed', totalScore: 2026 }
  ]
})
</script>

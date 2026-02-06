<template>
  <div class="fixed bottom-0 left-0 right-0 max-w-[430px] mx-auto bg-white border-t border-gray-200 h-[80px] flex items-center justify-around px-6">
    <router-link
      to="/"
      class="tabbar-item"
      :class="{ 'tabbar-active': activeTab === 'home' }"
    >
      <i class="fa-solid fa-house text-[22px]"></i>
      <span>首页</span>
    </router-link>
    <router-link
      to="/match-pool"
      class="tabbar-item"
      :class="{ 'tabbar-active': activeTab === 'match' }"
    >
      <i class="fa-solid fa-magnifying-glass text-[22px]"></i>
      <span>找分数</span>
    </router-link>
    <router-link
      to="/profile"
      class="tabbar-item"
      :class="{ 'tabbar-active': activeTab === 'profile' }"
    >
      <i class="fa-solid fa-user text-[22px]"></i>
      <span>我的</span>
    </router-link>
  </div>
</template>

<script setup>
defineProps({
  activeTab: {
    type: String,
    default: 'home'
  }
})
</script>

<style scoped>
a {
  text-decoration: none;
}
</style>

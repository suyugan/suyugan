import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useUserStore = defineStore('user', () => {
  const currentUser = ref(null)
  const isLoggedIn = ref(false)
  const token = ref('')

  // 计算属性
  const userAvatar = computed(() => currentUser.value?.avatar || '')
  const userName = computed(() => currentUser.value?.username || '游客')

  // Actions
  const setUser = (user) => {
    currentUser.value = user
    isLoggedIn.value = !!user
    if (user?.token) {
      token.value = user.token
      localStorage.setItem('userToken', user.token)
    }
  }

  const setToken = (newToken) => {
    token.value = newToken
    localStorage.setItem('userToken', newToken)
  }

  const logout = () => {
    currentUser.value = null
    isLoggedIn.value = false
    token.value = ''
    localStorage.removeItem('userToken')
  }

  // 从localStorage恢复登录状态
  const restoreSession = () => {
    const savedToken = localStorage.getItem('userToken')
    if (savedToken) {
      token.value = savedToken
      isLoggedIn.value = true
      // TODO: 验证token有效性
    }
  }

  return {
    currentUser,
    isLoggedIn,
    token,
    userAvatar,
    userName,
    setUser,
    setToken,
    logout,
    restoreSession
  }
})

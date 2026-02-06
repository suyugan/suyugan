import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import axios from 'axios'

export const useMatchStore = defineStore('match', () => {
  const currentMatch = ref(null)
  const matchStatus = ref('idle') // idle, waiting, matched, completed
  const currentToken = ref('')
  const currentScore = ref(0)
  const matchId = ref('')

  // 计算属性
  const isInMatch = computed(() => currentMatch.value !== null)
  const isWaiting = computed(() => matchStatus.value === 'waiting')

  // Actions
  const setToken = (token) => {
    currentToken.value = token
  }

  const setScore = (score) => {
    currentScore.value = score
  }

  const setMatchId = (id) => {
    matchId.value = id
  }

  const setMatchStatus = (status) => {
    matchStatus.value = status
  }

  const setCurrentMatch = (match) => {
    currentMatch.value = match
  }

  // API: 加入匹配池
  const joinMatchPool = async () => {
    try {
      const response = await axios.post('/api/match/join', {
        token: currentToken.value,
        score: currentScore.value
      })

      if (response.data.success) {
        setMatchStatus('waiting')
        setMatchId(response.data.data.matchId)
        setCurrentMatch(response.data.data)
        return response.data
      } else {
        throw new Error(response.data.error || '加入匹配池失败')
      }
    } catch (error) {
      console.error('加入匹配池失败:', error)
      throw error
    }
  }

  // API: 查询匹配状态
  const checkMatchStatus = async () => {
    if (!matchId.value) return null

    try {
      const response = await axios.get(`/api/match/status/${matchId.value}`)
      if (response.data.success) {
        const data = response.data.data
        setMatchStatus(data.status)
        setCurrentMatch(data)
        return data
      }
      return null
    } catch (error) {
      console.error('查询匹配状态失败:', error)
      throw error
    }
  }

  // 重置状态
  const resetMatch = () => {
    currentMatch.value = null
    matchStatus.value = 'idle'
    currentToken.value = ''
    currentScore.value = 0
    matchId.value = ''
  }

  return {
    currentMatch,
    matchStatus,
    currentToken,
    currentScore,
    matchId,
    isInMatch,
    isWaiting,
    setToken,
    setScore,
    setMatchId,
    setMatchStatus,
    setCurrentMatch,
    joinMatchPool,
    checkMatchStatus,
    resetMatch
  }
})

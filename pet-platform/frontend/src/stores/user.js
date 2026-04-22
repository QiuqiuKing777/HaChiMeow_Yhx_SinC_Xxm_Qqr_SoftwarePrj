import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authApi } from '@/api'

export const useUserStore = defineStore('user', () => {
  const token = ref(localStorage.getItem('token') || '')
  const userInfo = ref(JSON.parse(localStorage.getItem('userInfo') || 'null'))

  const isLoggedIn = computed(() => !!token.value)
  const isUser = computed(() => userInfo.value?.role_type === 'user')
  const isPublisher = computed(() => userInfo.value?.role_type === 'publisher')
  const isAdmin = computed(() => userInfo.value?.role_type === 'admin')
  const roleType = computed(() => userInfo.value?.role_type || '')

  function setAuthData(data) {
    token.value = data?.token || ''
    userInfo.value = data?.user || null

    if (token.value) {
      localStorage.setItem('token', token.value)
    } else {
      localStorage.removeItem('token')
    }

    if (userInfo.value) {
      localStorage.setItem('userInfo', JSON.stringify(userInfo.value))
    } else {
      localStorage.removeItem('userInfo')
    }
  }

  function setUserInfo(user) {
    userInfo.value = user || null

    if (userInfo.value) {
      localStorage.setItem('userInfo', JSON.stringify(userInfo.value))
    } else {
      localStorage.removeItem('userInfo')
    }
  }

  async function login(credentials) {
    const res = await authApi.login(credentials)
    setAuthData(res)
    return res
  }

  async function register(data) {
    const res = await authApi.register(data)
    setAuthData(res)
    return res
  }

  async function fetchMe() {
    if (!token.value) return null

    try {
      const res = await authApi.getMe()
      setUserInfo(res)
      return res
    } catch (error) {
      logout()
      throw error
    }
  }

  function logout() {
    token.value = ''
    userInfo.value = null
    localStorage.removeItem('token')
    localStorage.removeItem('userInfo')
  }

  return {
    userInfo,
    token,
    isLoggedIn,
    isUser,
    isPublisher,
    isAdmin,
    roleType,
    login,
    register,
    fetchMe,
    logout,
    setUserInfo,
  }
})

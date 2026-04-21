import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authApi } from '@/api'

export const useUserStore = defineStore('user', () => {
  const userInfo = ref(null)
  const token    = ref(localStorage.getItem('token') || '')

  const isLoggedIn   = computed(() => !!token.value)
  const isUser       = computed(() => userInfo.value?.role_type === 'user')
  const isPublisher  = computed(() => userInfo.value?.role_type === 'publisher')
  const isAdmin      = computed(() => userInfo.value?.role_type === 'admin')
  const roleType     = computed(() => userInfo.value?.role_type || '')

  async function login(credentials) {
    const res = await authApi.login(credentials)
    token.value    = res.token
    userInfo.value = res.user
    localStorage.setItem('token', res.token)
    return res
  }

  async function register(data) {
    const res = await authApi.register(data)
    token.value    = res.token
    userInfo.value = res.user
    localStorage.setItem('token', res.token)
    return res
  }

  async function fetchMe() {
    if (!token.value) return
    try {
      const res = await authApi.getMe()
      userInfo.value = res
    } catch {
      logout()
    }
  }

  function logout() {
    token.value    = ''
    userInfo.value = null
    localStorage.removeItem('token')
  }

  return { userInfo, token, isLoggedIn, isUser, isPublisher, isAdmin, roleType, login, register, fetchMe, logout }
})

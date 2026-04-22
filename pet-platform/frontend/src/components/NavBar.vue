<template>
  <el-container class="layout">
    <el-header class="navbar">
      <div class="navbar-inner">
        <router-link to="/" class="logo">🐱 宠爱平台</router-link>

        <el-menu mode="horizontal" :default-active="activeRoute" router class="nav-menu">
          <el-menu-item index="/pets">领养宠物</el-menu-item>
          <el-menu-item index="/products">宠物用品</el-menu-item>
          <el-menu-item index="/services">宠物服务</el-menu-item>
          <el-menu-item v-if="userStore.isAdmin" index="/admin">老大后台🐱</el-menu-item>
          <el-menu-item v-if="userStore.isPublisher" index="/publisher">老板后台🐱</el-menu-item>
        </el-menu>

        <div class="nav-right">
          <template v-if="userStore.isLoggedIn">
            <div class="nav-action">
              <el-badge :value="unreadCount || ''" :hidden="!unreadCount" class="notif-badge">
                <el-button :icon="Bell" circle @click="$router.push('/user/notifications')" />
              </el-badge>
            </div>

            <div class="nav-action">
              <el-badge :value="cartCount || ''" :hidden="!cartCount" class="cart-badge">
                <el-button :icon="ShoppingCart" circle @click="$router.push('/cart')" />
              </el-badge>
            </div>

            <div class="nav-action">
              <el-dropdown @command="handleDropdown">
                <el-avatar :src="userStore.userInfo?.avatar" :size="42" class="nav-avatar">
                  {{ userStore.userInfo?.nickname?.charAt(0) || 'U' }}
                </el-avatar>
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item command="profile">个人中心</el-dropdown-item>
                    <el-dropdown-item command="orders" v-if="userStore.isUser">我的订单</el-dropdown-item>
                    <el-dropdown-item command="applications" v-if="userStore.isUser">我的申请</el-dropdown-item>
                    <el-dropdown-item command="bookings">我的预约</el-dropdown-item>
                    <el-dropdown-item command="favorites">我的收藏</el-dropdown-item>
                    <el-dropdown-item command="messages">我的消息</el-dropdown-item>
                    <el-dropdown-item divided command="publisher" v-if="userStore.isPublisher">发布方工作台</el-dropdown-item>
                    <el-dropdown-item command="admin" v-if="userStore.isAdmin">管理员后台</el-dropdown-item>
                    <el-dropdown-item divided command="logout">退出登录</el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
            </div>
          </template>

          <template v-else>
            <el-button class="nav-btn" @click="$router.push('/login')">登录</el-button>
            <el-button class="nav-btn" type="primary" @click="$router.push('/register')">注册</el-button>
          </template>
        </div>
      </div>
    </el-header>

    <el-main class="main-content">
      <slot />
    </el-main>

    <el-footer class="footer">
      © 2025 宠物领养与宠物用品服务一体化平台 · 南开大学软件工程课程作业
    </el-footer>
  </el-container>
</template>


<script setup>
import {ref, computed, onMounted, watch} from 'vue'
import {useRoute, useRouter} from 'vue-router'
import {Bell, ShoppingCart} from '@element-plus/icons-vue'
import {useUserStore} from '@/stores/user'
import http from '@/api'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const cartCount = ref(0)
const unreadCount = ref(0)
const activeRoute = computed(() => route.path)

async function loadCounts() {
  if (!userStore.isLoggedIn) return

  if (userStore.isUser) {
    try {
      const cart = await http.get('/cart', {_silent: true})
      cartCount.value = Array.isArray(cart) ? cart.length : 0
    } catch {
    }
  }

  try {
    const notif = await http.get('/user/notifications', {
      params: {is_read: '0', per_page: 1},
      _silent: true,
    })
    unreadCount.value = notif.unread_count || 0
  } catch {
  }
}

function handleDropdown(cmd) {
  const map = {
    profile: '/user/profile',
    orders: '/orders',
    applications: '/user/applications',
    bookings: '/bookings',
    favorites: '/user/favorites',
    messages: '/messages',
    publisher: '/publisher/dashboard',
    admin: '/admin/dashboard',
  }

  if (cmd === 'logout') {
    userStore.logout()
    router.push('/login')
  } else if (map[cmd]) {
    router.push(map[cmd])
  }
}

onMounted(() => {
  if (userStore.isLoggedIn) loadCounts()
})

watch(() => userStore.isLoggedIn, (loggedIn) => {
  if (loggedIn) loadCounts()
  else {
    cartCount.value = 0
    unreadCount.value = 0
  }
})
</script>

<style scoped>
.layout {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: #f0eeff;
}

.navbar {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-bottom: none;
  padding: 0;
  height: 78px !important;
  box-shadow: 0 4px 18px rgba(118, 75, 162, 0.35);
}

.navbar-inner {
  display: flex;
  align-items: center;
  max-width: 1320px;
  margin: 0 auto;
  width: 100%;
  height: 78px;
  padding: 0 10px 0 8px;
  gap: 28px;
}

.logo {
  font-size: 34px;
  font-weight: 900;
  color: #fff;
  text-decoration: none;
  white-space: nowrap;
  text-shadow: 0 2px 6px rgba(0, 0, 0, 0.18);
  margin-left: -6px;
  letter-spacing: 0.5px;
  display: flex;
  align-items: center;
  height: 78px;
}

.nav-menu {
  border-bottom: none;
  flex: 1;
  min-width: 0;
  height: 78px;
  --el-menu-bg-color: transparent;
  --el-menu-hover-bg-color: rgba(255, 255, 255, 0.18);
  --el-menu-text-color: rgba(255, 255, 255, 0.92);
  --el-menu-active-color: #fff;
  --el-menu-hover-text-color: #fff;
  --el-menu-border-color: transparent;
}

.nav-menu :deep(.el-menu) {
  height: 78px;
  align-items: center;
  border-bottom: none !important;
}

.nav-menu :deep(.el-menu-item) {
  height: 78px;
  line-height: 78px;
  font-size: 22px;
  font-weight: 800;
  padding: 0 26px;
  min-width: 140px;
  text-align: center;
  border-bottom: none !important;
}

.nav-menu :deep(.el-menu-item:hover) {
  background: rgba(255, 255, 255, 0.16) !important;
  border-radius: 12px 12px 0 0;
}

.nav-menu :deep(.el-menu-item.is-active) {
  background: rgba(255, 255, 255, 0.14) !important;
  border-radius: 12px 12px 0 0;
  font-weight: 900;
}

.nav-right {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 14px;
  flex-shrink: 0;
  height: 78px;
}

/* 关键：统一右侧三个按钮的布局容器 */
.nav-action {
  width: 46px;
  height: 78px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.nav-right :deep(.el-badge) {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 46px;
  line-height: 1;
}

.nav-right :deep(.el-dropdown) {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 46px;
}

.nav-right :deep(.el-button) {
  --el-button-text-color: rgba(255, 255, 255, 0.95);
  --el-button-bg-color: rgba(255, 255, 255, 0.12);
  --el-button-border-color: rgba(255, 255, 255, 0.45);
  --el-button-hover-text-color: #fff;
  --el-button-hover-bg-color: rgba(255, 255, 255, 0.22);
  --el-button-hover-border-color: rgba(255, 255, 255, 0.72);
  width: 46px;
  height: 46px;
  padding: 0;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  vertical-align: middle;
}

.nav-right :deep(.el-button--primary) {
  --el-button-bg-color: rgba(255, 255, 255, 0.22);
  --el-button-border-color: rgba(255, 255, 255, 0.65);
  --el-button-hover-bg-color: rgba(255, 255, 255, 0.35);
}

.nav-avatar {
  cursor: pointer;
  border: 2px solid rgba(255, 255, 255, 0.7);
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.15);
  display: flex;
  align-items: center;
  justify-content: center;
}

.nav-right :deep(.el-avatar) {
  display: flex;
  align-items: center;
  justify-content: center;
  vertical-align: middle;
}

.notif-badge,
.cart-badge {
  margin-right: 0;
}

.main-content {
  flex: 1;
  max-width: 1200px;
  margin: 0 auto;
  width: 100%;
  padding: 24px 16px;
}

.footer {
  text-align: center;
  color: #7b6caa;
  font-size: 13px;
  padding: 16px;
  background: #e8e0ff;
  border-top: 1px solid #d4c8f0;
}
</style>

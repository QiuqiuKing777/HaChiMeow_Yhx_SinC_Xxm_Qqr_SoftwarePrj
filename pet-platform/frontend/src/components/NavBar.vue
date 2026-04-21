<template>
  <el-container class="layout">
    <!-- 顶部导航 -->
    <el-header class="navbar">
      <div class="navbar-inner">
        <router-link to="/" class="logo">🐾 宠爱平台</router-link>
        <el-menu mode="horizontal" :default-active="activeRoute" router class="nav-menu">
          <el-menu-item index="/pets">领养宠物</el-menu-item>
          <el-menu-item index="/products">宠物用品</el-menu-item>
          <el-menu-item index="/services">宠物服务</el-menu-item>
        </el-menu>
        <div class="nav-right">
          <template v-if="userStore.isLoggedIn">
            <el-badge :value="unreadCount || ''" :hidden="!unreadCount" class="notif-badge">
              <el-button :icon="Bell" circle @click="$router.push('/user/notifications')" />
            </el-badge>
            <el-badge :value="cartCount || ''" :hidden="!cartCount" class="cart-badge">
              <el-button :icon="ShoppingCart" circle @click="$router.push('/cart')" />
            </el-badge>
            <el-dropdown @command="handleDropdown">
              <el-avatar :src="userStore.userInfo?.avatar" :size="36" style="cursor:pointer">
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
          </template>
          <template v-else>
            <el-button @click="$router.push('/login')">登录</el-button>
            <el-button type="primary" @click="$router.push('/register')">注册</el-button>
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
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Bell, ShoppingCart } from '@element-plus/icons-vue'
import { useUserStore } from '@/stores/user'
import http from '@/api'

const route      = useRoute()
const router     = useRouter()
const userStore  = useUserStore()
const cartCount  = ref(0)
const unreadCount = ref(0)
const activeRoute = computed(() => route.path)

async function loadCounts() {
  if (!userStore.isLoggedIn) return
  // 购物车仅 user 角色有权限，使用 _silent 静默失败
  if (userStore.isUser) {
    try {
      const cart = await http.get('/cart', { _silent: true })
      cartCount.value = Array.isArray(cart) ? cart.length : 0
    } catch {}
  }
  // 通知徽标，使用 _silent 静默失败
  try {
    const notif = await http.get('/user/notifications', {
      params: { is_read: '0', per_page: 1 },
      _silent: true,
    })
    unreadCount.value = notif.unread_count || 0
  } catch {}
}

function handleDropdown(cmd) {
  const map = {
    'profile':      '/user/profile',
    'orders':       '/orders',
    'applications': '/user/applications',
    'bookings':     '/bookings',
    'favorites':    '/user/favorites',
    'messages':     '/messages',
    'publisher':    '/publisher/dashboard',
    'admin':        '/admin/dashboard',
  }
  if (cmd === 'logout') {
    userStore.logout()
    router.push('/login')
  } else if (map[cmd]) {
    router.push(map[cmd])
  }
}

// 仅在登录状态改变时加载（避免每次路由跳转重复触发）
onMounted(() => {
  if (userStore.isLoggedIn) loadCounts()
})
watch(() => userStore.isLoggedIn, (loggedIn) => {
  if (loggedIn) loadCounts()
  else { cartCount.value = 0; unreadCount.value = 0 }
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
  height: 64px !important;
  box-shadow: 0 2px 16px rgba(118, 75, 162, 0.35);
}
.navbar-inner {
  display: flex;
  align-items: center;
  max-width: 1200px;
  margin: 0 auto;
  width: 100%;
  height: 100%;
  padding: 0 20px;
  gap: 24px;
}
.logo {
  font-size: 20px;
  font-weight: bold;
  color: #fff;
  text-decoration: none;
  white-space: nowrap;
  text-shadow: 0 1px 4px rgba(0,0,0,0.15);
}
.nav-menu {
  border-bottom: none;
  flex: 1;
  --el-menu-bg-color: transparent;
  --el-menu-hover-bg-color: rgba(255, 255, 255, 0.18);
  --el-menu-text-color: rgba(255, 255, 255, 0.88);
  --el-menu-active-color: #fff;
  --el-menu-hover-text-color: #fff;
  --el-menu-border-color: transparent;
}
.nav-right {
  display: flex;
  align-items: center;
  gap: 12px;
}
.nav-right :deep(.el-button) {
  --el-button-text-color: rgba(255, 255, 255, 0.92);
  --el-button-bg-color: rgba(255, 255, 255, 0.12);
  --el-button-border-color: rgba(255, 255, 255, 0.4);
  --el-button-hover-text-color: #fff;
  --el-button-hover-bg-color: rgba(255, 255, 255, 0.22);
  --el-button-hover-border-color: rgba(255, 255, 255, 0.7);
}
.nav-right :deep(.el-button--primary) {
  --el-button-bg-color: rgba(255, 255, 255, 0.22);
  --el-button-border-color: rgba(255, 255, 255, 0.65);
  --el-button-hover-bg-color: rgba(255, 255, 255, 0.35);
}
.notif-badge, .cart-badge { margin-right: 4px; }
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

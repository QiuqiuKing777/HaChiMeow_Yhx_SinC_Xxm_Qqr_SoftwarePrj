<template>
  <div class="pub-layout">
    <!-- 侧边栏 -->
    <aside class="pub-aside" :class="{ collapsed: sideCollapsed }">
      <!-- Logo 区 -->
      <div class="aside-logo">
        <span class="logo-icon">🐾</span>
        <span class="logo-text" v-show="!sideCollapsed">发布方工作台</span>
      </div>

      <!-- 菜单 -->
      <el-menu
        :default-active="activeRoute"
        router
        :collapse="sideCollapsed"
        :collapse-transition="false"
        class="pub-menu"
      >
        <el-menu-item index="/publisher/dashboard">
          <el-icon><DataAnalysis /></el-icon>
          <template #title>数据概览</template>
        </el-menu-item>
        <el-menu-item index="/publisher/pets">
          <el-icon><PieChart /></el-icon>
          <template #title>宠物管理</template>
        </el-menu-item>
        <el-menu-item index="/publisher/applications">
          <el-icon><DocumentChecked /></el-icon>
          <template #title>领养申请</template>
        </el-menu-item>
        <el-menu-item index="/publisher/products">
          <el-icon><ShoppingBag /></el-icon>
          <template #title>商品管理</template>
        </el-menu-item>
        <el-menu-item index="/publisher/services">
          <el-icon><Operation /></el-icon>
          <template #title>服务管理</template>
        </el-menu-item>
        <el-menu-item index="/publisher/orders">
          <el-icon><List /></el-icon>
          <template #title>订单管理</template>
        </el-menu-item>
        <el-menu-item index="/publisher/bookings">
          <el-icon><Calendar /></el-icon>
          <template #title>预约管理</template>
        </el-menu-item>
      </el-menu>

      <!-- 底部操作 -->
      <div class="aside-bottom">
        <div class="aside-bottom-item" @click="goFront">
          <el-icon><House /></el-icon>
          <span v-show="!sideCollapsed">返回前台</span>
        </div>
        <div class="aside-bottom-item logout" @click="logout">
          <el-icon><SwitchButton /></el-icon>
          <span v-show="!sideCollapsed">退出登录</span>
        </div>
      </div>
    </aside>

    <!-- 右侧区域 -->
    <div class="pub-right" :class="{ expanded: sideCollapsed }">
      <!-- 顶部 Header -->
      <header class="pub-header">
        <div class="header-left">
          <el-icon class="collapse-btn" @click="sideCollapsed = !sideCollapsed">
            <Expand v-if="sideCollapsed" /><Fold v-else />
          </el-icon>
          <el-breadcrumb separator="/">
            <el-breadcrumb-item :to="{ path: '/publisher/dashboard' }">首页</el-breadcrumb-item>
            <el-breadcrumb-item v-if="breadcrumbLabel">{{ breadcrumbLabel }}</el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        <div class="header-right">
          <el-tooltip content="刷新页面">
            <el-icon class="header-action" @click="$router.go(0)"><Refresh /></el-icon>
          </el-tooltip>
          <el-divider direction="vertical" />
          <el-dropdown>
            <div class="user-info">
              <el-avatar :size="28" style="background:#67c23a">
                {{ (userStore.userInfo?.username || 'P')[0].toUpperCase() }}
              </el-avatar>
              <span class="username">{{ userStore.userInfo?.username || '发布方' }}</span>
              <el-icon style="font-size:12px"><ArrowDown /></el-icon>
            </div>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item @click="goFront"><el-icon><House /></el-icon>返回前台</el-dropdown-item>
                <el-dropdown-item divided @click="logout"><el-icon><SwitchButton /></el-icon>退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </header>

      <!-- 页面内容 -->
      <!-- 页面内容 -->
<main class="pub-main">
  <div v-if="showWelcome" class="empty-state">
    <div class="empty-cat">🐱</div>
    <div class="empty-text">哈~吉~马~路~哟~</div>
  </div>
  <router-view v-else />
</main>

    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  DataAnalysis, DocumentChecked, ShoppingBag, Calendar, List,
  House, SwitchButton, Expand, Fold, Refresh, ArrowDown, PieChart, Operation
} from '@element-plus/icons-vue'
import { useUserStore } from '@/stores/user'

const route     = useRoute()
const router    = useRouter()
const userStore = useUserStore()
const sideCollapsed = ref(false)

const activeRoute = computed(() => route.path)
const showWelcome = computed(() => route.path === '/publisher')

const routeLabels = {
  '/publisher/dashboard':    null,
  '/publisher/pets':         '宠物管理',
  '/publisher/applications': '领养申请',
  '/publisher/products':     '商品管理',
  '/publisher/services':     '服务管理',
  '/publisher/orders':       '订单管理',
  '/publisher/bookings':     '预约管理',
}
const breadcrumbLabel = computed(() => routeLabels[route.path] ?? null)

function goFront() { router.push('/') }
function logout()  { userStore.logout(); router.push('/login') }
</script>

<style scoped>
/* ---- 整体布局 ---- */
.pub-layout {
  display: flex;
  min-height: 100vh;
  background: #f0f2f5;
}

/* ---- 侧边栏 ---- */
.pub-aside {
  width: 220px;
  min-height: 100vh;
  background: #1a1a2e;
  display: flex;
  flex-direction: column;
  transition: width .25s;
  flex-shrink: 0;
  position: fixed;
  left: 0; top: 0; bottom: 0;
  z-index: 100;
}
.pub-aside.collapsed { width: 64px; }

.aside-logo {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 18px 20px;
  border-bottom: 1px solid #2a2a4a;
  white-space: nowrap;
  overflow: hidden;
}
.logo-icon  { font-size: 22px; flex-shrink: 0; }
.logo-text  { font-size: 15px; font-weight: 700; color: #e8eaf6; letter-spacing: .5px; }

.pub-menu {
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
  border-right: none;
  background: transparent;
  --el-menu-text-color: #a0a8c0;
  --el-menu-active-color: #fff;
  --el-menu-hover-bg-color: rgba(103,194,58,.15);
  --el-menu-bg-color: transparent;
  --el-menu-item-height: 50px;
}
.pub-menu :deep(.el-menu-item.is-active) {
  background: linear-gradient(90deg, rgba(103,194,58,.25), rgba(103,194,58,.08)) !important;
  border-right: 3px solid #67c23a;
  color: #fff !important;
}
.pub-menu :deep(.el-menu-item) {
  border-radius: 0;
  font-size: 14px;
}

.aside-bottom {
  padding: 12px 0;
  border-top: 1px solid #2a2a4a;
}
.aside-bottom-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 20px;
  color: #7b8499;
  font-size: 14px;
  cursor: pointer;
  transition: color .2s, background .2s;
  white-space: nowrap;
  overflow: hidden;
}
.aside-bottom-item:hover { background: rgba(255,255,255,.06); color: #c4c9d8; }
.aside-bottom-item.logout:hover { color: #f56c6c; }

/* ---- 右侧容器 ---- */
.pub-right {
  margin-left: 220px;
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  transition: margin-left .25s;
}
.pub-right.expanded { margin-left: 64px; }

/* ---- 顶部 Header ---- */
.pub-header {
  height: 56px;
  background: #fff;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
  box-shadow: 0 1px 4px rgba(0,21,41,.08);
  position: sticky;
  top: 0;
  z-index: 99;
}
.header-left {
  display: flex;
  align-items: center;
  gap: 14px;
}
.collapse-btn {
  font-size: 18px;
  cursor: pointer;
  color: #595959;
  transition: color .2s;
}
.collapse-btn:hover { color: #67c23a; }

.header-right {
  display: flex;
  align-items: center;
  gap: 12px;
}
.header-action {
  font-size: 17px;
  cursor: pointer;
  color: #595959;
  transition: color .2s;
}
.header-action:hover { color: #67c23a; }

.user-info {
  display: flex;
  align-items: center;
  gap: 6px;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 4px;
  transition: background .2s;
}
.user-info:hover { background: #f5f7fa; }
.username { font-size: 13px; color: #333; }

/* ---- 主内容 ---- */
.pub-main {
  flex: 1;
  padding: 20px;
  overflow: auto;
}
.pub-main {
  flex: 1;
  padding: 20px;
  overflow: auto;
  min-height: calc(100vh - 56px);
}

/* ---- 空状态 ---- */
.empty-state {
  min-height: calc(100vh - 96px);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  user-select: none;
  text-align: center;
}

.empty-cat {
  line-height: 1;
  font-size: min(45vw, 60vh);
  opacity: 0.92;
  transform: translateY(-2vh);
}

.empty-text {
  margin-top: 12px;
  font-size: 28px;
  font-weight: 700;
  color: #595959;
  letter-spacing: 4px;
}

</style>

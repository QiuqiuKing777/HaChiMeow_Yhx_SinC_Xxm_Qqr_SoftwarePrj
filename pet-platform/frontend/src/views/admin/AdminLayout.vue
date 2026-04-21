<template>
  <el-container class="admin-layout">
    <!-- 侧边栏 -->
    <el-aside width="220px" class="admin-aside">
      <div class="aside-logo">🐾 管理员后台</div>
      <el-menu :default-active="activeRoute" router class="admin-menu">
        <el-menu-item index="/admin/dashboard">
          <el-icon><DataAnalysis /></el-icon>数据概览
        </el-menu-item>
        <el-menu-item index="/admin/users">
          <el-icon><User /></el-icon>用户管理
        </el-menu-item>
        <el-menu-item index="/admin/review">
          <el-icon><DocumentChecked /></el-icon>内容审核
        </el-menu-item>
        <el-menu-item index="/admin/stats">
          <el-icon><TrendCharts /></el-icon>统计报表
        </el-menu-item>
        <el-divider />
        <el-menu-item index="/" @click="goFront">
          <el-icon><House /></el-icon>返回前台
        </el-menu-item>
        <el-menu-item @click="logout">
          <el-icon><SwitchButton /></el-icon>退出登录
        </el-menu-item>
      </el-menu>
    </el-aside>

    <!-- 主内容 -->
    <el-main class="admin-main">
      <router-view />
    </el-main>
  </el-container>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { DataAnalysis, User, DocumentChecked, TrendCharts, House, SwitchButton } from '@element-plus/icons-vue'
import { useUserStore } from '@/stores/user'

const route     = useRoute()
const router    = useRouter()
const userStore = useUserStore()
const activeRoute = computed(() => route.path)

function goFront() { router.push('/') }
function logout()  { userStore.logout(); router.push('/login') }
</script>

<style scoped>
.admin-layout { min-height: 100vh; }
.admin-aside  { background: #1a1a2e; }
.aside-logo   { padding: 20px 24px; font-size: 16px; font-weight: 700; color: #fff; border-bottom: 1px solid #2a2a4a; }
.admin-menu   { border-right: none; background: #1a1a2e; --el-menu-text-color:#adb5bd; --el-menu-active-color:#409eff; --el-menu-hover-bg-color:#2a2a4a; }
.admin-main   { background: #f5f7fa; padding: 24px; }
</style>

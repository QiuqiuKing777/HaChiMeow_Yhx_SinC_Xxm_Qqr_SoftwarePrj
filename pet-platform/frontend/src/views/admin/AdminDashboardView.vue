<template>
  <div>
    <h2 style="margin:0 0 24px">数据概览</h2>

    <!-- 核心统计卡片 -->
    <el-row :gutter="16" v-loading="loading">
      <el-col :span="6" v-for="card in statCards" :key="card.label">
        <el-card class="stat-card" :style="{ borderTop: `4px solid ${card.color}` }">
          <div class="stat-value">{{ card.value }}</div>
          <div class="stat-label">{{ card.label }}</div>
          <el-icon class="stat-icon" :style="{ color: card.color }">
            <component :is="card.icon" />
          </el-icon>
        </el-card>
      </el-col>
    </el-row>

    <!-- 二级指标 -->
    <el-row :gutter="16" style="margin-top:16px">
      <!-- 宠物状态 -->
      <el-col :span="8">
        <el-card>
          <template #header><span>🐾 宠物状态分布</span></template>
          <el-descriptions :column="1" size="small">
            <el-descriptions-item label="在线可领养">{{ stats.pets?.online || 0 }}</el-descriptions-item>
            <el-descriptions-item label="已领养">{{ stats.pets?.adopted || 0 }}</el-descriptions-item>
            <el-descriptions-item label="待审核">{{ stats.pets?.pending || 0 }}</el-descriptions-item>
            <el-descriptions-item label="合计">{{ stats.pets?.total || 0 }}</el-descriptions-item>
          </el-descriptions>
        </el-card>
      </el-col>

      <!-- 订单状态 -->
      <el-col :span="8">
        <el-card>
          <template #header><span>🛒 订单状态</span></template>
          <el-descriptions :column="1" size="small">
            <el-descriptions-item label="待支付">{{ stats.orders?.pending || 0 }}</el-descriptions-item>
            <el-descriptions-item label="已支付">{{ stats.orders?.paid || 0 }}</el-descriptions-item>
            <el-descriptions-item label="累计交易额">
              <span style="color:#f56c6c;font-weight:700">¥{{ stats.orders?.total_amount?.toFixed(2) || '0.00' }}</span>
            </el-descriptions-item>
            <el-descriptions-item label="合计订单">{{ stats.orders?.total || 0 }}</el-descriptions-item>
          </el-descriptions>
        </el-card>
      </el-col>

      <!-- 领养申请 -->
      <el-col :span="8">
        <el-card>
          <template #header><span>📋 领养申请</span></template>
          <el-descriptions :column="1" size="small">
            <el-descriptions-item label="待审核">
              <el-badge :value="stats.adoptions?.pending || 0" type="warning">
                <span>{{ stats.adoptions?.pending || 0 }} 条</span>
              </el-badge>
            </el-descriptions-item>
            <el-descriptions-item label="已通过">{{ stats.adoptions?.approved || 0 }}</el-descriptions-item>
            <el-descriptions-item label="合计">{{ stats.adoptions?.total || 0 }}</el-descriptions-item>
          </el-descriptions>
        </el-card>
      </el-col>
    </el-row>

    <!-- 预约状态 -->
    <el-row :gutter="16" style="margin-top:16px">
      <el-col :span="8">
        <el-card>
          <template #header><span>📅 服务预约</span></template>
          <el-descriptions :column="1" size="small">
            <el-descriptions-item label="待确认">{{ stats.bookings?.pending || 0 }}</el-descriptions-item>
            <el-descriptions-item label="已完成">{{ stats.bookings?.finished || 0 }}</el-descriptions-item>
            <el-descriptions-item label="合计">{{ stats.bookings?.total || 0 }}</el-descriptions-item>
          </el-descriptions>
        </el-card>
      </el-col>

      <!-- 快捷操作 -->
      <el-col :span="16">
        <el-card>
          <template #header><span>⚡ 快捷操作</span></template>
          <el-space wrap>
            <el-button type="primary" @click="$router.push('/admin/users')">用户管理</el-button>
            <el-button type="warning" @click="$router.push('/admin/review?tab=pets')">审核宠物</el-button>
            <el-button type="success" @click="$router.push('/admin/review?tab=products')">审核商品</el-button>
            <el-button type="info" @click="$router.push('/admin/stats')">查看报表</el-button>
          </el-space>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { User, ShoppingBag, Tickets, Calendar } from '@element-plus/icons-vue'
import { adminApi } from '@/api'

const stats   = ref({})
const loading = ref(false)

const statCards = computed(() => [
  { label: '注册用户',   value: stats.value.users?.total || 0,    color: '#409eff', icon: User },
  { label: '在架商品',   value: stats.value.products?.online || 0, color: '#67c23a', icon: ShoppingBag },
  { label: '待审核申请', value: stats.value.adoptions?.pending || 0, color: '#e6a23c', icon: Tickets },
  { label: '服务预约',   value: stats.value.bookings?.total || 0,  color: '#f56c6c', icon: Calendar },
])

async function loadStats() {
  loading.value = true
  try { stats.value = await adminApi.stats() }
  finally { loading.value = false }
}

onMounted(loadStats)
</script>

<style scoped>
.stat-card { position: relative; overflow: hidden; }
.stat-value { font-size: 32px; font-weight: 700; color: #303133; }
.stat-label { font-size: 14px; color: #909399; margin-top: 4px; }
.stat-icon  { position: absolute; right: 20px; top: 50%; transform: translateY(-50%); font-size: 48px; opacity: .15; }
</style>

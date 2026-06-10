<template>
  <div class="dashboard">
    <div class="welcome-banner">
      <div class="welcome-text">
        <h2>你好，{{ userStore.userInfo?.username || 'Admin' }}</h2>
        <p>今天是 {{ today }}，祝您工作顺利。</p>
      </div>
      <div class="welcome-deco">ADMIN</div>
    </div>

    <el-row :gutter="16" v-loading="loading" class="stat-row">
      <el-col :xs="12" :sm="6" v-for="card in statCards" :key="card.label">
        <div class="stat-card" :style="{ '--card-color': card.color }" @click="$router.push(card.to)">
          <div class="stat-card-main">
            <div>
              <div class="stat-value">{{ card.value }}</div>
              <div class="stat-label">{{ card.label }}</div>
            </div>
            <div class="stat-icon-wrap" :style="{ background: card.color + '22' }">
              <el-icon :style="{ color: card.color }"><component :is="card.icon" /></el-icon>
            </div>
          </div>
          <div class="stat-footer">
            <el-tag size="small" :style="{ background: card.color + '14', color: card.color, border: 'none' }">
              {{ card.tag }}
            </el-tag>
          </div>
        </div>
      </el-col>
    </el-row>

    <el-row :gutter="16" style="margin-top: 16px">
      <el-col :xs="24" :sm="14">
        <div class="chart-card">
          <div class="chart-card-header">
            <span class="chart-title">近7日平台动态</span>
            <el-tag size="small" type="info">真实数据</el-tag>
          </div>
          <div ref="barChartRef" class="chart-body"></div>
        </div>
      </el-col>
      <el-col :xs="24" :sm="10">
        <div class="chart-card">
          <div class="chart-card-header">
            <span class="chart-title">宠物状态分布</span>
          </div>
          <div ref="pieChartRef" class="chart-body"></div>
        </div>
      </el-col>
    </el-row>

    <el-row :gutter="16" style="margin-top: 16px; align-items: stretch">
      <el-col :xs="24" :sm="14" style="display: flex; flex-direction: column">
        <div class="detail-card" style="flex: 1">
          <div class="chart-card-header">
            <span class="chart-title">业务指标详情</span>
          </div>
          <el-row :gutter="0">
            <el-col :span="8" v-for="item in detailItems" :key="item.label">
              <div class="detail-item">
                <div class="detail-value" :style="{ color: item.color }">{{ item.value }}</div>
                <div class="detail-label">{{ item.label }}</div>
                <el-progress
                  :percentage="item.pct"
                  :color="item.color"
                  :stroke-width="4"
                  :show-text="false"
                  style="margin-top: 6px"
                />
              </div>
            </el-col>
          </el-row>
        </div>
      </el-col>
      <el-col :xs="24" :sm="10" style="display: flex; flex-direction: column">
        <div class="detail-card" style="flex: 1; display: flex; flex-direction: column">
          <div class="chart-card-header">
            <span class="chart-title">快捷操作</span>
          </div>
          <div class="quick-actions" style="flex: 1">
            <div
              v-for="action in quickActions"
              :key="action.label"
              class="quick-btn"
              :style="{ '--qc': action.color }"
              @click="$router.push(action.to)"
            >
              <el-icon><component :is="action.icon" /></el-icon>
              <span>{{ action.label }}</span>
            </div>
          </div>
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import { User, ShoppingBag, Tickets, Calendar, TrendCharts, UserFilled } from '@element-plus/icons-vue'
import { adminApi } from '@/api'
import { useUserStore } from '@/stores/user'
import * as echarts from 'echarts/core'
import { BarChart, PieChart } from 'echarts/charts'
import { GridComponent, TooltipComponent, LegendComponent } from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'

echarts.use([BarChart, PieChart, GridComponent, TooltipComponent, LegendComponent, CanvasRenderer])

const userStore = useUserStore()
const stats = ref({})
const loading = ref(false)

const today = new Date().toLocaleDateString('zh-CN', {
  year: 'numeric',
  month: 'long',
  day: 'numeric',
  weekday: 'long',
})

const statCards = computed(() => [
  { label: '注册用户', value: stats.value.users?.total || 0, color: '#409eff', icon: User, tag: '全部用户', to: '/admin/users' },
  { label: '在架商品', value: stats.value.products?.online || 0, color: '#67c23a', icon: ShoppingBag, tag: '上架中', to: '/admin/review?tab=products' },
  { label: '待审核申请', value: stats.value.adoptions?.pending || 0, color: '#e6a23c', icon: Tickets, tag: '需处理', to: '/admin/review?tab=pets' },
  { label: '服务预约', value: stats.value.bookings?.total || 0, color: '#f56c6c', icon: Calendar, tag: '累计', to: '/admin/stats' },
])

const detailItems = computed(() => {
  const data = stats.value
  const totalPets = Math.max(data.pets?.total || 1, 1)
  const totalOrders = Math.max(data.orders?.total || 1, 1)
  const totalBookings = Math.max(data.bookings?.total || 1, 1)
  return [
    { label: '可领养', value: data.pets?.online || 0, color: '#409eff', pct: Math.min(100, ((data.pets?.online || 0) / totalPets) * 100) },
    { label: '已领养', value: data.pets?.adopted || 0, color: '#67c23a', pct: Math.min(100, ((data.pets?.adopted || 0) / totalPets) * 100) },
    { label: '待审宠物', value: data.pets?.pending || 0, color: '#e6a23c', pct: Math.min(100, ((data.pets?.pending || 0) / totalPets) * 100) },
    { label: '待支付', value: data.orders?.pending || 0, color: '#f56c6c', pct: Math.min(100, ((data.orders?.pending || 0) / totalOrders) * 100) },
    { label: '已支付订单', value: data.orders?.paid || 0, color: '#409eff', pct: Math.min(100, ((data.orders?.paid || 0) / totalOrders) * 100) },
    { label: '待确认预约', value: data.bookings?.pending || 0, color: '#9b59b6', pct: Math.min(100, ((data.bookings?.pending || 0) / totalBookings) * 100) },
  ]
})

const quickActions = [
  { label: '用户管理', to: '/admin/users', color: '#409eff', icon: UserFilled },
  { label: '审核宠物', to: '/admin/review?tab=pets', color: '#e6a23c', icon: Tickets },
  { label: '审核商品', to: '/admin/review?tab=products', color: '#67c23a', icon: ShoppingBag },
  { label: '统计报表', to: '/admin/stats', color: '#f56c6c', icon: TrendCharts },
]

const barChartRef = ref(null)
const pieChartRef = ref(null)
let barChart = null
let pieChart = null

function getLast7DayLabels() {
  const labels = []
  for (let i = 6; i >= 0; i -= 1) {
    const date = new Date()
    date.setDate(date.getDate() - i)
    labels.push(`${date.getMonth() + 1}/${date.getDate()}`)
  }
  return labels
}

function normalizeTrend(rows) {
  const map = new Map((rows || []).map((row) => [String(row.date), Number(row.count || 0)]))
  const result = []
  for (let i = 6; i >= 0; i -= 1) {
    const date = new Date()
    date.setDate(date.getDate() - i)
    const key = date.toISOString().slice(0, 10)
    result.push(map.get(key) || 0)
  }
  return result
}

function initBarChart() {
  if (!barChartRef.value) return
  if (!barChart) {
    barChart = echarts.init(barChartRef.value)
  }

  const trend = stats.value.trend || {}
  const orders = normalizeTrend(trend.orders)
  const adoptions = normalizeTrend(trend.adoptions)

  barChart.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    legend: { data: ['新增订单', '新增领养申请'], top: 0, right: 0, textStyle: { fontSize: 14, color: '#606266' } },
    grid: { left: 10, right: 10, bottom: 0, top: 36, containLabel: true },
    xAxis: {
      type: 'category',
      data: getLast7DayLabels(),
      axisLine: { lineStyle: { color: '#e4e7ed' } },
      axisLabel: { color: '#909399', fontSize: 13 },
    },
    yAxis: {
      type: 'value',
      minInterval: 1,
      splitLine: { lineStyle: { color: '#f0f2f5' } },
      axisLabel: { color: '#909399', fontSize: 13 },
    },
    series: [
      { name: '新增订单', type: 'bar', data: orders, barMaxWidth: 20, itemStyle: { color: '#409eff', borderRadius: [3, 3, 0, 0] } },
      { name: '新增领养申请', type: 'bar', data: adoptions, barMaxWidth: 20, itemStyle: { color: '#67c23a', borderRadius: [3, 3, 0, 0] } },
    ],
  })
}

function initPieChart() {
  if (!pieChartRef.value) return
  if (!pieChart) {
    pieChart = echarts.init(pieChartRef.value)
  }

  const pets = stats.value.pets || {}
  pieChart.setOption({
    tooltip: { trigger: 'item', formatter: '{b}: {c} ({d}%)' },
    legend: { bottom: 0, textStyle: { color: '#606266', fontSize: 14 } },
    series: [{
      type: 'pie',
      radius: ['42%', '68%'],
      center: ['50%', '44%'],
      avoidLabelOverlap: true,
      label: { show: false },
      emphasis: { label: { show: true, fontSize: 14, fontWeight: 'bold' } },
      data: [
        { value: pets.online || 0, name: '可领养', itemStyle: { color: '#409eff' } },
        { value: pets.adopted || 0, name: '已领养', itemStyle: { color: '#67c23a' } },
        { value: pets.pending || 0, name: '待审核', itemStyle: { color: '#e6a23c' } },
      ],
    }],
  })
}

function resizeCharts() {
  barChart?.resize()
  pieChart?.resize()
}

async function loadStats() {
  loading.value = true
  try {
    stats.value = await adminApi.stats()
    await nextTick()
    initBarChart()
    initPieChart()
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadStats()
  window.addEventListener('resize', resizeCharts)
})

onUnmounted(() => {
  window.removeEventListener('resize', resizeCharts)
  barChart?.dispose()
  pieChart?.dispose()
})
</script>

<style scoped>
.dashboard { padding-bottom: 20px; }

.welcome-banner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 60%, #0f3460 100%);
  border-radius: 12px;
  padding: 24px 28px;
  margin-bottom: 16px;
}

.welcome-text h2 { color: #fff; font-size: 20px; margin: 0 0 6px; }
.welcome-text p { color: #a0b0d0; font-size: 13px; margin: 0; }
.welcome-deco { font-size: 32px; color: rgba(255, 255, 255, 0.72); font-weight: 700; line-height: 1; }

.stat-card {
  background: #fff;
  border-radius: 10px;
  padding: 18px 20px 14px;
  box-shadow: 0 1px 6px rgba(0, 21, 41, 0.06);
  border-top: 3px solid var(--card-color);
  transition: box-shadow .2s, transform .2s;
  cursor: pointer;
  margin-bottom: 16px;
}

.stat-card:hover { box-shadow: 0 4px 16px rgba(0, 21, 41, 0.12); transform: translateY(-2px); }
.stat-card-main { display: flex; align-items: center; justify-content: space-between; }
.stat-value { font-size: 30px; font-weight: 800; color: #1f2937; line-height: 1; }
.stat-label { font-size: 13px; color: #8c9bb5; margin-top: 5px; }

.stat-icon-wrap {
  width: 52px;
  height: 52px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.stat-icon-wrap .el-icon { font-size: 24px; }
.stat-footer { margin-top: 14px; }

.chart-card,
.detail-card {
  background: #fff;
  border-radius: 10px;
  padding: 18px 20px;
  box-shadow: 0 1px 6px rgba(0, 21, 41, 0.06);
  margin-bottom: 0;
}

.chart-card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 14px;
}

.chart-title { font-size: 17px; font-weight: 600; color: #1f2937; }
.chart-body { height: 230px; }

.detail-item {
  padding: 12px 14px;
  border-right: 1px solid #f0f2f5;
  border-bottom: 1px solid #f0f2f5;
}

.detail-item:nth-child(3n) { border-right: none; }
.detail-item:nth-child(n+4) { border-bottom: none; }
.detail-value { font-size: 22px; font-weight: 700; }
.detail-label { font-size: 12px; color: #8c9bb5; margin-top: 3px; }

.quick-actions {
  display: grid;
  grid-template-columns: 1fr 1fr;
  grid-template-rows: 1fr 1fr;
  gap: 14px;
  margin-top: 4px;
}

.quick-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  padding: 0 16px;
  border-radius: 10px;
  border: 1.5px solid var(--qc);
  background: transparent;
  color: var(--qc);
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: all .2s;
  opacity: .85;
  min-height: 56px;
}

.quick-btn:hover {
  background: var(--qc);
  color: #fff;
  opacity: 1;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px color-mix(in srgb, var(--qc) 35%, transparent);
}

.quick-btn .el-icon { font-size: 20px; }
</style>

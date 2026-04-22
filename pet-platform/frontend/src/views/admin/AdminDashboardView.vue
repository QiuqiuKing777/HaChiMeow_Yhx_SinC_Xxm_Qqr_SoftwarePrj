<template>
  <div class="dashboard">
    <!-- 欢迎横幅 -->
    <div class="welcome-banner">
      <div class="welcome-text">
        <h2>你好，{{ userStore.userInfo?.username || 'Admin' }} 👋</h2>
        <p>今天是 {{ today }}，祝您工作顺利！</p>
      </div>
      <div class="welcome-deco">🐾</div>
    </div>

    <!-- 核心数据卡片 -->
    <el-row :gutter="16" v-loading="loading" class="stat-row">
      <el-col :xs="12" :sm="6" v-for="card in statCards" :key="card.label">
        <div class="stat-card" :style="{ '--card-color': card.color }">
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
            <el-tag size="small" :style="{ background: card.color+'14', color: card.color, border: 'none' }">
              {{ card.tag }}
            </el-tag>
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- 图表区 -->
    <el-row :gutter="16" style="margin-top:16px">
      <el-col :xs="24" :sm="14">
        <div class="chart-card">
          <div class="chart-card-header">
            <span class="chart-title">近7日平台动态</span>
            <el-tag size="small" type="info">实时</el-tag>
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

    <!-- 底部：详细指标 + 快捷操作 -->
    <el-row :gutter="16" style="margin-top:16px;align-items:stretch">
      <el-col :xs="24" :sm="14" style="display:flex;flex-direction:column">
        <div class="detail-card" style="flex:1">
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
                  style="margin-top:6px"
                />
              </div>
            </el-col>
          </el-row>
        </div>
      </el-col>
      <el-col :xs="24" :sm="10" style="display:flex;flex-direction:column">
        <div class="detail-card" style="flex:1;display:flex;flex-direction:column">
          <div class="chart-card-header">
            <span class="chart-title">快捷操作</span>
          </div>
          <div class="quick-actions" style="flex:1">
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
const stats     = ref({})
const loading   = ref(false)

const today = new Date().toLocaleDateString('zh-CN', {
  year: 'numeric', month: 'long', day: 'numeric', weekday: 'long'
})

const statCards = computed(() => [
  { label: '注册用户',   value: stats.value.users?.total || 0,           color: '#409eff', icon: User,        tag: '全部用户' },
  { label: '在架商品',   value: stats.value.products?.online || 0,       color: '#67c23a', icon: ShoppingBag, tag: '上架中' },
  { label: '待审核申请', value: stats.value.adoptions?.pending || 0,     color: '#e6a23c', icon: Tickets,     tag: '需处理' },
  { label: '服务预约',   value: stats.value.bookings?.total || 0,        color: '#f56c6c', icon: Calendar,    tag: '累计' },
])

const detailItems = computed(() => {
  const o = stats.value
  const tp = Math.max(o.pets?.total || 1, 1)
  const to = Math.max(o.orders?.total || 1, 1)
  const tb = Math.max(o.bookings?.total || 1, 1)
  return [
    { label: '可领养',    value: o.pets?.online   || 0, color: '#409eff', pct: Math.min(100, ((o.pets?.online   ||0)/tp)*100) },
    { label: '已领养',    value: o.pets?.adopted  || 0, color: '#67c23a', pct: Math.min(100, ((o.pets?.adopted  ||0)/tp)*100) },
    { label: '待审宠物',  value: o.pets?.pending  || 0, color: '#e6a23c', pct: Math.min(100, ((o.pets?.pending  ||0)/tp)*100) },
    { label: '待支付',    value: o.orders?.pending|| 0, color: '#f56c6c', pct: Math.min(100, ((o.orders?.pending||0)/to)*100) },
    { label: '已完成订单',value: o.orders?.paid   || 0, color: '#409eff', pct: Math.min(100, ((o.orders?.paid   ||0)/to)*100) },
    { label: '待确认预约',value: o.bookings?.pending||0, color: '#9b59b6', pct: Math.min(100, ((o.bookings?.pending||0)/tb)*100) },
  ]
})

const quickActions = [
  { label: '用户管理', to: '/admin/users',               color: '#409eff', icon: UserFilled  },
  { label: '审核宠物', to: '/admin/review?tab=pets',     color: '#e6a23c', icon: Tickets     },
  { label: '审核商品', to: '/admin/review?tab=products', color: '#67c23a', icon: ShoppingBag },
  { label: '统计报表', to: '/admin/stats',               color: '#f56c6c', icon: TrendCharts },
]

const barChartRef = ref(null)
const pieChartRef = ref(null)
let barChart = null
let pieChart = null

function initBarChart() {
  if (!barChartRef.value) return
  barChart = echarts.init(barChartRef.value)
  const days = []
  for (let i = 6; i >= 0; i--) {
    const d = new Date(); d.setDate(d.getDate() - i)
    days.push(`${d.getMonth() + 1}/${d.getDate()}`)
  }
  const base   = Math.max(stats.value.users?.total || 5, 5)
  const users  = days.map(() => Math.floor(base * (0.02 + Math.random() * 0.06)))
  const orders = days.map(() => Math.floor(base * (0.01 + Math.random() * 0.04)))
  barChart.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    legend: { data: ['新增用户', '新增订单'], top: 0, right: 0, textStyle: { fontSize: 14, color: '#606266' } },
    grid: { left: 10, right: 10, bottom: 0, top: 36, containLabel: true },
    xAxis: {
      type: 'category', data: days,
      axisLine: { lineStyle: { color: '#e4e7ed' } },
      axisLabel: { color: '#909399', fontSize: 13 }
    },
    yAxis: {
      type: 'value',
      splitLine: { lineStyle: { color: '#f0f2f5' } },
      axisLabel: { color: '#909399', fontSize: 13 }
    },
    series: [
      { name: '新增用户',  type: 'bar', data: users,  barMaxWidth: 20, itemStyle: { color: '#409eff', borderRadius: [3,3,0,0] } },
      { name: '新增订单', type: 'bar', data: orders, barMaxWidth: 20, itemStyle: { color: '#67c23a', borderRadius: [3,3,0,0] } },
    ]
  })
}

function initPieChart() {
  if (!pieChartRef.value) return
  pieChart = echarts.init(pieChartRef.value)
  const p       = stats.value.pets || {}
  const online  = p.online  || 0
  const adopted = p.adopted || 0
  const pending = p.pending || 0
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
        { value: online,  name: '可领养', itemStyle: { color: '#409eff' } },
        { value: adopted, name: '已领养', itemStyle: { color: '#67c23a' } },
        { value: pending, name: '待审核', itemStyle: { color: '#e6a23c' } },
      ]
    }]
  })
}

function resizeCharts() { barChart?.resize(); pieChart?.resize() }

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

onMounted(() => { loadStats(); window.addEventListener('resize', resizeCharts) })
onUnmounted(() => { window.removeEventListener('resize', resizeCharts); barChart?.dispose(); pieChart?.dispose() })
</script>

<style scoped>
.dashboard { padding-bottom: 20px; }

/* ---- 欢迎横幅 ---- */
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
.welcome-text p  { color: #a0b0d0; font-size: 13px; margin: 0; }
.welcome-deco    { font-size: 52px; opacity: .8; line-height: 1; }

/* ---- 统计卡片 ---- */
.stat-card {
  background: #fff;
  border-radius: 10px;
  padding: 18px 20px 14px;
  box-shadow: 0 1px 6px rgba(0,21,41,.06);
  border-top: 3px solid var(--card-color);
  transition: box-shadow .2s, transform .2s;
  cursor: default;
  margin-bottom: 16px;
}
.stat-card:hover { box-shadow: 0 4px 16px rgba(0,21,41,.12); transform: translateY(-2px); }
.stat-card-main  { display: flex; align-items: center; justify-content: space-between; }
.stat-value      { font-size: 30px; font-weight: 800; color: #1f2937; line-height: 1; }
.stat-label      { font-size: 13px; color: #8c9bb5; margin-top: 5px; }
.stat-icon-wrap  {
  width: 52px; height: 52px; border-radius: 12px;
  display: flex; align-items: center; justify-content: center;
}
.stat-icon-wrap .el-icon { font-size: 24px; }
.stat-footer { margin-top: 14px; }

/* ---- 图表卡片 ---- */
.chart-card, .detail-card {
  background: #fff;
  border-radius: 10px;
  padding: 18px 20px;
  box-shadow: 0 1px 6px rgba(0,21,41,.06);
  margin-bottom: 0;
}
.chart-card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 14px;
}
.chart-title { font-size: 17px; font-weight: 600; color: #1f2937; }
.chart-body  { height: 230px; }

/* ---- 详细指标 ---- */
.detail-item {
  padding: 12px 14px;
  border-right: 1px solid #f0f2f5;
  border-bottom: 1px solid #f0f2f5;
}
.detail-item:nth-child(3n)  { border-right: none; }
.detail-item:nth-child(n+4) { border-bottom: none; }
.detail-value { font-size: 22px; font-weight: 700; }
.detail-label { font-size: 12px; color: #8c9bb5; margin-top: 3px; }

/* ---- 快捷操作 ---- */
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
  border: 1.5px solid;
  border-color: var(--qc);
  background: transparent;
  color: var(--qc);
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: all .2s;
  opacity: .85;
  min-height: 56px;
}
.quick-btn:hover { background: var(--qc); color: #fff; opacity: 1; transform: translateY(-2px); box-shadow: 0 4px 12px color-mix(in srgb, var(--qc) 35%, transparent); }
.quick-btn .el-icon { font-size: 20px; }
</style>

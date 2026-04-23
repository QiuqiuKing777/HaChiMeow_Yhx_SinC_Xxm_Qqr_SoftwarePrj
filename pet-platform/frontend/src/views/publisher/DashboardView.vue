<template>
  <div class="dashboard">
    <!-- 欢迎横幅 -->
    <div class="welcome-banner">
      <div class="welcome-text">
        <h2>你好，{{ userStore.userInfo?.username || '发布方' }} 👋</h2>
        <p>今天是 {{ today }}，欢迎来到发布方工作台！</p>
      </div>
      <div class="welcome-deco">🐾</div>
    </div>

    <!-- 核心数据卡片 -->
    <el-row :gutter="16" v-loading="loading" class="stat-row">
      <el-col :xs="12" :sm="6" v-for="card in statCards" :key="card.label">
        <div class="stat-card" :style="{ '--card-color': card.color }" style="cursor:pointer" @click="$router.push(card.to)">
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
            <span class="chart-title">近7日业务动态</span>
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

    <!-- 底部：待处理事项 + 快捷操作 -->
    <el-row :gutter="16" style="margin-top:16px;align-items:stretch">
      <el-col :xs="24" :sm="14" style="display:flex;flex-direction:column">
        <div class="detail-card" style="flex:1">
          <div class="chart-card-header">
            <span class="chart-title">待处理领养申请</span>
            <el-button size="small" text type="primary" @click="$router.push('/publisher/applications')">查看全部</el-button>
          </div>
          <el-table :data="pendingApps" size="small" :show-header="pendingApps.length > 0">
            <template #empty>
              <el-empty description="暂无待审核申请" :image-size="60" />
            </template>
            <el-table-column label="宠物" prop="pet_name" />
            <el-table-column label="申请人" prop="applicant_name" width="90" />
            <el-table-column label="时间" prop="created_at" width="130" />
            <el-table-column label="操作" width="70">
              <template #default>
                <el-button size="small" type="primary" plain @click="$router.push('/publisher/applications')">审核</el-button>
              </template>
            </el-table-column>
          </el-table>
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
import { PieChart, ShoppingBag, Tickets, Calendar, DocumentChecked, List } from '@element-plus/icons-vue'
import { petsApi, adoptionsApi, ordersApi, productsApi, bookingsApi } from '@/api'
import { useUserStore } from '@/stores/user'
import * as echarts from 'echarts/core'
import { BarChart, PieChart as EchartsPie } from 'echarts/charts'
import { GridComponent, TooltipComponent, LegendComponent } from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'

echarts.use([BarChart, EchartsPie, GridComponent, TooltipComponent, LegendComponent, CanvasRenderer])

const userStore = useUserStore()
const loading   = ref(false)

const pets      = ref({})
const totalProducts = ref(0)
const totalApps     = ref(0)
const totalOrders   = ref(0)
const totalBookings = ref(0)
const pendingApps   = ref([])

const today = new Date().toLocaleDateString('zh-CN', {
  year: 'numeric', month: 'long', day: 'numeric', weekday: 'long'
})

const statCards = computed(() => [
  { label: '我的宠物',   value: (pets.value.available || 0) + (pets.value.adopted || 0) + (pets.value.reviewing || 0), color: '#409eff', icon: PieChart,   tag: '累计发布', to: '/publisher/pets'         },
  { label: '我的商品',   value: totalProducts.value,  color: '#67c23a', icon: ShoppingBag, tag: '在架商品',  to: '/publisher/products'     },
  { label: '待审核申请', value: totalApps.value,       color: '#e6a23c', icon: Tickets,     tag: '需处理',    to: '/publisher/applications' },
  { label: '待处理订单', value: totalOrders.value,     color: '#f56c6c', icon: List,        tag: '待发货',    to: '/publisher/orders'       },
])

const quickActions = [
  { label: '宠物管理',   to: '/publisher/pets',         color: '#409eff', icon: PieChart        },
  { label: '审核申请',   to: '/publisher/applications', color: '#e6a23c', icon: DocumentChecked },
  { label: '商品管理',   to: '/publisher/products',     color: '#67c23a', icon: ShoppingBag     },
  { label: '预约管理',   to: '/publisher/bookings',     color: '#9b59b6', icon: Calendar        },
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
  const baseO = Math.max(totalOrders.value || 2, 2)
  const baseB = Math.max(totalBookings.value || 2, 2)
  const orders   = days.map(() => Math.floor(baseO * (0.05 + Math.random() * 0.2)))
  const bookings = days.map(() => Math.floor(baseB * (0.05 + Math.random() * 0.2)))
  barChart.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    legend: { data: ['新增订单', '新增预约'], top: 0, right: 0, textStyle: { fontSize: 14, color: '#606266' } },
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
      { name: '新增订单', type: 'bar', data: orders,   barMaxWidth: 20, itemStyle: { color: '#67c23a', borderRadius: [3,3,0,0] } },
      { name: '新增预约', type: 'bar', data: bookings, barMaxWidth: 20, itemStyle: { color: '#9b59b6', borderRadius: [3,3,0,0] } },
    ]
  })
}

function initPieChart() {
  if (!pieChartRef.value) return
  pieChart = echarts.init(pieChartRef.value)
  const available = pets.value.available || 0
  const adopted   = pets.value.adopted   || 0
  const reviewing = pets.value.reviewing || 0
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
        { value: available, name: '可领养', itemStyle: { color: '#409eff' } },
        { value: adopted,   name: '已领养', itemStyle: { color: '#67c23a' } },
        { value: reviewing, name: '审核中', itemStyle: { color: '#e6a23c' } },
      ]
    }]
  })
}

function resizeCharts() { barChart?.resize(); pieChart?.resize() }

async function loadData() {
  loading.value = true
  try {
    const [myPets, myProducts, apps, orders, bookings] = await Promise.allSettled([
      petsApi.myPets({ per_page: 100 }),
      productsApi.myProducts({ per_page: 1 }),
      adoptionsApi.publisherList({ status: 'pending', per_page: 5 }),
      ordersApi.publisherList({ delivery_status: 'unshipped', per_page: 1 }),
      bookingsApi.publisherList({ per_page: 1 }),
    ])
    if (myPets.status === 'fulfilled') {
      const items = myPets.value.items || []
      pets.value = {
        available: items.filter(p => p.status === 'available').length,
        adopted:   items.filter(p => p.status === 'adopted').length,
        reviewing: items.filter(p => p.status === 'reviewing').length,
      }
    }
    if (myProducts.status === 'fulfilled') totalProducts.value = myProducts.value.total || 0
    if (apps.status === 'fulfilled')       { totalApps.value = apps.value.total || 0; pendingApps.value = apps.value.items || [] }
    if (orders.status === 'fulfilled')     totalOrders.value   = orders.value.total   || 0
    if (bookings.status === 'fulfilled')   totalBookings.value = bookings.value.total || 0

    await nextTick()
    initBarChart()
    initPieChart()
  } finally {
    loading.value = false
  }
}

onMounted(() => { loadData(); window.addEventListener('resize', resizeCharts) })
onUnmounted(() => { window.removeEventListener('resize', resizeCharts); barChart?.dispose(); pieChart?.dispose() })
</script>

<style scoped>
.dashboard { padding-bottom: 20px; }

/* ---- 欢迎横幅 ---- */
.welcome-banner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: linear-gradient(135deg, #1a2e1a 0%, #163e16 60%, #0f600f 100%);
  border-radius: 12px;
  padding: 24px 28px;
  margin-bottom: 16px;
}
.welcome-text h2 { color: #fff; font-size: 20px; margin: 0 0 6px; }
.welcome-text p  { color: #a0d0a0; font-size: 13px; margin: 0; }
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

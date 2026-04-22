<template>
  <div class="admin-page">
    <!-- 页面横幅 -->
    <div class="page-banner">
      <div>
        <h2 class="page-banner-title">统计报表</h2>
        <p class="page-banner-sub">平台核心业务数据汇总与状态分布分析</p>
      </div>
      <el-button @click="loadAll" :loading="statsLoading" class="refresh-btn">
        刷新数据
      </el-button>
    </div>

    <!-- 核心指标卡片 -->
    <el-row :gutter="16" v-loading="statsLoading" class="metric-row">
      <el-col :xs="12" :sm="4" v-for="item in metrics" :key="item.label">
        <div class="metric-card" :style="{ '--mc': item.color }">
          <div class="metric-icon-wrap" :style="{ background: item.color + '18' }">
            <el-icon :style="{ color: item.color }"><component :is="item.icon" /></el-icon>
          </div>
          <div class="metric-value">{{ item.value }}</div>
          <div class="metric-label">{{ item.label }}</div>
        </div>
      </el-col>
    </el-row>

    <!-- 状态分布表格 -->
    <el-row :gutter="16" style="margin-top:16px">
      <el-col :xs="24" :sm="12">
        <div class="page-card">
          <div class="card-toolbar"><span class="card-title">宠物状态分布</span></div>
          <el-table :data="petStats" size="small" stripe class="admin-table">
            <el-table-column prop="status" label="状态">
              <template #default="{ row }">
                <el-tag :type="petStatusType(row.status)">{{ petStatusLabel(row.status) }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="count" label="数量" width="100">
              <template #default="{ row }">
                <span class="count-num">{{ row.count }}</span>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </el-col>
      <el-col :xs="24" :sm="12">
        <div class="page-card">
          <div class="card-toolbar"><span class="card-title">领养申请状态分布</span></div>
          <el-table :data="adoptionStats" size="small" stripe class="admin-table">
            <el-table-column prop="status" label="状态">
              <template #default="{ row }">
                <el-tag :type="adoptionStatusType(row.status)">{{ adoptionStatusLabel(row.status) }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="count" label="数量" width="100">
              <template #default="{ row }">
                <span class="count-num">{{ row.count }}</span>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </el-col>
    </el-row>

    <el-row :gutter="16" style="margin-top:16px">
      <el-col :xs="24" :sm="12">
        <div class="page-card">
          <div class="card-toolbar"><span class="card-title">订单状态分布</span></div>
          <el-table :data="orderStats" size="small" stripe class="admin-table">
            <el-table-column prop="status" label="状态">
              <template #default="{ row }">
                <el-tag :type="orderStatusType(row.status)">{{ orderStatusLabel(row.status) }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="count" label="数量" width="100">
              <template #default="{ row }">
                <span class="count-num">{{ row.count }}</span>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </el-col>
      <el-col :xs="24" :sm="12">
        <div class="page-card">
          <div class="card-toolbar"><span class="card-title">预约状态分布</span></div>
          <el-table :data="bookingStats" size="small" stripe class="admin-table">
            <el-table-column prop="status" label="状态">
              <template #default="{ row }">
                <el-tag :type="bookingStatusType(row.status)">{{ bookingStatusLabel(row.status) }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="count" label="数量" width="100">
              <template #default="{ row }">
                <span class="count-num">{{ row.count }}</span>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </el-col>
    </el-row>

    <!-- 操作日志 -->
    <div class="page-card" style="margin-top:16px">
      <div class="card-toolbar">
        <span class="card-title">操作日志</span>
        <div style="display:flex;gap:8px">
          <el-input v-model="log.keyword" placeholder="搜索操作员/操作类型" clearable @change="loadLogs" style="width:220px" />
          <el-button type="primary" @click="loadLogs">搜索</el-button>
          <el-button @click="log.keyword='';loadLogs()">重置</el-button>
        </div>
      </div>
      <el-table :data="log.list" v-loading="log.loading" stripe class="admin-table">
        <el-table-column prop="log_id" label="ID" width="70" />
        <el-table-column label="操作员" width="120">
          <template #default="{ row }">{{ row.operator?.username || row.operator_id }}</template>
        </el-table-column>
        <el-table-column prop="action" label="操作" width="150" />
        <el-table-column prop="target_type" label="对象类型" width="100" />
        <el-table-column prop="target_id" label="对象ID" width="80" />
        <el-table-column prop="detail" label="详情" show-overflow-tooltip />
        <el-table-column prop="created_at" label="时间" width="160">
          <template #default="{ row }">{{ row.created_at?.replace('T', ' ').substring(0, 19) }}</template>
        </el-table-column>
      </el-table>
      <el-pagination
        background layout="prev,pager,next,total" :total="log.total"
        :page-size="20" v-model:current-page="log.page"
        @current-change="loadLogs" style="margin-top:12px;display:flex;justify-content:flex-end"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { User, ShoppingBag, Tickets, Calendar, DataAnalysis, List } from '@element-plus/icons-vue'
import { adminApi } from '@/api'

const statsLoading = ref(false)
const stats = ref({})

const metrics = computed(() => [
  { label: '用户总数',    value: stats.value.total_users    ?? '-', color: '#409eff', icon: User },
  { label: '宠物总数',    value: stats.value.total_pets     ?? '-', color: '#e6a23c', icon: Tickets },
  { label: '商品总数',    value: stats.value.total_products ?? '-', color: '#67c23a', icon: ShoppingBag },
  { label: '服务总数',    value: stats.value.total_services ?? '-', color: '#9b59b6', icon: DataAnalysis },
  { label: '订单总数',    value: stats.value.total_orders   ?? '-', color: '#f56c6c', icon: List },
  { label: '预约总数',    value: stats.value.total_bookings ?? '-', color: '#1abc9c', icon: Calendar },
])

const petStats      = computed(() => stats.value.pet_stats      || [])
const adoptionStats = computed(() => stats.value.adoption_stats || [])
const orderStats    = computed(() => stats.value.order_stats    || [])
const bookingStats  = computed(() => stats.value.booking_stats  || [])

async function loadStats() {
  statsLoading.value = true
  try { stats.value = await adminApi.stats() } finally { statsLoading.value = false }
}

/* ---- logs ---- */
const log = reactive({ list: [], total: 0, page: 1, loading: false, keyword: '' })
async function loadLogs() {
  log.loading = true
  try {
    const res = await adminApi.logs({ page: log.page, per_page: 20, keyword: log.keyword })
    log.list = res.items || []; log.total = res.total || 0
  } finally { log.loading = false }
}

function loadAll() { loadStats(); loadLogs() }
onMounted(loadAll)

/* ---- 标签辅助 ---- */
const petStatusLabel = s => ({ available: '可领养', pending: '待审核', offline: '已下线', adopted: '已领养' })[s] || s
const petStatusType  = s => ({ available: 'success', pending: 'warning', offline: 'info', adopted: '' })[s] || ''

const adoptionStatusLabel = s => ({ pending: '待处理', reviewing: '审核中', approved: '已通过', rejected: '已拒绝', supplement: '补充材料', cancelled: '已取消' })[s] || s
const adoptionStatusType  = s => ({ pending: 'warning', reviewing: 'primary', approved: 'success', rejected: 'danger', supplement: 'warning', cancelled: 'info' })[s] || ''

const orderStatusLabel = s => ({ pending_payment: '待付款', pending_shipment: '待发货', shipped: '已发货', completed: '已完成', cancelled: '已取消', refunding: '退款中', refunded: '已退款' })[s] || s
const orderStatusType  = s => ({ pending_payment: 'warning', pending_shipment: 'primary', shipped: '', completed: 'success', cancelled: 'info', refunding: 'danger', refunded: 'info' })[s] || ''

const bookingStatusLabel = s => ({ pending: '待确认', confirmed: '已确认', cancelled: '已取消', completed: '已完成' })[s] || s
const bookingStatusType  = s => ({ pending: 'warning', confirmed: 'primary', cancelled: 'info', completed: 'success' })[s] || ''
</script>

<style scoped>
.admin-page { padding-bottom: 20px; }

.page-banner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 60%, #0f3460 100%);
  border-radius: 12px;
  padding: 20px 28px;
  margin-bottom: 16px;
}
.page-banner-title { color: #fff; font-size: 18px; font-weight: 700; margin: 0 0 4px; }
.page-banner-sub   { color: #a0b0d0; font-size: 13px; margin: 0; }
.refresh-btn { background: rgba(255,255,255,.12); border-color: rgba(255,255,255,.25); color: #fff; }
.refresh-btn:hover { background: rgba(255,255,255,.22); }

/* 核心指标卡片 */
.metric-row { margin-bottom: 0; }
.metric-card {
  background: #fff;
  border-radius: 10px;
  padding: 16px 18px;
  box-shadow: 0 1px 6px rgba(0,21,41,.06);
  border-top: 3px solid var(--mc);
  text-align: center;
  margin-bottom: 16px;
  transition: box-shadow .2s, transform .2s;
}
.metric-card:hover { box-shadow: 0 4px 16px rgba(0,21,41,.12); transform: translateY(-2px); }
.metric-icon-wrap {
  width: 44px; height: 44px;
  border-radius: 10px;
  display: flex; align-items: center; justify-content: center;
  margin: 0 auto 10px;
}
.metric-icon-wrap .el-icon { font-size: 22px; }
.metric-value { font-size: 26px; font-weight: 800; color: #1f2937; line-height: 1; }
.metric-label { font-size: 12px; color: #8c9bb5; margin-top: 5px; }

/* 通用卡片 */
.page-card {
  background: #fff;
  border-radius: 10px;
  padding: 18px 20px;
  box-shadow: 0 1px 6px rgba(0,21,41,.06);
  margin-bottom: 0;
}
.card-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
}
.card-title {
  font-size: 15px;
  font-weight: 600;
  color: #1f2937;
  padding-left: 10px;
  border-left: 3px solid #409eff;
}
.count-num { font-weight: 700; color: #409eff; }

.admin-table :deep(th.el-table__cell) {
  background: #f5f7fa;
  color: #606266;
  font-weight: 600;
}
</style>

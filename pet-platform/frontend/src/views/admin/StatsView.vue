<template>
  <div>
    <div class="page-header">
      <h2>统计报表</h2>
      <el-button @click="loadAll" :loading="statsLoading">刷新数据</el-button>
    </div>

    <!-- 核心指标 -->
    <el-row :gutter="16" v-loading="statsLoading">
      <el-col :span="4" v-for="item in metrics" :key="item.label">
        <el-card class="metric-card">
          <div class="metric-value">{{ item.value }}</div>
          <div class="metric-label">{{ item.label }}</div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 图表区 -->
    <el-row :gutter="16" style="margin-top:16px">
      <el-col :span="12">
        <el-card header="宠物状态分布">
          <el-table :data="petStats" size="small" stripe>
            <el-table-column prop="status" label="状态">
              <template #default="{ row }">
                <el-tag :type="petStatusType(row.status)">{{ petStatusLabel(row.status) }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="count" label="数量" />
          </el-table>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card header="领养申请状态分布">
          <el-table :data="adoptionStats" size="small" stripe>
            <el-table-column prop="status" label="状态">
              <template #default="{ row }">
                <el-tag :type="adoptionStatusType(row.status)">{{ adoptionStatusLabel(row.status) }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="count" label="数量" />
          </el-table>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="16" style="margin-top:16px">
      <el-col :span="12">
        <el-card header="订单状态分布">
          <el-table :data="orderStats" size="small" stripe>
            <el-table-column prop="status" label="状态">
              <template #default="{ row }">
                <el-tag :type="orderStatusType(row.status)">{{ orderStatusLabel(row.status) }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="count" label="数量" />
          </el-table>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card header="预约状态分布">
          <el-table :data="bookingStats" size="small" stripe>
            <el-table-column prop="status" label="状态">
              <template #default="{ row }">
                <el-tag :type="bookingStatusType(row.status)">{{ bookingStatusLabel(row.status) }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="count" label="数量" />
          </el-table>
        </el-card>
      </el-col>
    </el-row>

    <!-- 操作日志 -->
    <el-card style="margin-top:16px" header="操作日志">
      <el-row :gutter="12" style="margin-bottom:12px">
        <el-col :span="5">
          <el-input v-model="log.keyword" placeholder="搜索操作员/操作类型" clearable @change="loadLogs" />
        </el-col>
        <el-col :span="4">
          <el-button type="primary" @click="loadLogs">搜索</el-button>
          <el-button @click="log.keyword='';loadLogs()">重置</el-button>
        </el-col>
      </el-row>

      <el-table :data="log.list" v-loading="log.loading" stripe>
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
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { adminApi } from '@/api'

const statsLoading = ref(false)
const stats = ref({})

const metrics = computed(() => [
  { label: '用户总数',     value: stats.value.total_users     ?? '-' },
  { label: '宠物总数',     value: stats.value.total_pets      ?? '-' },
  { label: '商品总数',     value: stats.value.total_products  ?? '-' },
  { label: '服务总数',     value: stats.value.total_services  ?? '-' },
  { label: '订单总数',     value: stats.value.total_orders    ?? '-' },
  { label: '预约总数',     value: stats.value.total_bookings  ?? '-' },
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
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.page-header h2 { margin: 0; }
.metric-card { text-align: center; }
.metric-value { font-size: 32px; font-weight: bold; color: #409eff; }
.metric-label { margin-top: 6px; color: #606266; font-size: 14px; }
</style>

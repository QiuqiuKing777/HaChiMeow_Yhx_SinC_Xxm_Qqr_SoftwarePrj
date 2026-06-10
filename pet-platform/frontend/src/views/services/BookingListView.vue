<template>
  <NavBar>
    <h2>我的预约</h2>

    <div v-loading="loading">
      <el-empty v-if="!loading && bookings.length === 0" description="暂无预约记录" />

      <el-table :data="bookings" border>
        <el-table-column label="服务名称">
          <template #default="{ row }">
            {{ row.service?.service_name }}
          </template>
        </el-table-column>

        <el-table-column label="预约时间" width="200">
          <template #default="{ row }">
            {{ row.slot?.slot_date }} {{ row.slot?.slot_time }}
          </template>
        </el-table-column>

        <el-table-column label="金额" width="100">
          <template #default="{ row }">
            {{ row.service?.price != null ? '\xa5' + Number(row.service.price).toFixed(2) : '-' }}
          </template>
        </el-table-column>

        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="statusType(row.booking_status)">
              {{ statusLabel(row.booking_status) }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column label="操作" width="190">
          <template #default="{ row }">
            <div class="action-buttons">
              <el-button
                size="small"
                type="primary"
                plain
                @click="goComplaint(row)"
              >
                评价
              </el-button>

              <el-button
                v-if="row.booking_status === 'pending'"
                size="small"
                type="danger"
                @click="cancelBooking(row)"
              >
                取消
              </el-button>
            </div>
          </template>
        </el-table-column>
      </el-table>

      <el-pagination
        v-if="total > 0"
        background
        layout="prev,pager,next,total"
        :total="total"
        :page-size="10"
        v-model:current-page="page"
        @current-change="load"
        style="margin-top:20px;justify-content:center;display:flex"
      />
    </div>
  </NavBar>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import NavBar from '@/components/NavBar.vue'
import { bookingsApi } from '@/api'

const router = useRouter()
const route = useRoute()

const bookings = ref([])
const total    = ref(0)
const page     = ref(1)
const loading  = ref(false)

const statusLabel = s => ({
  pending: '待确认',
  confirmed: '已确认',
  finished: '已完成',
  cancelled: '已取消'
})[s] || s

const statusType = s => ({
  pending: 'warning',
  confirmed: 'primary',
  finished: 'success',
  cancelled: 'danger'
})[s] || ''

function getServiceId(row) {
  return row.service_id || row.service?.service_id || row.service?.id
}

function getServiceName(row) {
  return row.service?.service_name || row.service_name || row.service?.name || '服务'
}

function goComplaint(row) {
  const serviceId = getServiceId(row)

  if (!serviceId) {
    ElMessage.error('服务信息不存在，无法评价')
    return
  }

  router.push({
    path: '/complaints/create',
    query: {
      target_type: 'services',
      target_id: serviceId,
      target_name: getServiceName(row),
      return_to: route.fullPath
    }
  })
}

async function load() {
  loading.value = true
  try {
    const res = await bookingsApi.myList({ page: page.value, per_page: 10 })
    bookings.value = res.items || []
    total.value    = res.total || 0
  } catch {} finally {
    loading.value = false
  }
}

async function cancelBooking(row) {
  await bookingsApi.cancel(row.booking_id)
  ElMessage.success('已取消预约')
  load()
}

onMounted(load)
</script>

<style scoped>
.action-buttons {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}
</style>

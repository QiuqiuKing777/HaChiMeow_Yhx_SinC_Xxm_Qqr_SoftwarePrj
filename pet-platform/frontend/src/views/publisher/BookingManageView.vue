<template>
  <div>
    <h2>预约管理</h2>
    <el-select v-model="statusFilter" placeholder="状态筛选" clearable style="width:140px;margin-bottom:16px" @change="load">
      <el-option label="待确认" value="pending" />
      <el-option label="已确认" value="confirmed" />
      <el-option label="已完成" value="finished" />
      <el-option label="已取消" value="cancelled" />
    </el-select>
    <el-table :data="bookings" border v-loading="loading">
      <el-table-column label="服务" prop="service_name" />
      <el-table-column label="用户" prop="user_name" width="100" />
      <el-table-column label="预约时间" width="200">
        <template #default="{ row }">{{ row.slot_date }} {{ row.start_time }}-{{ row.end_time }}</template>
      </el-table-column>
      <el-table-column label="金额" prop="total_price" width="90">
        <template #default="{ row }">¥{{ row.total_price }}</template>
      </el-table-column>
      <el-table-column label="状态" width="90">
        <template #default="{ row }">
          <el-tag :type="{ pending:'warning', confirmed:'primary', finished:'success', cancelled:'danger' }[row.status]">
            {{ { pending:'待确认', confirmed:'已确认', finished:'已完成', cancelled:'已取消' }[row.status] }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="160">
        <template #default="{ row }">
          <el-button v-if="row.status === 'pending'" size="small" type="primary" @click="confirmBooking(row)">确认</el-button>
          <el-button v-if="row.status === 'confirmed'" size="small" type="success" @click="finishBooking(row)">完成</el-button>
          <el-button v-if="row.status === 'pending'" size="small" type="danger" @click="cancelBooking(row)">取消</el-button>
        </template>
      </el-table-column>
    </el-table>
    <el-pagination v-if="total > 0" background layout="prev,pager,next,total"
      :total="total" :page-size="10" v-model:current-page="page"
      @current-change="load" style="margin-top:16px;justify-content:center;display:flex" />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { bookingsApi } from '@/api'

const bookings      = ref([])
const total         = ref(0)
const page          = ref(1)
const loading       = ref(false)
const statusFilter  = ref('pending')

async function load() {
  loading.value = true
  try {
    const res = await bookingsApi.publisherList({ page: page.value, per_page: 10, status: statusFilter.value })
    bookings.value = res.items || []
    total.value    = res.total || 0
  } finally { loading.value = false }
}

async function confirmBooking(row) { await bookingsApi.confirm(row.booking_id); ElMessage.success('已确认'); load() }
async function finishBooking(row)  { await bookingsApi.finish(row.booking_id);  ElMessage.success('已完成'); load() }
async function cancelBooking(row)  { await bookingsApi.cancel(row.booking_id);  ElMessage.success('已取消'); load() }

onMounted(load)
</script>

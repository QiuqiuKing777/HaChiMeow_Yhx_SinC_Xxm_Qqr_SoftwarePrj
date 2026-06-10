<template>
  <div>
    <h2>预约管理</h2>

    <el-select
      v-model="statusFilter"
      placeholder="状态筛选"
      clearable
      style="width:140px;margin-bottom:16px"
      @change="handleFilterChange"
    >
      <el-option label="全部" value="" />
      <el-option label="待确认" value="pending" />
      <el-option label="已确认" value="confirmed" />
      <el-option label="已完成" value="finished" />
      <el-option label="已取消" value="cancelled" />
    </el-select>

    <el-table :data="bookings" border v-loading="loading">
      <el-table-column label="服务" min-width="160">
        <template #default="{ row }">
          {{ row.service_name || '-' }}
        </template>
      </el-table-column>

      <el-table-column label="预约用户" width="120">
        <template #default="{ row }">
          {{ row.user_name || `用户${row.user_id}` }}
        </template>
      </el-table-column>

      <el-table-column label="宠物信息" min-width="140">
        <template #default="{ row }">
          <div v-if="row.pet_name || row.pet_breed">
            {{ row.pet_name || '未填写' }}
            <span v-if="row.pet_breed"> / {{ row.pet_breed }}</span>
          </div>
          <span v-else>-</span>
        </template>
      </el-table-column>

      <el-table-column label="预约时间" min-width="190">
        <template #default="{ row }">
          {{ row.appointment_time || '-' }}
        </template>
      </el-table-column>

      <el-table-column label="金额" width="100">
        <template #default="{ row }">
          ¥{{ formatPrice(row.total_price) }}
        </template>
      </el-table-column>

      <el-table-column label="备注" min-width="160">
        <template #default="{ row }">
          {{ row.remark || '-' }}
        </template>
      </el-table-column>

      <el-table-column label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="statusType(row.status)">
            {{ statusText(row.status) }}
          </el-tag>
        </template>
      </el-table-column>

      <el-table-column label="操作" width="180">
        <template #default="{ row }">
          <el-button
            v-if="row.status === 'pending'"
            size="small"
            type="primary"
            @click="confirmBooking(row)"
          >
            确认
          </el-button>

          <el-button
            v-if="row.status === 'confirmed'"
            size="small"
            type="success"
            @click="finishBooking(row)"
          >
            完成
          </el-button>

          <el-button
            v-if="row.status === 'pending' || row.status === 'confirmed'"
            size="small"
            type="danger"
            @click="cancelBooking(row)"
          >
            取消
          </el-button>
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
      style="margin-top:16px;justify-content:center;display:flex"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { bookingsApi } from '@/api'

const bookings = ref([])
const total = ref(0)
const page = ref(1)
const loading = ref(false)
const statusFilter = ref('pending')

const userCache = new Map()

function unwrapResponse(res) {
  return res?.data ?? res
}

function getToken() {
  const directToken =
    localStorage.getItem('token') ||
    localStorage.getItem('access_token') ||
    localStorage.getItem('jwt') ||
    sessionStorage.getItem('token') ||
    sessionStorage.getItem('access_token') ||
    sessionStorage.getItem('jwt')

  if (directToken) {
    return directToken
  }

  try {
    const user = JSON.parse(localStorage.getItem('user') || '{}')
    return user.token || user.access_token || ''
  } catch {
    return ''
  }
}

async function getUserById(userId) {
  if (!userId) return null

  if (userCache.has(userId)) {
    return userCache.get(userId)
  }

  try {
    const token = getToken()

    const res = await fetch(`/api/users/${userId}`, {
      method: 'GET',
      headers: {
        Authorization: token ? `Bearer ${token}` : ''
      }
    })

    if (!res.ok) {
      throw new Error(`HTTP ${res.status}`)
    }

    const data = await res.json()
    const user = data?.data ?? data?.user ?? data

    userCache.set(userId, user)
    return user
  } catch (e) {
    console.error('获取预约用户信息失败:', userId, e)
    userCache.set(userId, null)
    return null
  }
}

function buildAppointmentTime(slotDate, slotTime, startTime, endTime) {
  const date = slotDate || ''
  const time =
    slotTime ||
    (startTime && endTime ? `${startTime}-${endTime}` : '') ||
    startTime ||
    ''

  return `${date} ${time}`.trim()
}

function normalizeBooking(raw) {
  const service = raw.service || {}
  const slot = raw.slot || {}

  const status =
    raw.status ||
    raw.booking_status ||
    'pending'

  const serviceName =
    raw.service_name ||
    service.service_name ||
    service.name ||
    '-'

  const slotDate =
    raw.slot_date ||
    slot.slot_date ||
    ''

  const slotTime =
    raw.slot_time ||
    slot.slot_time ||
    ''

  const startTime =
    raw.start_time ||
    slot.start_time ||
    ''

  const endTime =
    raw.end_time ||
    slot.end_time ||
    ''

  const totalPrice =
    raw.total_price ??
    raw.total_amount ??
    raw.price ??
    service.price ??
    0

  const user = raw.user || raw.customer || raw.applicant || null

  return {
    ...raw,

    service,
    slot,

    status,
    booking_status: raw.booking_status || status,

    service_name: serviceName,

    user,
    user_name:
      raw.user_name ||
      user?.nickname ||
      user?.username ||
      (raw.user_id ? `用户${raw.user_id}` : '-'),

    slot_date: slotDate,
    slot_time: slotTime,
    start_time: startTime,
    end_time: endTime,

    appointment_time: buildAppointmentTime(
      slotDate,
      slotTime,
      startTime,
      endTime
    ),

    total_price: totalPrice,

    pet_name: raw.pet_name || '',
    pet_breed: raw.pet_breed || '',
    remark: raw.remark || ''
  }
}

async function enrichUsers(normalizedBookings) {
  const userIds = [
    ...new Set(
      normalizedBookings
        .filter(item => !item.user && item.user_id)
        .map(item => item.user_id)
    )
  ]

  if (userIds.length === 0) {
    return normalizedBookings
  }

  const pairs = await Promise.all(
    userIds.map(async userId => {
      const user = await getUserById(userId)
      return [userId, user]
    })
  )

  const userMap = Object.fromEntries(pairs)

  return normalizedBookings.map(item => {
    const user = item.user || userMap[item.user_id] || null

    return {
      ...item,
      user,
      user_name:
        user?.nickname ||
        user?.username ||
        item.user_name ||
        (item.user_id ? `用户${item.user_id}` : '-')
    }
  })
}

async function load() {
  loading.value = true

  try {
    const res = await bookingsApi.publisherList({
      page: page.value,
      per_page: 10,
      status: statusFilter.value
    })

    const data = unwrapResponse(res)
    const rawItems = data.items || []

    const normalized = rawItems.map(normalizeBooking)
    bookings.value = await enrichUsers(normalized)

    total.value = data.total || 0
  } finally {
    loading.value = false
  }
}

function handleFilterChange() {
  page.value = 1
  load()
}

async function confirmBooking(row) {
  await bookingsApi.confirm(row.booking_id)
  ElMessage.success('已确认')
  load()
}

async function finishBooking(row) {
  await bookingsApi.finish(row.booking_id)
  ElMessage.success('已完成')
  load()
}

async function cancelBooking(row) {
  await bookingsApi.cancel(row.booking_id)
  ElMessage.success('已取消')
  load()
}

function statusText(status) {
  const map = {
    pending: '待确认',
    confirmed: '已确认',
    finished: '已完成',
    cancelled: '已取消'
  }

  return map[status] || status || '-'
}

function statusType(status) {
  const map = {
    pending: 'warning',
    confirmed: 'primary',
    finished: 'success',
    cancelled: 'danger'
  }

  return map[status] || 'info'
}

function formatPrice(price) {
  const n = Number(price || 0)
  return n.toFixed(2)
}

onMounted(load)
</script>

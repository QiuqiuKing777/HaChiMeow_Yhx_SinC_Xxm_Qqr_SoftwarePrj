<template>
  <div>
    <h2>订单管理</h2>

    <el-select
      v-model="deliveryFilter"
      placeholder="发货状态"
      clearable
      style="width:140px;margin-bottom:16px"
      @change="load"
    >
      <el-option label="待发货" value="pending" />
      <el-option label="已发货" value="shipped" />
      <el-option label="已完成" value="delivered" />
    </el-select>

    <el-table :data="orders" border v-loading="loading">
      <el-table-column label="订单号" prop="order_no" width="180" />

      <el-table-column label="购买人" width="120">
        <template #default="{ row }">
          {{ row.buyer_name || `用户${row.buyer_id}` }}
        </template>
      </el-table-column>

      <el-table-column label="金额" prop="total_amount" width="90">
        <template #default="{ row }">
          ¥{{ row.total_amount }}
        </template>
      </el-table-column>

      <el-table-column label="支付状态" width="100">
        <template #default="{ row }">
          <el-tag :type="payStatusType(row.pay_status)">
            {{ payStatusText(row.pay_status) }}
          </el-tag>
        </template>
      </el-table-column>

      <el-table-column label="发货状态" width="100">
        <template #default="{ row }">
          <el-tag :type="deliveryStatusType(row.delivery_status)">
            {{ deliveryStatusText(row.delivery_status) }}
          </el-tag>
        </template>
      </el-table-column>

      <el-table-column label="下单时间" prop="created_at" width="160" />

      <el-table-column label="操作" width="100">
        <template #default="{ row }">
          <el-button
            v-if="row.pay_status === 'paid' && row.delivery_status === 'pending'"
            size="small"
            type="primary"
            @click="ship(row)"
          >
            发货
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
import { ordersApi } from '@/api'

const orders = ref([])
const total = ref(0)
const page = ref(1)
const loading = ref(false)
const deliveryFilter = ref('')

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
    const userStore = JSON.parse(localStorage.getItem('user') || '{}')
    return userStore.token || userStore.access_token || ''
  } catch {
    return ''
  }
}

async function getBuyerById(buyerId) {
  if (!buyerId) return null

  if (userCache.has(buyerId)) {
    return userCache.get(buyerId)
  }

  try {
    const token = getToken()

    const res = await fetch(`/api/users/${buyerId}`, {
      method: 'GET',
      headers: {
        Authorization: token ? `Bearer ${token}` : ''
      }
    })

    if (!res.ok) {
      throw new Error(`HTTP ${res.status}`)
    }

    const user = await res.json()

    userCache.set(buyerId, user)
    return user
  } catch (e) {
    console.error('获取购买人信息失败:', buyerId, e)
    userCache.set(buyerId, null)
    return null
  }
}


async function enrichOrdersBuyer(rawOrders) {
  const buyerIds = [
    ...new Set(
      rawOrders
        .map(order => order.buyer_id)
        .filter(Boolean)
    )
  ]

  const buyerPairs = await Promise.all(
    buyerIds.map(async buyerId => {
      const buyer = await getBuyerById(buyerId)
      return [buyerId, buyer]
    })
  )

  const buyerMap = Object.fromEntries(buyerPairs)

  return rawOrders.map(order => {
    const buyer = buyerMap[order.buyer_id]

    return {
      ...order,
      buyer,
      buyer_name: buyer?.username || buyer?.nickname || `用户${order.buyer_id}`
    }
  })
}

async function load() {
  loading.value = true

  try {
    const res = await ordersApi.publisherList({
      page: page.value,
      per_page: 10,
      delivery_status: deliveryFilter.value
    })

    const data = unwrapResponse(res)
    const rawOrders = data.items || []

    orders.value = await enrichOrdersBuyer(rawOrders)
    total.value = data.total || 0
  } finally {
    loading.value = false
  }
}

async function ship(row) {
  await ordersApi.ship(row.order_id)
  ElMessage.success('已发货')
  load()
}

function payStatusText(status) {
  const map = {
    pending: '待支付',
    paid: '已支付',
    refunded: '已退款',
    cancelled: '已取消'
  }

  return map[status] || status
}

function payStatusType(status) {
  const map = {
    pending: 'warning',
    paid: 'success',
    refunded: 'info',
    cancelled: 'danger'
  }

  return map[status] || 'info'
}

function deliveryStatusText(status) {
  const map = {
    pending: '待发货',
    shipped: '已发货',
    delivered: '已完成'
  }

  return map[status] || status
}

function deliveryStatusType(status) {
  const map = {
    pending: 'info',
    shipped: 'primary',
    delivered: 'success'
  }

  return map[status] || 'info'
}

onMounted(load)
</script>

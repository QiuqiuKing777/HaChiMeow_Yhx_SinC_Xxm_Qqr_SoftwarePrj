<template>
  <NavBar>
    <h2>我的订单</h2>
    <el-tabs v-model="activeTab" @tab-change="loadOrders">
      <el-tab-pane label="全部" name="" />
      <el-tab-pane label="待付款" name="pending" />
      <el-tab-pane label="已付款" name="paid" />
      <el-tab-pane label="已取消" name="cancelled" />
    </el-tabs>

    <div v-loading="loading">
      <el-empty v-if="!loading && orders.length === 0" description="暂无订单" />
      <div v-for="order in orders" :key="order.order_id" class="order-card">
        <div class="order-header">
          <span class="order-no">订单编号：{{ order.order_no }}</span>
          <el-tag :type="statusType(order.pay_status)">{{ statusLabel(order.pay_status) }}</el-tag>
        </div>
        <div v-for="item in order.items" :key="item.item_id" class="order-item">
          <img :src="item.image_url || '/placeholder.jpg'" class="item-img" />
          <div class="item-info">
            <div class="item-name">{{ item.product_name }}</div>
            <div class="item-price">¥{{ item.price }} × {{ item.quantity }}</div>
          </div>
        </div>
        <div class="order-footer">
          <span>实付：<strong class="price">¥{{ order.total_amount }}</strong></span>
          <div class="order-actions">
            <el-button v-if="order.pay_status === 'pending'" type="primary" size="small" @click="payOrder(order)">立即付款</el-button>
            <el-button v-if="order.pay_status === 'pending'" size="small" @click="cancelOrder(order)">取消订单</el-button>
            <el-button v-if="order.delivery_status === 'shipped'" type="success" size="small" @click="receiveOrder(order)">确认收货</el-button>
          </div>
        </div>
      </div>
      <el-pagination v-if="total > 0" background layout="prev,pager,next,total"
        :total="total" :page-size="10" v-model:current-page="page"
        @current-change="loadOrders" style="margin-top:20px;justify-content:center;display:flex" />
    </div>
  </NavBar>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import NavBar from '@/components/NavBar.vue'
import { ordersApi } from '@/api'

const orders    = ref([])
const total     = ref(0)
const page      = ref(1)
const loading   = ref(false)
const activeTab = ref('')

const statusLabel = s => ({ pending:'待付款', paid:'已付款', refunded:'已退款', cancelled:'已取消' })[s] || s
const statusType  = s => ({ pending:'warning', paid:'success', refunded:'info', cancelled:'danger' })[s] || ''

async function loadOrders() {
  loading.value = true
  try {
    const res = await ordersApi.myList({ page: page.value, per_page: 10, pay_status: activeTab.value })
    orders.value = res.items || []
    total.value  = res.total || 0
  } catch {} finally {
    loading.value = false
  }
}

async function payOrder(order) {
  await ordersApi.pay(order.order_id)
  ElMessage.success('支付成功（模拟）')
  loadOrders()
}

async function cancelOrder(order) {
  await ordersApi.cancel(order.order_id)
  ElMessage.success('订单已取消')
  loadOrders()
}

async function receiveOrder(order) {
  await ordersApi.receive(order.order_id)
  ElMessage.success('确认收货成功')
  loadOrders()
}

onMounted(loadOrders)
</script>

<style scoped>
.order-card { background: #fff; border: 1px solid #e8e8e8; border-radius: 8px; margin-bottom: 16px; overflow: hidden; }
.order-header { display: flex; justify-content: space-between; align-items: center; padding: 12px 16px; background: #f9f9f9; border-bottom: 1px solid #e8e8e8; }
.order-no { font-size: 13px; color: #909399; }
.order-item { display: flex; gap: 12px; padding: 12px 16px; border-bottom: 1px solid #f0f0f0; }
.item-img { width: 60px; height: 60px; object-fit: cover; border-radius: 6px; }
.item-info { flex: 1; }
.item-name { font-size: 14px; color: #303133; }
.item-price { font-size: 13px; color: #909399; margin-top: 4px; }
.order-footer { display: flex; justify-content: space-between; align-items: center; padding: 12px 16px; }
.price { color: #f56c6c; font-size: 18px; }
.order-actions { display: flex; gap: 8px; }
</style>

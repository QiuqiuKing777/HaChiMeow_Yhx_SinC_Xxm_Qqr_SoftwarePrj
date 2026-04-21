<template>
  <NavBar>
    <h2>订单管理</h2>
    <el-select v-model="deliveryFilter" placeholder="发货状态" clearable style="width:140px;margin-bottom:16px" @change="load">
      <el-option label="待发货" value="unshipped" />
      <el-option label="已发货" value="shipped" />
      <el-option label="已完成" value="completed" />
    </el-select>
    <el-table :data="orders" border v-loading="loading">
      <el-table-column label="订单号" prop="order_no" width="180" />
      <el-table-column label="购买人" prop="buyer_name" width="100" />
      <el-table-column label="金额" prop="total_amount" width="90">
        <template #default="{ row }">¥{{ row.total_amount }}</template>
      </el-table-column>
      <el-table-column label="支付状态" width="100">
        <template #default="{ row }">
          <el-tag :type="{ pending:'warning', paid:'success', cancelled:'danger' }[row.pay_status]">{{ row.pay_status }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="发货状态" width="100">
        <template #default="{ row }">
          <el-tag :type="{ unshipped:'info', shipped:'primary', completed:'success' }[row.delivery_status]">{{ row.delivery_status }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="下单时间" prop="created_at" width="160" />
      <el-table-column label="操作" width="100">
        <template #default="{ row }">
          <el-button v-if="row.pay_status === 'paid' && row.delivery_status === 'unshipped'"
            size="small" type="primary" @click="ship(row)">发货</el-button>
        </template>
      </el-table-column>
    </el-table>
    <el-pagination v-if="total > 0" background layout="prev,pager,next,total"
      :total="total" :page-size="10" v-model:current-page="page"
      @current-change="load" style="margin-top:16px;justify-content:center;display:flex" />
  </NavBar>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import NavBar from '@/components/NavBar.vue'
import { ordersApi } from '@/api'

const orders         = ref([])
const total          = ref(0)
const page           = ref(1)
const loading        = ref(false)
const deliveryFilter = ref('')

async function load() {
  loading.value = true
  try {
    const res = await ordersApi.publisherList({ page: page.value, per_page: 10, delivery_status: deliveryFilter.value })
    orders.value = res.items || []
    total.value  = res.total || 0
  } finally { loading.value = false }
}

async function ship(row) {
  await ordersApi.ship(row.order_id)
  ElMessage.success('已发货')
  load()
}

onMounted(load)
</script>

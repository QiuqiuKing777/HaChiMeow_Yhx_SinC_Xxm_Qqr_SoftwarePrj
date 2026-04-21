<template>
  <NavBar>
    <h2>发布方工作台</h2>
    <el-row :gutter="20" style="margin-bottom:24px">
      <el-col :span="6" v-for="card in statCards" :key="card.label">
        <el-card shadow="hover">
          <div class="stat-card">
            <div class="stat-num">{{ card.value }}</div>
            <div class="stat-label">{{ card.label }}</div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20">
      <el-col :span="12">
        <el-card>
          <template #header>待处理领养申请</template>
          <el-table :data="pendingApps" border size="small" max-height="260">
            <el-table-column label="宠物" prop="pet_name" />
            <el-table-column label="申请人" prop="applicant_name" />
            <el-table-column label="时间" prop="created_at" width="140" />
            <el-table-column label="操作" width="80">
              <template #default>
                <el-button size="small" @click="$router.push('/publisher/applications')">审核</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card>
          <template #header>待发货订单</template>
          <el-table :data="pendingOrders" border size="small" max-height="260">
            <el-table-column label="订单号" prop="order_no" />
            <el-table-column label="金额" prop="total_amount" width="80">
              <template #default="{ row }">¥{{ row.total_amount }}</template>
            </el-table-column>
            <el-table-column label="操作" width="80">
              <template #default>
                <el-button size="small" @click="$router.push('/publisher/orders')">处理</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>
  </NavBar>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import NavBar from '@/components/NavBar.vue'
import { petsApi, adoptionsApi, ordersApi, productsApi } from '@/api'

const statCards   = ref([
  { label: '我的宠物', value: 0 },
  { label: '我的商品', value: 0 },
  { label: '待审核申请', value: 0 },
  { label: '待发货订单', value: 0 }
])
const pendingApps   = ref([])
const pendingOrders = ref([])

onMounted(async () => {
  const [myPets, myProducts, apps, orders] = await Promise.allSettled([
    petsApi.myList(),
    productsApi.myList(),
    adoptionsApi.publisherList({ status: 'pending', per_page: 5 }),
    ordersApi.publisherList({ delivery_status: 'unshipped', per_page: 5 })
  ])
  if (myPets.status === 'fulfilled')    statCards.value[0].value = myPets.value.total || 0
  if (myProducts.status === 'fulfilled') statCards.value[1].value = myProducts.value.total || 0
  if (apps.status === 'fulfilled')      { statCards.value[2].value = apps.value.total || 0; pendingApps.value = apps.value.items || [] }
  if (orders.status === 'fulfilled')    { statCards.value[3].value = orders.value.total || 0; pendingOrders.value = orders.value.items || [] }
})
</script>

<style scoped>
.stat-card { text-align: center; padding: 8px 0; }
.stat-num { font-size: 32px; font-weight: 700; color: #409eff; }
.stat-label { color: #909399; font-size: 14px; margin-top: 4px; }
</style>

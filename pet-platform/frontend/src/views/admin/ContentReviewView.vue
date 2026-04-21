<template>
  <div>
    <div class="page-header">
      <h2>内容审核</h2>
    </div>

    <el-card>
      <el-tabs v-model="activeTab" @tab-change="onTabChange">
        <!-- 宠物审核 -->
        <el-tab-pane label="宠物审核" name="pets">
          <el-row :gutter="12" style="margin-bottom:16px">
            <el-col :span="5">
              <el-input v-model="pets.keyword" placeholder="搜索宠物名称" clearable @change="loadPets" />
            </el-col>
            <el-col :span="4">
              <el-select v-model="pets.status" placeholder="状态" clearable @change="loadPets">
                <el-option label="待审核" value="pending" />
                <el-option label="已上线" value="available" />
                <el-option label="已下线" value="offline" />
              </el-select>
            </el-col>
            <el-col :span="4"><el-button type="primary" @click="loadPets">搜索</el-button></el-col>
          </el-row>

          <el-table :data="pets.list" v-loading="pets.loading" stripe>
            <el-table-column prop="pet_id" label="ID" width="70" />
            <el-table-column label="头像" width="70">
              <template #default="{ row }">
                <el-avatar :size="40" :src="row.cover_image" shape="square">宠</el-avatar>
              </template>
            </el-table-column>
            <el-table-column prop="name" label="名称" width="120" />
            <el-table-column prop="species" label="种类" width="80" />
            <el-table-column prop="age" label="年龄" width="80" />
            <el-table-column label="发布方" width="120">
              <template #default="{ row }">{{ row.publisher?.nickname }}</template>
            </el-table-column>
            <el-table-column label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="statusType(row.status)">{{ petStatusLabel(row.status) }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="created_at" label="发布时间" width="120">
              <template #default="{ row }">{{ row.created_at?.substring(0,10) }}</template>
            </el-table-column>
            <el-table-column label="操作" fixed="right" width="180">
              <template #default="{ row }">
                <el-button
                  v-if="row.status !== 'available'"
                  type="success" size="small"
                  @click="setPetStatus(row, 'available')"
                >上线</el-button>
                <el-button
                  v-if="row.status === 'available'"
                  type="danger" size="small"
                  @click="setPetStatus(row, 'offline')"
                >下线</el-button>
              </template>
            </el-table-column>
          </el-table>
          <el-pagination
            background layout="prev,pager,next,total" :total="pets.total"
            :page-size="15" v-model:current-page="pets.page"
            @current-change="loadPets" style="margin-top:16px;display:flex;justify-content:flex-end"
          />
        </el-tab-pane>

        <!-- 商品审核 -->
        <el-tab-pane label="商品审核" name="products">
          <el-row :gutter="12" style="margin-bottom:16px">
            <el-col :span="5">
              <el-input v-model="products.keyword" placeholder="搜索商品名称" clearable @change="loadProducts" />
            </el-col>
            <el-col :span="4">
              <el-select v-model="products.status" placeholder="状态" clearable @change="loadProducts">
                <el-option label="上架" value="on_sale" />
                <el-option label="下架" value="off_sale" />
              </el-select>
            </el-col>
            <el-col :span="4"><el-button type="primary" @click="loadProducts">搜索</el-button></el-col>
          </el-row>

          <el-table :data="products.list" v-loading="products.loading" stripe>
            <el-table-column prop="product_id" label="ID" width="70" />
            <el-table-column label="图片" width="70">
              <template #default="{ row }">
                <el-avatar :size="40" :src="row.cover_image" shape="square">品</el-avatar>
              </template>
            </el-table-column>
            <el-table-column prop="name" label="商品名称" min-width="150" />
            <el-table-column prop="category" label="分类" width="100" />
            <el-table-column label="价格" width="100">
              <template #default="{ row }">¥{{ row.price }}</template>
            </el-table-column>
            <el-table-column prop="stock" label="库存" width="80" />
            <el-table-column label="发布方" width="120">
              <template #default="{ row }">{{ row.publisher?.nickname }}</template>
            </el-table-column>
            <el-table-column label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="row.status === 'on_sale' ? 'success' : 'info'">
                  {{ row.status === 'on_sale' ? '上架' : '下架' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" fixed="right" width="140">
              <template #default="{ row }">
                <el-button
                  v-if="row.status !== 'on_sale'"
                  type="success" size="small"
                  @click="setProductStatus(row, 'on_sale')"
                >上架</el-button>
                <el-button
                  v-if="row.status === 'on_sale'"
                  type="danger" size="small"
                  @click="setProductStatus(row, 'off_sale')"
                >下架</el-button>
              </template>
            </el-table-column>
          </el-table>
          <el-pagination
            background layout="prev,pager,next,total" :total="products.total"
            :page-size="15" v-model:current-page="products.page"
            @current-change="loadProducts" style="margin-top:16px;display:flex;justify-content:flex-end"
          />
        </el-tab-pane>

        <!-- 服务审核 -->
        <el-tab-pane label="服务审核" name="services">
          <el-row :gutter="12" style="margin-bottom:16px">
            <el-col :span="5">
              <el-input v-model="services.keyword" placeholder="搜索服务名称" clearable @change="loadServices" />
            </el-col>
            <el-col :span="4">
              <el-select v-model="services.status" placeholder="状态" clearable @change="loadServices">
                <el-option label="上线" value="active" />
                <el-option label="下线" value="inactive" />
              </el-select>
            </el-col>
            <el-col :span="4"><el-button type="primary" @click="loadServices">搜索</el-button></el-col>
          </el-row>

          <el-table :data="services.list" v-loading="services.loading" stripe>
            <el-table-column prop="service_id" label="ID" width="70" />
            <el-table-column prop="name" label="服务名称" min-width="150" />
            <el-table-column prop="category" label="分类" width="100" />
            <el-table-column label="价格" width="100">
              <template #default="{ row }">¥{{ row.price }}</template>
            </el-table-column>
            <el-table-column label="提供方" width="120">
              <template #default="{ row }">{{ row.publisher?.nickname }}</template>
            </el-table-column>
            <el-table-column label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="row.status === 'active' ? 'success' : 'info'">
                  {{ row.status === 'active' ? '上线' : '下线' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" fixed="right" width="160">
              <template #default="{ row }">
                <el-button
                  v-if="row.status !== 'active'"
                  type="success" size="small"
                  @click="setServiceStatus(row, 'active')"
                >上线</el-button>
                <el-button
                  v-if="row.status === 'active'"
                  type="danger" size="small"
                  @click="setServiceStatus(row, 'inactive')"
                >下线</el-button>
              </template>
            </el-table-column>
          </el-table>
          <el-pagination
            background layout="prev,pager,next,total" :total="services.total"
            :page-size="15" v-model:current-page="services.page"
            @current-change="loadServices" style="margin-top:16px;display:flex;justify-content:flex-end"
          />
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { adminApi } from '@/api'

const route = useRoute()
const activeTab = ref(route.query.tab || 'pets')

/* ---- pets ---- */
const pets = reactive({ list: [], total: 0, page: 1, loading: false, keyword: '', status: '' })
async function loadPets() {
  pets.loading = true
  try {
    const res = await adminApi.pets({ page: pets.page, per_page: 15, keyword: pets.keyword, status: pets.status })
    pets.list = res.items || []; pets.total = res.total || 0
  } finally { pets.loading = false }
}
async function setPetStatus(row, status) {
  const label = status === 'available' ? '上线' : '下线'
  await ElMessageBox.confirm(`确认要${label}宠物「${row.name}」吗？`, '操作确认', { type: 'warning' })
  await adminApi.setPetStatus(row.pet_id, { status })
  ElMessage.success(`已${label}`)
  loadPets()
}

/* ---- products ---- */
const products = reactive({ list: [], total: 0, page: 1, loading: false, keyword: '', status: '' })
async function loadProducts() {
  products.loading = true
  try {
    const res = await adminApi.products({ page: products.page, per_page: 15, keyword: products.keyword, status: products.status })
    products.list = res.items || []; products.total = res.total || 0
  } finally { products.loading = false }
}
async function setProductStatus(row, status) {
  const label = status === 'on_sale' ? '上架' : '下架'
  await ElMessageBox.confirm(`确认要${label}商品「${row.name}」吗？`, '操作确认', { type: 'warning' })
  await adminApi.setProductStatus(row.product_id, { status })
  ElMessage.success(`已${label}`)
  loadProducts()
}

/* ---- services ---- */
const services = reactive({ list: [], total: 0, page: 1, loading: false, keyword: '', status: '' })
async function loadServices() {
  services.loading = true
  try {
    const res = await adminApi.services({ page: services.page, per_page: 15, keyword: services.keyword, status: services.status })
    services.list = res.items || []; services.total = res.total || 0
  } finally { services.loading = false }
}
async function setServiceStatus(row, status) {
  const label = status === 'active' ? '上线' : '下线'
  await ElMessageBox.confirm(`确认要${label}服务「${row.name}」吗？`, '操作确认', { type: 'warning' })
  await adminApi.setServiceStatus(row.service_id, { status })
  ElMessage.success(`已${label}`)
  loadServices()
}

function onTabChange(tab) {
  if (tab === 'pets' && !pets.list.length) loadPets()
  if (tab === 'products' && !products.list.length) loadProducts()
  if (tab === 'services' && !services.list.length) loadServices()
}

const statusType = s => ({ available: 'success', pending: 'warning', offline: 'info', adopted: '' })[s] || ''
const petStatusLabel = s => ({ available: '可领养', pending: '待审核', offline: '已下线', adopted: '已领养' })[s] || s

onMounted(() => {
  if (activeTab.value === 'pets') loadPets()
  else if (activeTab.value === 'products') loadProducts()
  else if (activeTab.value === 'services') loadServices()
  else loadPets()
})
</script>

<style scoped>
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.page-header h2 { margin: 0; }
</style>

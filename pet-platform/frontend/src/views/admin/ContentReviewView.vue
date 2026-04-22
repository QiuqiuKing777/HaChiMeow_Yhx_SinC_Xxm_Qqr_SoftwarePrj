<template>
  <div class="admin-page">
    <!-- 页面横幅 -->
    <div class="page-banner">
      <div>
        <h2 class="page-banner-title">内容审核</h2>
        <p class="page-banner-sub">审核平台发布的宠物、商品和服务，管理上下线状态</p>
      </div>
    </div>

    <div class="page-card">
      <el-tabs v-model="activeTab" @tab-change="onTabChange" class="admin-tabs">
        <!-- 宠物审核 -->
        <el-tab-pane label="🐾 宠物审核" name="pets">
          <div class="filter-bar">
            <el-input v-model="pets.keyword" placeholder="搜索宠物名称" clearable @change="loadPets" style="width:200px" />
            <el-select v-model="pets.status" placeholder="状态筛选" clearable @change="loadPets" style="width:140px">
              <el-option label="待审核" value="pending" />
              <el-option label="已上线" value="available" />
              <el-option label="已下线" value="offline" />
            </el-select>
            <el-button type="primary" @click="loadPets">搜索</el-button>
          </div>

          <el-table :data="pets.list" v-loading="pets.loading" stripe class="admin-table" style="width:100%">
            <el-table-column prop="pet_id" label="ID" width="70" />
            <el-table-column label="头像" width="70">
              <template #default="{ row }">
                <el-avatar :size="40" :src="row.cover_image" shape="square" style="background:#e6a23c">宠</el-avatar>
              </template>
            </el-table-column>
            <el-table-column prop="name" label="名称" min-width="150" />
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
                <el-button v-if="row.status !== 'available'" type="success" size="small" @click="setPetStatus(row, 'available')">上线</el-button>
                <el-button v-if="row.status === 'available'" type="danger" size="small" @click="setPetStatus(row, 'offline')">下线</el-button>
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
        <el-tab-pane label="🛒 商品审核" name="products">
          <div class="filter-bar">
            <el-input v-model="products.keyword" placeholder="搜索商品名称" clearable @change="loadProducts" style="width:200px" />
            <el-select v-model="products.status" placeholder="状态筛选" clearable @change="loadProducts" style="width:140px">
              <el-option label="上架" value="on_sale" />
              <el-option label="下架" value="off_sale" />
            </el-select>
            <el-button type="primary" @click="loadProducts">搜索</el-button>
          </div>

          <el-table :data="products.list" v-loading="products.loading" stripe class="admin-table" style="width:100%;font-size:16px">
            <el-table-column prop="product_id" label="ID" width="70" />
            <el-table-column label="图片" width="70">
              <template #default="{ row }">
                <el-avatar :size="40" :src="row.cover_image" shape="square" style="background:#67c23a">品</el-avatar>
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
                <el-button v-if="row.status !== 'on_sale'" type="success" size="small" @click="setProductStatus(row, 'on_sale')">上架</el-button>
                <el-button v-if="row.status === 'on_sale'" type="danger" size="small" @click="setProductStatus(row, 'off_sale')">下架</el-button>
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
        <el-tab-pane label="📋 服务审核" name="services">
          <div class="filter-bar">
            <el-input v-model="services.keyword" placeholder="搜索服务名称" clearable @change="loadServices" style="width:200px" />
            <el-select v-model="services.status" placeholder="状态筛选" clearable @change="loadServices" style="width:140px">
              <el-option label="上线" value="active" />
              <el-option label="下线" value="inactive" />
            </el-select>
            <el-button type="primary" @click="loadServices">搜索</el-button>
          </div>

          <el-table :data="services.list" v-loading="services.loading" stripe class="admin-table" style="width:100%;font-size:16px">
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
                <el-button v-if="row.status !== 'active'" type="success" size="small" @click="setServiceStatus(row, 'active')">上线</el-button>
                <el-button v-if="row.status === 'active'" type="danger" size="small" @click="setServiceStatus(row, 'inactive')">下线</el-button>
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
    </div>
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

.page-card {
  background: #fff;
  border-radius: 10px;
  padding: 18px 20px;
  box-shadow: 0 1px 6px rgba(0,21,41,.06);
}

.filter-bar {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 14px;
  padding: 12px 0 4px;
}

.admin-tabs :deep(.el-tabs__header) { margin-bottom: 0; }
.admin-tabs :deep(.el-tabs__nav-wrap::after) { height: 1px; background: #f0f2f5; }
.admin-tabs :deep(.el-tabs__item) { font-size: 14px; font-weight: 500; }
.admin-tabs :deep(.el-tabs__item.is-active) { font-weight: 600; color: #409eff; }

.admin-table :deep(th.el-table__cell) {
  background: #f5f7fa;
  color: #606266;
  font-weight: 600;
  font-size: 16px !important;
}
.admin-table :deep(td.el-table__cell) {
  font-size: 16px !important;
}
</style>

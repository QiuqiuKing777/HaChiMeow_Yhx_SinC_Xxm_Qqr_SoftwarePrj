<template>
  <NavBar>
    <div class="page-header">
      <h2>宠物服务</h2>
      <el-form :inline="true" :model="query" @submit.prevent="doSearch">
        <el-form-item>
          <el-input v-model="query.keyword" placeholder="搜索服务名称" clearable />
        </el-form-item>
        <el-form-item>
          <el-select v-model="query.category" placeholder="服务类别" clearable style="width:140px">
            <el-option label="美容" value="美容" />
            <el-option label="医疗" value="医疗" />
            <el-option label="上门" value="上门" />
            <el-option label="洗护" value="洗护" />
            <el-option label="寄养" value="寄养" />
            <el-option label="其他" value="其他" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="doSearch">搜索</el-button>
        </el-form-item>
      </el-form>
    </div>

    <div v-loading="loading">
      <el-empty v-if="!loading && services.length === 0" description="暂无服务" />

      <el-row :gutter="16">
        <el-col
          v-for="svc in services"
          :key="svc.service_id"
          :xs="24"
          :sm="12"
          :md="8"
          :lg="6"
        >
          <el-card
            :body-style="{ padding: '0' }"
            class="svc-card"
            @click="$router.push('/services/' + svc.service_id)"
          >
            <img
              :src="getServiceImage(svc)"
              class="svc-img"
              @error="handleImgError"
            />
            <div class="svc-info">
              <div class="svc-name">{{ svc.service_name }}</div>
              <div class="svc-type">{{ svc.category || svc.service_type || '其他' }}</div>
              <div class="svc-price">¥{{ svc.price }}</div>
            </div>
          </el-card>
        </el-col>
      </el-row>

      <el-pagination
        v-if="total > 0"
        background
        layout="prev,pager,next,total"
        :total="total"
        :page-size="query.per_page"
        v-model:current-page="query.page"
        @current-change="loadServices"
        style="margin-top:24px;justify-content:center;display:flex"
      />
    </div>
  </NavBar>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import NavBar from '@/components/NavBar.vue'
import { servicesApi } from '@/api'

const services = ref([])
const total = ref(0)
const loading = ref(false)

const query = reactive({
  keyword: '',
  category: '',
  page: 1,
  per_page: 12,
})

async function loadServices() {
  loading.value = true
  try {
    const res = await servicesApi.list({ ...query })
    services.value = res.items || []
    total.value = res.total || 0
  } finally {
    loading.value = false
  }
}

function doSearch() {
  query.page = 1
  loadServices()
}

function getServiceImage(svc) {
  return svc.cover_image || svc.image_url
}

function handleImgError(event) {
  event.target.src = '/NKU.png'
}

onMounted(loadServices)
</script>

<style scoped>
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  margin-bottom: 16px;
}

.svc-card {
  cursor: pointer;
  margin-bottom: 16px;
  transition: box-shadow .2s, transform .2s;
  border-radius: 10px;
  overflow: hidden;
}

.svc-card:hover {
  box-shadow: 0 4px 16px rgba(0,0,0,.12);
  transform: translateY(-2px);
}

.svc-img {
  width: 100%;
  height: 160px;
  object-fit: cover;
  display: block;
}

.svc-info {
  padding: 12px;
}

.svc-name {
  font-weight: 600;
  font-size: 15px;
  margin-bottom: 4px;
}

.svc-type {
  font-size: 12px;
  color: #909399;
  margin-bottom: 6px;
}

.svc-price {
  color: #f56c6c;
  font-size: 16px;
  font-weight: 600;
}
</style>

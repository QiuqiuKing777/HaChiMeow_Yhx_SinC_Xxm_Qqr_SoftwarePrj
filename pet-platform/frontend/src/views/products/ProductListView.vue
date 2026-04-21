<template>
  <NavBar>
    <el-card class="filter-card">
      <el-row :gutter="16" align="middle">
        <el-col :span="8">
          <el-input v-model="filters.keyword" placeholder="搜索商品名称" clearable @change="loadProducts" :prefix-icon="Search" />
        </el-col>
        <el-col :span="5">
          <el-select v-model="filters.category" placeholder="商品分类" clearable @change="loadProducts">
            <el-option v-for="c in categories" :key="c" :label="c" :value="c" />
          </el-select>
        </el-col>
        <el-col :span="4">
          <el-button type="primary" :icon="Search" @click="loadProducts">搜索</el-button>
          <el-button @click="resetFilters">重置</el-button>
        </el-col>
      </el-row>
    </el-card>

    <div v-loading="loading" style="margin-top:20px">
      <el-empty v-if="!loading && products.length === 0" description="暂无商品" />
      <el-row :gutter="16">
        <el-col :span="6" v-for="product in products" :key="product.product_id" style="margin-bottom:20px">
          <ProductCard :product="product" />
        </el-col>
      </el-row>
      <el-pagination v-if="total > 0" background layout="prev,pager,next,total"
        :total="total" :page-size="pageSize" v-model:current-page="page"
        @current-change="loadProducts" style="margin-top:20px;justify-content:center;display:flex" />
    </div>
  </NavBar>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { Search } from '@element-plus/icons-vue'
import NavBar from '@/components/NavBar.vue'
import ProductCard from '@/components/ProductCard.vue'
import { productsApi } from '@/api'

const products  = ref([])
const total     = ref(0)
const page      = ref(1)
const pageSize  = 12
const loading   = ref(false)
const filters   = reactive({ keyword: '', category: '' })
const categories = ['猫粮', '狗粮', '玩具', '零食', '出行', '日常用品', '清洁用品', '其他']

async function loadProducts() {
  loading.value = true
  try {
    const res = await productsApi.list({ page: page.value, per_page: pageSize, ...filters })
    products.value = res.items || []
    total.value    = res.total || 0
  } finally {
    loading.value = false
  }
}

function resetFilters() {
  Object.assign(filters, { keyword: '', category: '' })
  page.value = 1
  loadProducts()
}

onMounted(loadProducts)
</script>

<style scoped>
.filter-card { margin-bottom: 16px; }
</style>

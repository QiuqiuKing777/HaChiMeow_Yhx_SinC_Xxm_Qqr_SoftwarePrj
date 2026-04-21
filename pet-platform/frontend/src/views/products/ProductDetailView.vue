<template>
  <NavBar>
    <div v-loading="loading">
      <el-row :gutter="24" v-if="product">
        <el-col :span="10">
          <el-image :src="product.cover_image || '/placeholder.jpg'" fit="cover" style="width:100%;height:360px;border-radius:10px" />
        </el-col>
        <el-col :span="14">
          <h2 class="product-name">{{ product.product_name }}</h2>
          <el-tag type="info">{{ product.category || '其他' }}</el-tag>
          <div class="price-row">
            <span class="price">¥{{ product.price }}</span>
            <span class="sales">已售 {{ product.sales_count }} 件</span>
          </div>
          <div class="stock-info">库存：{{ product.stock }} 件</div>
          <div class="qty-row">
            <span>数量：</span>
            <el-input-number v-model="quantity" :min="1" :max="product.stock" />
          </div>
          <div class="actions">
            <el-button @click="addToCart">加入购物车</el-button>
            <el-button type="primary" @click="buyNow">立即购买</el-button>
            <el-button :icon="isFav ? StarFilled : Star" circle @click="toggleFav" />
          </div>
          <div class="description" v-if="product.description">
            <h4>商品描述</h4>
            <p>{{ product.description }}</p>
          </div>
        </el-col>
      </el-row>
    </div>
  </NavBar>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Star, StarFilled } from '@element-plus/icons-vue'
import NavBar from '@/components/NavBar.vue'
import { productsApi, cartApi, userApi } from '@/api'
import { useUserStore } from '@/stores/user'

const route     = useRoute()
const router    = useRouter()
const userStore = useUserStore()
const product   = ref(null)
const quantity  = ref(1)
const loading   = ref(false)
const isFav     = ref(false)

async function addToCart() {
  if (!userStore.isLoggedIn) return router.push('/login')
  try {
    await cartApi.add({ product_id: product.value.product_id, quantity: quantity.value })
    ElMessage.success('已加入购物车')
  } catch (e) {
    const msg = e.response?.data?.error || '加入购物车失败'
    ElMessage.error(msg)
  }
}

async function buyNow() {
  if (!userStore.isLoggedIn) return router.push('/login')
  try {
    await cartApi.add({ product_id: product.value.product_id, quantity: quantity.value })
    router.push('/cart')
  } catch (e) {
    const msg = e.response?.data?.error || '操作失败'
    ElMessage.error(msg)
  }
}

async function toggleFav() {
  if (!userStore.isLoggedIn) return router.push('/login')
  try {
    if (isFav.value) {
      await userApi.removeFavorite('product', product.value.product_id)
      isFav.value = false
      ElMessage.success('已取消收藏')
    } else {
      await userApi.addFavorite({ target_type: 'product', target_id: product.value.product_id })
      isFav.value = true
      ElMessage.success('收藏成功')
    }
  } catch {}
}

onMounted(async () => {
  loading.value = true
  try {
    product.value = await productsApi.get(route.params.id)
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.product-name { font-size: 22px; margin-bottom: 12px; }
.price-row { margin: 16px 0 8px; display: flex; align-items: baseline; gap: 12px; }
.price { font-size: 28px; color: #f56c6c; font-weight: 700; }
.sales { color: #c0c4cc; font-size: 14px; }
.stock-info { color: #909399; font-size: 14px; margin-bottom: 16px; }
.qty-row { display: flex; align-items: center; gap: 12px; margin-bottom: 20px; }
.actions { display: flex; gap: 12px; margin-bottom: 20px; }
.description h4 { margin-bottom: 8px; }
.description p { color: #606266; line-height: 1.8; }
</style>

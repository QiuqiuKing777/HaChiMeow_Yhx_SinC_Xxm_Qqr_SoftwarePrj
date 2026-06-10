```vue
<template>
  <NavBar>
    <div v-loading="loading">
      <div v-if="product" class="detail-wrap">
        <el-row :gutter="24">
          <!-- 左侧：商品图片 -->
          <el-col :span="10">
            <el-image
              :src="product.cover_image || '/NKU.png'"
              fit="cover"
              class="main-img"
            />

            <el-row
              v-if="product.images?.length"
              :gutter="8"
              class="image-list"
            >
              <el-col
                v-for="img in product.images"
                :key="img.image_id || img.image_url"
                :span="6"
              >
                <el-image
                  :src="img.image_url || '/NKU.png'"
                  fit="cover"
                  class="small-img"
                />
              </el-col>
            </el-row>
          </el-col>

          <!-- 右侧：商品信息 -->
          <el-col :span="14">
            <h2 class="product-name">
              {{ product.product_name }}
            </h2>

            <el-tag type="info">
              {{ product.category || '其他' }}
            </el-tag>

            <div class="price-row">
              <span class="price">¥{{ product.price }}</span>
              <span class="sales">
                已售 {{ product.sales_count || 0 }} 件
              </span>
            </div>

            <div class="stock-info">
              库存：{{ product.stock }} 件
            </div>

            <div class="qty-row">
              <span>数量：</span>

              <el-input-number
                v-model="quantity"
                :min="1"
                :max="Math.max(Number(product.stock || 0), 1)"
                :disabled="Number(product.stock || 0) <= 0"
              />
            </div>

            <div class="actions">
              <el-button
                :disabled="Number(product.stock || 0) <= 0"
                @click="addToCart"
              >
                加入购物车
              </el-button>

              <el-button
                type="primary"
                :disabled="Number(product.stock || 0) <= 0"
                @click="buyNow"
              >
                立即购买
              </el-button>

              <el-button
                :icon="isFav ? StarFilled : Star"
                circle
                @click="toggleFav"
              />
            </div>

            <div
              v-if="product.description"
              class="description"
            >
              <h4>商品描述</h4>
              <p>{{ product.description }}</p>
            </div>
          </el-col>
        </el-row>

        <!-- 商品评价 -->
        <div class="review-section">
          <h3>评价 ({{ reviews.length }})</h3>

          <el-empty
            v-if="reviews.length === 0"
            description="暂无评价"
          />

          <div
            v-for="review in reviews"
            :key="review.review_id"
            class="review-item"
          >
            <el-avatar :size="36">
              {{ getReviewerName(review).charAt(0) }}
            </el-avatar>

            <div class="review-content">
              <div class="review-user">
                {{ getReviewerName(review) }}
              </div>

              <el-rate
                :model-value="Number(review.rating || 0)"
                disabled
              />

              <div class="review-text">
                {{ review.content || '暂无评价内容' }}
              </div>

              <div class="review-time">
                {{ review.created_at?.substring(0, 10) }}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </NavBar>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Star, StarFilled } from '@element-plus/icons-vue'
import NavBar from '@/components/NavBar.vue'
import { productsApi, cartApi, userApi, complaintsApi } from '@/api'
import { useUserStore } from '@/stores/user'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const product = ref(null)
const reviews = ref([])
const quantity = ref(1)
const loading = ref(false)
const isFav = ref(false)

async function loadProduct() {
  loading.value = true

  try {
    const id = route.params.id

    product.value = await productsApi.get(id)

    const res = await complaintsApi.list({
      target_type: 'products',
      target_id: id
    })

    const list = Array.isArray(res)
      ? res
      : (res.items || [])

    reviews.value = list.map(item => ({
      review_id: item.review_id || item.complaint_id,
      reviewer: item.reviewer || item.user,
      rating: item.rating ?? item.score ?? 0,
      content: item.content,
      created_at: item.created_at
    }))
  } catch (e) {
    console.error(e)
    ElMessage.error(
      e?.response?.data?.error ||
      '商品详情或评价加载失败'
    )
  } finally {
    loading.value = false
  }
}

async function addToCart() {
  if (!userStore.isLoggedIn) {
    router.push('/login')
    return
  }

  if (!product.value || Number(product.value.stock || 0) <= 0) {
    ElMessage.warning('当前商品库存不足')
    return
  }

  try {
    await cartApi.add({
      product_id: product.value.product_id,
      quantity: quantity.value
    })

    ElMessage.success('已加入购物车')
  } catch (e) {
    ElMessage.error(
      e?.response?.data?.error ||
      '加入购物车失败'
    )
  }
}

async function buyNow() {
  if (!userStore.isLoggedIn) {
    router.push('/login')
    return
  }

  if (!product.value || Number(product.value.stock || 0) <= 0) {
    ElMessage.warning('当前商品库存不足')
    return
  }

  try {
    await cartApi.add({
      product_id: product.value.product_id,
      quantity: quantity.value
    })

    router.push('/cart')
  } catch (e) {
    ElMessage.error(
      e?.response?.data?.error ||
      '操作失败'
    )
  }
}

async function toggleFav() {
  if (!userStore.isLoggedIn) {
    router.push('/login')
    return
  }

  try {
    if (isFav.value) {
      await userApi.removeFavorite(
        'product',
        product.value.product_id
      )

      isFav.value = false
      ElMessage.success('已取消收藏')
    } else {
      await userApi.addFavorite({
        target_type: 'product',
        target_id: product.value.product_id
      })

      isFav.value = true
      ElMessage.success('收藏成功')
    }
  } catch (e) {
    ElMessage.error(
      e?.response?.data?.error ||
      '收藏操作失败'
    )
  }
}

function getReviewerName(review) {
  return (
    review.reviewer?.nickname ||
    review.reviewer?.username ||
    review.user?.nickname ||
    review.user?.username ||
    '匿名用户'
  )
}

onMounted(loadProduct)
</script>

<style scoped>
.detail-wrap {
  max-width: 960px;
  margin: 0 auto;
}

.main-img {
  width: 100%;
  height: 360px;
  border-radius: 10px;
}

.image-list {
  margin-top: 8px;
}

.small-img {
  width: 100%;
  height: 80px;
  border-radius: 6px;
}

.product-name {
  font-size: 22px;
  margin-bottom: 12px;
}

.price-row {
  margin: 16px 0 8px;
  display: flex;
  align-items: baseline;
  gap: 12px;
}

.price {
  font-size: 28px;
  color: #f56c6c;
  font-weight: 700;
}

.sales {
  color: #c0c4cc;
  font-size: 14px;
}

.stock-info {
  color: #909399;
  font-size: 14px;
  margin-bottom: 16px;
}

.qty-row {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 20px;
}

.actions {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
}

.description h4 {
  margin-bottom: 8px;
}

.description p {
  color: #606266;
  line-height: 1.8;
}

.review-section {
  margin-top: 32px;
}

.review-item {
  display: flex;
  gap: 12px;
  padding: 14px 0;
  border-bottom: 1px solid #ebeef5;
}

.review-content {
  flex: 1;
}

.review-user {
  font-weight: 600;
  color: #303133;
  margin-bottom: 4px;
}

.review-text {
  color: #606266;
  line-height: 1.7;
  margin-top: 6px;
}

.review-time {
  color: #c0c4cc;
  font-size: 12px;
  margin-top: 4px;
}
</style>
```

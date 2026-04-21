<template>
  <NavBar>
    <div v-loading="loading">
      <el-row :gutter="24" v-if="pet">
        <!-- 左：图片 -->
        <el-col :span="10">
          <el-image :src="pet.cover_image || '/placeholder.jpg'" fit="cover" style="width:100%;border-radius:10px;height:360px" />
          <el-row :gutter="8" style="margin-top:8px">
            <el-col :span="6" v-for="img in pet.images" :key="img.image_id">
              <el-image :src="img.image_url" fit="cover" style="width:100%;height:80px;border-radius:6px" />
            </el-col>
          </el-row>
        </el-col>

        <!-- 右：信息 -->
        <el-col :span="14">
          <div class="pet-header">
            <div>
              <h2 class="pet-name">{{ pet.pet_name }}</h2>
              <el-space wrap>
                <el-tag>{{ pet.species }}</el-tag>
                <el-tag type="info">{{ pet.breed || '未知品种' }}</el-tag>
                <el-tag type="warning">{{ genderLabel }}</el-tag>
                <el-tag type="success">{{ pet.age_desc || '未知' }}</el-tag>
              </el-space>
            </div>
            <el-button :icon="favIcon" circle @click="toggleFav" />
          </div>

          <el-descriptions :column="1" style="margin-top:16px" border>
            <el-descriptions-item label="健康状况">{{ pet.health_status || '暂无' }}</el-descriptions-item>
            <el-descriptions-item label="所在地区">{{ pet.location || '暂无' }}</el-descriptions-item>
            <el-descriptions-item label="领养要求">{{ pet.adoption_requirements || '暂无' }}</el-descriptions-item>
            <el-descriptions-item label="发布方">{{ pet.publisher?.nickname || '' }}</el-descriptions-item>
            <el-descriptions-item label="浏览次数">{{ pet.view_count }}</el-descriptions-item>
          </el-descriptions>

          <div class="description" v-if="pet.description">
            <h4>详细介绍</h4>
            <p>{{ pet.description }}</p>
          </div>

          <div class="actions">
            <template v-if="pet.status === 'online'">
              <el-button type="primary" size="large" @click="goApply" v-if="userStore.isUser">申请领养</el-button>
              <el-button size="large" @click="goMessage">咨询发布方</el-button>
            </template>
            <el-tag type="info" size="large" v-else>{{ statusLabel }}</el-tag>
          </div>
        </el-col>
      </el-row>

      <!-- 评价 -->
      <div style="margin-top:32px" v-if="pet">
        <h3>评价 ({{ reviews.length }})</h3>
        <el-empty v-if="reviews.length === 0" description="暂无评价" />
        <div v-for="r in reviews" :key="r.review_id" class="review-item">
          <el-avatar :size="36">{{ r.reviewer?.nickname?.charAt(0) }}</el-avatar>
          <div class="review-content">
            <div class="review-user">{{ r.reviewer?.nickname }}</div>
            <el-rate v-model="r.rating" disabled />
            <div class="review-text">{{ r.content }}</div>
            <div class="review-time">{{ r.created_at?.substring(0, 10) }}</div>
          </div>
        </div>
      </div>
    </div>
  </NavBar>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Star, StarFilled } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import NavBar from '@/components/NavBar.vue'
import { petsApi, reviewsApi, userApi } from '@/api'
import { useUserStore } from '@/stores/user'

const route     = useRoute()
const router    = useRouter()
const userStore = useUserStore()
const pet       = ref(null)
const reviews   = ref([])
const loading   = ref(false)
const isFav     = ref(false)
const favIcon   = computed(() => isFav.value ? StarFilled : Star)

const genderLabel  = computed(() => ({ male:'公', female:'母', unknown:'性别未知' })[pet.value?.gender] || '')
const statusLabel  = computed(() => ({ adopted:'已被领养', offline:'已下架', pending:'审核中' })[pet.value?.status] || '')

async function loadPet() {
  loading.value = true
  try {
    pet.value = await petsApi.get(route.params.id)
    const rv  = await reviewsApi.list({ target_type: 'pet', target_id: route.params.id })
    reviews.value = rv
  } finally {
    loading.value = false
  }
}

async function toggleFav() {
  if (!userStore.isLoggedIn) return router.push('/login')
  try {
    if (isFav.value) {
      await userApi.removeFavorite('pet', pet.value.pet_id)
      isFav.value = false
      ElMessage.success('已取消收藏')
    } else {
      await userApi.addFavorite({ target_type: 'pet', target_id: pet.value.pet_id })
      isFav.value = true
      ElMessage.success('收藏成功')
    }
  } catch {}
}

function goApply() {
  if (!userStore.isLoggedIn) return router.push('/login')
  router.push(`/pets/${pet.value.pet_id}/apply`)
}

function goMessage() {
  if (!userStore.isLoggedIn) return router.push('/login')
  router.push({ path: '/messages', query: { to: pet.value.publisher_id, pet: pet.value.pet_id } })
}

onMounted(loadPet)
</script>

<style scoped>
.pet-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 8px; }
.pet-name { margin: 0 0 12px; font-size: 24px; }
.description { margin-top: 16px; }
.description p { color: #606266; line-height: 1.8; }
.actions { margin-top: 24px; display: flex; gap: 12px; }
.review-item { display: flex; gap: 12px; padding: 16px 0; border-bottom: 1px solid #f0f0f0; }
.review-user { font-weight: 600; margin-bottom: 4px; }
.review-text { color: #606266; margin: 6px 0; }
.review-time { color: #c0c4cc; font-size: 12px; }
</style>

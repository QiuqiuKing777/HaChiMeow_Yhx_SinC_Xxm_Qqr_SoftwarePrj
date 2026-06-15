<template>
  <div>
    <div class="toolbar">
      <div class="toolbar-left">
        <el-button class="action-btn" @click="$router.push('/publisher/pets')">← 返回</el-button>
        <h2>宠物反馈记录</h2>
      </div>
    </div>

    <!-- 宠物信息卡片 -->
    <el-card class="pet-info-card" v-if="pet">
      <div class="pet-info">
        <img :src="pet.cover_image || '/NKU.png'" class="pet-thumb" />
        <div class="pet-detail">
          <h3>{{ pet.pet_name }}</h3>
          <p>种类：{{ pet.species }} {{ pet.breed ? ' / ' + pet.breed : '' }}</p>
          <el-tag :type="pet.status === 'adopted' ? 'info' : 'warning'">{{ pet.status }}</el-tag>
        </div>
      </div>
    </el-card>

    <!-- 反馈列表 -->
    <el-card class="feedback-list-card">
      <template #header>
        <h3>反馈记录（共 {{ total }} 条）</h3>
      </template>

      <div v-loading="loading">
        <el-empty v-if="!loading && total === 0" description="暂无反馈记录" />

        <el-timeline v-if="feedbacks.length > 0">
          <el-timeline-item
            v-for="item in feedbacks"
            :key="item.feedback_id"
            :timestamp="item.created_at"
            placement="top"
          >
            <el-card shadow="hover" class="feedback-item">
              <div class="feedback-header">
                <span class="feedback-user">
                  领养者：{{ item.user?.nickname || item.user?.username || '未知' }}
                </span>
              </div>

              <div class="feedback-body">
                <div class="feedback-photo-area" v-if="item.photo_url">
                  <img
                    :src="item.photo_url"
                    class="feedback-photo"
                    @click="openPreview(item.photo_url)"
                  />
                </div>

                <div class="feedback-data">
                  <el-descriptions :column="1" border size="small">
                    <el-descriptions-item label="体重" v-if="item.weight !== null">
                      {{ item.weight }} kg
                    </el-descriptions-item>
                    <el-descriptions-item label="备注" v-if="item.notes">
                      {{ item.notes }}
                    </el-descriptions-item>
                  </el-descriptions>
                </div>
              </div>
            </el-card>
          </el-timeline-item>
        </el-timeline>

        <el-pagination
          v-if="total > 10"
          background
          layout="prev,pager,next,total"
          :total="total"
          :page-size="10"
          v-model:current-page="page"
          @current-change="load"
          style="margin-top:16px;justify-content:center;display:flex"
        />
      </div>
    </el-card>

    <!-- 照片预览 -->
    <el-dialog v-model="previewVisible" title="照片预览">
      <img :src="previewUrl" style="width:100%" v-if="previewUrl" />
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { feedbacksApi } from '@/api'

const route = useRoute()
const petId = ref(Number(route.params.id))

const pet = ref(null)
const feedbacks = ref([])
const total = ref(0)
const page = ref(1)
const loading = ref(false)

const previewVisible = ref(false)
const previewUrl = ref('')

function openPreview(url) {
  previewUrl.value = url
  previewVisible.value = true
}

async function load() {
  loading.value = true
  try {
    const res = await feedbacksApi.petFeedbacks(petId.value, {
      page: page.value,
      per_page: 10,
    })
    pet.value = res.pet || null
    feedbacks.value = res.items || []
    total.value = res.total || 0
  } finally {
    loading.value = false
  }
}

watch(() => route.params.id, (val) => {
  petId.value = Number(val)
  page.value = 1
  load()
})

onMounted(load)
</script>

<style scoped>
.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}
.toolbar-left {
  display: flex;
  align-items: center;
  gap: 16px;
}
.toolbar-left h2 {
  margin: 0;
}
.pet-info-card {
  margin-bottom: 20px;
}
.pet-info {
  display: flex;
  gap: 20px;
  align-items: center;
}
.pet-thumb {
  width: 80px;
  height: 80px;
  object-fit: cover;
  border-radius: 8px;
  border: 1px solid #ebeef5;
}
.pet-detail h3 {
  margin: 0 0 8px 0;
}
.pet-detail p {
  margin: 0 0 8px 0;
  color: #606266;
}
.feedback-list-card {
  min-height: 200px;
}
.feedback-item {
  margin-bottom: 4px;
}
.feedback-header {
  margin-bottom: 10px;
}
.feedback-user {
  color: #409eff;
  font-weight: 600;
}
.feedback-body {
  display: flex;
  gap: 16px;
}
.feedback-photo-area {
  flex-shrink: 0;
}
.feedback-photo {
  width: 150px;
  height: 150px;
  object-fit: cover;
  border-radius: 8px;
  cursor: pointer;
  border: 1px solid #ebeef5;
}
.feedback-data {
  flex: 1;
}
.action-btn {
  border-radius: 10px;
  font-weight: 600;
}
</style>

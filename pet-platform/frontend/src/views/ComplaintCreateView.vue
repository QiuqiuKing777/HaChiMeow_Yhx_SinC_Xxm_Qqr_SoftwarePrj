<template>
  <NavBar>
    <div class="complaint-page">
      <el-card class="complaint-card">
        <template #header>
          <div class="card-header">评价{{ targetLabel }}</div>
        </template>

        <div class="target-info">
          <div class="target-label">当前评价对象</div>
          <div class="target-name">{{ targetName }}</div>
        </div>

        <div class="form-block">
          <div class="form-label">评分</div>
          <div class="stars">
            <button
              v-for="n in 5"
              :key="n"
              type="button"
              class="star-btn"
              :class="{ active: n <= score }"
              @click="setScore(n)"
            >
              ★
            </button>
          </div>
          <div class="score-text">{{ score }} 星</div>
        </div>

        <div class="form-block">
          <div class="form-label">评价内容</div>
          <el-input
            v-model="content"
            type="textarea"
            :rows="5"
            maxlength="300"
            show-word-limit
            placeholder="请填写你的评价内容"
          />
        </div>

        <div class="actions">
          <el-button @click="goBack">返回</el-button>
          <el-button type="primary" :loading="submitting" @click="submitComplaint">
            提交评价
          </el-button>
        </div>
      </el-card>
    </div>
  </NavBar>
</template>


<script setup>
import { ref, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import NavBar from '@/components/NavBar.vue'
import { complaintsApi } from '@/api'

const route = useRoute()
const router = useRouter()

const score = ref(5)
const content = ref('')
const submitting = ref(false)

const typeMap = {
  product: 'products',
  products: 'products',
  pet: 'pets',
  pets: 'pets',
  service: 'services',
  services: 'services'
}

const labelMap = {
  products: '商品',
  pets: '宠物',
  services: '服务'
}

const targetType = computed(() => {
  const raw = String(route.query.target_type || '').trim()
  return typeMap[raw] || ''
})

const targetId = computed(() => Number(route.query.target_id || 0))
const targetName = computed(() => route.query.target_name || labelMap[targetType.value] || '评价对象')

const targetLabel = computed(() => labelMap[targetType.value] || '评价对象')

function setScore(n) {
  score.value = n
}

function goBack() {
  router.back()
}

async function submitComplaint() {
  if (!targetType.value) {
    ElMessage.error('评价类型不正确')
    return
  }

  if (!targetId.value) {
    ElMessage.error('评价对象不存在')
    return
  }

  if (!content.value.trim()) {
    ElMessage.warning('请填写评价内容')
    return
  }

  submitting.value = true

  try {
    await complaintsApi.create({
      target_type: targetType.value,
      target_id: targetId.value,
      score: score.value,
      content: content.value.trim()
    })

    ElMessage.success('评价提交成功')

    const returnTo = route.query.return_to
    if (returnTo) {
      router.push(String(returnTo))
    } else {
      router.back()
    }
  } catch (e) {
    console.error(e)
    ElMessage.error(e?.response?.data?.error || e?.message || '评价提交失败')
  } finally {
    submitting.value = false
  }
}
</script>


<style scoped>
.complaint-page {
  display: flex;
  justify-content: center;
  padding: 24px 0;
}

.complaint-card {
  width: 640px;
  border-radius: 14px;
}

.card-header {
  font-size: 18px;
  font-weight: 700;
}

.target-info {
  padding: 14px 16px;
  background: linear-gradient(135deg, rgba(255, 192, 203, 0.18), rgba(255, 255, 255, 0.72));
  border: 1px solid rgba(255, 182, 193, 0.35);
  border-radius: 12px;
  margin-bottom: 22px;
  backdrop-filter: blur(10px);
}

.target-label {
  font-size: 13px;
  color: #909399;
  margin-bottom: 6px;
}

.target-name {
  font-size: 16px;
  color: #303133;
  font-weight: 600;
}

.form-block {
  margin-bottom: 24px;
}

.form-label {
  font-size: 14px;
  color: #606266;
  margin-bottom: 10px;
}

.stars {
  display: flex;
  gap: 10px;
  align-items: center;
}

.star-btn {
  border: none;
  background: rgba(255, 255, 255, 0.45);
  width: 46px;
  height: 46px;
  border-radius: 14px;
  font-size: 30px;
  line-height: 46px;
  cursor: pointer;
  color: rgba(196, 196, 196, 0.7);
  box-shadow:
    inset 0 1px 2px rgba(255, 255, 255, 0.75),
    0 6px 18px rgba(255, 105, 180, 0.12);
  backdrop-filter: blur(8px);
  transition: all 0.18s ease;
}

.star-btn.active {
  color: #ff6fb3;
  background: linear-gradient(145deg, rgba(255, 182, 213, 0.72), rgba(255, 255, 255, 0.45));
  text-shadow:
    0 1px 0 rgba(255, 255, 255, 0.95),
    0 0 12px rgba(255, 105, 180, 0.75),
    0 0 24px rgba(255, 182, 193, 0.6);
  box-shadow:
    inset 0 1px 3px rgba(255, 255, 255, 0.9),
    inset 0 -2px 6px rgba(255, 105, 180, 0.28),
    0 8px 22px rgba(255, 105, 180, 0.28);
}

.star-btn:hover {
  transform: translateY(-2px) scale(1.05);
}

.score-text {
  margin-top: 8px;
  color: #ff6fb3;
  font-weight: 600;
}

.actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}
</style>

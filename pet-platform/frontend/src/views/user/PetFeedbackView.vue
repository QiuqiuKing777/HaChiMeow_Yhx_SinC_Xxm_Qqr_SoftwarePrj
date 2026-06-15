<template>
  <NavBar>
    <div class="feedback-page">
      <div class="header">
        <el-button class="action-btn" @click="$router.back()">← 返回</el-button>
        <h2>宠物状态反馈</h2>
      </div>

      <!-- 反馈状态 -->
      <el-card class="status-card" v-if="fbStatus">
        <div class="status-row">
          <span class="label">反馈状态：</span>
          <el-tag :type="fbStatus.overdue ? 'danger' : 'success'">
            {{ fbStatus.overdue ? '已逾期' : '正常' }}
          </el-tag>
          <span v-if="fbStatus.overdue" class="overdue-warn">
            请尽快提交反馈！（已逾期 {{ fbStatus.days_since_last }} 天）
          </span>
          <span v-else class="next-info">
            距下次反馈还有 {{ fbStatus.days_remaining }} 天
          </span>
        </div>
        <div class="status-detail">
          <span>已提交反馈次数：{{ fbStatus.total_count }}</span>
          <span v-if="fbStatus.last_feedback_date">
            上次反馈：{{ fbStatus.last_feedback_date }}
          </span>
          <span>下次反馈截止：{{ fbStatus.next_due_date }}</span>
        </div>
      </el-card>

      <!-- 提交反馈表单 -->
      <el-card class="form-card">
        <template #header><h3>提交新反馈</h3></template>
        <el-form :model="form" label-width="100px">
          <el-form-item label="宠物照片">
            <div class="upload-wrap">
              <el-upload
                :show-file-list="false"
                :auto-upload="false"
                :before-upload="beforeUpload"
                :on-change="handlePhotoChange"
                accept=".png,.jpg,.jpeg,.webp"
              >
                <el-button class="action-btn" type="primary" plain>选择照片</el-button>
              </el-upload>
              <img v-if="photoPreview" :src="photoPreview" class="preview-img" />
            </div>
          </el-form-item>

          <el-form-item label="体重(kg)">
            <el-input-number
              v-model="form.weight"
              :min="0"
              :precision="2"
              :step="0.1"
              placeholder="请输入宠物当前体重"
            />
          </el-form-item>

          <el-form-item label="备注说明">
            <el-input
              v-model="form.notes"
              type="textarea"
              rows="4"
              placeholder="请描述宠物近况，如饮食、活动、健康状况等"
            />
          </el-form-item>

          <el-form-item>
            <el-button class="action-btn" type="primary" @click="submitFeedback" :loading="submitting">
              提交反馈
            </el-button>
          </el-form-item>
        </el-form>
      </el-card>

      <!-- 历史反馈 -->
      <el-card class="history-card">
        <template #header><h3>历史反馈记录</h3></template>
        <div v-loading="loading">
          <el-empty v-if="!loading && feedbacks.length === 0" description="暂无反馈记录" />

          <el-timeline v-if="feedbacks.length > 0">
            <el-timeline-item
              v-for="item in feedbacks"
              :key="item.feedback_id"
              :timestamp="item.created_at"
              placement="top"
            >
              <el-card shadow="hover" class="feedback-item">
                <div class="feedback-content">
                  <img
                    v-if="item.photo_url"
                    :src="item.photo_url"
                    class="feedback-photo"
                    @click="previewPhoto = item.photo_url"
                  />
                  <div class="feedback-info">
                    <p v-if="item.weight !== null">
                      <strong>体重：</strong>{{ item.weight }} kg
                    </p>
                    <p v-if="item.notes">
                      <strong>备注：</strong>{{ item.notes }}
                    </p>
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
            @current-change="loadFeedbacks"
            style="margin-top:16px;justify-content:center;display:flex"
          />
        </div>
      </el-card>

      <!-- 照片预览 -->
      <el-dialog v-model="photoDialogVisible" title="照片预览">
        <img :src="previewPhoto" style="width:100%" v-if="previewPhoto" />
      </el-dialog>
    </div>
  </NavBar>
</template>

<script setup>
import { ref, reactive, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import NavBar from '@/components/NavBar.vue'
import { feedbacksApi } from '@/api'

const route = useRoute()
const router = useRouter()

const applicationId = ref(Number(route.params.id))

const fbStatus = ref(null)
const feedbacks = ref([])
const total = ref(0)
const page = ref(1)
const loading = ref(false)
const submitting = ref(false)

const form = reactive({
  weight: null,
  notes: '',
})

const photoFile = ref(null)
const photoPreview = ref('')
const previewPhoto = ref('')
const photoDialogVisible = ref(false)

function beforeUpload(file) {
  const allowed = ['image/png', 'image/x-png', 'image/jpeg', 'image/webp']
  const ok = allowed.includes(file.type)
  if (!ok) ElMessage.error('仅支持 PNG、JPG、JPEG、WEBP 格式')
  return false
}

function handlePhotoChange(file) {
  const raw = file.raw
  if (!raw) return
  const allowed = ['image/png', 'image/x-png', 'image/jpeg', 'image/webp']
  if (!allowed.includes(raw.type)) {
    ElMessage.error('仅支持 PNG、JPG、JPEG、WEBP 格式')
    return
  }
  photoFile.value = raw
  photoPreview.value = URL.createObjectURL(raw)
}

async function loadStatus() {
  try {
    fbStatus.value = await feedbacksApi.status(applicationId.value)
  } catch {
    fbStatus.value = null
  }
}

async function loadFeedbacks() {
  loading.value = true
  try {
    const res = await feedbacksApi.myList({
      application_id: applicationId.value,
      page: page.value,
      per_page: 10,
    })
    feedbacks.value = res.items || []
    total.value = res.total || 0
  } finally {
    loading.value = false
  }
}

async function submitFeedback() {
  if (!photoFile.value && !form.weight && !form.notes) {
    ElMessage.warning('请至少填写一项反馈内容')
    return
  }
  submitting.value = true
  try {
    const fd = new FormData()
    fd.append('application_id', applicationId.value)
    if (photoFile.value) fd.append('photo', photoFile.value)
    if (form.weight !== null && form.weight !== undefined) fd.append('weight', form.weight)
    fd.append('notes', form.notes || '')

    await feedbacksApi.submit(fd)
    ElMessage.success('反馈提交成功')
    form.weight = null
    form.notes = ''
    photoFile.value = null
    photoPreview.value = ''
    loadStatus()
    loadFeedbacks()
  } finally {
    submitting.value = false
  }
}

watch(() => route.params.id, (val) => {
  applicationId.value = Number(val)
  loadStatus()
  loadFeedbacks()
})

onMounted(() => {
  loadStatus()
  loadFeedbacks()
})
</script>

<style scoped>
.feedback-page {
  max-width: 800px;
  margin: 0 auto;
}
.header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 20px;
}
.header h2 {
  margin: 0;
}
.status-card {
  margin-bottom: 20px;
}
.status-row {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 8px;
}
.overdue-warn {
  color: #f56c6c;
  font-weight: 600;
}
.next-info {
  color: #67c23a;
}
.status-detail {
  display: flex;
  gap: 24px;
  color: #909399;
  font-size: 13px;
}
.form-card {
  margin-bottom: 20px;
}
.history-card {
  margin-bottom: 20px;
}
.upload-wrap {
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.preview-img {
  width: 150px;
  height: 150px;
  object-fit: cover;
  border-radius: 8px;
  border: 1px solid #ebeef5;
}
.feedback-content {
  display: flex;
  gap: 16px;
}
.feedback-photo {
  width: 120px;
  height: 120px;
  object-fit: cover;
  border-radius: 8px;
  cursor: pointer;
  border: 1px solid #ebeef5;
}
.feedback-info {
  flex: 1;
}
.feedback-info p {
  margin: 4px 0;
}
.action-btn {
  border-radius: 10px;
  font-weight: 600;
}
</style>

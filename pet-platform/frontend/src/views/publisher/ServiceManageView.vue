<template>
  <div>
    <div class="toolbar">
      <h2>服务管理</h2>
      <el-button class="action-btn" type="primary" @click="openDialog()">+ 发布服务</el-button>
    </div>

    <el-table :data="services" border v-loading="loading">
      <el-table-column label="图片" width="90">
        <template #default="{ row }">
          <img :src="row.cover_image || '/NKU.png'" class="thumb" />
        </template>
      </el-table-column>

      <el-table-column label="名称" prop="service_name" />
      <el-table-column label="类别" prop="category" width="100" />

      <el-table-column label="价格" prop="price" width="90">
        <template #default="{ row }">¥{{ row.price }}</template>
      </el-table-column>

      <el-table-column label="时长" prop="duration" width="100" />

      <el-table-column label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="{ online:'success', offline:'info', pending:'warning' }[row.status] || 'info'">
            {{ row.status }}
          </el-tag>
        </template>
      </el-table-column>

      <el-table-column label="操作" width="180">
        <template #default="{ row }">
          <el-button class="mini-btn" size="small" @click="openSlotDialog(row)">时段</el-button>
          <el-button class="mini-btn" size="small" @click="openDialog(row)">编辑</el-button>
          <el-popconfirm title="确认删除？" @confirm="deleteService(row)">
            <template #reference>
              <el-button class="mini-btn" size="small" type="danger">删除</el-button>
            </template>
          </el-popconfirm>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="dialogVisible" :title="editId ? '编辑服务' : '发布服务'" width="540px">
      <el-form :model="form" label-width="90px">
        <el-form-item label="服务名称"><el-input v-model="form.service_name" /></el-form-item>
        <el-form-item label="服务类别"><el-input v-model="form.category" /></el-form-item>
        <el-form-item label="价格"><el-input-number v-model="form.price" :min="0" :precision="2" /></el-form-item>
        <el-form-item label="服务时长"><el-input v-model="form.duration" placeholder="如：约2小时" /></el-form-item>
        <el-form-item label="服务地点"><el-input v-model="form.location" /></el-form-item>
        <el-form-item label="描述"><el-input v-model="form.description" type="textarea" rows="3" /></el-form-item>

        <el-form-item label="上传图片">
          <div class="upload-wrap">
            <el-upload
              :show-file-list="false"
              :auto-upload="false"
              :before-upload="beforeImageUpload"
              :on-change="handleServiceImageChange"
              accept=".png,.jpg,.jpeg,.svg"
            >
              <el-button class="action-btn" type="primary" plain>选择图片</el-button>
            </el-upload>
            <div class="upload-tip">仅支持 PNG / JPG / SVG</div>
            <img v-if="imagePreview" :src="imagePreview" class="preview-img" />
          </div>
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button class="action-btn" @click="dialogVisible = false">取消</el-button>
        <el-button class="action-btn" type="primary" @click="saveService" :loading="saving">保存</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="slotDialog" title="时段管理" width="600px">
      <el-button class="action-btn" type="primary" size="small" @click="showAddSlot = !showAddSlot" style="margin-bottom:12px">
        {{ showAddSlot ? '收起' : '添加时段' }}
      </el-button>

      <el-form v-if="showAddSlot" :model="slotForm" inline style="margin-bottom:12px">
        <el-form-item label="日期">
          <el-date-picker v-model="slotForm.slot_date" type="date" value-format="YYYY-MM-DD" placeholder="选择日期" style="width:140px" />
        </el-form-item>
        <el-form-item label="时段">
          <el-input v-model="slotForm.slot_time" placeholder="如：09:00-11:00" style="width:130px" />
        </el-form-item>
        <el-form-item label="容量">
          <el-input-number v-model="slotForm.capacity" :min="1" style="width:90px" />
        </el-form-item>
        <el-form-item>
          <el-button class="action-btn" type="primary" :loading="slotSaving" @click="submitSlot">确认添加</el-button>
        </el-form-item>
      </el-form>

      <el-table :data="slots" border size="small">
        <el-table-column label="日期" prop="slot_date" width="120" />
        <el-table-column label="时段" prop="slot_time" />
        <el-table-column label="容量" prop="capacity" width="80" />
        <el-table-column label="已预约" prop="booked_count" width="80" />
      </el-table>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { servicesApi } from '@/api'

const services = ref([])
const loading = ref(false)
const saving = ref(false)
const dialogVisible = ref(false)
const slotDialog = ref(false)
const showAddSlot = ref(false)
const slotSaving = ref(false)
const editId = ref(null)
const currentServiceId = ref(null)
const slots = ref([])

const slotForm = reactive({ slot_date: '', slot_time: '', capacity: 5 })

const imageFile = ref(null)
const imagePreview = ref('')

const form = reactive({
  service_name: '',
  category: '',
  price: 0,
  duration: '',
  location: '',
  description: '',
})

function resetForm() {
  Object.assign(form, {
    service_name: '',
    category: '',
    price: 0,
    duration: '',
    location: '',
    description: '',
  })
  imageFile.value = null
  imagePreview.value = ''
}

function beforeImageUpload(file) {
  const allowed = ['image/png', 'image/jpeg', 'image/svg+xml']
  const ok = allowed.includes(file.type)
  if (!ok) ElMessage.error('仅支持 PNG、JPG、SVG 格式')
  return false
}

function handleServiceImageChange(file) {
  const raw = file.raw
  if (!raw) return
  const allowed = ['image/png', 'image/jpeg', 'image/svg+xml']
  if (!allowed.includes(raw.type)) {
    ElMessage.error('仅支持 PNG、JPG、SVG 格式')
    return
  }
  imageFile.value = raw
  imagePreview.value = URL.createObjectURL(raw)
}

async function load() {
  loading.value = true
  try {
    const res = await servicesApi.myServices()
    services.value = res.items || res || []
  } finally {
    loading.value = false
  }
}

function openDialog(svc = null) {
  resetForm()
  if (svc) {
    editId.value = svc.service_id
    Object.assign(form, {
      service_name: svc.service_name || '',
      category: svc.category || '',
      price: svc.price || 0,
      duration: svc.duration || '',
      location: svc.location || '',
      description: svc.description || '',
    })
    imagePreview.value = svc.cover_image || '/NKU.png'
  } else {
    editId.value = null
  }
  dialogVisible.value = true
}

async function saveService() {
  saving.value = true
  try {
    const fd = new FormData()
    fd.append('service_name', form.service_name)
    fd.append('category', form.category)
    fd.append('price', form.price)
    fd.append('duration', form.duration)
    fd.append('location', form.location)
    fd.append('description', form.description)
    if (imageFile.value) fd.append('image', imageFile.value)

    if (editId.value) await servicesApi.update(editId.value, fd)
    else await servicesApi.create(fd)

    ElMessage.success('保存成功')
    dialogVisible.value = false
    load()
  } finally {
    saving.value = false
  }
}

async function deleteService(row) {
  try {
    await servicesApi.remove(row.service_id)
    ElMessage.success('已删除')
    load()
  } catch (err) {
    ElMessage.error(err?.response?.data?.error || '删除失败')
  }
}

async function submitSlot() {
  if (!slotForm.slot_date || !slotForm.slot_time) {
    ElMessage.warning('请填写日期和时段')
    return
  }
  slotSaving.value = true
  try {
    await servicesApi.addSlot(currentServiceId.value, { ...slotForm })
    ElMessage.success('时段已添加')
    Object.assign(slotForm, { slot_date: '', slot_time: '', capacity: 5 })
    showAddSlot.value = false
    const res = await servicesApi.slots(currentServiceId.value)
    slots.value = res.items || res || []
  } finally {
    slotSaving.value = false
  }
}

async function openSlotDialog(svc) {
  currentServiceId.value = svc.service_id
  const res = await servicesApi.slots(svc.service_id)
  slots.value = res.items || res || []
  slotDialog.value = true
}

onMounted(load)
</script>

<style scoped>
.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.thumb {
  width: 52px;
  height: 52px;
  object-fit: cover;
  border-radius: 6px;
}

.upload-wrap {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.upload-tip {
  color: #909399;
  font-size: 12px;
}

.preview-img {
  width: 120px;
  height: 120px;
  object-fit: cover;
  border-radius: 8px;
  border: 1px solid #ebeef5;
}

.action-btn {
  border-radius: 10px;
  min-width: 92px;
  font-weight: 600;
}

.mini-btn {
  border-radius: 8px;
}
</style>

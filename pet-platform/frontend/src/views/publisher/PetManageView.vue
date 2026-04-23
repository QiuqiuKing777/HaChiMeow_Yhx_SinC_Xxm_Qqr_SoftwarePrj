<template>
  <div>
    <div class="toolbar">
      <h2>宠物管理</h2>
      <el-button class="action-btn" type="primary" @click="openDialog()">+ 发布宠物</el-button>
    </div>

    <el-table :data="pets" border v-loading="loading">
      <el-table-column label="图片" width="90">
        <template #default="{ row }">
<!--          <img :src="row.cover_image ? '/' + row.cover_image : '/NKU.png'" class="thumb" />-->
<!--          <img :src="getImageUrl(row.cover_image)" class="thumb" />-->
          <img :src="row.cover_image || '/NKU.png'" class="thumb" />
        </template>
      </el-table-column>
      <el-table-column label="名称" prop="pet_name" />
      <el-table-column label="品种" prop="breed" />
      <el-table-column label="年龄" prop="age_desc" width="100" />
      <el-table-column label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="{ online:'success', adopted:'info', pending:'warning', offline:'danger' }[row.status] || 'info'">
            {{ row.status }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="160">
        <template #default="{ row }">
          <el-button class="mini-btn" size="small" @click="openDialog(row)">编辑</el-button>
          <el-popconfirm title="确认删除？" @confirm="deletePet(row)">
            <template #reference>
              <el-button class="mini-btn" size="small" type="danger">删除</el-button>
            </template>
          </el-popconfirm>
        </template>
      </el-table-column>
    </el-table>

    <el-pagination
      v-if="total > 0"
      background
      layout="prev,pager,next,total"
      :total="total"
      :page-size="10"
      v-model:current-page="page"
      @current-change="load"
      style="margin-top:16px;justify-content:center;display:flex"
    />

    <el-dialog v-model="dialogVisible" :title="editId ? '编辑宠物' : '发布宠物'" width="600px">
      <el-form :model="form" label-width="90px">
        <el-form-item label="名称"><el-input v-model="form.pet_name" /></el-form-item>
        <el-form-item label="种类">
          <el-select v-model="form.species">
            <el-option label="猫" value="猫" />
            <el-option label="狗" value="狗" />
            <el-option label="其他" value="其他" />
          </el-select>
        </el-form-item>
        <el-form-item label="品种"><el-input v-model="form.breed" /></el-form-item>
        <el-form-item label="年龄描述"><el-input v-model="form.age_desc" placeholder="如：3个月 / 1岁" /></el-form-item>
        <el-form-item label="性别">
          <el-select v-model="form.gender">
            <el-option label="公" value="male" />
            <el-option label="母" value="female" />
            <el-option label="未知" value="unknown" />
          </el-select>
        </el-form-item>
        <el-form-item label="健康状况"><el-input v-model="form.health_status" /></el-form-item>
        <el-form-item label="所在地区"><el-input v-model="form.location" placeholder="如：天津市 南开区" /></el-form-item>
        <el-form-item label="描述"><el-input v-model="form.description" type="textarea" rows="3" /></el-form-item>

        <el-form-item label="上传图片">
          <div class="upload-wrap">
            <el-upload
              :show-file-list="false"
              :auto-upload="false"
              :before-upload="beforeImageUpload"
              :on-change="handlePetImageChange"
              accept=".png,.jpg,.jpeg,.svg,.webp,.gif"
            >
              <el-button class="action-btn" type="primary" plain>选择图片</el-button>
            </el-upload>
            <div class="upload-tip">支持 PNG / JPG / JPEG / SVG / WEBP / GIF</div>
            <img v-if="imagePreview" :src="imagePreview" class="preview-img" />
          </div>
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button class="action-btn" @click="dialogVisible = false">取消</el-button>
        <el-button class="action-btn" type="primary" @click="savePet" :loading="saving">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { petsApi } from '@/api'

const pets = ref([])
const total = ref(0)
const page = ref(1)
const loading = ref(false)
const saving = ref(false)
const dialogVisible = ref(false)
const editId = ref(null)

const imageFile = ref(null)
const imagePreview = ref('')

const form = reactive({
  pet_name: '',
  species: '猫',
  breed: '',
  age_desc: '',
  gender: 'male',
  health_status: '',
  location: '',
  description: '',
})

function resetForm() {
  Object.assign(form, {
    pet_name: '',
    species: '猫',
    breed: '',
    age_desc: '',
    gender: 'male',
    health_status: '',
    location: '',
    description: '',
  })
  imageFile.value = null
  imagePreview.value = ''
}

// function getImageUrl(path) {
//   if (!path) return '/NKU.png'
//   if (path.startsWith('http')) return path
//   if (path.startsWith('/static/')) return `http://localhost:5001${path}`
//   return `/${path}`
// }


function beforeImageUpload(file) {
  const allowed = ['image/png', 'image/x-png', 'image/jpeg', 'image/svg+xml', 'image/webp', 'image/gif']
  const ok = allowed.includes(file.type)
  if (!ok) ElMessage.error('仅支持 PNG、JPG、JPEG、SVG、WEBP、GIF 格式')
  return ok ? false : false
}

function handlePetImageChange(file) {
  const raw = file.raw
  if (!raw) return
  const allowed = ['image/png', 'image/x-png', 'image/jpeg', 'image/svg+xml', 'image/webp', 'image/gif']
  if (!allowed.includes(raw.type)) {
    ElMessage.error('仅支持 PNG、JPG、JPEG、SVG、WEBP、GIF 格式')
    return
  }
  imageFile.value = raw
  imagePreview.value = URL.createObjectURL(raw)
}


async function load() {
  loading.value = true
  try {
    const res = await petsApi.myPets({ page: page.value, per_page: 10 })
    pets.value = res.items || []
    total.value = res.total || 0
  } finally {
    loading.value = false
  }
}

function openDialog(pet = null) {
  resetForm()
  if (pet) {
    editId.value = pet.pet_id
    Object.assign(form, {
      pet_name: pet.pet_name || '',
      species: pet.species || '猫',
      breed: pet.breed || '',
      age_desc: pet.age_desc || '',
      gender: pet.gender || 'male',
      health_status: pet.health_status || '',
      location: pet.location || '',
      description: pet.description || '',
    })
    imagePreview.value = pet.cover_image || '/NKU.png'
  } else {
    editId.value = null
  }
  dialogVisible.value = true
}

async function savePet() {
  saving.value = true
  try {
    const fd = new FormData()
    fd.append('pet_name', form.pet_name)
    fd.append('species', form.species)
    fd.append('breed', form.breed)
    fd.append('age_desc', form.age_desc)
    fd.append('gender', form.gender)
    fd.append('health_status', form.health_status)
    fd.append('location', form.location)
    fd.append('description', form.description)
    if (imageFile.value) fd.append('image', imageFile.value)

    if (editId.value) await petsApi.update(editId.value, fd)
    else await petsApi.create(fd)

    ElMessage.success('保存成功')
    dialogVisible.value = false
    load()
  } finally {
    saving.value = false
  }
}

async function deletePet(row) {
  try {
    await petsApi.remove(row.pet_id)
    ElMessage.success('已删除')
    load()
  } catch (err) {
    ElMessage.error(err?.response?.data?.error || '删除失败')
  }
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

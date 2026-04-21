<template>
  <NavBar>
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:16px">
      <h2>宠物管理</h2>
      <el-button type="primary" @click="openDialog()">+ 发布宠物</el-button>
    </div>
    <el-table :data="pets" border v-loading="loading">
      <el-table-column label="图片" width="80">
        <template #default="{ row }">
          <img :src="row.main_image || '/placeholder.jpg'" style="width:50px;height:50px;object-fit:cover;border-radius:4px" />
        </template>
      </el-table-column>
      <el-table-column label="名称" prop="name" />
      <el-table-column label="品种" prop="breed" />
      <el-table-column label="年龄" prop="age" width="60" />
      <el-table-column label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="{ available:'success', adopted:'info', reviewing:'warning', rejected:'danger' }[row.status]">{{ row.status }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="140">
        <template #default="{ row }">
          <el-button size="small" @click="openDialog(row)">编辑</el-button>
          <el-popconfirm title="确认删除？" @confirm="deletePet(row)">
            <template #reference><el-button size="small" type="danger">删除</el-button></template>
          </el-popconfirm>
        </template>
      </el-table-column>
    </el-table>
    <el-pagination v-if="total > 0" background layout="prev,pager,next,total"
      :total="total" :page-size="10" v-model:current-page="page"
      @current-change="load" style="margin-top:16px;justify-content:center;display:flex" />

    <el-dialog v-model="dialogVisible" :title="editId ? '编辑宠物' : '发布宠物'" width="560px">
      <el-form :model="form" label-width="80px">
        <el-form-item label="名称"><el-input v-model="form.name" /></el-form-item>
        <el-form-item label="品种"><el-input v-model="form.breed" /></el-form-item>
        <el-form-item label="年龄(月)"><el-input-number v-model="form.age" :min="0" /></el-form-item>
        <el-form-item label="性别">
          <el-select v-model="form.gender">
            <el-option label="公" value="male" /><el-option label="母" value="female" />
          </el-select>
        </el-form-item>
        <el-form-item label="颜色"><el-input v-model="form.color" /></el-form-item>
        <el-form-item label="健康状况"><el-input v-model="form.health_status" /></el-form-item>
        <el-form-item label="描述"><el-input v-model="form.description" type="textarea" rows="3" /></el-form-item>
        <el-form-item label="图片URL"><el-input v-model="form.main_image" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="savePet" :loading="saving">保存</el-button>
      </template>
    </el-dialog>
  </NavBar>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import NavBar from '@/components/NavBar.vue'
import { petsApi } from '@/api'

const pets    = ref([])
const total   = ref(0)
const page    = ref(1)
const loading = ref(false)
const saving  = ref(false)
const dialogVisible = ref(false)
const editId  = ref(null)
const form = reactive({ name:'', breed:'', age:0, gender:'male', color:'', health_status:'', description:'', main_image:'' })

async function load() {
  loading.value = true
  try {
    const res = await petsApi.myList({ page: page.value, per_page: 10 })
    pets.value  = res.items || []
    total.value = res.total || 0
  } finally { loading.value = false }
}

function openDialog(pet = null) {
  editId.value = pet?.pet_id || null
  Object.assign(form, pet || { name:'', breed:'', age:0, gender:'male', color:'', health_status:'', description:'', main_image:'' })
  dialogVisible.value = true
}

async function savePet() {
  saving.value = true
  try {
    if (editId.value) await petsApi.update(editId.value, form)
    else              await petsApi.create(form)
    ElMessage.success('保存成功')
    dialogVisible.value = false
    load()
  } finally { saving.value = false }
}

async function deletePet(row) {
  await petsApi.delete(row.pet_id)
  ElMessage.success('已删除')
  load()
}

onMounted(load)
</script>

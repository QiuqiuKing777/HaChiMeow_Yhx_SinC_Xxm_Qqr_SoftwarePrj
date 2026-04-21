<template>
  <NavBar>
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:16px">
      <h2>服务管理</h2>
      <el-button type="primary" @click="openDialog()">+ 发布服务</el-button>
    </div>
    <el-table :data="services" border v-loading="loading">
      <el-table-column label="名称" prop="service_name" />
      <el-table-column label="类别" prop="service_type" width="100" />
      <el-table-column label="价格" prop="price" width="90">
        <template #default="{ row }">¥{{ row.price }}</template>
      </el-table-column>
      <el-table-column label="时长(分)" prop="duration_minutes" width="80" />
      <el-table-column label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="{ active:'success', inactive:'info' }[row.status || 'active']">{{ row.status || 'active' }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="180">
        <template #default="{ row }">
          <el-button size="small" @click="openSlotDialog(row)">时段</el-button>
          <el-button size="small" @click="openDialog(row)">编辑</el-button>
          <el-popconfirm title="确认删除？" @confirm="deleteService(row)">
            <template #reference><el-button size="small" type="danger">删除</el-button></template>
          </el-popconfirm>
        </template>
      </el-table-column>
    </el-table>

    <!-- 服务编辑弹窗 -->
    <el-dialog v-model="dialogVisible" :title="editId ? '编辑服务' : '发布服务'" width="520px">
      <el-form :model="form" label-width="90px">
        <el-form-item label="服务名称"><el-input v-model="form.service_name" /></el-form-item>
        <el-form-item label="服务类别">
          <el-select v-model="form.service_type">
            <el-option label="美容护理" value="grooming" />
            <el-option label="医疗保健" value="medical" />
            <el-option label="寄养训练" value="boarding" />
            <el-option label="其他" value="other" />
          </el-select>
        </el-form-item>
        <el-form-item label="价格"><el-input-number v-model="form.price" :min="0" :precision="2" /></el-form-item>
        <el-form-item label="时长(分钟)"><el-input-number v-model="form.duration_minutes" :min="15" /></el-form-item>
        <el-form-item label="描述"><el-input v-model="form.description" type="textarea" rows="3" /></el-form-item>
        <el-form-item label="图片URL"><el-input v-model="form.image_url" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveService" :loading="saving">保存</el-button>
      </template>
    </el-dialog>

    <!-- 时段管理弹窗 -->
    <el-dialog v-model="slotDialog" title="时段管理" width="600px">
      <el-button type="primary" size="small" @click="showAddSlot = true" style="margin-bottom:12px">添加时段</el-button>
      <el-table :data="slots" border size="small">
        <el-table-column label="日期" prop="slot_date" width="110" />
        <el-table-column label="开始" prop="start_time" width="80" />
        <el-table-column label="结束" prop="end_time" width="80" />
        <el-table-column label="容量" prop="capacity" width="60" />
        <el-table-column label="剩余" prop="available_count" width="60" />
      </el-table>

      <div v-if="showAddSlot" style="margin-top:16px;padding:12px;border:1px solid #e8e8e8;border-radius:8px">
        <el-form :model="slotForm" :inline="true">
          <el-form-item label="日期"><el-date-picker v-model="slotForm.slot_date" type="date" format="YYYY-MM-DD" value-format="YYYY-MM-DD" /></el-form-item>
          <el-form-item label="开始"><el-time-picker v-model="slotForm.start_time" format="HH:mm" value-format="HH:mm" /></el-form-item>
          <el-form-item label="结束"><el-time-picker v-model="slotForm.end_time" format="HH:mm" value-format="HH:mm" /></el-form-item>
          <el-form-item label="容量"><el-input-number v-model="slotForm.capacity" :min="1" style="width:80px" /></el-form-item>
          <el-form-item>
            <el-button type="primary" size="small" @click="addSlot">添加</el-button>
            <el-button size="small" @click="showAddSlot = false">取消</el-button>
          </el-form-item>
        </el-form>
      </div>
    </el-dialog>
  </NavBar>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import NavBar from '@/components/NavBar.vue'
import { servicesApi } from '@/api'

const services = ref([])
const loading  = ref(false)
const saving   = ref(false)
const dialogVisible = ref(false)
const slotDialog    = ref(false)
const showAddSlot   = ref(false)
const editId   = ref(null)
const currentServiceId = ref(null)
const slots    = ref([])

const form     = reactive({ service_name:'', service_type:'grooming', price:0, duration_minutes:60, description:'', image_url:'' })
const slotForm = reactive({ slot_date:'', start_time:'', end_time:'', capacity:10 })

async function load() {
  loading.value = true
  try {
    const res = await servicesApi.myList()
    services.value = res.items || res || []
  } finally { loading.value = false }
}

function openDialog(svc = null) {
  editId.value = svc?.service_id || null
  Object.assign(form, svc || { service_name:'', service_type:'grooming', price:0, duration_minutes:60, description:'', image_url:'' })
  dialogVisible.value = true
}

async function saveService() {
  saving.value = true
  try {
    if (editId.value) await servicesApi.update(editId.value, form)
    else              await servicesApi.create(form)
    ElMessage.success('保存成功')
    dialogVisible.value = false
    load()
  } finally { saving.value = false }
}

async function deleteService(row) {
  await servicesApi.delete(row.service_id)
  ElMessage.success('已删除')
  load()
}

async function openSlotDialog(svc) {
  currentServiceId.value = svc.service_id
  const res = await servicesApi.slots(svc.service_id)
  slots.value = res.items || res || []
  slotDialog.value = true
}

async function addSlot() {
  await servicesApi.addSlot(currentServiceId.value, slotForm)
  ElMessage.success('时段已添加')
  const res = await servicesApi.slots(currentServiceId.value)
  slots.value = res.items || res || []
  showAddSlot.value = false
}

onMounted(load)
</script>

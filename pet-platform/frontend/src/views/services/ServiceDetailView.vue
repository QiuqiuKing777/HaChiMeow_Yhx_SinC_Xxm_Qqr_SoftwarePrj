<template>
  <NavBar>
    <div v-loading="loading">
      <div v-if="service" class="detail-wrap">
        <el-row :gutter="32">
          <el-col :span="10">
            <img :src="service.cover_image || service.image_url || '/placeholder.jpg'" class="main-img" />
          </el-col>
          <el-col :span="14">
            <h2>{{ service.service_name }}</h2>
            <el-tag>{{ service.service_type }}</el-tag>
            <div class="price">¥{{ service.price }}</div>
            <div class="desc">{{ service.description }}</div>
            <div class="publisher">服务方：{{ service.publisher_name }}</div>

            <div style="margin-top:20px">
              <h4>选择预约时间</h4>
              <div v-if="slots.length === 0" class="no-slot">暂无可用时段</div>
              <div class="slot-grid">
                <div v-for="slot in slots" :key="slot.slot_id"
                  class="slot-item"
                  :class="{ selected: selectedSlot === slot.slot_id, disabled: slot.available <= 0 }"
                  @click="selectSlot(slot)">
                  <div>{{ slot.slot_date }} {{ slot.slot_time }}</div>
                  <div class="slot-remain">剩余 {{ slot.available }}</div>
                </div>
              </div>
            </div>

            <el-form v-if="selectedSlot" :model="form" style="margin-top:16px">
              <el-form-item label="备注">
                <el-input v-model="form.remark" type="textarea" rows="2" placeholder="可填写特殊要求" />
              </el-form-item>
              <el-button type="primary" @click="submitBooking" :loading="submitting">立即预约</el-button>
            </el-form>
          </el-col>
        </el-row>
      </div>
    </div>
  </NavBar>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import NavBar from '@/components/NavBar.vue'
import { servicesApi, bookingsApi } from '@/api'
import { useUserStore } from '@/stores/user'

const route   = useRoute()
const router  = useRouter()
const userStore = useUserStore()

const service      = ref(null)
const slots        = ref([])
const loading      = ref(false)
const submitting   = ref(false)
const selectedSlot = ref(null)
const form         = reactive({ remark: '' })

async function loadData() {
  loading.value = true
  try {
    const id = route.params.id
    service.value = await servicesApi.get(id)
    const slotsRes = await servicesApi.slots(id)
    slots.value = Array.isArray(slotsRes) ? slotsRes : (slotsRes.items || [])
  } finally {
    loading.value = false
  }
}

function selectSlot(slot) {
  if (slot.available <= 0) return
  selectedSlot.value = slot.slot_id
}

async function submitBooking() {
  if (!userStore.isLoggedIn) { router.push('/login'); return }
  submitting.value = true
  try {
    await bookingsApi.create({ slot_id: selectedSlot.value, remark: form.remark })
    ElMessage.success('预约成功')
    router.push('/bookings')
  } finally {
    submitting.value = false
  }
}

onMounted(loadData)
</script>

<style scoped>
.detail-wrap { max-width: 960px; margin: 0 auto; }
.main-img { width: 100%; border-radius: 12px; }
.price { color: #f56c6c; font-size: 28px; font-weight: 700; margin: 16px 0; }
.desc { color: #606266; line-height: 1.8; margin-bottom: 8px; }
.publisher { color: #909399; font-size: 13px; }
.slot-grid { display: flex; flex-wrap: wrap; gap: 10px; margin-top: 8px; }
.slot-item { padding: 8px 14px; border: 1px solid #dcdfe6; border-radius: 8px; cursor: pointer; font-size: 13px; text-align: center; }
.slot-item:hover { border-color: #409eff; }
.slot-item.selected { border-color: #409eff; background: #ecf5ff; color: #409eff; }
.slot-item.disabled { opacity: .5; cursor: not-allowed; }
.slot-remain { font-size: 11px; color: #909399; margin-top: 2px; }
.no-slot { color: #c0c4cc; font-size: 14px; }
</style>

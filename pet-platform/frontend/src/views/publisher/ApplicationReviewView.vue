<template>
  <div>
    <div style="display:flex;justify-content:space-between;margin-bottom:16px">
      <h2>领养申请审核</h2>
      <el-select v-model="statusFilter" placeholder="筛选状态" clearable style="width:140px" @change="load">
        <el-option label="待审核" value="pending" />
        <el-option label="已通过" value="approved" />
        <el-option label="已拒绝" value="rejected" />
      </el-select>
    </div>
    <el-table :data="applications" border v-loading="loading">
      <el-table-column label="宠物" prop="pet_name" width="100" />
      <el-table-column label="申请人" prop="applicant_name" width="100" />
      <el-table-column label="申请理由" prop="reason" show-overflow-tooltip />
      <el-table-column label="居住条件" prop="living_condition" show-overflow-tooltip />
      <el-table-column label="时间" prop="created_at" width="150" />
      <el-table-column label="状态" width="90">
        <template #default="{ row }">
          <el-tag :type="{ pending:'warning', approved:'success', rejected:'danger' }[row.status]">
            {{ { pending:'待审核', approved:'已通过', rejected:'已拒绝' }[row.status] }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="150">
        <template #default="{ row }">
          <template v-if="row.status === 'pending'">
            <el-button size="small" type="success" @click="review(row, 'approved')">通过</el-button>
            <el-button size="small" type="danger" @click="openReject(row)">拒绝</el-button>
          </template>
        </template>
      </el-table-column>
    </el-table>
    <el-pagination v-if="total > 0" background layout="prev,pager,next,total"
      :total="total" :page-size="10" v-model:current-page="page"
      @current-change="load" style="margin-top:16px;justify-content:center;display:flex" />

    <el-dialog v-model="rejectDialog" title="填写拒绝原因" width="400px">
      <el-input v-model="rejectComment" type="textarea" rows="3" placeholder="请填写拒绝原因" />
      <template #footer>
        <el-button @click="rejectDialog = false">取消</el-button>
        <el-button type="danger" @click="confirmReject">确认拒绝</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { adoptionsApi } from '@/api'

const applications = ref([])
const total        = ref(0)
const page         = ref(1)
const loading      = ref(false)
const statusFilter = ref('pending')
const rejectDialog = ref(false)
const rejectComment = ref('')
const currentRow   = ref(null)

async function load() {
  loading.value = true
  try {
    const res = await adoptionsApi.publisherList({ page: page.value, per_page: 10, status: statusFilter.value })
    applications.value = res.items || []
    total.value = res.total || 0
  } finally { loading.value = false }
}

async function review(row, status, comment = '') {
  await adoptionsApi.review(row.application_id, { status, comment })
  ElMessage.success(status === 'approved' ? '已通过' : '已拒绝')
  load()
}

function openReject(row) {
  currentRow.value = row
  rejectComment.value = ''
  rejectDialog.value = true
}

async function confirmReject() {
  await review(currentRow.value, 'rejected', rejectComment.value)
  rejectDialog.value = false
}

onMounted(load)
</script>

<template>
  <div>
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:16px">
      <h2 style="margin:0">领养申请审核</h2>
      <el-select v-model="statusFilter" placeholder="筛选状态" clearable style="width:150px" @change="load">
        <el-option label="待审核" value="pending" />
        <el-option label="需补材料" value="supplement" />
        <el-option label="已通过" value="approved" />
        <el-option label="已拒绝" value="rejected" />
      </el-select>
    </div>

    <el-table :data="applications" border v-loading="loading" row-key="application_id">
      <el-table-column label="宠物" width="110">
        <template #default="{ row }">{{ row.pet?.pet_name }}</template>
      </el-table-column>
      <el-table-column label="申请人" width="110">
        <template #default="{ row }">{{ row.applicant?.nickname }}</template>
      </el-table-column>
      <el-table-column label="居住情况" show-overflow-tooltip>
        <template #default="{ row }">{{ row.housing_info }}</template>
      </el-table-column>
      <el-table-column label="联系方式" width="130">
        <template #default="{ row }">{{ row.contact_info || '—' }}</template>
      </el-table-column>
      <el-table-column label="申请时间" width="160">
        <template #default="{ row }">{{ row.submitted_at?.substring(0, 16) }}</template>
      </el-table-column>
      <el-table-column label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="statusType(row.review_status)">{{ statusLabel(row.review_status) }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="审核意见" width="140" show-overflow-tooltip>
        <template #default="{ row }">{{ row.review_remark || '—' }}</template>
      </el-table-column>
      <el-table-column label="操作" width="200" fixed="right">
        <template #default="{ row }">
          <el-button size="small" @click="openDetail(row)">详情</el-button>
          <template v-if="row.review_status === 'pending' || row.review_status === 'supplement'">
            <el-button size="small" type="success" @click="doApprove(row)">通过</el-button>
            <el-button size="small" type="danger"  @click="openRemarkDialog(row, 'rejected')">拒绝</el-button>
            <el-button size="small" type="warning" @click="openRemarkDialog(row, 'supplement')">补材料</el-button>
          </template>
        </template>
      </el-table-column>
    </el-table>

    <el-pagination v-if="total > 0" background layout="prev,pager,next,total"
      :total="total" :page-size="10" v-model:current-page="page"
      @current-change="load" style="margin-top:16px;justify-content:center;display:flex" />

    <!-- 详情抽屉 -->
    <el-drawer v-model="detailVisible" title="申请详情" size="420px">
      <el-descriptions :column="1" border v-if="detailRow">
        <el-descriptions-item label="宠物">{{ detailRow.pet?.pet_name }}</el-descriptions-item>
        <el-descriptions-item label="申请人">{{ detailRow.applicant?.nickname }}</el-descriptions-item>
        <el-descriptions-item label="联系方式">{{ detailRow.contact_info || '—' }}</el-descriptions-item>
        <el-descriptions-item label="居住情况">{{ detailRow.housing_info }}</el-descriptions-item>
        <el-descriptions-item label="养宠经验">{{ detailRow.pet_experience || '—' }}</el-descriptions-item>
        <el-descriptions-item label="家庭态度">{{ detailRow.family_attitude || '—' }}</el-descriptions-item>
        <el-descriptions-item label="领养承诺">{{ detailRow.promise_statement }}</el-descriptions-item>
        <el-descriptions-item label="申请时间">{{ detailRow.submitted_at?.substring(0, 16) }}</el-descriptions-item>
        <el-descriptions-item label="当前状态">
          <el-tag :type="statusType(detailRow.review_status)">{{ statusLabel(detailRow.review_status) }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="审核意见" v-if="detailRow.review_remark">{{ detailRow.review_remark }}</el-descriptions-item>
      </el-descriptions>
      <div style="margin-top:20px;display:flex;gap:10px"
           v-if="detailRow && (detailRow.review_status === 'pending' || detailRow.review_status === 'supplement')">
        <el-button type="success" @click="doApprove(detailRow); detailVisible=false">通过</el-button>
        <el-button type="danger"  @click="openRemarkDialog(detailRow, 'rejected'); detailVisible=false">拒绝</el-button>
        <el-button type="warning" @click="openRemarkDialog(detailRow, 'supplement'); detailVisible=false">要求补材料</el-button>
      </div>
    </el-drawer>

    <!-- 填写意见弹窗（拒绝 / 补材料） -->
    <el-dialog v-model="remarkDialog" :title="remarkAction === 'rejected' ? '填写拒绝原因' : '填写补充要求'" width="420px">
      <el-input v-model="remarkText" type="textarea" :rows="4"
        :placeholder="remarkAction === 'rejected' ? '请填写拒绝原因（将通知申请人）' : '请说明需要申请人补充哪些材料'" />
      <template #footer>
        <el-button @click="remarkDialog = false">取消</el-button>
        <el-button :type="remarkAction === 'rejected' ? 'danger' : 'warning'" @click="confirmRemark">确认</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { adoptionsApi } from '@/api'

const applications  = ref([])
const total         = ref(0)
const page          = ref(1)
const loading       = ref(false)
const statusFilter  = ref('pending')

const detailVisible = ref(false)
const detailRow     = ref(null)

const remarkDialog  = ref(false)
const remarkText    = ref('')
const remarkAction  = ref('')   // 'rejected' | 'supplement'
const remarkRow     = ref(null)

const statusLabel = s => ({ pending:'待审核', approved:'已通过', rejected:'已拒绝', supplement:'需补材料', cancelled:'已取消' })[s] || s
const statusType  = s => ({ pending:'warning', approved:'success', rejected:'danger', supplement:'info', cancelled:'' })[s] || ''

async function load() {
  loading.value = true
  try {
    const res = await adoptionsApi.publisherList({ page: page.value, per_page: 10, status: statusFilter.value })
    applications.value = res.items || []
    total.value = res.total || 0
  } finally { loading.value = false }
}

function openDetail(row) {
  detailRow.value = row
  detailVisible.value = true
}

async function doApprove(row) {
  await adoptionsApi.review(row.application_id, { review_status: 'approved', review_remark: '' })
  ElMessage.success('已通过')
  load()
}

function openRemarkDialog(row, action) {
  remarkRow.value    = row
  remarkAction.value = action
  remarkText.value   = ''
  remarkDialog.value = true
}

async function confirmRemark() {
  if (!remarkText.value.trim()) {
    ElMessage.warning('请填写意见后再提交')
    return
  }
  await adoptionsApi.review(remarkRow.value.application_id, {
    review_status: remarkAction.value,
    review_remark: remarkText.value.trim(),
  })
  ElMessage.success(remarkAction.value === 'rejected' ? '已拒绝' : '已要求补充材料，申请人将收到通知')
  remarkDialog.value = false
  load()
}

onMounted(load)
</script>

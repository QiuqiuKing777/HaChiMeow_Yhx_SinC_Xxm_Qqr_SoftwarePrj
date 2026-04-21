<template>
  <NavBar>
    <h2>我的领养申请</h2>
    <div v-loading="loading">
      <el-empty v-if="!loading && applications.length === 0" description="暂无领养申请" />
      <el-table :data="applications" border>
        <el-table-column label="宠物" width="120">
          <template #default="{ row }">{{ row.pet?.pet_name }}</template>
        </el-table-column>
        <el-table-column label="种类" width="100">
          <template #default="{ row }">{{ row.pet?.species }}</template>
        </el-table-column>
        <el-table-column label="居住情况" show-overflow-tooltip>
          <template #default="{ row }">{{ row.housing_info }}</template>
        </el-table-column>
        <el-table-column label="申请时间" prop="submitted_at" width="160" />
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="statusType(row.review_status)">{{ statusLabel(row.review_status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="审核意见" prop="review_remark" width="160" show-overflow-tooltip />
        <el-table-column label="操作" width="80">
          <template #default="{ row }">
            <el-popconfirm title="确定撤销申请？" @confirm="cancel(row)" v-if="row.review_status === 'pending'">
              <template #reference><el-button size="small" type="danger">撤销</el-button></template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>
      <el-pagination v-if="total > 0" background layout="prev,pager,next,total"
        :total="total" :page-size="10" v-model:current-page="page"
        @current-change="load" style="margin-top:16px;justify-content:center;display:flex" />
    </div>
  </NavBar>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import NavBar from '@/components/NavBar.vue'
import { adoptionsApi } from '@/api'

const applications = ref([])
const total   = ref(0)
const page    = ref(1)
const loading = ref(false)

const statusLabel = s => ({ pending:'审核中', approved:'已通过', rejected:'已拒绝' })[s] || s
const statusType  = s => ({ pending:'warning', approved:'success', rejected:'danger' })[s] || ''

async function load() {
  loading.value = true
  try {
    const res = await adoptionsApi.myList({ page: page.value, per_page: 10 })
    applications.value = res.items || []
    total.value = res.total || 0
  } catch {} finally {
    loading.value = false
  }
}

async function cancel(row) {
  await adoptionsApi.cancel(row.application_id)
  ElMessage.success('已撤销')
  load()
}

onMounted(load)
</script>

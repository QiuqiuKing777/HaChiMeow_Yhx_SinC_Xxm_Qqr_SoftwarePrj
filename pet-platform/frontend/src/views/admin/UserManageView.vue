<template>
  <div class="admin-page">
    <!-- 页面横幅 -->
    <div class="page-banner">
      <div>
        <h2 class="page-banner-title">用户管理</h2>
        <p class="page-banner-sub">管理平台所有注册用户，可修改状态与角色权限</p>
      </div>
    </div>

    <!-- 筛选 -->
    <div class="page-card filter-card">
      <el-row :gutter="16" align="middle">
        <el-col :span="6">
          <el-input v-model="filters.keyword" placeholder="搜索用户名/昵称" clearable @change="load" />
        </el-col>
        <el-col :span="4">
          <el-select v-model="filters.role_type" placeholder="角色" clearable @change="load">
            <el-option label="普通用户" value="user" />
            <el-option label="发布方" value="publisher" />
            <el-option label="管理员" value="admin" />
          </el-select>
        </el-col>
        <el-col :span="4">
          <el-select v-model="filters.status" placeholder="账号状态" clearable @change="load">
            <el-option label="正常" value="active" />
            <el-option label="已禁用" value="disabled" />
          </el-select>
        </el-col>
        <el-col :span="4">
          <el-button type="primary" @click="load">搜索</el-button>
          <el-button @click="resetFilters">重置</el-button>
        </el-col>
      </el-row>
    </div>

    <!-- 表格 -->
    <div class="page-card">
      <div class="card-toolbar">
        <span class="card-title">用户列表</span>
        <el-tag type="info" size="small">共 {{ total }} 条</el-tag>
      </div>
      <el-table :data="users" v-loading="loading" stripe class="admin-table" style="width:100%;font-size:16px">
        <el-table-column prop="user_id" label="ID" width="70" />
        <el-table-column label="头像" width="70">
          <template #default="{ row }">
            <el-avatar :size="32" :src="row.avatar" style="background:#409eff">
              {{ (row.nickname?.charAt(0) || 'U').toUpperCase() }}
            </el-avatar>
          </template>
        </el-table-column>
        <el-table-column prop="username" label="用户名" min-width="130" />
        <el-table-column prop="nickname" label="昵称" width="120" />
        <el-table-column prop="phone" label="手机号" width="130" />
        <el-table-column label="角色" width="100">
          <template #default="{ row }">
            <el-tag :type="roleTagType(row.role_type)">{{ roleLabel(row.role_type) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 'active' ? 'success' : 'danger'">
              {{ row.status === 'active' ? '正常' : '已禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="注册时间" width="160">
          <template #default="{ row }">{{ row.created_at?.substring(0, 10) }}</template>
        </el-table-column>
        <el-table-column label="操作" fixed="right" width="160">
          <template #default="{ row }">
            <el-button
              v-if="row.role_type !== 'admin'"
              :type="row.status === 'active' ? 'danger' : 'success'"
              size="small"
              @click="toggleStatus(row)"
            >
              {{ row.status === 'active' ? '禁用' : '解禁' }}
            </el-button>
            <el-tag type="info" v-else>管理员</el-tag>
          </template>
        </el-table-column>
      </el-table>

      <el-pagination
        background layout="prev,pager,next,total" :total="total"
        :page-size="20" v-model:current-page="page"
        @current-change="load" style="margin-top:16px;display:flex;justify-content:flex-end"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { adminApi } from '@/api'

const users   = ref([])
const total   = ref(0)
const page    = ref(1)
const loading = ref(false)
const filters = reactive({ keyword: '', role_type: '', status: '' })

const roleLabel   = t => ({ user: '普通用户', publisher: '发布方', admin: '管理员' })[t] || t
const roleTagType = t => ({ user: '', publisher: 'warning', admin: 'danger' })[t] || ''

async function load() {
  loading.value = true
  try {
    const res = await adminApi.users({ page: page.value, per_page: 20, ...filters })
    users.value = res.items || []
    total.value = res.total || 0
  } finally { loading.value = false }
}

function resetFilters() {
  Object.assign(filters, { keyword: '', role_type: '', status: '' })
  page.value = 1
  load()
}

async function toggleStatus(row) {
  const nextStatus = row.status === 'active' ? 'disabled' : 'active'
  const action     = nextStatus === 'disabled' ? '禁用' : '解禁'
  await ElMessageBox.confirm(`确认要${action}用户「${row.username}」吗？`, '操作确认', {
    type: 'warning', confirmButtonText: '确认', cancelButtonText: '取消'
  })
  await adminApi.setUserStatus(row.user_id, { status: nextStatus })
  ElMessage.success(`已${action}`)
  load()
}

onMounted(load)
</script>

<style scoped>
.admin-page { padding-bottom: 20px; }

.page-banner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 60%, #0f3460 100%);
  border-radius: 12px;
  padding: 20px 28px;
  margin-bottom: 16px;
}
.page-banner-title { color: #fff; font-size: 18px; font-weight: 700; margin: 0 0 4px; }
.page-banner-sub   { color: #a0b0d0; font-size: 13px; margin: 0; }

.page-card {
  background: #fff;
  border-radius: 10px;
  padding: 18px 20px;
  box-shadow: 0 1px 6px rgba(0,21,41,.06);
  margin-bottom: 16px;
}
.filter-card { padding: 14px 20px; }

.card-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 14px;
}
.card-title {
  font-size: 15px;
  font-weight: 600;
  color: #1f2937;
  padding-left: 10px;
  border-left: 3px solid #409eff;
}

.admin-table :deep(th.el-table__cell) {
  background: #f5f7fa;
  color: #606266;
  font-weight: 600;
  font-size: 16px !important;
}
.admin-table :deep(td.el-table__cell) {
  font-size: 16px !important;
}
</style>

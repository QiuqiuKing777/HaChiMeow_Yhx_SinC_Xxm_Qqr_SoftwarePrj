<template>
  <NavBar>
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:16px">
      <h2>消息通知</h2>
      <el-button size="small" @click="readAll">全部已读</el-button>
    </div>
    <div v-loading="loading">
      <el-empty v-if="!loading && notifications.length === 0" description="暂无通知" />
      <div v-for="n in notifications" :key="n.notification_id"
        class="notif-item" :class="{ unread: !n.is_read }" @click="readOne(n)">
        <div class="notif-title">{{ n.title }}</div>
        <div class="notif-content">{{ n.content }}</div>
        <div class="notif-time">{{ n.created_at }}</div>
      </div>
      <el-pagination v-if="total > 0" background layout="prev,pager,next"
        :total="total" :page-size="20" v-model:current-page="page"
        @current-change="load" style="margin-top:16px;justify-content:center;display:flex" />
    </div>
  </NavBar>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import NavBar from '@/components/NavBar.vue'
import { userApi } from '@/api'

const notifications = ref([])
const total   = ref(0)
const page    = ref(1)
const loading = ref(false)

async function load() {
  loading.value = true
  try {
    const res = await userApi.getNotifications({ page: page.value, per_page: 20 })
    notifications.value = res.items || []
    total.value = res.total || 0
  } finally {
    loading.value = false
  }
}

async function readOne(n) {
  if (!n.is_read) {
    await userApi.readNotification(n.notification_id)
    n.is_read = true
  }
}

async function readAll() {
  await userApi.readAllNotifications()
  notifications.value.forEach(n => n.is_read = true)
}

onMounted(load)
</script>

<style scoped>
.notif-item { padding: 14px 16px; border-bottom: 1px solid #f0f0f0; cursor: pointer; }
.notif-item:hover { background: #f9f9f9; }
.notif-item.unread { background: #ecf5ff; }
.notif-title { font-weight: 600; font-size: 14px; margin-bottom: 4px; }
.notif-content { color: #606266; font-size: 13px; }
.notif-time { color: #c0c4cc; font-size: 12px; margin-top: 4px; }
</style>

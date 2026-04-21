<template>
  <NavBar>
    <h2>我的收藏</h2>
    <el-tabs v-model="tab" @tab-change="load">
      <el-tab-pane label="宠物" name="pet" />
      <el-tab-pane label="商品" name="product" />
    </el-tabs>
    <div v-loading="loading">
      <el-empty v-if="!loading && items.length === 0" description="暂无收藏" />
      <el-row :gutter="16">
        <el-col v-for="item in items" :key="item.favorite_id" :xs="12" :sm="8" :md="6">
          <el-card :body-style="{ padding: '0' }" class="fav-card">
            <img :src="item.image_url || '/placeholder.jpg'" class="fav-img"
              @click="$router.push(tab === 'pet' ? '/pets/' + item.target_id : '/products/' + item.target_id)" />
            <div class="fav-info">
              <div class="fav-name">{{ item.target_name }}</div>
              <el-button type="danger" size="small" plain @click="removeFav(item)">取消收藏</el-button>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>
  </NavBar>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import NavBar from '@/components/NavBar.vue'
import { userApi } from '@/api'

const tab     = ref('pet')
const items   = ref([])
const loading = ref(false)

async function load() {
  loading.value = true
  try {
    const res = await userApi.getFavorites({ target_type: tab.value })
    items.value = res.items || res || []
  } finally {
    loading.value = false
  }
}

async function removeFav(item) {
  await userApi.removeFavorite(item.target_type, item.target_id)
  ElMessage.success('已取消收藏')
  load()
}

onMounted(load)
</script>

<style scoped>
.fav-card { margin-bottom: 16px; cursor: pointer; }
.fav-img { width: 100%; height: 140px; object-fit: cover; }
.fav-info { padding: 10px; display: flex; justify-content: space-between; align-items: center; }
.fav-name { font-size: 14px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; max-width: 100px; }
</style>

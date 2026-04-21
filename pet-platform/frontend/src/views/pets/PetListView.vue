<template>
  <NavBar>
    <!-- 筛选 -->
    <el-card class="filter-card">
      <el-row :gutter="16" align="middle">
        <el-col :span="6">
          <el-input v-model="filters.keyword" placeholder="搜索宠物名称" clearable @change="loadPets" :prefix-icon="Search" />
        </el-col>
        <el-col :span="4">
          <el-select v-model="filters.species" placeholder="选择种类" clearable @change="loadPets">
            <el-option label="猫" value="猫" />
            <el-option label="狗" value="狗" />
            <el-option label="其他" value="其他" />
          </el-select>
        </el-col>
        <el-col :span="4">
          <el-select v-model="filters.gender" placeholder="性别" clearable @change="loadPets">
            <el-option label="公" value="male" />
            <el-option label="母" value="female" />
          </el-select>
        </el-col>
        <el-col :span="5">
          <el-input v-model="filters.location" placeholder="所在地区" clearable @change="loadPets" />
        </el-col>
        <el-col :span="5">
          <el-button type="primary" :icon="Search" @click="loadPets">搜索</el-button>
          <el-button @click="resetFilters">重置</el-button>
        </el-col>
      </el-row>
    </el-card>

    <!-- 列表 -->
    <div v-loading="loading" style="margin-top:20px">
      <el-empty v-if="!loading && pets.length === 0" description="暂无符合条件的宠物" />
      <el-row :gutter="16">
        <el-col :span="6" v-for="pet in pets" :key="pet.pet_id" style="margin-bottom:20px">
          <PetCard :pet="pet" />
        </el-col>
      </el-row>
      <el-pagination
        v-if="total > 0"
        background layout="prev,pager,next,total"
        :total="total" :page-size="pageSize" v-model:current-page="page"
        @current-change="loadPets" style="margin-top:20px;justify-content:center;display:flex"
      />
    </div>
  </NavBar>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { Search } from '@element-plus/icons-vue'
import NavBar from '@/components/NavBar.vue'
import PetCard from '@/components/PetCard.vue'
import { petsApi } from '@/api'

const pets     = ref([])
const total    = ref(0)
const page     = ref(1)
const pageSize = 12
const loading  = ref(false)
const filters  = reactive({ keyword: '', species: '', gender: '', location: '' })

async function loadPets() {
  loading.value = true
  try {
    const res = await petsApi.list({ page: page.value, per_page: pageSize, ...filters })
    pets.value  = res.items || []
    total.value = res.total || 0
  } finally {
    loading.value = false
  }
}

function resetFilters() {
  Object.assign(filters, { keyword: '', species: '', gender: '', location: '' })
  page.value = 1
  loadPets()
}

onMounted(loadPets)
</script>

<style scoped>
.filter-card { margin-bottom: 16px; }
</style>

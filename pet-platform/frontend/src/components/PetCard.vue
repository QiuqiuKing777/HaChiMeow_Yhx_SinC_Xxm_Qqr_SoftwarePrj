<template>
  <el-card class="pet-card" @click="$router.push(`/pets/${pet.pet_id}`)">
    <div class="pet-img-wrap">
      <img :src="pet.cover_image || '/placeholder.jpg'" class="pet-img" alt="宠物图片" />
      <el-tag class="species-tag" :type="pet.species === '猫' ? 'warning' : 'success'" size="small">{{ pet.species }}</el-tag>
    </div>
    <div class="pet-info">
      <div class="pet-name">{{ pet.pet_name }}</div>
      <div class="pet-meta">
        <span>{{ pet.breed || '未知品种' }}</span>
        <span>{{ genderLabel }}</span>
        <span>{{ pet.age_desc || '月龄未知' }}</span>
      </div>
      <div class="pet-location"><el-icon><Location /></el-icon> {{ pet.location || '地址未知' }}</div>
    </div>
  </el-card>
</template>

<script setup>
import { computed } from 'vue'
import { Location } from '@element-plus/icons-vue'

const props = defineProps({ pet: { type: Object, required: true } })
const genderLabel = computed(() => ({ male: '公', female: '母', unknown: '性别未知' })[props.pet.gender] || '未知')
</script>

<style scoped>
.pet-card { cursor: pointer; transition: all .2s; border-radius: 10px; overflow: hidden; }
.pet-card:hover { box-shadow: 0 8px 24px rgba(0,0,0,.12); transform: translateY(-2px); }
.pet-img-wrap { position: relative; }
.pet-img { width: 100%; height: 180px; object-fit: cover; display: block; }
.species-tag { position: absolute; top: 8px; left: 8px; }
.pet-info { padding: 12px; }
.pet-name { font-size: 16px; font-weight: 600; color: #303133; }
.pet-meta { display: flex; gap: 8px; font-size: 12px; color: #909399; margin: 6px 0; flex-wrap: wrap; }
.pet-location { font-size: 12px; color: #c0c4cc; display: flex; align-items: center; gap: 4px; }
</style>

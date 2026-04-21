<template>
  <NavBar>
    <div style="max-width:680px;margin:0 auto">
      <h2>申请领养 · {{ pet?.pet_name }}</h2>
      <el-alert type="info" :closable="false" style="margin-bottom:20px"
        description="请如实填写以下信息，发布方将根据您的情况进行审核。我们希望每只宠物都能找到真正适合的家庭。" show-icon />

      <el-form :model="form" :rules="rules" ref="formRef" label-position="top">
        <el-form-item label="居住情况（房屋类型、面积、是否允许养宠等）" prop="housing_info">
          <el-input v-model="form.housing_info" type="textarea" :rows="3" placeholder="例如：租住两居室，房东知情并同意养宠，面积约60㎡" />
        </el-form-item>
        <el-form-item label="既往养宠经验">
          <el-input v-model="form.pet_experience" type="textarea" :rows="3" placeholder="如从未养过请填写无" />
        </el-form-item>
        <el-form-item label="家庭成员对领养的态度">
          <el-input v-model="form.family_attitude" type="textarea" :rows="2" placeholder="家庭成员是否支持，是否有过敏史等" />
        </el-form-item>
        <el-form-item label="您的领养承诺（必填）" prop="promise_statement">
          <el-input v-model="form.promise_statement" type="textarea" :rows="4"
            placeholder="请承诺：不遗弃、不虐待、定期检查身体、如发生变化第一时间联系发布方..." />
        </el-form-item>
        <el-form-item label="联系方式（手机/微信）">
          <el-input v-model="form.contact_info" placeholder="方便发布方联系您" />
        </el-form-item>
        <div style="display:flex;gap:12px;margin-top:8px">
          <el-button @click="$router.back()">返回</el-button>
          <el-button type="primary" :loading="loading" @click="onSubmit">提交申请</el-button>
        </div>
      </el-form>
    </div>
  </NavBar>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import NavBar from '@/components/NavBar.vue'
import { petsApi, adoptionsApi } from '@/api'

const route   = useRoute()
const router  = useRouter()
const pet     = ref(null)
const formRef = ref()
const loading = ref(false)
const form    = ref({ housing_info: '', pet_experience: '', family_attitude: '', promise_statement: '', contact_info: '' })

const rules = {
  housing_info:      [{ required: true, message: '请描述您的居住情况', trigger: 'blur' }],
  promise_statement: [{ required: true, message: '请填写领养承诺', trigger: 'blur' }],
}

async function onSubmit() {
  try {
    await formRef.value.validate()
  } catch {
    return // 表单验证失败，Element Plus 已自动显示提示
  }
  loading.value = true
  try {
    await adoptionsApi.submit({ pet_id: Number(route.params.id), ...form.value })
    ElMessage.success('申请已提交，请等待发布方审核')
    router.push('/user/applications')
  } catch {
    // axios 拦截器已展示错误
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  pet.value = await petsApi.get(route.params.id)
})
</script>

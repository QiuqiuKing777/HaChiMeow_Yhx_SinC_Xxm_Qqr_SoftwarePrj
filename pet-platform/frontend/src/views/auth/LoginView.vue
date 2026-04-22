<template>
  <div class="login-page">
    <el-card class="login-card">
      <h2 class="title">登录账号</h2>
      <el-form :model="form" :rules="rules" ref="formRef" label-position="top" @submit.prevent="onSubmit">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="form.username" placeholder="请输入用户名" clearable />
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input v-model="form.password" type="password" placeholder="请输入密码" show-password @keyup.enter="onSubmit" />
        </el-form-item>
        <el-button type="primary" :loading="loading" style="width:100%;margin-top:8px" @click="onSubmit">
          登录
        </el-button>
      </el-form>
      <div class="bottom-link">
        还没有账号？<router-link to="/register">立即注册</router-link>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()
const formRef = ref()
const loading = ref(false)
const form = ref({ username: '', password: '' })

const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
}

async function onSubmit() {
  await formRef.value.validate()
  loading.value = true
  try {
    await userStore.login(form.value)
    ElMessage.success('登录成功')

    const redirect = route.query.redirect
    const roleType = userStore.userInfo?.role_type

    if (redirect) {
      router.push(redirect)
    } else if (roleType === 'admin') {
      router.push('/admin')
    } else if (roleType === 'publisher') {
      router.push('/publisher')
    } else {
      router.push('/')
    }
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}
</script>


<style scoped>
.login-page { min-height: 100vh; display: flex; align-items: center; justify-content: center; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
.login-card { width: 400px; border-radius: 12px; padding: 12px; }
.title { text-align: center; margin-bottom: 24px; color: #303133; }
.bottom-link { text-align: center; margin-top: 16px; color: #909399; font-size: 14px; }
</style>

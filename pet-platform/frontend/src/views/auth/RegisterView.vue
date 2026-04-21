<template>
  <div class="register-page">
    <el-card class="register-card">
      <h2 class="title">注册账号</h2>
      <el-form :model="form" :rules="rules" ref="formRef" label-position="top">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="form.username" placeholder="3-50个字符" clearable />
        </el-form-item>
        <el-form-item label="昵称" prop="nickname">
          <el-input v-model="form.nickname" placeholder="用于展示的名字" clearable />
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input v-model="form.password" type="password" show-password placeholder="至少6位" />
        </el-form-item>
        <el-form-item label="手机号">
          <el-input v-model="form.phone" placeholder="选填" clearable />
        </el-form-item>
        <el-form-item label="注册身份" prop="role_type">
          <el-radio-group v-model="form.role_type">
            <el-radio value="user">普通用户（领养/购物）</el-radio>
            <el-radio value="publisher">发布方（发布宠物/商品）</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-button type="primary" :loading="loading" style="width:100%;margin-top:8px" @click="onSubmit">
          注册
        </el-button>
      </el-form>
      <div class="bottom-link">
        已有账号？<router-link to="/login">立即登录</router-link>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/stores/user'

const router    = useRouter()
const userStore = useUserStore()
const formRef   = ref()
const loading   = ref(false)
const form      = ref({ username: '', nickname: '', password: '', phone: '', role_type: 'user' })

const rules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 50, message: '长度3-50', trigger: 'blur' },
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '至少6位', trigger: 'blur' },
  ],
  role_type: [{ required: true, message: '请选择注册身份', trigger: 'change' }],
}

async function onSubmit() {
  await formRef.value.validate()
  loading.value = true
  try {
    await userStore.register(form.value)
    ElMessage.success('注册成功，欢迎加入！')
    router.push('/')
  } catch {
    // 错误已由 axios 拦截器统一处理
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.register-page { min-height: 100vh; display: flex; align-items: center; justify-content: center; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
.register-card { width: 480px; border-radius: 12px; padding: 12px; }
.title { text-align: center; margin-bottom: 24px; color: #303133; }
.bottom-link { text-align: center; margin-top: 16px; color: #909399; font-size: 14px; }
</style>

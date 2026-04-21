<template>
  <NavBar>
    <el-row :gutter="24">
      <el-col :span="6">
        <el-card>
          <div class="avatar-wrap">
            <el-avatar :size="80" :src="userStore.userInfo?.avatar_url">{{ userStore.userInfo?.nickname?.charAt(0) }}</el-avatar>
            <div class="nick">{{ userStore.userInfo?.nickname }}</div>
            <el-tag size="small">{{ roleLabel }}</el-tag>
          </div>
          <el-menu :router="true" :default-active="$route.path" style="border:none;margin-top:12px">
            <el-menu-item index="/profile">个人资料</el-menu-item>
            <el-menu-item index="/favorites">我的收藏</el-menu-item>
            <el-menu-item index="/orders">我的订单</el-menu-item>
            <el-menu-item index="/applications">我的领养申请</el-menu-item>
            <el-menu-item index="/bookings">我的预约</el-menu-item>
            <el-menu-item index="/notifications">消息通知</el-menu-item>
          </el-menu>
        </el-card>
      </el-col>
      <el-col :span="18">
        <el-card>
          <template #header>个人资料</template>
          <el-form :model="form" label-width="90px" style="max-width:480px">
            <el-form-item label="昵称">
              <el-input v-model="form.nickname" />
            </el-form-item>
            <el-form-item label="手机号">
              <el-input v-model="form.phone" />
            </el-form-item>
            <el-form-item label="居住城市">
              <el-input v-model="form.city" />
            </el-form-item>
            <el-form-item label="个人简介">
              <el-input v-model="form.bio" type="textarea" rows="3" />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="saveProfile" :loading="saving">保存资料</el-button>
            </el-form-item>
          </el-form>

          <el-divider>收货地址</el-divider>
          <el-button type="primary" plain size="small" @click="showAddAddr = true" style="margin-bottom:12px">新增地址</el-button>
          <el-table :data="addresses" border size="small">
            <el-table-column label="收货人" prop="receiver_name" width="80" />
            <el-table-column label="手机" prop="phone" width="120" />
            <el-table-column label="地址" min-width="200">
              <template #default="{ row }">{{ row.province }}{{ row.city }}{{ row.district }}{{ row.detail }}</template>
            </el-table-column>
            <el-table-column label="默认" width="60">
              <template #default="{ row }"><el-tag v-if="row.is_default" type="success" size="small">默认</el-tag></template>
            </el-table-column>
            <el-table-column label="操作" width="120">
              <template #default="{ row }">
                <el-button size="small" @click="setDefault(row)" v-if="!row.is_default">设为默认</el-button>
                <el-popconfirm title="确定删除？" @confirm="deleteAddr(row)">
                  <template #reference><el-button size="small" type="danger">删除</el-button></template>
                </el-popconfirm>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>

    <!-- 新增地址弹窗 -->
    <el-dialog v-model="showAddAddr" title="新增收货地址" width="480px">
      <el-form :model="addrForm" label-width="80px">
        <el-form-item label="收货人"><el-input v-model="addrForm.receiver_name" /></el-form-item>
        <el-form-item label="手机号"><el-input v-model="addrForm.phone" /></el-form-item>
        <el-form-item label="省份"><el-input v-model="addrForm.province" /></el-form-item>
        <el-form-item label="城市"><el-input v-model="addrForm.city" /></el-form-item>
        <el-form-item label="区县"><el-input v-model="addrForm.district" /></el-form-item>
        <el-form-item label="详细地址"><el-input v-model="addrForm.detail" /></el-form-item>
        <el-form-item label="设为默认"><el-switch v-model="addrForm.is_default" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAddAddr = false">取消</el-button>
        <el-button type="primary" @click="saveAddr">保存</el-button>
      </template>
    </el-dialog>
  </NavBar>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import NavBar from '@/components/NavBar.vue'
import { userApi } from '@/api'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()
const saving    = ref(false)
const addresses = ref([])
const showAddAddr = ref(false)

const roleLabel = computed(() => ({ user:'普通用户', publisher:'发布方', admin:'管理员' })[userStore.userInfo?.role] || '')

const form = reactive({
  nickname: userStore.userInfo?.nickname || '',
  phone: userStore.userInfo?.phone || '',
  city: userStore.userInfo?.city || '',
  bio: userStore.userInfo?.bio || ''
})

const addrForm = reactive({ receiver_name:'', phone:'', province:'', city:'', district:'', detail:'', is_default: false })

async function saveProfile() {
  saving.value = true
  try {
    await userApi.updateProfile(form)
    await userStore.fetchMe()
    ElMessage.success('资料已保存')
  } finally {
    saving.value = false
  }
}

async function loadAddresses() {
  const res = await userApi.addresses()
  addresses.value = res.items || res || []
}

async function saveAddr() {
  await userApi.addAddress(addrForm)
  ElMessage.success('地址已添加')
  showAddAddr.value = false
  Object.assign(addrForm, { receiver_name: '', phone: '', province: '', city: '', district: '', detail: '', is_default: false })
  loadAddresses()
}

async function setDefault(row) {
  await userApi.updateAddress(row.address_id, { is_default: true })
  loadAddresses()
}

async function deleteAddr(row) {
  await userApi.deleteAddress(row.address_id)
  ElMessage.success('已删除')
  loadAddresses()
}

onMounted(loadAddresses)
</script>

<style scoped>
.avatar-wrap { text-align: center; padding: 12px 0; }
.nick { font-size: 16px; font-weight: 600; margin: 8px 0 4px; }
</style>

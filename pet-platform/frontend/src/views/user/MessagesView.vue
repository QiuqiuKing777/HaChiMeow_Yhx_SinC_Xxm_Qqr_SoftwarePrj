<template>
  <NavBar>
    <div class="chat-page">
      <!-- 头部 -->
      <div class="chat-header">
        <el-button text @click="$router.back()" style="padding:0">← 返回</el-button>
        <div class="chat-title">
          咨询 {{ otherUser?.nickname || '发布方' }}
          <el-tag v-if="petName" size="small" style="margin-left:8px">{{ petName }}</el-tag>
        </div>
      </div>

      <!-- 消息区 -->
      <div class="chat-body" ref="chatBody" v-loading="loading">
        <el-empty v-if="!loading && filteredMessages.length === 0" description="暂无消息，向发布方发起咨询吧" />
        <div
          v-for="msg in filteredMessages"
          :key="msg.message_id"
          :class="['msg-row', msg.sender_id === myId ? 'msg-row--self' : 'msg-row--other']"
        >
          <div class="msg-bubble">{{ msg.content }}</div>
          <div class="msg-time">{{ (msg.created_at || '').substring(0, 16).replace('T', ' ') }}</div>
        </div>
      </div>

      <!-- 输入区 -->
      <div class="chat-input">
        <el-input
          v-model="inputText"
          placeholder="输入消息，按 Enter 发送..."
          :maxlength="500"
          @keyup.enter.exact="sendMsg"
        />
        <el-button type="primary" :loading="sending" :disabled="!inputText.trim()" @click="sendMsg">
          发送
        </el-button>
      </div>
    </div>
  </NavBar>
</template>

<script setup>
import { ref, computed, onMounted, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import NavBar from '@/components/NavBar.vue'
import { userApi, petsApi } from '@/api'
import { useUserStore } from '@/stores/user'

const route     = useRoute()
const userStore = useUserStore()

const myId    = computed(() => userStore.userInfo?.user_id)
const otherId = computed(() => Number(route.query.to))
const petId   = computed(() => route.query.pet ? Number(route.query.pet) : null)

const petName      = ref('')
const allMessages  = ref([])
const otherUser    = ref(null)
const loading      = ref(false)
const sending      = ref(false)
const inputText    = ref('')
const chatBody     = ref()

const filteredMessages = computed(() =>
  allMessages.value
    .filter(m =>
      (m.sender_id === myId.value && m.receiver_id === otherId.value) ||
      (m.sender_id === otherId.value && m.receiver_id === myId.value)
    )
    .sort((a, b) => new Date(a.created_at) - new Date(b.created_at))
)

async function loadMessages() {
  loading.value = true
  try {
    const msgs = await userApi.messages()
    allMessages.value = msgs || []
    // 从消息中提取对方用户信息
    const otherMsg = allMessages.value.find(m => m.sender_id === otherId.value)
    if (otherMsg?.sender) otherUser.value = otherMsg.sender
  } catch {} finally {
    loading.value = false
    await scrollToBottom()
  }
}

async function scrollToBottom() {
  await nextTick()
  if (chatBody.value) chatBody.value.scrollTop = chatBody.value.scrollHeight
}

async function sendMsg() {
  const text = inputText.value.trim()
  if (!text) return
  sending.value = true
  try {
    await userApi.sendMessage({ receiver_id: otherId.value, content: text, pet_id: petId.value })
    inputText.value = ''
    await loadMessages()
  } catch {
    ElMessage.error('发送失败，请稍后重试')
  } finally {
    sending.value = false
  }
}

onMounted(async () => {
  if (petId.value) {
    try {
      const pet = await petsApi.get(petId.value)
      petName.value = pet.pet_name
      if (!otherUser.value && pet.publisher) otherUser.value = pet.publisher
    } catch {}
  }
  await loadMessages()
})
</script>

<style scoped>
.chat-page {
  display: flex;
  flex-direction: column;
  height: calc(100vh - 160px);
  min-height: 400px;
}
.chat-header {
  display: flex;
  align-items: center;
  gap: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid #e8e0ff;
  margin-bottom: 12px;
}
.chat-title {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}
.chat-body {
  flex: 1;
  overflow-y: auto;
  padding: 8px 4px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.msg-row {
  display: flex;
  flex-direction: column;
  max-width: 70%;
}
.msg-row--self  { align-self: flex-end;  align-items: flex-end; }
.msg-row--other { align-self: flex-start; align-items: flex-start; }
.msg-bubble {
  background: #f0eeff;
  border-radius: 12px 12px 4px 12px;
  padding: 8px 14px;
  font-size: 14px;
  color: #303133;
  word-break: break-word;
  line-height: 1.5;
}
.msg-row--self .msg-bubble {
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: #fff;
  border-radius: 12px 12px 12px 4px;
}
.msg-time {
  font-size: 11px;
  color: #bbb;
  margin-top: 4px;
}
.chat-input {
  display: flex;
  gap: 8px;
  padding-top: 12px;
  border-top: 1px solid #e8e0ff;
  margin-top: 8px;
}
</style>

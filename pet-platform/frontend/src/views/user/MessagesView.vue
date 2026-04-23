<template>
  <NavBar>
    <div class="chat-page">
      <!-- 头部 -->
      <div class="chat-header">
        <el-button text @click="$router.back()" style="padding:0">← 返回</el-button>
        <div class="chat-title">
          咨询 {{ currentOtherName }}
          <el-tag v-if="petName" size="small" style="margin-left:8px">{{ petName }}</el-tag>
        </div>
      </div>

      <div class="chat-layout">
        <div class="chat-sidebar" v-if="!hasExplicitTarget">
          <div class="sidebar-title">最近会话</div>
          <el-empty v-if="!loading && conversations.length === 0" description="暂无会话" />
          <div
            v-for="item in conversations"
            :key="item.otherId"
            :class="['conversation-item', item.otherId === selectedOtherId ? 'is-active' : '']"
            @click="selectConversation(item)"
          >
            <div class="conversation-name">{{ item.otherName }}</div>
            <div class="conversation-preview">{{ item.preview }}</div>
          </div>
        </div>

        <!-- 消息区 -->
        <div class="chat-main">
          <div class="chat-body" ref="chatBody" v-loading="loading">
            <el-empty v-if="!loading && !selectedOtherId" description="请先选择一个会话" />
            <el-empty v-else-if="!loading && filteredMessages.length === 0" description="暂无消息，向发布方发起咨询吧" />
            <div
              v-for="msg in filteredMessages"
              :key="msg.message_id"
              :class="['msg-row', msg.sender_id === myId ? 'msg-row--self' : 'msg-row--other']"
            >
              <div class="msg-card">
                <div class="msg-avatar">{{ getAvatarText(msg) }}</div>
                <div class="msg-content-wrap">
                  <div class="msg-meta">
                    <span class="msg-sender">{{ getSenderLabel(msg) }}</span>
                    <span class="msg-time">{{ (msg.created_at || '').substring(0, 16).replace('T', ' ') }}</span>
                  </div>
                  <div class="msg-bubble">{{ msg.content }}</div>
                </div>
              </div>
            </div>
          </div>

          <!-- 输入区 -->
          <div class="chat-input">
            <el-input
              v-model="inputText"
              placeholder="输入消息，按 Enter 发送..."
              :maxlength="500"
              :disabled="!selectedOtherId"
              @keyup.enter.exact="sendMsg"
            />
            <el-button type="primary" :loading="sending" :disabled="!inputText.trim() || !selectedOtherId" @click="sendMsg">
              发送
            </el-button>
          </div>
        </div>
      </div>
    </div>
  </NavBar>
</template>

<script setup>
import { ref, computed, onMounted, nextTick, watch } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import NavBar from '@/components/NavBar.vue'
import { userApi, petsApi } from '@/api'
import { useUserStore } from '@/stores/user'

const route     = useRoute()
const userStore = useUserStore()

const myId = computed(() => userStore.userInfo?.user_id)
const routeOtherId = computed(() => {
  const value = Number(route.query.to)
  return Number.isFinite(value) && value > 0 ? value : null
})
const petId = computed(() => route.query.pet ? Number(route.query.pet) : null)
const hasExplicitTarget = computed(() => !!routeOtherId.value)

const petName      = ref('')
const allMessages  = ref([])
const selectedOtherId = ref(null)
const loading      = ref(false)
const sending      = ref(false)
const inputText    = ref('')
const chatBody     = ref()

const conversations = computed(() => {
  const map = new Map()
  const me = myId.value

  allMessages.value.forEach(m => {
    const otherId = m.sender_id === me ? m.receiver_id : m.sender_id
    if (!otherId || otherId === me) return

    const fromOther = m.sender_id === otherId
    const otherName = fromOther ? (m.sender?.nickname || `用户${otherId}`) : (map.get(otherId)?.otherName || `用户${otherId}`)
    const prev = map.get(otherId)
    const prevTime = prev?.created_at ? new Date(prev.created_at).getTime() : 0
    const currentTime = m.created_at ? new Date(m.created_at).getTime() : 0

    if (!prev || currentTime >= prevTime) {
      map.set(otherId, {
        otherId,
        otherName,
        preview: m.content,
        created_at: m.created_at,
      })
    }
  })

  return Array.from(map.values()).sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
})

const currentOtherName = computed(() => {
  if (!selectedOtherId.value) return '发布方'
  const conv = conversations.value.find(c => c.otherId === selectedOtherId.value)
  return conv?.otherName || `用户${selectedOtherId.value}`
})

const filteredMessages = computed(() =>
  allMessages.value
    .filter(m =>
      selectedOtherId.value && (
        (m.sender_id === myId.value && m.receiver_id === selectedOtherId.value) ||
        (m.sender_id === selectedOtherId.value && m.receiver_id === myId.value)
      )
    )
    .sort((a, b) => new Date(a.created_at) - new Date(b.created_at))
)

async function loadMessages() {
  loading.value = true
  try {
    const msgs = await userApi.messages()
    allMessages.value = msgs || []
    if (routeOtherId.value) {
      selectedOtherId.value = routeOtherId.value
    } else if (!selectedOtherId.value && conversations.value.length > 0) {
      selectedOtherId.value = conversations.value[0].otherId
    }
  } catch {} finally {
    loading.value = false
    await scrollToBottom()
  }
}

function selectConversation(item) {
  selectedOtherId.value = item.otherId
  scrollToBottom()
}

function getSenderLabel(msg) {
  return msg.sender_id === myId.value ? '我' : currentOtherName.value
}

function getAvatarText(msg) {
  const label = getSenderLabel(msg)
  return label?.trim()?.charAt(0) || '?'
}

async function scrollToBottom() {
  await nextTick()
  if (chatBody.value) chatBody.value.scrollTop = chatBody.value.scrollHeight
}

async function sendMsg() {
  const text = inputText.value.trim()
  if (!text) return
  if (!selectedOtherId.value) {
    ElMessage.warning('请先选择会话对象')
    return
  }
  sending.value = true
  try {
    await userApi.sendMessage({ receiver_id: selectedOtherId.value, content: text, pet_id: petId.value })
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
    } catch {}
  }
  await loadMessages()
})

watch(routeOtherId, async value => {
  if (value) {
    selectedOtherId.value = value
    await scrollToBottom()
  }
})
</script>

<style scoped>
.chat-page {
  display: flex;
  flex-direction: column;
  height: calc(100vh - 160px);
  min-height: 400px;
}
.chat-layout {
  display: flex;
  gap: 12px;
  flex: 1;
  min-height: 0;
}
.chat-sidebar {
  width: 260px;
  border: 1px solid #e8e0ff;
  border-radius: 10px;
  padding: 10px;
  overflow-y: auto;
}
.sidebar-title {
  font-size: 13px;
  color: #909399;
  margin-bottom: 8px;
}
.conversation-item {
  border: 1px solid #ebeef5;
  border-radius: 8px;
  padding: 8px;
  margin-bottom: 8px;
  cursor: pointer;
}
.conversation-item.is-active {
  border-color: #667eea;
  background: #f5f6ff;
}
.conversation-name {
  font-size: 14px;
  font-weight: 600;
  color: #303133;
}
.conversation-preview {
  margin-top: 4px;
  font-size: 12px;
  color: #909399;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
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
  padding: 12px 8px;
  display: flex;
  flex-direction: column;
  gap: 16px;
  background: linear-gradient(180deg, #fcfbff 0%, #f7f4ff 100%);
  border-radius: 12px;
}
.chat-main {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
}
.msg-row {
  display: flex;
  max-width: 82%;
}
.msg-row--self  { align-self: flex-end; }
.msg-row--other { align-self: flex-start; }
.msg-card {
  display: flex;
  align-items: flex-end;
  gap: 10px;
}
.msg-row--self .msg-card {
  flex-direction: row-reverse;
}
.msg-avatar {
  width: 34px;
  height: 34px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  font-size: 13px;
  font-weight: 700;
  box-shadow: 0 6px 14px rgba(102, 126, 234, 0.14);
}
.msg-row--self .msg-avatar {
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: #fff;
}
.msg-row--other .msg-avatar {
  background: #fff;
  color: #667eea;
  border: 1px solid #dfe4ff;
}
.msg-content-wrap {
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.msg-row--self .msg-content-wrap {
  align-items: flex-end;
}
.msg-row--other .msg-content-wrap {
  align-items: flex-start;
}
.msg-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 0 4px;
}
.msg-row--self .msg-meta {
  flex-direction: row-reverse;
}
.msg-sender {
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.3px;
  color: #606266;
}
.msg-bubble {
  background: #ffffff;
  border: 1px solid #e7eaf6;
  border-radius: 16px 16px 16px 6px;
  padding: 10px 14px;
  font-size: 14px;
  color: #303133;
  word-break: break-word;
  line-height: 1.5;
  box-shadow: 0 8px 22px rgba(103, 117, 163, 0.08);
}
.msg-row--self .msg-bubble {
  background: linear-gradient(135deg, #667eea, #764ba2);
  border-color: transparent;
  color: #fff;
  border-radius: 16px 16px 6px 16px;
}
.msg-time {
  font-size: 11px;
  color: #a0a4b8;
}
.chat-input {
  display: flex;
  gap: 8px;
  padding-top: 12px;
  border-top: 1px solid #e8e0ff;
  margin-top: 8px;
}

@media (max-width: 900px) {
  .chat-layout {
    flex-direction: column;
  }
  .chat-sidebar {
    width: 100%;
    max-height: 180px;
  }
}
</style>

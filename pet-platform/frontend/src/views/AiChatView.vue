<template>
  <NavBar>
    <div class="chat-wrapper">
      <div class="chat-header">
        <div class="chat-header-avatar">🐾</div>
        <div>
          <div class="chat-header-title">AI 宠物助手</div>
          <div class="chat-header-sub">关于领养、养护、平台使用，随时提问</div>
        </div>
      </div>

      <!-- 消息列表 -->
      <div class="chat-body" ref="bodyRef">
        <div
          v-for="(msg, idx) in messages"
          :key="idx"
          :class="['bubble-row', msg.role === 'user' ? 'user-row' : 'ai-row']"
        >
          <div v-if="msg.role === 'assistant'" class="bubble-avatar">🐾</div>
          <div :class="['bubble', msg.role === 'user' ? 'bubble-user' : 'bubble-ai']">
            <pre class="bubble-text">{{ msg.content }}</pre>
          </div>
        </div>
        <div v-if="loading" class="bubble-row ai-row">
          <div class="bubble-avatar">🐾</div>
          <div class="bubble bubble-ai typing-indicator">
            <span /><span /><span />
          </div>
        </div>
      </div>

      <!-- 快捷问题 -->
      <div class="quick-bar" v-if="messages.length <= 1">
        <el-button
          v-for="q in quickQuestions"
          :key="q"
          size="small"
          round
          @click="sendQuick(q)"
        >{{ q }}</el-button>
      </div>

      <!-- 输入框 -->
      <div class="chat-input-bar">
        <el-input
          v-model="inputText"
          placeholder="请输入您的问题，例如：如何领养宠物？"
          :disabled="loading"
          @keyup.enter.exact="sendMessage"
          class="chat-input"
          maxlength="500"
          show-word-limit
        />
        <el-button
          type="primary"
          :loading="loading"
          :disabled="!inputText.trim()"
          @click="sendMessage"
          class="send-btn"
        >发送</el-button>
      </div>
    </div>
  </NavBar>
</template>

<script setup>
import { ref, nextTick } from 'vue'
import NavBar from '@/components/NavBar.vue'
import { aiApi } from '@/api'

const inputText = ref('')
const loading   = ref(false)
const bodyRef   = ref(null)

const quickQuestions = [
  '如何领养宠物？',
  '领养需要什么条件？',
  '猫咪多久打一次疫苗？',
  '宠物驱虫怎么做？',
  '如何预约洗护服务？',
]

// 初始欢迎语
const messages = ref([
  {
    role: 'assistant',
    content:
      '您好！我是宠爱有家平台的 AI 宠物助手 🐾\n' +
      '我可以回答关于宠物领养、日常护理、平台操作等问题。\n' +
      '请问有什么可以帮助您的？',
  },
])

async function sendMessage() {
  const text = inputText.value.trim()
  if (!text || loading.value) return

  messages.value.push({ role: 'user', content: text })
  inputText.value = ''
  loading.value = true
  await scrollBottom()

  // 构建上下文历史（最近 10 条）
  const history = messages.value.slice(-10).map(m => ({ role: m.role, content: m.content }))

  try {
    const res = await aiApi.chat({ message: text, history })
    messages.value.push({ role: 'assistant', content: res.reply || '抱歉，暂时无法回答，请稍后再试。' })
  } catch {
    messages.value.push({ role: 'assistant', content: '网络异常，请稍后重试。' })
  } finally {
    loading.value = false
    await scrollBottom()
  }
}

function sendQuick(q) {
  inputText.value = q
  sendMessage()
}

async function scrollBottom() {
  await nextTick()
  if (bodyRef.value) {
    bodyRef.value.scrollTop = bodyRef.value.scrollHeight
  }
}
</script>

<style scoped>
.chat-wrapper {
  max-width: 760px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  height: calc(100vh - 120px);
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 2px 16px rgba(0,21,41,.08);
  overflow: hidden;
}

.chat-header {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 18px 24px;
  background: linear-gradient(135deg, #1a1a2e, #0f3460);
  color: #fff;
}
.chat-header-avatar { font-size: 30px; }
.chat-header-title  { font-size: 16px; font-weight: 700; }
.chat-header-sub    { font-size: 12px; color: #a0b0d0; margin-top: 2px; }

.chat-body {
  flex: 1;
  overflow-y: auto;
  padding: 20px 20px 10px;
  background: #f6f8fb;
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.bubble-row {
  display: flex;
  align-items: flex-end;
  gap: 10px;
}
.user-row  { flex-direction: row-reverse; }
.ai-row    { flex-direction: row; }

.bubble-avatar { font-size: 24px; flex-shrink: 0; }

.bubble {
  max-width: 72%;
  padding: 10px 14px;
  border-radius: 12px;
  line-height: 1.6;
}
.bubble-user {
  background: #409eff;
  color: #fff;
  border-bottom-right-radius: 2px;
}
.bubble-ai {
  background: #fff;
  color: #1f2937;
  border: 1px solid #e8edf3;
  border-bottom-left-radius: 2px;
  box-shadow: 0 1px 4px rgba(0,21,41,.06);
}

.bubble-text {
  margin: 0;
  font-family: inherit;
  font-size: 14px;
  white-space: pre-wrap;
  word-break: break-word;
}

/* 打字动画 */
.typing-indicator {
  display: flex;
  align-items: center;
  gap: 5px;
  padding: 12px 16px;
}
.typing-indicator span {
  width: 8px; height: 8px;
  border-radius: 50%;
  background: #a0aec0;
  animation: typing 1.2s infinite ease-in-out;
}
.typing-indicator span:nth-child(2) { animation-delay: .2s; }
.typing-indicator span:nth-child(3) { animation-delay: .4s; }
@keyframes typing {
  0%,80%,100% { transform: scale(1); opacity: .5; }
  40%          { transform: scale(1.3); opacity: 1; }
}

.quick-bar {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  padding: 8px 20px 0;
  background: #f6f8fb;
}

.chat-input-bar {
  display: flex;
  gap: 10px;
  padding: 14px 20px;
  border-top: 1px solid #eaedf3;
  background: #fff;
}
.chat-input { flex: 1; }
.send-btn   { flex-shrink: 0; }
</style>

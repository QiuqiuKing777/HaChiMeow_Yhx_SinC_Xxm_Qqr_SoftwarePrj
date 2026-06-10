<template>
  <div class="register-page" ref="pageRef">
    <img
      src="/Register.png"
      class="bg-image"
      ref="bgImage"
      alt="background"
      @load="onImageLoad"
    />

    <div class="eyes-layer" ref="eyesLayer" :class="{ ready }">
      <div
        v-for="eye in eyeList"
        :key="eye.id"
        class="eye"
        :data-id="eye.id"
      >
        <div class="pupil"></div>
      </div>
    </div>

    <div class="form-area">
      <el-card class="register-card" shadow="always">
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
          <el-button type="primary" :loading="loading" style="width: 100%; margin-top: 8px" @click="onSubmit">
            注册
          </el-button>
        </el-form>
        <div class="bottom-link">
          已有账号？<router-link to="/login">立即登录</router-link>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()
const formRef = ref()
const loading = ref(false)
const form = ref({ username: '', nickname: '', password: '', phone: '', role_type: 'user' })

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

const IMG_W = 1672
const IMG_H = 941

const pageRef = ref(null)
const bgImage = ref(null)
const eyesLayer = ref(null)
const ready = ref(false)

const EYE_DEFS = [
  { id: 'a1l', x: 115, y: 155, whiteR: 9, pupilR: 3 },
  { id: 'a1r', x: 199, y: 155, whiteR: 9, pupilR: 3 },
  { id: 'a2l', x: 401, y: 124, whiteR: 9, pupilR: 3 },
  { id: 'a2r', x: 490, y: 121, whiteR: 9, pupilR: 3 },
  { id: 'a3l', x: 694, y: 130, whiteR: 9, pupilR: 3 },
  { id: 'a3r', x: 780, y: 129, whiteR: 9, pupilR: 3 },
  { id: 'a4l', x: 979, y: 120, whiteR: 9, pupilR: 3 },
  { id: 'a4r', x: 1064, y: 121, whiteR: 9, pupilR: 3 },
  { id: 'a5l', x: 1246, y: 158, whiteR: 9, pupilR: 3 },
  { id: 'a5r', x: 1328, y: 158, whiteR: 9, pupilR: 3 },
  { id: 'a6l', x: 1496, y: 170, whiteR: 9, pupilR: 3 },
  { id: 'a6r', x: 1577, y: 173, whiteR: 9, pupilR: 3 },
  { id: 'a7l', x: 110, y: 396, whiteR: 9, pupilR: 3 },
  { id: 'a7r', x: 200, y: 397, whiteR: 9, pupilR: 3 },
  { id: 'a8l', x: 394, y: 416, whiteR: 9, pupilR: 3 },
  { id: 'a8r', x: 487, y: 416, whiteR: 9, pupilR: 3 },
  { id: 'a9l', x: 678, y: 422, whiteR: 9, pupilR: 3 },
  { id: 'a9r', x: 766, y: 422, whiteR: 9, pupilR: 3 },
  { id: 'a10l', x: 951, y: 412, whiteR: 9, pupilR: 3 },
  { id: 'a10r', x: 1061, y: 412, whiteR: 9, pupilR: 3 },
  { id: 'a11l', x: 1235, y: 417, whiteR: 9, pupilR: 3 },
  { id: 'a11r', x: 1325, y: 418, whiteR: 9, pupilR: 3 },
  { id: 'a12l', x: 1491, y: 434, whiteR: 9, pupilR: 3 },
  { id: 'a12r', x: 1579, y: 435, whiteR: 9, pupilR: 3 },
  { id: 'a13l', x: 114, y: 644, whiteR: 9, pupilR: 3 },
  { id: 'a13r', x: 192, y: 644, whiteR: 9, pupilR: 3 },
  { id: 'a14l', x: 383, y: 653, whiteR: 9, pupilR: 3 },
  { id: 'a14r', x: 466, y: 654, whiteR: 9, pupilR: 3 },
  { id: 'a15l', x: 631, y: 618, whiteR: 9, pupilR: 3 },
  { id: 'a15r', x: 726, y: 616, whiteR: 9, pupilR: 3 },
  { id: 'a16l', x: 896, y: 631, whiteR: 9, pupilR: 3 },
  { id: 'a16r', x: 984, y: 634, whiteR: 9, pupilR: 3 },
  { id: 'a17l', x: 1191, y: 630, whiteR: 9, pupilR: 3 },
  { id: 'a17r', x: 1280, y: 634, whiteR: 9, pupilR: 3 },
  { id: 'a18l', x: 1478, y: 630, whiteR: 9, pupilR: 3 },
  { id: 'a18r', x: 1560, y: 631, whiteR: 9, pupilR: 3 },
  { id: 'a19l', x: 121, y: 849, whiteR: 9, pupilR: 3 },
  { id: 'a19r', x: 203, y: 850, whiteR: 9, pupilR: 3 },
  { id: 'a20l', x: 383, y: 851, whiteR: 9, pupilR: 3 },
  { id: 'a20r', x: 462, y: 849, whiteR: 9, pupilR: 3 },
  { id: 'a21l', x: 644, y: 854, whiteR: 9, pupilR: 3 },
  { id: 'a21r', x: 727, y: 851, whiteR: 9, pupilR: 3 },
  { id: 'a22l', x: 914, y: 849, whiteR: 9, pupilR: 3 },
  { id: 'a22r', x: 991, y: 850, whiteR: 9, pupilR: 3 },
  { id: 'a23l', x: 1179, y: 861, whiteR: 9, pupilR: 3 },
  { id: 'a23r', x: 1265, y: 865, whiteR: 9, pupilR: 3 },
  { id: 'a24l', x: 1474, y: 852, whiteR: 9, pupilR: 3 },
  { id: 'a24r', x: 1551, y: 851, whiteR: 9, pupilR: 3 },
]

const eyeList = EYE_DEFS.map((e) => ({
  id: e.id,
}))

let rafId = null
let targetX = null
let targetY = null
let pupilStates = []
let reducedMotion = false
let motionMediaQuery = null
let resizeObserver = null
let cachedRect = null

function getImageRenderRect() {
  if (cachedRect) return cachedRect
  const page = pageRef.value
  if (!page) return { offsetX: 0, offsetY: 0, renderW: 0, renderH: 0, scale: 1 }

  const cw = page.clientWidth
  const ch = page.clientHeight
  const imgAspect = IMG_W / IMG_H
  const contAspect = cw / ch

  let rw
  let rh
  let ox
  let oy

  if (contAspect > imgAspect) {
    rw = cw
    rh = rw / imgAspect
    ox = 0
    oy = (ch - rh) / 2
  } else {
    rh = ch
    rw = rh * imgAspect
    ox = (cw - rw) / 2
    oy = 0
  }

  cachedRect = {
    offsetX: ox,
    offsetY: oy,
    renderW: rw,
    renderH: rh,
    scale: rw / IMG_W,
  }
  return cachedRect
}

function updateGeometry() {
  const allEyes = eyesLayer.value?.querySelectorAll('.eye')
  if (!allEyes || allEyes.length === 0) return

  const rect = getImageRenderRect()

  allEyes.forEach((el) => {
    const def = EYE_DEFS.find((item) => item.id === el.dataset.id)
    if (!def) return

    const cssWhiteR = def.whiteR * rect.scale
    const cssPupilR = def.pupilR * rect.scale
    const cssMaxMove = (def.whiteR - def.pupilR) * rect.scale
    const cx = rect.offsetX + (def.x / IMG_W) * rect.renderW
    const cy = rect.offsetY + (def.y / IMG_H) * rect.renderH

    el.style.left = `${cx - cssWhiteR}px`
    el.style.top = `${cy - cssWhiteR}px`
    el.style.width = `${cssWhiteR * 2}px`
    el.style.height = `${cssWhiteR * 2}px`
    el.dataset.radius = `${cssMaxMove}`

    const pupil = el.querySelector('.pupil')
    if (pupil) {
      pupil.style.width = `${cssPupilR * 2}px`
      pupil.style.height = `${cssPupilR * 2}px`
    }
  })

  if (pupilStates.length !== eyeList.length) {
    pupilStates = eyeList.map(() => ({ tx: 0, ty: 0 }))
  }
}

function animate() {
  if (reducedMotion) {
    rafId = requestAnimationFrame(animate)
    return
  }

  const allEyes = eyesLayer.value?.querySelectorAll('.eye')
  if (!allEyes || allEyes.length === 0) {
    rafId = requestAnimationFrame(animate)
    return
  }

  const hasTarget = targetX !== null

  allEyes.forEach((el, i) => {
    const pupil = el.querySelector('.pupil')
    if (!pupil) return

    const maxR = parseFloat(el.dataset.radius) || 0
    const eyeRect = el.getBoundingClientRect()
    const eyeCX = eyeRect.left + eyeRect.width / 2
    const eyeCY = eyeRect.top + eyeRect.height / 2

    let curTx = pupilStates[i]?.tx || 0
    let curTy = pupilStates[i]?.ty || 0

    if (hasTarget) {
      const dx = targetX - eyeCX
      const dy = targetY - eyeCY
      const dist = Math.sqrt(dx * dx + dy * dy)
      const angle = Math.atan2(dy, dx)
      const moveDist = Math.min(dist, maxR)
      const targetTx = Math.cos(angle) * moveDist
      const targetTy = Math.sin(angle) * moveDist

      curTx += (targetTx - curTx) * 0.25
      curTy += (targetTy - curTy) * 0.25
    } else {
      curTx *= 0.92
      curTy *= 0.92
      if (Math.abs(curTx) < 0.01) curTx = 0
      if (Math.abs(curTy) < 0.01) curTy = 0
    }

    pupilStates[i] = { tx: curTx, ty: curTy }
    pupil.style.transform = `translate(calc(-50% + ${curTx}px), calc(-50% + ${curTy}px))`
  })

  rafId = requestAnimationFrame(animate)
}

function onMouseMove(e) {
  targetX = e.clientX
  targetY = e.clientY
}

function onMouseLeave() {
  targetX = null
  targetY = null
}

function onTouchMove(e) {
  if (e.touches.length > 0) {
    targetX = e.touches[0].clientX
    targetY = e.touches[0].clientY
  }
}

function onTouchEnd() {
  targetX = null
  targetY = null
}

function onImageLoad() {
  nextTick(() => {
    cachedRect = null
    ready.value = true
    updateGeometry()
    if (!rafId) {
      rafId = requestAnimationFrame(animate)
    }
  })
}

function onResize() {
  cachedRect = null
  updateGeometry()
}

function onMotionChange(e) {
  reducedMotion = e.matches
  if (!reducedMotion) return

  pupilStates = eyeList.map(() => ({ tx: 0, ty: 0 }))
  const allEyes = eyesLayer.value?.querySelectorAll('.eye')
  allEyes?.forEach((el) => {
    const pupil = el.querySelector('.pupil')
    if (pupil) pupil.style.transform = 'translate(-50%, -50%)'
  })
}

onMounted(() => {
  motionMediaQuery = window.matchMedia('(prefers-reduced-motion: reduce)')
  reducedMotion = motionMediaQuery.matches
  motionMediaQuery.addEventListener('change', onMotionChange)

  resizeObserver = new ResizeObserver(() => {
    cachedRect = null
    updateGeometry()
  })

  nextTick(() => {
    if (pageRef.value) {
      resizeObserver.observe(pageRef.value)
    }
    updateGeometry()
    if (bgImage.value?.complete) {
      onImageLoad()
    }
  })

  document.addEventListener('mousemove', onMouseMove)
  document.addEventListener('mouseleave', onMouseLeave)
  document.addEventListener('touchmove', onTouchMove, { passive: true })
  document.addEventListener('touchend', onTouchEnd)
  window.addEventListener('resize', onResize)
})

onUnmounted(() => {
  if (rafId) cancelAnimationFrame(rafId)
  resizeObserver?.disconnect()
  motionMediaQuery?.removeEventListener('change', onMotionChange)
  document.removeEventListener('mousemove', onMouseMove)
  document.removeEventListener('mouseleave', onMouseLeave)
  document.removeEventListener('touchmove', onTouchMove)
  document.removeEventListener('touchend', onTouchEnd)
  window.removeEventListener('resize', onResize)
})
</script>

<style scoped>
.register-page {
  position: relative;
  width: 100vw;
  height: 100vh;
  overflow: hidden;
  background: #1a1a2e;
}

.bg-image {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  display: block;
  object-fit: cover;
  z-index: 0;
}

.eyes-layer {
  position: absolute;
  inset: 0;
  z-index: 1;
  pointer-events: none;
  opacity: 0;
}

.eyes-layer.ready {
  opacity: 1;
}

.eye {
  position: absolute;
  border-radius: 50%;
}

.pupil {
  position: absolute;
  left: 50%;
  top: 50%;
  background: #000;
  border-radius: 2px;
  transform: translate(-50%, -50%);
  will-change: transform;
}

.form-area {
  position: absolute;
  right: max(2%, 20px);
  top: 50%;
  transform: translateY(-50%);
  z-index: 10;
  width: 420px;
  max-width: 90vw;
}

.register-card {
  border-radius: 12px;
  padding: 12px;
  background: rgba(255, 255, 255, 0.92);
  backdrop-filter: blur(8px);
}

.title {
  text-align: center;
  margin-bottom: 24px;
  color: #303133;
}

.bottom-link {
  text-align: center;
  margin-top: 16px;
  color: #909399;
  font-size: 14px;
}

@media (max-width: 768px) {
  .form-area {
    right: 50%;
    transform: translate(50%, -50%);
    width: 340px;
  }

  .register-card {
    background: rgba(255, 255, 255, 0.85);
  }
}
</style>

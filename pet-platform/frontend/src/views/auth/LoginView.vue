<template>
  <div
    class="login-page"
    ref="pageRef"
    @mousemove="onMouseMove"
    @mouseleave="onMouseLeave"
    @touchmove="onTouchMove"
    @touchend="onTouchEnd"
  >
    <!-- 背景图片：16:9，object-fit: cover -->
    <img
      ref="bgRef"
      class="bg-image"
      src="/Scene.png"
      alt=""
      @load="onImageLoad"
    />

    <!-- 瞳孔覆盖图层（图片加载完成后显示） -->
    <div class="eyes-layer" ref="eyesLayerRef" v-if="ready">
      <div
        v-for="(def, i) in eyeDefs"
        :key="i"
        class="eye"
        :data-idx="i"
        :data-radius="def.r"
      >
        <!-- 像素风格黑色瞳孔 -->
        <div class="pupil"></div>
      </div>
    </div>

    <!-- 登录表单 —— 画面右侧，z-index 高于眼睛图层 -->
    <div class="form-wrapper">
      <el-card class="login-card">
        <h2 class="title">登录账号</h2>
        <el-form
          :model="form"
          :rules="rules"
          ref="formRef"
          label-position="top"
          @submit.prevent="onSubmit"
        >
          <el-form-item label="用户名" prop="username">
            <el-input
              v-model="form.username"
              placeholder="请输入用户名"
              clearable
            />
          </el-form-item>
          <el-form-item label="密码" prop="password">
            <el-input
              v-model="form.password"
              type="password"
              placeholder="请输入密码"
              show-password
              @keyup.enter="onSubmit"
            />
          </el-form-item>
          <el-button
            type="primary"
            :loading="loading"
            style="width: 100%; margin-top: 8px"
            @click="onSubmit"
          >
            登录
          </el-button>
        </el-form>
        <div class="bottom-link">
          还没有账号？<router-link to="/register">立即注册</router-link>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick, onMounted, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/stores/user'

// ============================================================
//  眼睛坐标定义 —— 基于原始图片像素坐标的 17 组眼睛对
//  每组 [左眼/右眼, 右眼/左眼]，数值为瞳孔中心在原始图片上的 (x, y)
//
//  ★ 如需调整某只眼睛的位置，直接修改对应的像素坐标即可 ★
//  ★ 添加/删除眼睛只需修改此数组 ★
// ============================================================
const EYE_PAIRS = [
  [[890, 112], [803, 117]],   // 动物 1
  [[1081, 193], [1151, 209]], // 动物 2
  [[553, 253], [606, 255]],   // 动物 3
  [[364, 255], [303, 272]],   // 动物 4
  [[1276, 266], [1339, 281]], // 动物 5
  [[729, 384], [669, 390]],   // 动物 6
  [[952, 388], [1010, 396]],  // 动物 7
  [[182, 432], [124, 447]],   // 动物 8
  [[1194, 461], [1255, 472]], // 动物 9
  [[1433, 466], [1500, 480]], // 动物 10
  [[521, 514], [471, 523]],   // 动物 11
  [[354, 539], [290, 543]],   // 动物 12
  [[805, 569], [870, 581]],   // 动物 13
  [[997, 617], [1050, 628]],  // 动物 14
  [[645, 642], [572, 650]],   // 动物 15
  [[1491, 687], [1567, 702]], // 动物 16
  [[1211, 706], [1147, 729]], // 动物 17
]

/**
 * 根据图片原始尺寸，将像素坐标转换为百分比坐标，
 * 并根据双眼间距估算每只眼睛的白色眼眶半径和瞳孔最大移动距离。
 */
function buildEyeDefs(pairs, imgW, imgH) {
  return pairs.flatMap(([a, b]) => {
    // 双眼间距（原始图片像素）
    const pairDist = Math.hypot(b[0] - a[0], b[1] - a[1])

    // 估算白色眼眶直径 ≈ 双眼间距 × 0.45
    const eyeDiamPx = pairDist * 0.45
    const eyeRPx = eyeDiamPx / 2          // 眼眶半径 (px)
    const pupilRPx = eyeRPx * 0.3         // 瞳孔半径 = 眼眶半径 × 30%
    const maxMovePx = eyeRPx - pupilRPx   // 最大移动距离 (px)

    return [a, b].map(([px, py]) => ({
      x: (px / imgW) * 100,              // 眼睛中心 X → 图片宽度百分比
      y: (py / imgH) * 100,              // 眼睛中心 Y → 图片高度百分比
      eyeR: (eyeRPx / imgW) * 100,       // 眼眶半径 → 图片宽度百分比
      r: (maxMovePx / imgW) * 100,       // 最大移动距离 → 图片宽度百分比
    }))
  })
}

// ---- 路由 & 登录状态 ----
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
    ElMessage.error('密码或用户名错误，请重新输入')
  } finally {
    loading.value = false
  }
}

// ---- 眼睛追踪核心 ----
const pageRef = ref(null)
const bgRef = ref(null)
const eyesLayerRef = ref(null)
const ready = ref(false)

const mouseX = ref(0)
const mouseY = ref(0)
const mouseOnPage = ref(false)
const reducedMotion = ref(false)

let eyeDefs = []            // buildEyeDefs 输出的百分比坐标数组
let imageNaturalW = 1920
let imageNaturalH = 1080
let cachedRect = null       // getImageRenderRect 缓存
let animId = 0
const pupilOffsets = []     // 每个瞳孔的当前 { x, y } 偏移 (px)

/** 计算 object-fit: cover 下图片在容器中的实际渲染矩形 */
function getImageRenderRect() {
  if (cachedRect) return cachedRect
  const c = pageRef.value
  if (!c) return { offsetX: 0, offsetY: 0, renderW: 0, renderH: 0 }

  const cw = c.clientWidth
  const ch = c.clientHeight
  const imgAspect = imageNaturalW / imageNaturalH
  const contAspect = cw / ch

  let rw, rh, ox, oy
  if (contAspect > imgAspect) {
    // cover: 容器更宽时，图片宽度撑满容器，上下会被裁切
    rw = cw
    rh = rw / imgAspect
    ox = 0
    oy = (ch - rh) / 2
  } else {
    // cover: 容器更高时，图片高度撑满容器，左右会被裁切
    rh = ch
    rw = rh * imgAspect
    ox = (cw - rw) / 2
    oy = 0
  }
  cachedRect = { offsetX: ox, offsetY: oy, renderW: rw, renderH: rh }
  return cachedRect
}

/** 根据当前渲染矩形定位所有 .eye 容器并设置瞳孔尺寸 */
function positionEyes() {
  const eyes = eyesLayerRef.value?.querySelectorAll('.eye')
  if (!eyes || eyes.length === 0) return

  const rect = getImageRenderRect()

  eyeDefs.forEach((def, i) => {
    const el = eyes[i]
    if (!el) return

    // 眼睛容器直径 = 眼眶半径 × 2（屏幕像素）
    const eyeDiam = (def.eyeR / 100) * rect.renderW * 2
    // 眼睛中心屏幕坐标
    const cx = rect.offsetX + (def.x / 100) * rect.renderW
    const cy = rect.offsetY + (def.y / 100) * rect.renderH

    const half = eyeDiam / 2
    el.style.left   = `${cx - half}px`
    el.style.top    = `${cy - half}px`
    el.style.width  = `${eyeDiam}px`
    el.style.height = `${eyeDiam}px`

    // 瞳孔尺寸 = 眼眶直径 × 30%
    const pupil = el.querySelector('.pupil')
    if (pupil) {
      const ps = Math.round(eyeDiam * 0.3)
      pupil.style.width  = `${ps}px`
      pupil.style.height = `${ps}px`
    }
  })
}

/** RAF 主循环：逐帧计算瞳孔偏移 */
function animate() {
  if (reducedMotion.value) {
    animId = requestAnimationFrame(animate)
    return
  }

  const rect = getImageRenderRect()
  const eyes = eyesLayerRef.value?.querySelectorAll('.eye')
  if (!eyes || eyes.length === 0) {
    animId = requestAnimationFrame(animate)
    return
  }

  eyeDefs.forEach((def, i) => {
    const eyeEl = eyes[i]
    if (!eyeEl) return
    const pupil = eyeEl.querySelector('.pupil')
    if (!pupil) return

    // 眼睛中心屏幕坐标
    const eyeCX = rect.offsetX + (def.x / 100) * rect.renderW
    const eyeCY = rect.offsetY + (def.y / 100) * rect.renderH
    // 最大移动距离（屏幕像素）
    const maxDist = (def.r / 100) * rect.renderW

    let targetX = 0
    let targetY = 0

    if (mouseOnPage.value) {
      const dx = mouseX.value - eyeCX
      const dy = mouseY.value - eyeCY
      const dist = Math.hypot(dx, dy)
      if (dist > 0.5) {
        const angle = Math.atan2(dy, dx)
        const clamped = Math.min(dist, maxDist)
        targetX = Math.cos(angle) * clamped
        targetY = Math.sin(angle) * clamped
      }
    }
    // 鼠标离开页面 → target 保持 (0, 0)，靠 lerp 缓慢回中

    if (!pupilOffsets[i]) pupilOffsets[i] = { x: 0, y: 0 }
    const cur = pupilOffsets[i]

    // 跟踪时快速响应 (0.6)，离开时缓慢回中 (0.05)
    const factor = mouseOnPage.value ? 0.6 : 0.05
    cur.x += (targetX - cur.x) * factor
    cur.y += (targetY - cur.y) * factor

    pupil.style.transform =
      `translate(calc(-50% + ${cur.x}px), calc(-50% + ${cur.y}px))`
  })

  animId = requestAnimationFrame(animate)
}

// ---- 图片加载：读取原始尺寸，构建眼睛定义，启动追踪 ----
function onImageLoad() {
  const img = bgRef.value
  if (img) {
    imageNaturalW = img.naturalWidth || 1920
    imageNaturalH = img.naturalHeight || 1080
  }
  eyeDefs = buildEyeDefs(EYE_PAIRS, imageNaturalW, imageNaturalH)
  ready.value = true
  nextTick(() => {
    positionEyes()
    animId = requestAnimationFrame(animate)
  })
}

// ---- 鼠标 ----
function onMouseMove(e) {
  mouseX.value = e.clientX
  mouseY.value = e.clientY
  mouseOnPage.value = true
}

function onMouseLeave() {
  mouseOnPage.value = false
}

// ---- 触摸 ----
function onTouchMove(e) {
  if (e.touches.length > 0) {
    mouseX.value = e.touches[0].clientX
    mouseY.value = e.touches[0].clientY
    mouseOnPage.value = true
  }
}

function onTouchEnd() {
  mouseOnPage.value = false
}

// ---- 窗口缩放：使缓存失效并重新定位 ----
let resizeTimer = 0
function onResize() {
  cachedRect = null
  clearTimeout(resizeTimer)
  resizeTimer = setTimeout(() => positionEyes(), 120)
}

function onReducedMotionChange(e) {
  reducedMotion.value = e.matches
}

// ---- 生命周期 ----
let mq
onMounted(() => {
  mq = window.matchMedia('(prefers-reduced-motion: reduce)')
  reducedMotion.value = mq.matches
  mq.addEventListener('change', onReducedMotionChange)
  window.addEventListener('resize', onResize)
})

onUnmounted(() => {
  cancelAnimationFrame(animId)
  window.removeEventListener('resize', onResize)
  mq?.removeEventListener('change', onReducedMotionChange)
})
</script>

<style scoped>
/* ===== 全屏容器 ===== */
.login-page {
  position: relative;
  width: 100vw;
  height: 100vh;
  overflow: hidden;
}

/* ===== 背景图片：16:9，object-fit: cover ===== */
.bg-image {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
  z-index: 0;
}

/* ===== 瞳孔覆盖层 ===== */
.eyes-layer {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 1;
  pointer-events: none;
}

/* ===== 单个眼眶容器：透明圆形，裁剪瞳孔 ===== */
.eye {
  position: absolute;
  border-radius: 50%;
  overflow: hidden;
}

/* ===== 像素风格黑色瞳孔 ===== */
.pupil {
  position: absolute;
  left: 50%;
  top: 50%;
  background: #000;
  border-radius: 50%;

  /* 复古像素游戏效果：纯黑色块，无渐变/阴影/抗锯齿 */
  outline: none;
  box-shadow: none;
  backface-visibility: hidden;
  -webkit-backface-visibility: hidden;
  transform: translate(-50%, -50%);
}

/* ===== 登录表单：画面右侧，层级高于眼睛 ===== */
.form-wrapper {
  position: absolute;
  right: 8%;
  top: 50%;
  transform: translateY(-50%);
  z-index: 10;
}

.login-card {
  width: 400px;
  border-radius: 12px;
  padding: 12px;
  background: rgba(255, 255, 255, 0.92);
  backdrop-filter: blur(6px);
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

/* ===== 无障碍：prefers-reduced-motion 时瞳孔保持居中 ===== */
@media (prefers-reduced-motion: reduce) {
  .pupil {
    transition: none !important;
  }
}
</style>

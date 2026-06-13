<template>
  <NavBar>
    <el-row :gutter="20">
      <!-- Banner -->
      <el-col :span="24">
        <el-carousel height="300px" class="banner">
          <el-carousel-item v-for="item in banners" :key="item.title">
            <div class="banner-slide" :style="{ backgroundImage: 'url(' + item.image + ')' }">
              <div class="banner-text">
                <h2>{{ item.title }}</h2>
                <p>{{ item.desc }}</p>
                <el-button type="primary" @click="$router.push(item.link)">{{ item.btn }}</el-button>
              </div>
            </div>
          </el-carousel-item>
        </el-carousel>
      </el-col>

      <!-- 快捷入口 -->
      <el-col :span="24" style="margin-top:24px">
        <el-row :gutter="16" justify="center">
          <el-col :span="6" v-for="entry in quickEntries" :key="entry.title">
            <div class="quick-card" @click="$router.push(entry.path)">
              <div class="quick-icon">{{ entry.icon }}</div>
              <div class="quick-title">{{ entry.title }}</div>
              <div class="quick-desc">{{ entry.desc }}</div>
            </div>
          </el-col>
        </el-row>
      </el-col>

      <!-- 推荐宠物 -->
      <el-col :span="24" style="margin-top:32px">
        <div class="section-header">
          <h3>等待领养的小伙伴</h3>
          <el-button link @click="$router.push('/pets')">查看全部 →</el-button>
        </div>
        <el-row :gutter="16">
          <el-col :span="6" v-for="pet in recommendPets" :key="pet.pet_id">
            <PetCard :pet="pet" />
          </el-col>
        </el-row>
      </el-col>

      <!-- 热销商品 -->
      <el-col :span="24" style="margin-top:32px">
        <div class="section-header">
          <h3>热销宠物用品</h3>
          <el-button link @click="$router.push('/products')">查看全部 →</el-button>
        </div>
        <el-row :gutter="16">
          <el-col :span="6" v-for="product in hotProducts" :key="product.product_id">
            <ProductCard :product="product" />
          </el-col>
        </el-row>
      </el-col>

      <!-- 宠物服务 -->
      <el-col :span="24" style="margin-top:32px;margin-bottom:24px">
        <div class="section-header">
          <h3>热门的宠物服务</h3>
          <el-button link @click="$router.push('/services')">查看全部 →</el-button>
        </div>
        <el-row :gutter="16">
          <el-col :span="6" v-for="svc in recommendServices" :key="svc.service_id">
            <div class="svc-card" @click="$router.push('/services/' + svc.service_id)">
              <img :src="svc.cover_image || svc.image_url || '/NKU.png'" class="svc-img" />
              <div class="svc-info">
                <div class="svc-name">{{ svc.service_name }}</div>
                <div class="svc-cat">{{ svc.category || svc.service_type || '宠物服务' }}</div>
                <div class="svc-price">¥{{ svc.price }}</div>
              </div>
            </div>
          </el-col>
        </el-row>
      </el-col>
    </el-row>
  </NavBar>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import NavBar from '@/components/NavBar.vue'
import PetCard from '@/components/PetCard.vue'
import ProductCard from '@/components/ProductCard.vue'
import { petsApi, productsApi, servicesApi } from '@/api'
import { useUserStore } from '@/stores/user'

const recommendPets     = ref([])
const hotProducts       = ref([])
const recommendServices = ref([])
const userStore = useUserStore()

const banners = [
  { title: '给它一个家', desc: '每一只流浪动物都值得被爱', image: '/banner-adopt.png', link: '/pets', btn: '立即领养' },
  { title: '宠物用品精选', desc: '为您的爱宠挑选最好的', image: '/banner-products.png', link: '/products', btn: '去逛逛' },
  { title: '专业宠物服务', desc: '洗护 · 寄养 · 上门喂养', image: '/banner-services.png', link: '/services', btn: '预约服务' },
]

const quickEntries = computed(() => [
  { icon: '🐱', title: '领养宠物', desc: '找到你的缘分宝贝', path: '/pets' },
  { icon: '🛒', title: '宠物用品', desc: '品牌正品，放心购买', path: '/products' },
  { icon: '✂️', title: '宠物服务', desc: '洗护美容寄养一站式', path: '/services' },
  userStore.isPublisher
    ? { icon: '💬', title: '接受咨询', desc: '查看买家消息，及时回复', path: '/messages' }
    : { icon: '💬', title: '咨询发布方', desc: '直接沟通，快速匹配', path: '/pets' },
])

onMounted(async () => {
  try {
    const p = await petsApi.list({ per_page: 4 })
    recommendPets.value = p.items || []
  } catch {}
  try {
    const pr = await productsApi.list({ per_page: 4 })
    hotProducts.value = pr.items || []
  } catch {}
  try {
    const sr = await servicesApi.list({ per_page: 4 })
    recommendServices.value = sr.items || []
  } catch {}
})
</script>

<style scoped>
.banner { border-radius: 12px; overflow: hidden; }
.banner-slide { height: 100%; display: flex; align-items: center; justify-content: center; color: #fff; background-size: cover; background-position: center; position: relative; }
.banner-slide::before { content: ''; position: absolute; inset: 0; background: rgba(0,0,0,.35); z-index: 1; }
.banner-slide > * { position: relative; z-index: 2; }
.banner-text { text-align: center; }
.banner-text h2 { font-size: 32px; margin-bottom: 8px; }
.banner-text p  { font-size: 16px; margin-bottom: 20px; opacity: .9; }
.quick-card { background: #fff; border-radius: 12px; padding: 24px 16px; text-align: center; cursor: pointer; transition: all .2s; border: 1px solid #e8e8e8; }
.quick-card:hover { transform: translateY(-4px); box-shadow: 0 8px 24px rgba(0,0,0,.1); }
.quick-icon  { font-size: 40px; margin-bottom: 12px; }
.quick-title { font-size: 16px; font-weight: 600; color: #303133; }
.quick-desc  { font-size: 13px; color: #909399; margin-top: 4px; }
.section-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
.section-header h3 { margin: 0; font-size: 20px; }
.svc-card { background: #fff; border-radius: 10px; overflow: hidden; cursor: pointer; transition: box-shadow .2s, transform .2s; border: 1px solid #e8e8e8; }
.svc-card:hover { box-shadow: 0 4px 16px rgba(0,0,0,.12); transform: translateY(-2px); }
.svc-img { width: 100%; height: 160px; object-fit: cover; display: block; }
.svc-info { padding: 12px; }
.svc-name { font-weight: 600; font-size: 15px; color: #303133; }
.svc-cat  { font-size: 12px; color: #909399; margin: 4px 0; }
.svc-price { color: #f56c6c; font-size: 16px; font-weight: 600; }
</style>

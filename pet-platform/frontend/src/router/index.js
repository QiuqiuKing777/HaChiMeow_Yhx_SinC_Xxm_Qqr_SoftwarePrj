import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '@/stores/user'

const routes = [
  { path: '/',        name: 'Home',       component: () => import('@/views/HomeView.vue') },
  { path: '/login',   name: 'Login',      component: () => import('@/views/auth/LoginView.vue'),     meta: { guest: true } },
  { path: '/register', name: 'Register',  component: () => import('@/views/auth/RegisterView.vue'),  meta: { guest: true } },

  // 宠物
  { path: '/pets',            name: 'PetList',       component: () => import('@/views/pets/PetListView.vue') },
  { path: '/pets/:id',        name: 'PetDetail',     component: () => import('@/views/pets/PetDetailView.vue') },
  { path: '/pets/:id/apply',  name: 'AdoptApply',    component: () => import('@/views/pets/AdoptionApplyView.vue'), meta: { requiresAuth: true, roles: ['user'] } },

  // 商品
  { path: '/products',     name: 'ProductList',   component: () => import('@/views/products/ProductListView.vue') },
  { path: '/products/:id', name: 'ProductDetail', component: () => import('@/views/products/ProductDetailView.vue') },

  // 购物车 & 订单
  { path: '/cart',   name: 'Cart',      component: () => import('@/views/orders/CartView.vue'),      meta: { requiresAuth: true } },
  { path: '/orders', name: 'OrderList', component: () => import('@/views/orders/OrderListView.vue'), meta: { requiresAuth: true } },

  // 服务
  { path: '/services',     name: 'ServiceList',   component: () => import('@/views/services/ServiceListView.vue') },
  { path: '/services/:id', name: 'ServiceDetail', component: () => import('@/views/services/ServiceDetailView.vue') },
  { path: '/bookings',     name: 'BookingList',   component: () => import('@/views/services/BookingListView.vue'), meta: { requiresAuth: true } },

  // 用户中心
  { path: '/user/profile',       name: 'Profile',       component: () => import('@/views/user/ProfileView.vue'),       meta: { requiresAuth: true } },
  { path: '/user/favorites',     name: 'Favorites',     component: () => import('@/views/user/FavoritesView.vue'),     meta: { requiresAuth: true } },
  { path: '/user/notifications', name: 'Notifications', component: () => import('@/views/user/NotificationsView.vue'), meta: { requiresAuth: true } },
  { path: '/user/applications',  name: 'MyApplications', component: () => import('@/views/user/MyApplicationsView.vue'), meta: { requiresAuth: true } },
  { path: '/messages',           name: 'Messages',       component: () => import('@/views/user/MessagesView.vue'),       meta: { requiresAuth: true } },

  // 发布方工作台
  { path: '/publisher/dashboard',    name: 'PubDashboard',    component: () => import('@/views/publisher/DashboardView.vue'),            meta: { requiresAuth: true, roles: ['publisher'] } },
  { path: '/publisher/pets',         name: 'PubPets',         component: () => import('@/views/publisher/PetManageView.vue'),            meta: { requiresAuth: true, roles: ['publisher'] } },
  { path: '/publisher/applications', name: 'PubApplications', component: () => import('@/views/publisher/ApplicationReviewView.vue'),    meta: { requiresAuth: true, roles: ['publisher'] } },
  { path: '/publisher/products',     name: 'PubProducts',     component: () => import('@/views/publisher/ProductManageView.vue'),        meta: { requiresAuth: true, roles: ['publisher'] } },
  { path: '/publisher/services',     name: 'PubServices',     component: () => import('@/views/publisher/ServiceManageView.vue'),        meta: { requiresAuth: true, roles: ['publisher'] } },
  { path: '/publisher/orders',       name: 'PubOrders',       component: () => import('@/views/publisher/OrderManageView.vue'),          meta: { requiresAuth: true, roles: ['publisher'] } },
  { path: '/publisher/bookings',     name: 'PubBookings',     component: () => import('@/views/publisher/BookingManageView.vue'),        meta: { requiresAuth: true, roles: ['publisher'] } },

  // 管理员后台
  { path: '/admin/dashboard', name: 'AdminDashboard', component: () => import('@/views/admin/AdminDashboardView.vue'), meta: { requiresAuth: true, roles: ['admin'] } },
  { path: '/admin/users',     name: 'AdminUsers',     component: () => import('@/views/admin/UserManageView.vue'),    meta: { requiresAuth: true, roles: ['admin'] } },
  { path: '/admin/review',    name: 'AdminReview',    component: () => import('@/views/admin/ContentReviewView.vue'), meta: { requiresAuth: true, roles: ['admin'] } },
  { path: '/admin/stats',     name: 'AdminStats',     component: () => import('@/views/admin/StatsView.vue'),         meta: { requiresAuth: true, roles: ['admin'] } },

  { path: '/:pathMatch(.*)*', redirect: '/' },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior: () => ({ top: 0 }),
})

// 路由守卫
router.beforeEach(async (to, from, next) => {
  const userStore = useUserStore()

  if (!userStore.userInfo && userStore.token) {
    await userStore.fetchMe()
  }

  // 已登录用户访问 guest 页面（登录/注册）直接跳首页
  if (to.meta.guest && userStore.isLoggedIn) {
    return next({ path: '/' })
  }

  if (to.meta.requiresAuth && !userStore.isLoggedIn) {
    return next({ name: 'Login', query: { redirect: to.fullPath } })
  }

  if (to.meta.roles && !to.meta.roles.includes(userStore.roleType)) {
    return next({ path: '/' })
  }

  next()
})

export default router

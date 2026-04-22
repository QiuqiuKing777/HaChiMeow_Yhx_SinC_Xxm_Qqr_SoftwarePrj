import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '@/stores/user'

const routes = [
  { path: '/', name: 'Home', component: () => import('@/views/HomeView.vue') },

  { path: '/login', name: 'Login', component: () => import('@/views/auth/LoginView.vue'), meta: { guest: true } },
  { path: '/register', name: 'Register', component: () => import('@/views/auth/RegisterView.vue'), meta: { guest: true } },

  // 宠物
  { path: '/pets', name: 'PetList', component: () => import('@/views/pets/PetListView.vue') },
  { path: '/pets/:id', name: 'PetDetail', component: () => import('@/views/pets/PetDetailView.vue') },
  {
    path: '/pets/:id/apply',
    name: 'AdoptApply',
    component: () => import('@/views/pets/AdoptionApplyView.vue'),
    meta: { requiresAuth: true, roles: ['user'] },
  },

  // 商品
  { path: '/products', name: 'ProductList', component: () => import('@/views/products/ProductListView.vue') },
  { path: '/products/:id', name: 'ProductDetail', component: () => import('@/views/products/ProductDetailView.vue') },

  // 购物车 & 订单
  { path: '/cart', name: 'Cart', component: () => import('@/views/orders/CartView.vue'), meta: { requiresAuth: true, roles: ['user'] } },
  { path: '/orders', name: 'OrderList', component: () => import('@/views/orders/OrderListView.vue'), meta: { requiresAuth: true, roles: ['user'] } },

  // 服务
  { path: '/services', name: 'ServiceList', component: () => import('@/views/services/ServiceListView.vue') },
  { path: '/services/:id', name: 'ServiceDetail', component: () => import('@/views/services/ServiceDetailView.vue') },
  { path: '/bookings', name: 'BookingList', component: () => import('@/views/services/BookingListView.vue'), meta: { requiresAuth: true, roles: ['user'] } },

  // 用户中心
  { path: '/user/profile', name: 'Profile', component: () => import('@/views/user/ProfileView.vue'), meta: { requiresAuth: true, roles: ['user', 'publisher', 'admin'] } },
  { path: '/user/favorites', name: 'Favorites', component: () => import('@/views/user/FavoritesView.vue'), meta: { requiresAuth: true, roles: ['user'] } },
  { path: '/user/notifications', name: 'Notifications', component: () => import('@/views/user/NotificationsView.vue'), meta: { requiresAuth: true, roles: ['user', 'publisher', 'admin'] } },
  { path: '/user/applications', name: 'MyApplications', component: () => import('@/views/user/MyApplicationsView.vue'), meta: { requiresAuth: true, roles: ['user'] } },
  { path: '/messages', name: 'Messages', component: () => import('@/views/user/MessagesView.vue'), meta: { requiresAuth: true, roles: ['user', 'publisher', 'admin'] } },

  // 发布方工作台
  {
    path: '/publisher/dashboard',
    name: 'PubDashboard',
    component: () => import('@/views/publisher/DashboardView.vue'),
    meta: { requiresAuth: true, roles: ['publisher'] },
  },
  {
    path: '/publisher/pets',
    name: 'PubPets',
    component: () => import('@/views/publisher/PetManageView.vue'),
    meta: { requiresAuth: true, roles: ['publisher'] },
  },
  {
    path: '/publisher/applications',
    name: 'PubApplications',
    component: () => import('@/views/publisher/ApplicationReviewView.vue'),
    meta: { requiresAuth: true, roles: ['publisher'] },
  },
  {
    path: '/publisher/products',
    name: 'PubProducts',
    component: () => import('@/views/publisher/ProductManageView.vue'),
    meta: { requiresAuth: true, roles: ['publisher'] },
  },
  {
    path: '/publisher/services',
    name: 'PubServices',
    component: () => import('@/views/publisher/ServiceManageView.vue'),
    meta: { requiresAuth: true, roles: ['publisher'] },
  },
  {
    path: '/publisher/orders',
    name: 'PubOrders',
    component: () => import('@/views/publisher/OrderManageView.vue'),
    meta: { requiresAuth: true, roles: ['publisher'] },
  },
  {
    path: '/publisher/bookings',
    name: 'PubBookings',
    component: () => import('@/views/publisher/BookingManageView.vue'),
    meta: { requiresAuth: true, roles: ['publisher'] },
  },

  // 管理员后台
  {
    path: '/admin/dashboard',
    name: 'AdminDashboard',
    component: () => import('@/views/admin/AdminDashboardView.vue'),
    meta: { requiresAuth: true, roles: ['admin'] },
  },
  {
    path: '/admin/users',
    name: 'AdminUsers',
    component: () => import('@/views/admin/UserManageView.vue'),
    meta: { requiresAuth: true, roles: ['admin'] },
  },
  {
    path: '/admin/review',
    name: 'AdminReview',
    component: () => import('@/views/admin/ContentReviewView.vue'),
    meta: { requiresAuth: true, roles: ['admin'] },
  },
  {
    path: '/admin/stats',
    name: 'AdminStats',
    component: () => import('@/views/admin/StatsView.vue'),
    meta: { requiresAuth: true, roles: ['admin'] },
  },

  { path: '/:pathMatch(.*)*', redirect: '/' },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior: () => ({ top: 0 }),
})

function getDefaultRouteByRole(roleType) {
  if (roleType === 'admin') return '/admin/dashboard'
  if (roleType === 'publisher') return '/publisher/dashboard'
  if (roleType === 'user') return '/'
  return '/'
}

// 路由守卫
router.beforeEach(async (to, from, next) => {
  const userStore = useUserStore()

  // 刷新页面时，如果有 token 但没有 userInfo，主动恢复登录态
  if (!userStore.userInfo && userStore.token) {
    try {
      await userStore.fetchMe()
    } catch (error) {
      return next({ name: 'Login', query: { redirect: to.fullPath } })
    }
  }

  // 已登录用户访问登录/注册页，按角色跳到对应主页
  if (to.meta.guest && userStore.isLoggedIn) {
    return next(getDefaultRouteByRole(userStore.roleType))
  }

  // 需要登录但未登录
  if (to.meta.requiresAuth && !userStore.isLoggedIn) {
    return next({ name: 'Login', query: { redirect: to.fullPath } })
  }

  // 已登录但角色不匹配
  if (to.meta.roles && !to.meta.roles.includes(userStore.roleType)) {
    return next(getDefaultRouteByRole(userStore.roleType))
  }

  next()
})

export default router

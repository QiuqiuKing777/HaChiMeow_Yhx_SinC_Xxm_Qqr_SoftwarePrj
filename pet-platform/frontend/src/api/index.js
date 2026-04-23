import axios from 'axios'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/stores/user'

const http = axios.create({
  baseURL: '/api',
  timeout: 10000,
})

// 请求拦截器：自动带 Token
http.interceptors.request.use(config => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// 响应拦截器：统一错误处理
http.interceptors.response.use(
  res => res.data,
  err => {
    const status = err.response?.status
    const isGet  = err.config?.method === 'get'

    if (status === 401) {
      localStorage.removeItem('token')
      const path = window.location.pathname
      if (path !== '/login' && path !== '/register') {
        window.location.href = '/login'
      }
      return Promise.reject(err)
    }

    // GET 请求失败不弹窗（页面显示空态即可），显式标记 _silent 的请求也不弹窗
    if (isGet || err.config?._silent) {
      return Promise.reject(err)
    }

    const msg = err.response?.data?.error || '请求失败，请稍后再试'
    ElMessage.error(msg)
    return Promise.reject(err)
  }
)

// ---- Auth ----
export const authApi = {
  register: data => http.post('/auth/register', data),
  login:    data => http.post('/auth/login', data),
  getMe:    ()   => http.get('/auth/me'),
}

// ---- Pets ----
export const petsApi = {
  list:   params => http.get('/pets', { params }),
  get:    id     => http.get(`/pets/${id}`),
  myPets: params => http.get('/pets/my', { params }),
  create: data   => http.post('/pets', data),
  update: (id, data) => http.put(`/pets/${id}`, data),
  remove: id     => http.delete(`/pets/${id}`),
}

// ---- Adoptions ----
export const adoptionsApi = {
  submit:        data   => http.post('/adoptions', data),
  myList:        params => http.get('/adoptions/my', { params }),
  publisherList: params => http.get('/adoptions/publisher', { params }),
  get:           id     => http.get(`/adoptions/${id}`),
  review:        (id, data) => http.put(`/adoptions/${id}/review`, data),
  cancel:        id     => http.delete(`/adoptions/${id}`),
}

// ---- Products ----
export const productsApi = {
  list:       params => http.get('/products', { params }),
  get:        id     => http.get(`/products/${id}`),
  myProducts: params => http.get('/products/my', { params }),
  create:     data   => http.post('/products', data),
  update:     (id, data) => http.put(`/products/${id}`, data),
  remove:     id     => http.delete(`/products/${id}`),
}

// ---- Cart ----
export const cartApi = {
  list:   ()   => http.get('/cart'),
  add:    data => http.post('/cart', data),
  update: (id, data) => http.put(`/cart/${id}`, data),
  remove: id   => http.delete(`/cart/${id}`),
  clear:  ()   => http.delete('/cart/clear'),
}

// ---- Orders ----
export const ordersApi = {
  create:         data   => http.post('/orders', data),
  myList:         params => http.get('/orders', { params }),
  publisherList:  params => http.get('/orders/publisher', { params }),
  get:            id     => http.get(`/orders/${id}`),
  pay:            id     => http.put(`/orders/${id}/pay`),
  ship:           id     => http.put(`/orders/${id}/ship`),
  receive:        id     => http.put(`/orders/${id}/receive`),
  cancel:         id     => http.put(`/orders/${id}/cancel`),
}

// ---- Services ----
export const servicesApi = {
  list:       params => http.get('/services', { params }),
  get:        id     => http.get(`/services/${id}`),
  slots:      id     => http.get(`/services/${id}/slots`),
  myServices: params => http.get('/services/my', { params }),
  create:     data   => http.post('/services', data),
  update:     (id, data) => http.put(`/services/${id}`, data),
  remove:     id     => http.delete(`/services/${id}`),
  addSlot:    (id, data) => http.post(`/services/${id}/slots`, data),
}

// ---- Bookings ----
export const bookingsApi = {
  create:        data   => http.post('/bookings', data),
  myList:        params => http.get('/bookings/my', { params }),
  publisherList: params => http.get('/bookings/publisher', { params }),
  get:           id     => http.get(`/bookings/${id}`),
  confirm:       id     => http.put(`/bookings/${id}/confirm`),
  cancel:        id     => http.put(`/bookings/${id}/cancel`),
  finish:        id     => http.put(`/bookings/${id}/finish`),
}

// ---- User ----
export const userApi = {
  getProfile:    ()   => http.get('/user/profile'),
  updateProfile: data => http.put('/user/profile', data),
  addresses:     ()   => http.get('/user/addresses'),
  addAddress:    data => http.post('/user/addresses', data),
  updateAddress: (id, data) => http.put(`/user/addresses/${id}`, data),
  deleteAddress: id   => http.delete(`/user/addresses/${id}`),
  favorites:     params => http.get('/user/favorites', { params }),
  getFavorites:  params => http.get('/user/favorites', { params }),
  addFavorite:   data => http.post('/user/favorites', data),
  removeFavorite:(typeOrId, id) => {
    if (id === undefined) {
      return http.delete(`/user/favorites/${typeOrId}`)
    }
    return http.delete(`/user/favorites/${typeOrId}/${id}`)
  },
  notifications: params => http.get('/user/notifications', { params }),
  markRead:      id   => http.put(`/user/notifications/${id}/read`),
  markAllRead:   ()   => http.put('/user/notifications/read-all'),
  messages:      ()   => http.get('/user/messages'),
  sendMessage:   data => http.post('/user/messages', data, { _silent: true }),
}

// ---- Reviews ----
export const reviewsApi = {
  create: data   => http.post('/reviews', data),
  list:   params => http.get('/reviews', { params }),
}

// ---- Admin ----
export const adminApi = {
  users:         params => http.get('/admin/users', { params }),
  setUserStatus: (id, data) => http.put(`/admin/users/${id}/status`, data),
  pets:          params => http.get('/admin/pets', { params }),
  setPetStatus:  (id, data) => http.put(`/admin/pets/${id}/status`, data),
  products:      params => http.get('/admin/products', { params }),
  setProductStatus: (id, data) => http.put(`/admin/products/${id}/status`, data),
  services:      params => http.get('/admin/services', { params }),
  setServiceStatus: (id, data) => http.put(`/admin/services/${id}/status`, data),
  stats:         ()     => http.get('/admin/stats'),
  logs:          params => http.get('/admin/logs', { params }),
}

export default http

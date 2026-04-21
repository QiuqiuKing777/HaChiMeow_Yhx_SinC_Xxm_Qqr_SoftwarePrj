<template>
  <NavBar>
    <h2>购物车</h2>
    <div v-loading="loading">
      <el-empty v-if="!loading && items.length === 0" description="购物车为空">
        <el-button type="primary" @click="$router.push('/products')">去逛逛</el-button>
      </el-empty>
      <template v-else>
        <el-table :data="items" style="width:100%">
          <el-table-column type="selection" width="50" />
          <el-table-column label="商品" min-width="280">
            <template #default="{ row }">
              <div class="product-cell">
                <img :src="row.product?.cover_image || '/placeholder.jpg'" class="thumb" />
                <span>{{ row.product?.product_name }}</span>
              </div>
            </template>
          </el-table-column>
          <el-table-column label="单价" width="120">
            <template #default="{ row }">¥{{ row.product?.price }}</template>
          </el-table-column>
          <el-table-column label="数量" width="160">
            <template #default="{ row }">
              <el-input-number v-model="row.quantity" :min="1" :max="row.product?.stock" size="small"
                @change="updateQty(row)" />
            </template>
          </el-table-column>
          <el-table-column label="小计" width="120">
            <template #default="{ row }">
              <span class="price">¥{{ (row.product?.price * row.quantity).toFixed(2) }}</span>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="80">
            <template #default="{ row }">
              <el-button link type="danger" @click="removeItem(row)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>

        <div class="cart-footer">
          <el-button link type="danger" @click="clearCart">清空购物车</el-button>
          <div class="total-area">
            <span>合计：</span>
            <span class="total-price">¥{{ totalPrice.toFixed(2) }}</span>
            <el-button type="primary" size="large" @click="goCheckout">结算 ({{ items.length }} 件)</el-button>
          </div>
        </div>
      </template>
    </div>

    <!-- 结算弹窗 -->
    <el-dialog v-model="checkoutVisible" title="确认订单" width="500px">
      <el-select v-if="addresses.length > 0" v-model="selectedAddress" placeholder="选择收货地址" style="width:100%;margin-bottom:16px">
        <el-option v-for="addr in addresses" :key="addr.address_id"
          :label="`${addr.receiver_name} ${addr.phone} - ${addr.full_address}`"
          :value="addr.address_id" />
      </el-select>
      <el-empty v-else description="暂无收货地址">
        <el-button @click="$router.push('/user/profile')">前往添加</el-button>
      </el-empty>
      <el-input v-model="orderRemark" placeholder="订单备注（选填）" style="margin-bottom:16px" />
      <div class="checkout-total">应付金额：<span class="total-price">¥{{ totalPrice.toFixed(2) }}</span></div>
      <template #footer>
        <el-button @click="checkoutVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="submitOrder" :disabled="!selectedAddress">提交订单</el-button>
      </template>
    </el-dialog>
  </NavBar>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import NavBar from '@/components/NavBar.vue'
import { cartApi, ordersApi, userApi } from '@/api'

const router           = useRouter()
const items            = ref([])
const loading          = ref(false)
const checkoutVisible  = ref(false)
const submitting       = ref(false)
const addresses        = ref([])
const selectedAddress  = ref(null)
const orderRemark      = ref('')

const totalPrice = computed(() =>
  items.value.reduce((sum, item) => sum + (item.product?.price || 0) * item.quantity, 0)
)

async function load() {
  loading.value = true
  try {
    items.value = await cartApi.list()
  } catch {} finally {
    loading.value = false
  }
}

async function updateQty(row) {
  await cartApi.update(row.cart_id, { quantity: row.quantity })
}

async function removeItem(row) {
  await cartApi.remove(row.cart_id)
  items.value = items.value.filter(i => i.cart_id !== row.cart_id)
  ElMessage.success('已移除')
}

async function clearCart() {
  await ElMessageBox.confirm('确定清空购物车吗？', '提示', { type: 'warning' })
  await cartApi.clear()
  items.value = []
}

async function goCheckout() {
  if (items.value.length === 0) return
  addresses.value = await userApi.addresses()
  if (addresses.value.length > 0) {
    selectedAddress.value = addresses.value.find(a => a.is_default)?.address_id || addresses.value[0].address_id
  }
  checkoutVisible.value = true
}

async function submitOrder() {
  if (!selectedAddress.value) return ElMessage.warning('请选择收货地址')
  submitting.value = true
  try {
    const cartIds = items.value.map(i => i.cart_id)
    const order = await ordersApi.create({ address_id: selectedAddress.value, cart_ids: cartIds, remark: orderRemark.value })
    checkoutVisible.value = false
    ElMessage.success('订单创建成功！')
    router.push('/orders')
  } finally {
    submitting.value = false
  }
}

onMounted(load)
</script>

<style scoped>
.product-cell { display: flex; align-items: center; gap: 12px; }
.thumb { width: 60px; height: 60px; object-fit: cover; border-radius: 6px; }
.price { color: #f56c6c; font-weight: 600; }
.cart-footer { display: flex; justify-content: space-between; align-items: center; margin-top: 20px; padding: 16px; background: #f9f9f9; border-radius: 8px; }
.total-area { display: flex; align-items: center; gap: 16px; }
.total-price { font-size: 24px; color: #f56c6c; font-weight: 700; }
.checkout-total { font-size: 16px; text-align: right; margin-bottom: 8px; }
</style>

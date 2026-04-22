<template>
  <el-card class="product-card" @click="$router.push(`/products/${product.product_id}`)">
    <img
      :src="product.cover_image || '/NKU.png'"
      class="product-img"
      alt="商品图片"
      @error="handleImgError"
    />
    <div class="product-info">
      <div class="product-name">{{ product.product_name }}</div>
      <div class="product-category">
        <el-tag size="small" type="info">{{ product.category || '其他' }}</el-tag>
      </div>
      <div class="product-footer">
        <span class="price">¥{{ product.price }}</span>
        <span class="sales">已售{{ product.sales_count || 0 }}</span>
      </div>
    </div>
  </el-card>
</template>

<script setup>
defineProps({
  product: {
    type: Object,
    required: true,
  },
})

function handleImgError(event) {
  event.target.src = '/NKU.png'
}
</script>

<style scoped>
.product-card {
  cursor: pointer;
  transition: all .2s;
  border-radius: 10px;
  overflow: hidden;
}
.product-card:hover {
  box-shadow: 0 8px 24px rgba(0,0,0,.12);
  transform: translateY(-2px);
}
.product-img {
  width: 100%;
  height: 180px;
  object-fit: cover;
  display: block;
}
.product-info {
  padding: 12px;
}
.product-name {
  font-size: 14px;
  color: #303133;
  line-height: 1.4;
  height: 40px;
  overflow: hidden;
}
.product-category {
  margin: 6px 0;
}
.product-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 8px;
}
.price {
  color: #f56c6c;
  font-size: 18px;
  font-weight: 700;
}
.sales {
  color: #c0c4cc;
  font-size: 12px;
}
</style>

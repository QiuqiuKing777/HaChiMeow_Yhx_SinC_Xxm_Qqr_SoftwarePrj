<template>
  <div>
    <div class="toolbar">
      <h2>商品管理</h2>
      <el-button class="action-btn" type="primary" @click="openDialog()">+ 发布商品</el-button>
    </div>

    <el-table :data="products" border v-loading="loading">
      <el-table-column label="图片" width="90">
        <template #default="{ row }">
          <img :src="row.cover_image || '/NKU.png'" class="thumb" />
        </template>
      </el-table-column>

      <el-table-column label="名称" prop="product_name" />
      <el-table-column label="分类" prop="category" width="100" />

      <el-table-column label="价格" prop="price" width="90">
        <template #default="{ row }">¥{{ row.price }}</template>
      </el-table-column>

      <el-table-column label="库存" prop="stock" width="70" />

      <el-table-column label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="{ online:'success', offline:'info', pending:'warning' }[row.status] || 'info'">
            {{ row.status }}
          </el-tag>
        </template>
      </el-table-column>

      <el-table-column label="操作" width="160">
        <template #default="{ row }">
          <el-button class="mini-btn" size="small" @click="openDialog(row)">编辑</el-button>
          <el-popconfirm title="确认删除？" @confirm="deleteProduct(row)">
            <template #reference>
              <el-button class="mini-btn" size="small" type="danger">删除</el-button>
            </template>
          </el-popconfirm>
        </template>
      </el-table-column>
    </el-table>

    <el-pagination
      v-if="total > 0"
      background
      layout="prev,pager,next,total"
      :total="total"
      :page-size="10"
      v-model:current-page="page"
      @current-change="load"
      style="margin-top:16px;justify-content:center;display:flex"
    />

    <el-dialog v-model="dialogVisible" :title="editId ? '编辑商品' : '发布商品'" width="560px">
      <el-form :model="form" label-width="80px">
        <el-form-item label="名称"><el-input v-model="form.product_name" /></el-form-item>
        <el-form-item label="分类">
          <el-select v-model="form.category" placeholder="请选择商品分类" style="width: 100%;">
            <el-option
              v-for="item in categoryOptions"
              :key="item"
              :label="item"
              :value="item"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="价格"><el-input-number v-model="form.price" :min="0" :precision="2" /></el-form-item>
        <el-form-item label="库存"><el-input-number v-model="form.stock" :min="0" /></el-form-item>
        <el-form-item label="描述"><el-input v-model="form.description" type="textarea" rows="3" /></el-form-item>

        <el-form-item label="上传图片">
          <div class="upload-wrap">
            <el-upload
              :show-file-list="false"
              :auto-upload="false"
              :before-upload="beforeImageUpload"
              :on-change="handleProductImageChange"
              accept=".png,.jpg,.jpeg,.svg,.webp,.gif"
            >
              <el-button class="action-btn" type="primary" plain>选择图片</el-button>
            </el-upload>
            <div class="upload-tip">支持 PNG / JPG / JPEG / SVG / WEBP / GIF</div>
            <img v-if="imagePreview" :src="imagePreview" class="preview-img" />
          </div>
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button class="action-btn" @click="dialogVisible = false">取消</el-button>
        <el-button class="action-btn" type="primary" @click="saveProduct" :loading="saving">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { productsApi } from '@/api'

const products = ref([])
const total = ref(0)
const page = ref(1)
const loading = ref(false)
const saving = ref(false)
const dialogVisible = ref(false)
const editId = ref(null)
const categoryOptions = [
  '日常用品', 
  '猫粮',
  '狗粮',
  '玩具', 
  '零食', 
  '清洁用品', 
  '出行', 
  '其他'
]
const imageFile = ref(null)
const imagePreview = ref('')

const form = reactive({
  product_name: '',
  category: '',
  price: 0,
  stock: 0,
  description: '',
})

function resetForm() {
  Object.assign(form, {
    product_name: '',
    category: '',
    price: 0,
    stock: 0,
    description: '',
  })
  imageFile.value = null
  imagePreview.value = ''
}

function beforeImageUpload(file) {
  const allowed = ['image/png', 'image/x-png', 'image/jpeg', 'image/svg+xml', 'image/webp', 'image/gif']
  const ok = allowed.includes(file.type)
  if (!ok) ElMessage.error('仅支持 PNG、JPG、JPEG、SVG、WEBP、GIF 格式')
  return false
}

function handleProductImageChange(file) {
  const raw = file.raw
  if (!raw) return
  const allowed = ['image/png', 'image/x-png', 'image/jpeg', 'image/svg+xml', 'image/webp', 'image/gif']
  if (!allowed.includes(raw.type)) {
    ElMessage.error('仅支持 PNG、JPG、JPEG、SVG、WEBP、GIF 格式')
    return
  }
  imageFile.value = raw
  imagePreview.value = URL.createObjectURL(raw)
}

async function load() {
  loading.value = true
  try {
    const res = await productsApi.myProducts({ page: page.value, per_page: 10 })
    products.value = res.items || []
    total.value = res.total || 0
  } finally {
    loading.value = false
  }
}

function openDialog(product = null) {
  resetForm()
  if (product) {
    editId.value = product.product_id
    Object.assign(form, {
      product_name: product.product_name || '',
      category: product.category || '',
      price: product.price || 0,
      stock: product.stock || 0,
      description: product.description || '',
    })
    imagePreview.value = product.cover_image || '/NKU.png'
  } else {
    editId.value = null
  }
  dialogVisible.value = true
}

async function saveProduct() {
  saving.value = true
  try {
    const fd = new FormData()
    fd.append('product_name', form.product_name)
    fd.append('category', form.category)
    fd.append('price', form.price)
    fd.append('stock', form.stock)
    fd.append('description', form.description)
    if (imageFile.value) fd.append('image', imageFile.value)

    if (editId.value) await productsApi.update(editId.value, fd)
    else await productsApi.create(fd)

    ElMessage.success('保存成功')
    dialogVisible.value = false
    load()
  } finally {
    saving.value = false
  }
}

async function deleteProduct(row) {
  try {
    await productsApi.remove(row.product_id)
    ElMessage.success('已删除')
    load()
  } catch (err) {
    ElMessage.error(err?.response?.data?.error || '删除失败')
  }
}

onMounted(load)
</script>

<style scoped>
.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}
.thumb {
  width: 52px;
  height: 52px;
  object-fit: cover;
  border-radius: 6px;
}
.upload-wrap {
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.upload-tip {
  color: #909399;
  font-size: 12px;
}
.preview-img {
  width: 120px;
  height: 120px;
  object-fit: cover;
  border-radius: 8px;
  border: 1px solid #ebeef5;
}
.action-btn {
  border-radius: 10px;
  min-width: 92px;
  font-weight: 600;
}
.mini-btn {
  border-radius: 8px;
}
</style>

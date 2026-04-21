<template>
  <NavBar>
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:16px">
      <h2>商品管理</h2>
      <el-button type="primary" @click="openDialog()">+ 发布商品</el-button>
    </div>
    <el-table :data="products" border v-loading="loading">
      <el-table-column label="图片" width="80">
        <template #default="{ row }">
          <img :src="row.main_image || '/placeholder.jpg'" style="width:50px;height:50px;object-fit:cover;border-radius:4px" />
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
          <el-tag :type="{ on_sale:'success', off_sale:'info', reviewing:'warning' }[row.status]">{{ row.status }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="140">
        <template #default="{ row }">
          <el-button size="small" @click="openDialog(row)">编辑</el-button>
          <el-popconfirm title="确认删除？" @confirm="deleteProduct(row)">
            <template #reference><el-button size="small" type="danger">删除</el-button></template>
          </el-popconfirm>
        </template>
      </el-table-column>
    </el-table>
    <el-pagination v-if="total > 0" background layout="prev,pager,next,total"
      :total="total" :page-size="10" v-model:current-page="page"
      @current-change="load" style="margin-top:16px;justify-content:center;display:flex" />

    <el-dialog v-model="dialogVisible" :title="editId ? '编辑商品' : '发布商品'" width="560px">
      <el-form :model="form" label-width="80px">
        <el-form-item label="名称"><el-input v-model="form.product_name" /></el-form-item>
        <el-form-item label="分类">
          <el-select v-model="form.category">
            <el-option label="食品" value="food" /><el-option label="玩具" value="toy" />
            <el-option label="护理" value="care" /><el-option label="服装" value="clothing" />
            <el-option label="其他" value="other" />
          </el-select>
        </el-form-item>
        <el-form-item label="价格"><el-input-number v-model="form.price" :min="0" :precision="2" /></el-form-item>
        <el-form-item label="库存"><el-input-number v-model="form.stock" :min="0" /></el-form-item>
        <el-form-item label="描述"><el-input v-model="form.description" type="textarea" rows="3" /></el-form-item>
        <el-form-item label="图片URL"><el-input v-model="form.main_image" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveProduct" :loading="saving">保存</el-button>
      </template>
    </el-dialog>
  </NavBar>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import NavBar from '@/components/NavBar.vue'
import { productsApi } from '@/api'

const products = ref([])
const total    = ref(0)
const page     = ref(1)
const loading  = ref(false)
const saving   = ref(false)
const dialogVisible = ref(false)
const editId   = ref(null)
const form = reactive({ product_name:'', category:'food', price:0, stock:0, description:'', main_image:'' })

async function load() {
  loading.value = true
  try {
    const res = await productsApi.myList({ page: page.value, per_page: 10 })
    products.value = res.items || []
    total.value    = res.total || 0
  } finally { loading.value = false }
}

function openDialog(product = null) {
  editId.value = product?.product_id || null
  Object.assign(form, product || { product_name:'', category:'food', price:0, stock:0, description:'', main_image:'' })
  dialogVisible.value = true
}

async function saveProduct() {
  saving.value = true
  try {
    if (editId.value) await productsApi.update(editId.value, form)
    else              await productsApi.create(form)
    ElMessage.success('保存成功')
    dialogVisible.value = false
    load()
  } finally { saving.value = false }
}

async function deleteProduct(row) {
  await productsApi.delete(row.product_id)
  ElMessage.success('已删除')
  load()
}

onMounted(load)
</script>

<template>
  <div class="admin-page">
    <div class="page-banner">
      <div>
        <h2 class="page-banner-title">业务监管</h2>
        <p class="page-banner-sub">订单监管、预约监管、领养申请监管与投诉处理</p>
      </div>
    </div>

    <div class="page-card">
      <el-tabs v-model="activeTab" @tab-change="onTabChange" class="admin-tabs">

        <!-- 订单监管 -->
        <el-tab-pane label="订单监管" name="orders">
          <div class="filter-bar">
            <el-select v-model="orders.payStatus" placeholder="支付状态" clearable @change="loadOrders" style="width:140px">
              <el-option label="待支付" value="pending" />
              <el-option label="已支付" value="paid" />
              <el-option label="已退款" value="refunded" />
              <el-option label="已取消" value="cancelled" />
            </el-select>
            <el-input v-model="orders.keyword" placeholder="搜索买家用户名" clearable @change="loadOrders" style="width:200px" />
            <el-button type="primary" @click="loadOrders">搜索</el-button>
            <el-button @click="orders.payStatus='';orders.keyword='';loadOrders()">重置</el-button>
          </div>
          <el-table :data="orders.list" v-loading="orders.loading" stripe class="admin-table">
            <el-table-column prop="order_id" label="订单ID" width="80" />
            <el-table-column prop="order_no" label="订单号" min-width="160" />
            <el-table-column label="买家" width="120">
              <template #default="{ row }">{{ row.buyer?.nickname || row.buyer?.username || row.buyer_id }}</template>
            </el-table-column>
            <el-table-column label="总金额" width="100">
              <template #default="{ row }">¥{{ row.total_amount }}</template>
            </el-table-column>
            <el-table-column label="支付状态" width="100">
              <template #default="{ row }">
                <el-tag :type="payStatusType(row.pay_status)">{{ payStatusLabel(row.pay_status) }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="发货状态" width="100">
              <template #default="{ row }">
                <el-tag type="info">{{ deliveryLabel(row.delivery_status) }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="created_at" label="下单时间" width="160">
              <template #default="{ row }">{{ row.created_at?.replace('T', ' ').substring(0, 19) }}</template>
            </el-table-column>
          </el-table>
          <el-pagination background layout="prev,pager,next,total" :total="orders.total"
            :page-size="20" v-model:current-page="orders.page"
            @current-change="loadOrders" style="margin-top:12px;display:flex;justify-content:flex-end" />
        </el-tab-pane>

        <!-- 预约监管 -->
        <el-tab-pane label="预约监管" name="bookings">
          <div class="filter-bar">
            <el-select v-model="bookings.status" placeholder="预约状态" clearable @change="loadBookings" style="width:140px">
              <el-option label="待确认" value="pending" />
              <el-option label="已确认" value="confirmed" />
              <el-option label="已取消" value="cancelled" />
              <el-option label="已完成" value="finished" />
            </el-select>
            <el-button type="primary" @click="loadBookings">搜索</el-button>
            <el-button @click="bookings.status='';loadBookings()">重置</el-button>
          </div>
          <el-table :data="bookings.list" v-loading="bookings.loading" stripe class="admin-table">
            <el-table-column prop="booking_id" label="预约ID" width="80" />
            <el-table-column label="服务名称" min-width="150">
              <template #default="{ row }">{{ row.service?.service_name }}</template>
            </el-table-column>
            <el-table-column prop="pet_name" label="宠物名称" width="100" />
            <el-table-column label="预约日期" width="120">
              <template #default="{ row }">{{ row.slot?.slot_date }}</template>
            </el-table-column>
            <el-table-column label="时段" width="100">
              <template #default="{ row }">{{ row.slot?.slot_time }}</template>
            </el-table-column>
            <el-table-column label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="bookingStatusType(row.booking_status)">{{ bookingStatusLabel(row.booking_status) }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="created_at" label="提交时间" width="160">
              <template #default="{ row }">{{ row.created_at?.replace('T', ' ').substring(0, 19) }}</template>
            </el-table-column>
          </el-table>
          <el-pagination background layout="prev,pager,next,total" :total="bookings.total"
            :page-size="20" v-model:current-page="bookings.page"
            @current-change="loadBookings" style="margin-top:12px;display:flex;justify-content:flex-end" />
        </el-tab-pane>

        <!-- 领养申请监管 -->
        <el-tab-pane label="领养申请" name="adoptions">
          <div class="filter-bar">
            <el-select v-model="adoptions.status" placeholder="审核状态" clearable @change="loadAdoptions" style="width:140px">
              <el-option label="待审核" value="pending" />
              <el-option label="已通过" value="approved" />
              <el-option label="已拒绝" value="rejected" />
              <el-option label="待补材料" value="supplement" />
              <el-option label="已取消" value="cancelled" />
            </el-select>
            <el-button type="primary" @click="loadAdoptions">搜索</el-button>
            <el-button @click="adoptions.status='';loadAdoptions()">重置</el-button>
          </div>
          <el-table :data="adoptions.list" v-loading="adoptions.loading" stripe class="admin-table">
            <el-table-column prop="application_id" label="申请ID" width="80" />
            <el-table-column label="宠物" width="120">
              <template #default="{ row }">{{ row.pet?.pet_name }}</template>
            </el-table-column>
            <el-table-column label="申请人" width="120">
              <template #default="{ row }">{{ row.applicant?.nickname || row.applicant?.username }}</template>
            </el-table-column>
            <el-table-column label="状态" width="110">
              <template #default="{ row }">
                <el-tag :type="adoptionStatusType(row.review_status)">{{ adoptionStatusLabel(row.review_status) }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="review_remark" label="审核意见" min-width="150" show-overflow-tooltip />
            <el-table-column prop="submitted_at" label="提交时间" width="160">
              <template #default="{ row }">{{ row.submitted_at?.replace('T', ' ').substring(0, 19) }}</template>
            </el-table-column>
          </el-table>
          <el-pagination background layout="prev,pager,next,total" :total="adoptions.total"
            :page-size="20" v-model:current-page="adoptions.page"
            @current-change="loadAdoptions" style="margin-top:12px;display:flex;justify-content:flex-end" />
        </el-tab-pane>

        <!-- 投诉处理 -->
        <el-tab-pane label="投诉处理" name="complaints">
          <div class="filter-bar">
            <el-select v-model="complaints.status" placeholder="处理状态" clearable @change="loadComplaints" style="width:140px">
              <el-option label="待处理" value="pending" />
              <el-option label="处理中" value="handling" />
              <el-option label="已解决" value="resolved" />
              <el-option label="已关闭" value="closed" />
            </el-select>
            <el-button type="primary" @click="loadComplaints">搜索</el-button>
            <el-button @click="complaints.status='';loadComplaints()">重置</el-button>
          </div>
          <el-table :data="complaints.list" v-loading="complaints.loading" stripe class="admin-table">
            <el-table-column prop="complaint_id" label="ID" width="70" />
            <el-table-column label="投诉人" width="120">
              <template #default="{ row }">{{ row.user?.nickname || row.user?.username }}</template>
            </el-table-column>
            <el-table-column prop="target_type" label="对象类型" width="90" />
            <el-table-column prop="target_id" label="对象ID" width="80" />
            <el-table-column prop="content" label="投诉内容" min-width="200" show-overflow-tooltip />
            <el-table-column label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="complaintStatusType(row.status)">{{ complaintStatusLabel(row.status) }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="admin_reply" label="管理员回复" min-width="150" show-overflow-tooltip />
            <el-table-column prop="created_at" label="提交时间" width="160">
              <template #default="{ row }">{{ row.created_at?.replace('T', ' ').substring(0, 19) }}</template>
            </el-table-column>
            <el-table-column label="操作" fixed="right" width="90">
              <template #default="{ row }">
                <el-button v-if="row.status !== 'resolved' && row.status !== 'closed'"
                  type="primary" size="small" @click="openHandleDialog(row)">处理</el-button>
              </template>
            </el-table-column>
          </el-table>
          <el-pagination background layout="prev,pager,next,total" :total="complaints.total"
            :page-size="20" v-model:current-page="complaints.page"
            @current-change="loadComplaints" style="margin-top:12px;display:flex;justify-content:flex-end" />
        </el-tab-pane>

      </el-tabs>
    </div>

    <!-- 投诉处理弹窗 -->
    <el-dialog v-model="handleDialog.visible" title="处理投诉" width="500px">
      <el-form :model="handleDialog" label-width="90px">
        <el-form-item label="处理结果">
          <el-select v-model="handleDialog.status" style="width:100%">
            <el-option label="处理中" value="handling" />
            <el-option label="已解决" value="resolved" />
            <el-option label="已关闭" value="closed" />
          </el-select>
        </el-form-item>
        <el-form-item label="回复内容">
          <el-input v-model="handleDialog.admin_reply" type="textarea" :rows="4" placeholder="填写处理回复" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="handleDialog.visible = false">取消</el-button>
        <el-button type="primary" :loading="handleDialog.loading" @click="submitHandle">提交</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { adminApi } from '@/api'

const activeTab = ref('orders')

// ---- 订单 ----
const orders = reactive({ list: [], total: 0, page: 1, loading: false, payStatus: '', keyword: '' })
async function loadOrders() {
  orders.loading = true
  try {
    const res = await adminApi.orders({ page: orders.page, per_page: 20, pay_status: orders.payStatus, keyword: orders.keyword })
    orders.list  = res.items || []
    orders.total = res.total || 0
  } catch { orders.list = [] }
  finally { orders.loading = false }
}

// ---- 预约 ----
const bookings = reactive({ list: [], total: 0, page: 1, loading: false, status: '' })
async function loadBookings() {
  bookings.loading = true
  try {
    const res = await adminApi.bookings({ page: bookings.page, per_page: 20, status: bookings.status })
    bookings.list  = res.items || []
    bookings.total = res.total || 0
  } catch { bookings.list = [] }
  finally { bookings.loading = false }
}

// ---- 领养申请 ----
const adoptions = reactive({ list: [], total: 0, page: 1, loading: false, status: '' })
async function loadAdoptions() {
  adoptions.loading = true
  try {
    const res = await adminApi.adoptions({ page: adoptions.page, per_page: 20, status: adoptions.status })
    adoptions.list  = res.items || []
    adoptions.total = res.total || 0
  } catch { adoptions.list = [] }
  finally { adoptions.loading = false }
}

// ---- 投诉 ----
const complaints = reactive({ list: [], total: 0, page: 1, loading: false, status: '' })
async function loadComplaints() {
  complaints.loading = true
  try {
    const res = await adminApi.complaints({ page: complaints.page, per_page: 20, status: complaints.status })
    complaints.list  = res.items || []
    complaints.total = res.total || 0
  } catch { complaints.list = [] }
  finally { complaints.loading = false }
}

// ---- 投诉处理弹窗 ----
const handleDialog = reactive({ visible: false, loading: false, complaintId: null, status: 'resolved', admin_reply: '' })
function openHandleDialog(row) {
  handleDialog.complaintId = row.complaint_id
  handleDialog.status      = 'resolved'
  handleDialog.admin_reply = ''
  handleDialog.visible     = true
}
async function submitHandle() {
  if (!handleDialog.admin_reply.trim()) {
    ElMessage.warning('请填写处理回复')
    return
  }
  handleDialog.loading = true
  try {
    await adminApi.handleComplaint(handleDialog.complaintId, {
      status: handleDialog.status,
      admin_reply: handleDialog.admin_reply,
    })
    ElMessage.success('处理成功')
    handleDialog.visible = false
    loadComplaints()
  } catch { /* error shown by interceptor */ }
  finally { handleDialog.loading = false }
}

function onTabChange(tab) {
  if (tab === 'orders'     && !orders.list.length)    loadOrders()
  if (tab === 'bookings'   && !bookings.list.length)  loadBookings()
  if (tab === 'adoptions'  && !adoptions.list.length) loadAdoptions()
  if (tab === 'complaints' && !complaints.list.length) loadComplaints()
}

onMounted(() => { loadOrders() })

// ---- 标签辅助函数 ----
const payStatusLabel  = s => ({ pending: '待支付', paid: '已支付', refunded: '已退款', cancelled: '已取消' }[s] || s)
const payStatusType   = s => ({ pending: 'warning', paid: 'success', refunded: 'info', cancelled: 'danger' }[s])
const deliveryLabel   = s => ({ pending: '待发货', shipped: '已发货', delivered: '已送达' }[s] || s)
const bookingStatusLabel = s => ({ pending: '待确认', confirmed: '已确认', cancelled: '已取消', finished: '已完成' }[s] || s)
const bookingStatusType  = s => ({ pending: 'warning', confirmed: 'success', cancelled: 'danger', finished: 'info' }[s])
const adoptionStatusLabel = s => ({ pending: '待审核', approved: '已通过', rejected: '已拒绝', supplement: '待补材料', cancelled: '已取消' }[s] || s)
const adoptionStatusType  = s => ({ pending: 'warning', approved: 'success', rejected: 'danger', supplement: 'info', cancelled: '' }[s])
const complaintStatusLabel = s => ({ pending: '待处理', handling: '处理中', resolved: '已解决', closed: '已关闭' }[s] || s)
const complaintStatusType  = s => ({ pending: 'danger', handling: 'warning', resolved: 'success', closed: 'info' }[s])
</script>

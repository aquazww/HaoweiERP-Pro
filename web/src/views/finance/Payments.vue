<template>
  <div class="common-page finance-page">
    <div class="page-content">
      <div class="toolbar-card">
        <div class="toolbar-left">
          <div class="search-box">
            <el-icon class="search-icon"><Search /></el-icon>
            <el-input
              v-model="searchKeyword"
              placeholder="搜索单号、关联单号、往来单位"
              class="search-input"
              clearable
              @keyup.enter="loadPayments"
            />
          </div>
          <el-select v-model="query.type" placeholder="类型" clearable style="width: 120px" @change="loadPayments">
            <el-option label="全部" :value="''" />
            <el-option label="付款" value="pay" />
            <el-option label="收款" value="receive" />
          </el-select>
          <el-select v-model="query.status" placeholder="状态" clearable style="width: 120px" @change="loadPayments">
            <el-option label="全部" :value="''" />
            <el-option label="待付款" value="pending" />
            <el-option label="部分付款" value="partial" />
            <el-option label="已付款" value="paid" />
          </el-select>
        </div>
        <div class="toolbar-right">
          <el-button :icon="Refresh" @click="loadPayments">刷新</el-button>
          <el-button type="primary" :icon="Plus" @click="handleAdd" v-if="canAddFinance">新增收付款</el-button>
        </div>
      </div>

      <div class="table-card">
        <el-table 
          :data="paymentList" 
          style="width: 100%" 
          v-loading="loading"
          class="data-table"
          stripe
          :height="tableHeight"
          :header-cell-style="{ background: 'var(--color-bg-light)' }"
        >
          <el-table-column prop="related_party_name" label="往来单位" min-width="140">
            <template #default="{ row }">
              <span class="party-name">{{ row.related_party_name }}</span>
            </template>
          </el-table-column>
          <el-table-column label="类型" width="80" align="center">
            <template #default="{ row }">
              <el-tag :type="row.type === 'pay' ? 'warning' : 'success'" size="small">
                {{ row.type === 'pay' ? '付款' : '收款' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="related_order_no" label="关联单号" min-width="140" align="center">
            <template #default="{ row }">
              <span class="order-no-link" @click="handleViewOrder(row)">{{ row.related_order_no }}</span>
            </template>
          </el-table-column>
          <el-table-column label="总金额" width="120" align="right">
            <template #default="{ row }">
              <span class="price-text">¥{{ formatPrice(row.total_amount) }}</span>
            </template>
          </el-table-column>
          <el-table-column label="已付金额" width="120" align="right">
            <template #default="{ row }">
              <span class="price-text" style="color: var(--color-success);">¥{{ formatPrice(row.paid_amount) }}</span>
            </template>
          </el-table-column>
          <el-table-column label="未付金额" width="120" align="right">
            <template #default="{ row }">
              <span class="price-text" style="color: var(--color-danger);">¥{{ formatPrice(row.unpaid_amount) }}</span>
            </template>
          </el-table-column>
          <el-table-column label="状态" width="100" align="center">
            <template #default="{ row }">
              <div class="status-badge small" :class="row.status">
                <span class="status-dot"></span>
                {{ getStatusText(row.status) }}
              </div>
            </template>
          </el-table-column>
          <el-table-column prop="order_no" label="收付款单号" min-width="140" align="center">
            <template #default="{ row }">
              <span class="order-no-link" @click="handleView(row)">{{ row.order_no }}</span>
            </template>
          </el-table-column>
        </el-table>
        <div class="pagination-wrapper">
          <el-pagination
            v-model:current-page="query.page"
            v-model:page-size="query.pageSize"
            :page-sizes="[10, 20, 50, 100]"
            :total="query.total"
            layout="total, sizes, prev, pager, next, jumper"
            @size-change="loadPayments"
            @current-change="loadPayments"
          />
        </div>
      </div>
    </div>

    <!-- 查看详情弹窗 -->
    <el-dialog
      v-model="viewDialogVisible"
      width="700px"
      class="view-dialog"
      :show-close="false"
    >
      <template #header>
        <div class="dialog-header">
          <span class="dialog-title">{{ viewData?.type === 'pay' ? '付款详情' : '收款详情' }}</span>
          <div class="header-actions">
            <el-button class="action-btn pay-btn" size="small" @click="handlePayFromView" v-if="canEditFinance && viewData?.status !== 'paid'">{{ viewData?.type === 'pay' ? '付款' : '收款' }}</el-button>
          </div>
        </div>
        <span class="close-btn" @click="viewDialogVisible = false">×</span>
      </template>
      
      <div class="detail-container" v-if="viewData">
        <div class="info-section">
          <div class="info-row highlight-row">
            <div class="info-item-group">
              <span class="info-label">往来单位</span>
              <span class="info-value">{{ viewData.related_party_name }}</span>
            </div>
            <div class="info-item-group order-no-with-status">
              <span class="info-label">收付款单号</span>
              <div class="order-no-status-wrapper">
                <span class="info-value primary">{{ viewData.order_no }}</span>
                <div class="status-badge small" :class="viewData.status">
                  <span class="status-dot"></span>
                  {{ getStatusText(viewData.status) }}
                </div>
              </div>
            </div>
          </div>
          <div class="info-row highlight-row">
            <div class="info-item-group">
              <span class="info-label">关联单号</span>
              <span class="info-value">{{ viewData.related_order_no }}</span>
            </div>
            <div class="info-item-group">
              <span class="info-label">类型</span>
              <span class="info-value">{{ viewData.type === 'pay' ? '付款' : '收款' }}</span>
            </div>
          </div>
          <div class="info-row highlight-row">
            <div class="info-item-group">
              <span class="info-label">总金额</span>
              <span class="info-value price">¥{{ formatPrice(viewData.total_amount) }}</span>
            </div>
            <div class="info-item-group">
              <span class="info-label">已付金额</span>
              <span class="info-value price" style="color: var(--color-success);">¥{{ formatPrice(viewData.paid_amount) }}</span>
            </div>
          </div>
          <div class="info-row">
            <div class="info-item">
              <span class="info-label">未付金额</span>
              <span class="info-value price" style="color: var(--color-danger);">¥{{ formatPrice(viewData.unpaid_amount) }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">创建时间</span>
              <span class="info-value">{{ formatDateTime(viewData.created_at) }}</span>
            </div>
          </div>
        </div>
        
        <div class="remark-box" v-if="viewData.remark">
          <div class="remark-header">
            <el-icon class="remark-icon"><Document /></el-icon>
            <span>备注</span>
          </div>
          <div class="remark-text">{{ viewData.remark }}</div>
        </div>
        
        <div class="records-section" v-if="viewData.records && viewData.records.length > 0">
          <div class="records-header" @click="recordsExpanded = !recordsExpanded">
            <div class="header-left">
              <el-icon class="expand-icon" :class="{ expanded: recordsExpanded }"><ArrowRight /></el-icon>
              <span class="header-title">付款记录</span>
              <span class="header-count">{{ viewData.records.length }}笔</span>
            </div>
            <span class="expand-hint">{{ recordsExpanded ? '收起' : '展开' }}</span>
          </div>
          <el-collapse-transition>
            <div class="records-body" v-show="recordsExpanded">
              <el-table :data="viewData.records" border size="small" class="detail-table">
                <el-table-column label="付款金额" min-width="100" align="right">
                  <template #default="{ row }">
                    <span class="price-text">¥{{ formatPrice(row.amount) }}</span>
                  </template>
                </el-table-column>
                <el-table-column prop="payment_method_display" label="付款方式" min-width="90" align="center" />
                <el-table-column prop="payment_date" label="付款日期" min-width="100" align="center" />
                <el-table-column prop="created_by_name" label="操作人" min-width="80" align="center" />
                <el-table-column prop="created_at" label="操作时间" min-width="140" align="center">
                  <template #default="{ row }">{{ formatDateTime(row.created_at) }}</template>
                </el-table-column>
              </el-table>
            </div>
          </el-collapse-transition>
        </div>
      </div>
    </el-dialog>

    <!-- 新增收付款弹窗 -->
    <el-dialog
      v-model="addDialogVisible"
      width="600px"
      class="form-dialog"
      :show-close="false"
    >
      <template #header>
        <div class="dialog-header">
          <span class="dialog-title">新增收付款</span>
        </div>
        <span class="close-btn" @click="addDialogVisible = false">×</span>
      </template>
      
      <div class="form-container">
        <div class="form-section-card">
          <div class="form-section-header">
            <span class="section-title">选择单据</span>
          </div>
          <div class="form-section-body">
            <div class="form-row">
              <div class="form-item">
                <span class="form-label required">单据类型</span>
                <el-select v-model="addForm.order_type" placeholder="请选择单据类型" style="flex: 1" @change="handleOrderTypeChange">
                  <el-option label="采购订单（付款）" value="purchase" />
                  <el-option label="销售订单（收款）" value="sale" />
                </el-select>
              </div>
            </div>
            <div class="form-row">
              <div class="form-item">
                <span class="form-label required">关联单据</span>
                <el-select 
                  v-model="addForm.order_id" 
                  placeholder="请选择关联单据" 
                  style="flex: 1" 
                  filterable
                  @change="handleOrderChange"
                >
                  <el-option 
                    v-for="item in orderList" 
                    :key="item.id" 
                    :label="`${item.order_no} - ${item.related_party_name} - ¥${formatPrice(item.total_amount)}`" 
                    :value="item.id"
                  />
                </el-select>
              </div>
            </div>
          </div>
        </div>
        
        <div class="form-section-card" v-if="selectedOrderInfo">
          <div class="form-section-header">
            <span class="section-title">单据信息</span>
          </div>
          <div class="form-section-body">
            <div class="order-info-grid">
              <div class="info-item">
                <span class="info-label">往来单位</span>
                <span class="info-value">{{ selectedOrderInfo.related_party_name }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">总金额</span>
                <span class="info-value price">¥{{ formatPrice(selectedOrderInfo.total_amount) }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">已付金额</span>
                <span class="info-value" style="color: var(--color-success);">¥{{ formatPrice(selectedOrderInfo.paid_amount) }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">未付金额</span>
                <span class="info-value" style="color: var(--color-danger);">¥{{ formatPrice(selectedOrderInfo.unpaid_amount) }}</span>
              </div>
            </div>
          </div>
        </div>
        
        <div class="form-section-card">
          <div class="form-section-header">
            <span class="section-title">备注</span>
          </div>
          <div class="form-section-body">
            <el-input
              v-model="addForm.remark"
              type="textarea"
              :rows="2"
              placeholder="请输入备注（可选）"
            />
          </div>
        </div>
      </div>
      
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="addDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleConfirmAdd" :loading="addLoading">确认创建</el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 付款操作弹窗 -->
    <el-dialog
      v-model="payDialogVisible"
      width="500px"
      class="form-dialog"
      :show-close="false"
    >
      <template #header>
        <div class="dialog-header">
          <span class="dialog-title">{{ payForm.type === 'pay' ? '付款操作' : '收款操作' }}</span>
        </div>
        <span class="close-btn" @click="payDialogVisible = false">×</span>
      </template>
      
      <div class="form-container">
        <div class="form-section-card">
          <div class="form-section-header">
            <span class="section-title">{{ payForm.type === 'pay' ? '付款信息' : '收款信息' }}</span>
          </div>
          <div class="form-section-body">
            <div class="form-row">
              <div class="form-item">
                <span class="form-label">单号</span>
                <span class="form-value">{{ payForm.order_no }}</span>
              </div>
            </div>
            <div class="form-row">
              <div class="form-item">
                <span class="form-label">未付金额</span>
                <span class="form-value price" style="color: var(--color-danger);">¥{{ formatPrice(payForm.unpaid_amount) }}</span>
              </div>
            </div>
            <div class="form-row">
              <div class="form-item">
                <span class="form-label required">{{ payForm.type === 'pay' ? '付款金额' : '收款金额' }}</span>
                <el-input
                  v-model="payForm.amount"
                  placeholder="请输入金额"
                  type="number"
                  style="flex: 1"
                >
                  <template #prefix>¥</template>
                </el-input>
              </div>
            </div>
            <div class="form-row">
              <div class="form-item">
                <span class="form-label required">{{ payForm.type === 'pay' ? '付款方式' : '收款方式' }}</span>
                <el-select v-model="payForm.payment_method" placeholder="请选择" style="flex: 1">
                  <el-option label="现金" value="cash" />
                  <el-option label="银行转账" value="bank" />
                  <el-option label="支付宝" value="alipay" />
                  <el-option label="微信" value="wechat" />
                </el-select>
              </div>
            </div>
            <div class="form-row">
              <div class="form-item">
                <span class="form-label required">{{ payForm.type === 'pay' ? '付款日期' : '收款日期' }}</span>
                <el-date-picker
                  v-model="payForm.payment_date"
                  type="date"
                  placeholder="选择日期"
                  style="flex: 1"
                  value-format="YYYY-MM-DD"
                />
              </div>
            </div>
            <div class="form-row">
              <div class="form-item" style="align-items: flex-start;">
                <span class="form-label">备注</span>
                <el-input
                  v-model="payForm.remark"
                  type="textarea"
                  :rows="2"
                  placeholder="请输入备注（可选）"
                  style="flex: 1"
                />
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="payDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleConfirmPay" :loading="payLoading">确认</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick, onUnmounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Refresh, Plus, Document, ArrowRight } from '@element-plus/icons-vue'
import { getPayments, getPayment, createPayment, deletePayment, payPayment, getPaymentOrderInfo } from '../../api/finance'
import { getPurchaseOrders } from '../../api/purchase'
import { getSaleOrders } from '../../api/sale'
import { canAdd, canEdit, canDelete } from '../../utils/permission'
import { formatPrice } from '../../utils/format'

const canAddFinance = computed(() => canAdd('finance'))
const canEditFinance = computed(() => canEdit('finance'))
const canDeleteFinance = computed(() => canDelete('finance'))

const loading = ref(false)
const addLoading = ref(false)
const payLoading = ref(false)
const viewDialogVisible = ref(false)
const addDialogVisible = ref(false)
const payDialogVisible = ref(false)
const paymentList = ref([])
const viewData = ref(null)
const recordsExpanded = ref(false)
const selectedOrderInfo = ref(null)
const orderList = ref([])

const searchKeyword = ref('')
const query = ref({
  page: 1,
  pageSize: 20,
  total: 0,
  type: '',
  status: ''
})
const tableHeight = ref(0)

const addForm = ref({
  order_type: '',
  order_id: '',
  remark: ''
})

const payForm = ref({
  id: '',
  order_no: '',
  type: 'pay',
  unpaid_amount: 0,
  amount: '',
  payment_method: 'bank',
  payment_date: '',
  remark: ''
})

const formatDateTime = (datetime) => {
  if (!datetime) return '-'
  const date = new Date(datetime)
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  const hours = String(date.getHours()).padStart(2, '0')
  const minutes = String(date.getMinutes()).padStart(2, '0')
  return `${year}-${month}-${day} ${hours}:${minutes}`
}

const getStatusText = (status) => {
  const map = {
    'pending': '待付款',
    'partial': '部分付款',
    'paid': '已付款'
  }
  return map[status] || status
}

const loadPayments = async () => {
  loading.value = true
  try {
    const res = await getPayments({
      page: query.value.page,
      page_size: query.value.pageSize,
      search: searchKeyword.value,
      type: query.value.type,
      status: query.value.status
    })
    console.log('收付款列表响应:', res)
    paymentList.value = res.data?.items || res.data?.data?.items || res.data?.results || []
    query.value.total = res.data?.count || res.data?.data?.count || 0
  } catch (error) {
    console.error('加载失败:', error)
    ElMessage.error('加载失败')
  } finally {
    loading.value = false
  }
}

const handleView = async (row) => {
  try {
    const res = await getPayment(row.id)
    viewData.value = res.data.data || res.data
    viewDialogVisible.value = true
  } catch (error) {
    ElMessage.error('加载详情失败')
  }
}

const handleViewOrder = (row) => {
  if (row.related_order_type === 'purchase') {
    window.location.href = `/purchase?order_no=${row.related_order_no}`
  } else if (row.related_order_type === 'sale') {
    window.location.href = `/sale?order_no=${row.related_order_no}`
  }
}

const handleAdd = () => {
  addForm.value = {
    order_type: '',
    order_id: '',
    remark: ''
  }
  selectedOrderInfo.value = null
  orderList.value = []
  addDialogVisible.value = true
}

const handleOrderTypeChange = async () => {
  addForm.value.order_id = ''
  selectedOrderInfo.value = null
  orderList.value = []
  
  if (!addForm.value.order_type) return
  
  try {
    let res
    if (addForm.value.order_type === 'purchase') {
      res = await getPurchaseOrders({ page_size: 100 })
    } else {
      res = await getSaleOrders({ page_size: 100 })
    }
    console.log('API响应:', res)
    console.log('res.data:', res.data)
    let orders = res.data?.data?.items || res.data?.data?.results || res.data?.results || res.data?.items || []
    console.log('订单数据:', orders)
    orders = orders.filter(item => item.status !== 'cancelled')
    orderList.value = orders.map(item => ({
      ...item,
      related_party_name: item.supplier_name || item.customer_name
    }))
    console.log('处理后订单列表:', orderList.value)
  } catch (error) {
    console.error('加载订单列表失败:', error)
    ElMessage.error('加载订单列表失败: ' + (error.message || '未知错误'))
  }
}

const handleOrderChange = async () => {
  if (!addForm.value.order_id || !addForm.value.order_type) {
    selectedOrderInfo.value = null
    return
  }
  
  try {
    const res = await getPaymentOrderInfo(addForm.value.order_type, addForm.value.order_id)
    selectedOrderInfo.value = res.data.data
  } catch (error) {
    ElMessage.error('获取订单信息失败')
  }
}

const handleConfirmAdd = async () => {
  if (!addForm.value.order_type) {
    ElMessage.warning('请选择单据类型')
    return
  }
  if (!addForm.value.order_id) {
    ElMessage.warning('请选择关联单据')
    return
  }
  
  addLoading.value = true
  try {
    const paymentType = addForm.value.order_type === 'purchase' ? 'pay' : 'receive'
    await createPayment({
      type: paymentType,
      related_order_type: addForm.value.order_type,
      related_order_id: addForm.value.order_id,
      remark: addForm.value.remark
    })
    ElMessage.success('创建成功')
    addDialogVisible.value = false
    loadPayments()
  } catch (error) {
    ElMessage.error('创建失败：' + (error.response?.data?.msg || error.message || '未知错误'))
  } finally {
    addLoading.value = false
  }
}

const handlePay = (row) => {
  payForm.value = {
    id: row.id,
    order_no: row.order_no,
    type: row.type,
    unpaid_amount: row.unpaid_amount,
    amount: String(row.unpaid_amount),
    payment_method: 'bank',
    payment_date: new Date().toISOString().split('T')[0],
    remark: ''
  }
  payDialogVisible.value = true
}

const handlePayFromView = () => {
  if (!viewData.value) return
  viewDialogVisible.value = false
  handlePay(viewData.value)
}

const handleConfirmPay = async () => {
  if (!payForm.value.amount || parseFloat(payForm.value.amount) <= 0) {
    ElMessage.warning('请输入有效的付款金额')
    return
  }
  if (parseFloat(payForm.value.amount) > payForm.value.unpaid_amount) {
    ElMessage.warning('付款金额不能超过未付金额')
    return
  }
  if (!payForm.value.payment_method) {
    ElMessage.warning('请选择付款方式')
    return
  }
  if (!payForm.value.payment_date) {
    ElMessage.warning('请选择付款日期')
    return
  }
  
  payLoading.value = true
  try {
    await payPayment(payForm.value.id, {
      amount: parseFloat(payForm.value.amount),
      payment_method: payForm.value.payment_method,
      payment_date: payForm.value.payment_date,
      remark: payForm.value.remark
    })
    ElMessage.success('付款成功')
    payDialogVisible.value = false
    loadPayments()
  } catch (error) {
    ElMessage.error('付款失败：' + (error.response?.data?.msg || error.message || '未知错误'))
  } finally {
    payLoading.value = false
  }
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm(`确定删除收付款单「${row.order_no}」？`, '确认删除', { type: 'warning' })
    await deletePayment(row.id)
    ElMessage.success('删除成功')
    loadPayments()
  } catch (error) {
    if (error !== 'cancel') ElMessage.error('删除失败')
  }
}

const calculateTableHeight = () => {
  nextTick(() => {
    const windowHeight = window.innerHeight
    tableHeight.value = windowHeight - 200
  })
}

onMounted(() => {
  loadPayments()
  calculateTableHeight()
  window.addEventListener('resize', calculateTableHeight)
})

onUnmounted(() => {
  window.removeEventListener('resize', calculateTableHeight)
})
</script>

<style scoped>
@import '../../styles/page-common.css';

.finance-page .party-name {
  font-weight: 600;
  color: #303133;
}

.finance-page .order-no-link {
  display: inline-block;
  padding: 2px 10px;
  background-color: rgba(22, 93, 255, 0.08);
  color: var(--color-primary);
  font-weight: 600;
  font-size: var(--font-size-sm);
  border-radius: var(--border-radius-sm);
  font-family: 'Monaco', 'Consolas', monospace;
  cursor: pointer;
  transition: all 0.3s ease-in-out;
  text-decoration: none;
  transform-origin: center center;
}

.finance-page .order-no-link:hover {
  background-color: rgba(22, 93, 255, 0.2);
  color: #023e7d;
  text-decoration: none;
  transform: scale(1.1);
  box-shadow: 0 2px 8px rgba(22, 93, 255, 0.25);
}

.finance-page .data-table :deep(.el-table__row) {
  transition: all 0.2s ease-in-out;
}

.finance-page .data-table :deep(.el-table__row:hover) {
  outline: 1px solid #1890ff;
  outline-offset: -1px;
  background-color: #e6f7ff !important;
}

.finance-page .data-table :deep(.el-table__row:hover) .el-table__cell {
  border-top: 1px solid #1890ff;
  border-bottom: 1px solid #1890ff;
}

.finance-page .data-table :deep(.el-table__row:hover) .el-table__cell:first-child {
  border-left: 1px solid #1890ff;
}

.finance-page .data-table :deep(.el-table__row:hover) .el-table__cell:last-child {
  border-right: 1px solid #1890ff;
}

.finance-page .view-dialog :deep(.el-dialog__header) {
  padding: 0;
  margin: 0;
  position: relative;
}

.finance-page .view-dialog :deep(.el-dialog__body) {
  padding: 12px 16px;
}

.finance-page .dialog-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 14px 16px;
  background: linear-gradient(135deg, #f0f5ff 0%, #e6f4ff 100%);
  border-bottom: 1px solid #bae0ff;
  border-radius: var(--el-dialog-border-radius) var(--el-dialog-border-radius) 0 0;
  padding-right: 50px;
}

.finance-page .dialog-title {
  font-size: 16px;
  font-weight: 600;
  color: #333;
}

.finance-page .header-actions {
  display: flex;
  align-items: center;
  gap: 10px;
}

.finance-page .action-btn {
  padding: 6px 14px !important;
  font-size: 12px !important;
  font-weight: 500 !important;
  border-radius: 6px !important;
  border: none !important;
  transition: all 0.3s ease-in-out !important;
  transform-origin: center center;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.finance-page .action-btn:hover {
  transform: scale(1.05);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
}

.finance-page .pay-btn {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%) !important;
  color: #fff !important;
}

.finance-page .pay-btn:hover {
  background: linear-gradient(135deg, #059669 0%, #047857 100%) !important;
}

.finance-page .order-no-with-status {
  flex: 1;
}

.finance-page .order-no-status-wrapper {
  display: flex;
  align-items: center;
  gap: 12px;
  justify-content: flex-end;
}

.finance-page .order-no-status-wrapper .status-badge {
  flex-shrink: 0;
}

.finance-page .close-btn {
  position: absolute;
  top: 0;
  right: 0;
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  font-weight: 300;
  color: #999;
  cursor: pointer;
  line-height: 1;
  transition: all 0.2s;
  border-radius: 0 var(--el-dialog-border-radius) 0 6px;
  background: transparent;
}

.finance-page .close-btn:hover {
  color: #333;
  background: rgba(0, 0, 0, 0.04);
}

.finance-page .detail-container {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.finance-page .info-section {
  border: 1px solid #e8e8e8;
  border-radius: 8px;
  overflow: hidden;
}

.finance-page .info-row {
  display: flex;
  border-bottom: 1px solid #f0f0f0;
}

.finance-page .info-row:last-child {
  border-bottom: none;
}

.finance-page .info-row.highlight-row {
  background: linear-gradient(135deg, #fafbfc 0%, #f5f7fa 100%);
}

.finance-page .info-item-group {
  flex: 1;
  display: flex;
  align-items: center;
  padding: 10px 14px;
  gap: 8px;
}

.finance-page .info-item-group:not(:last-child) {
  border-right: 1px solid #f0f0f0;
}

.finance-page .info-item {
  flex: 1;
  display: flex;
  align-items: center;
  padding: 10px 14px;
  gap: 8px;
}

.finance-page .info-item:not(:last-child) {
  border-right: 1px solid #f0f0f0;
}

.finance-page .info-label {
  font-size: 12px;
  color: #909399;
  white-space: nowrap;
}

.finance-page .info-value {
  font-size: 13px;
  color: #303133;
  flex: 1;
  text-align: right;
}

.finance-page .info-value.primary {
  color: var(--color-primary);
  font-weight: 600;
  font-family: 'Monaco', 'Consolas', monospace;
}

.finance-page .info-value.price {
  font-weight: 600;
  font-family: 'Monaco', 'Consolas', monospace;
}

.finance-page .remark-box {
  border: 1px solid #e8e8e8;
  border-radius: 8px;
  overflow: hidden;
}

.finance-page .remark-header {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 10px 14px;
  background: #fafafa;
  border-bottom: 1px solid #e8e8e8;
  font-size: 13px;
  font-weight: 500;
  color: #666;
}

.finance-page .remark-icon {
  font-size: 14px;
  color: #909399;
}

.finance-page .remark-text {
  padding: 12px 14px;
  font-size: 13px;
  color: #606266;
  line-height: 1.6;
}

.finance-page .records-section {
  border: 1px solid #e8e8e8;
  border-radius: 8px;
  overflow: hidden;
}

.finance-page .records-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 14px;
  background: #fafafa;
  border-bottom: 1px solid #e8e8e8;
  cursor: pointer;
  user-select: none;
}

.finance-page .records-header:hover {
  background: #f5f5f5;
}

.finance-page .header-left {
  display: flex;
  align-items: center;
  gap: 8px;
}

.finance-page .expand-icon {
  font-size: 12px;
  color: #909399;
  transition: transform 0.3s;
}

.finance-page .expand-icon.expanded {
  transform: rotate(90deg);
}

.finance-page .header-title {
  font-size: 13px;
  font-weight: 500;
  color: #333;
}

.finance-page .header-count {
  font-size: 12px;
  color: #909399;
  background: #f0f0f0;
  padding: 2px 8px;
  border-radius: 10px;
}

.finance-page .expand-hint {
  font-size: 12px;
  color: #909399;
}

.finance-page .records-body {
  padding: 0;
}

.finance-page .detail-table {
  border: none;
}

.finance-page .detail-table :deep(.el-table__header th) {
  background: #fafafa;
  font-weight: 500;
  font-size: 12px;
  color: #666;
}

.finance-page .detail-table :deep(.el-table__body td) {
  padding: 10px 0;
  border-bottom: 1px solid #f0f2f5;
}

.finance-page .form-dialog :deep(.el-dialog__header) {
  padding: 0;
  margin: 0;
  position: relative;
}

.finance-page .form-dialog :deep(.el-dialog__body) {
  padding: 12px 16px;
}

.finance-page .form-dialog :deep(.el-dialog__footer) {
  padding: 12px 16px;
  border-top: 1px solid #e8e8e8;
}

.finance-page .form-container {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.finance-page .form-section-card {
  border: 1px solid #e8e8e8;
  border-radius: 8px;
  overflow: hidden;
}

.finance-page .form-section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 14px;
  background: linear-gradient(135deg, #f8fafc 0%, #f0f4f8 100%);
  border-bottom: 1px solid #e8e8e8;
}

.finance-page .form-section-header .section-title {
  font-size: 14px;
  font-weight: 600;
  color: #333;
  margin: 0;
  padding: 0;
  border: none;
}

.finance-page .form-section-body {
  padding: 14px;
}

.finance-page .form-row {
  display: flex;
  gap: 16px;
  margin-bottom: 10px;
}

.finance-page .form-row:last-child {
  margin-bottom: 0;
}

.finance-page .form-item {
  flex: 1;
  display: flex;
  flex-direction: row;
  align-items: center;
  gap: 8px;
}

.finance-page .form-label {
  font-size: 12px;
  color: #666;
  min-width: 60px;
  flex-shrink: 0;
  text-align: right;
  white-space: nowrap;
}

.finance-page .form-label.required::before {
  content: '*';
  color: #f5222d;
  margin-right: 2px;
}

.finance-page .form-value {
  font-size: 13px;
  color: #303133;
}

.finance-page .order-info-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
}

.finance-page .order-info-grid .info-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.finance-page .dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.finance-page .status-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 4px 14px;
  background-color: var(--color-bg-light);
  color: var(--color-text-secondary);
  font-size: var(--font-size-sm);
  border-radius: 20px;
  font-weight: 500;
  white-space: nowrap;
  min-width: 60px;
  line-height: 1.4;
}

.finance-page .status-badge.small {
  padding: 3px 10px;
  font-size: 12px;
  gap: 5px;
  min-width: 50px;
}

.finance-page .status-badge.small .status-dot {
  width: 5px;
  height: 5px;
  border-radius: 50%;
  background: currentColor;
}

.finance-page .status-badge.pending {
  background-color: #fff7e6;
  color: #fa8c16;
}

.finance-page .status-badge.partial {
  background-color: #e6f7ff;
  color: #1890ff;
}

.finance-page .status-badge.paid {
  background-color: #f6ffed;
  color: #52c41a;
}

.finance-page .price-text {
  font-weight: 600;
  font-family: 'Monaco', 'Consolas', monospace;
  color: var(--color-primary);
}
</style>

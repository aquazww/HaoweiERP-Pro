<template>
  <div class="purchase-page">
    <div class="page-header">
      <div class="header-title-section">
        <div class="title-icon">
          <el-icon :size="24"><ShoppingCart /></el-icon>
        </div>
        <div class="title-content">
          <h1 class="page-title">采购订单</h1>
          <p class="page-subtitle">管理和维护所有采购订单</p>
        </div>
      </div>
      <div class="header-stats">
        <div class="stat-item">
          <div class="stat-value">{{ orderList.length }}</div>
          <div class="stat-label">订单总数</div>
        </div>
      </div>
    </div>

    <div class="page-content">
      <div class="toolbar-card">
        <div class="toolbar-left">
          <div class="search-box">
            <el-icon class="search-icon"><Search /></el-icon>
            <el-input
              v-model="searchKeyword"
              placeholder="搜索采购单号、供应商"
              class="search-input"
              clearable
              @keyup.enter="loadOrders"
            />
          </div>
          <el-select v-model="statusFilter" placeholder="状态筛选" clearable @change="loadOrders">
            <el-option label="全部" :value="''" />
            <el-option label="待入库" value="pending" />
            <el-option label="部分入库" value="partial" />
            <el-option label="已入库" value="completed" />
            <el-option label="已取消" value="cancelled" />
          </el-select>
        </div>
        <div class="toolbar-right">
          <el-button :icon="Refresh" @click="loadOrders">刷新</el-button>
          <el-button type="primary" :icon="Plus" @click="handleAdd">新增采购单</el-button>
        </div>
      </div>

      <div class="table-card">
        <el-table 
          :data="orderList" 
          style="width: 100%" 
          v-loading="loading"
          :height="tableHeight"
          class="data-table"
          stripe
        >
          <el-table-column type="index" label="#" width="60" align="center" />
          <el-table-column prop="order_no" label="采购单号" width="160">
            <template #default="{ row }">
              <span class="order-no-badge">{{ row.order_no }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="supplier_name" label="供应商" min-width="160" />
          <el-table-column prop="warehouse_name" label="仓库" width="130" />
          <el-table-column prop="total_amount" label="总金额" width="140" align="right">
            <template #default="{ row }">
              <span class="price-text">¥{{ formatPrice(row.total_amount) }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="status" label="状态" width="110">
            <template #default="{ row }">
              <div class="status-badge" :class="row.status">
                <span class="status-dot"></span>
                {{ getStatusText(row.status) }}
              </div>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="260" fixed="right">
            <template #default="{ row }">
              <div class="action-buttons">
                <el-button type="primary" link :icon="View" size="small" @click="handleView(row)">查看</el-button>
                <el-button type="warning" link :icon="Edit" size="small" @click="handleEdit(row)">编辑</el-button>
                <el-button type="success" link :icon="Download" size="small" @click="handleStockIn(row)" v-if="row.status !== 'completed'">入库</el-button>
                <el-button type="danger" link :icon="Delete" size="small" @click="handleDelete(row)">删除</el-button>
              </div>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </div>

    <!-- 新增/编辑弹窗 -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? '编辑采购单' : '新增采购单'"
      width="1000px"
      class="form-dialog"
      destroy-on-close
      @close="resetForm"
    >
      <el-form :model="form" :rules="rules" ref="formRef" label-width="100px">
        <div class="form-section">
          <div class="section-title">基本信息</div>
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="供应商" prop="supplier">
                <el-select v-model="form.supplier" placeholder="请选择供应商" style="width: 100%" filterable>
                  <el-option 
                    v-for="item in supplierList" 
                    :key="item.id" 
                    :label="item.name" 
                    :value="item.id" 
                  />
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="仓库" prop="warehouse">
                <el-select v-model="form.warehouse" placeholder="请选择仓库" style="width: 100%">
                  <el-option 
                    v-for="item in warehouseList" 
                    :key="item.id" 
                    :label="item.name" 
                    :value="item.id" 
                  />
                </el-select>
              </el-form-item>
            </el-col>
          </el-row>
          
          <el-form-item label="采购日期" prop="order_date">
            <el-date-picker
              v-model="form.order_date"
              type="date"
              placeholder="选择日期"
              style="width: 100%"
              value-format="YYYY-MM-DD"
            />
          </el-form-item>

          <el-form-item label="备注">
            <el-input v-model="form.remark" type="textarea" :rows="2" placeholder="请输入备注" />
          </el-form-item>
        </div>

        <div class="form-section">
          <div class="section-title">采购明细</div>
          
          <div class="detail-table-wrapper">
            <el-table :data="form.items" border style="width: 100%;" class="detail-table">
              <el-table-column prop="goods" label="商品" min-width="220">
                <template #default="{ row, $index }">
                  <el-select v-model="row.goods" placeholder="选择商品" style="width: 100%" filterable @change="handleGoodsChange(row)">
                    <el-option 
                      v-for="item in goodsList" 
                      :key="item.id" 
                      :label="item.name" 
                      :value="item.id" 
                    />
                  </el-select>
                </template>
              </el-table-column>
              <el-table-column prop="quantity" label="数量" width="130">
                <template #default="{ row }">
                  <el-input-number v-model="row.quantity" :min="0" :precision="2" style="width: 100%" />
                </template>
              </el-table-column>
              <el-table-column prop="price" label="单价" width="130">
                <template #default="{ row }">
                  <el-input-number v-model="row.price" :min="0" :precision="2" style="width: 100%" />
                </template>
              </el-table-column>
              <el-table-column prop="amount" label="金额" width="140">
                <template #default="{ row }">
                  <span class="detail-price">¥{{ (row.quantity * row.price).toFixed(2) }}</span>
                </template>
              </el-table-column>
              <el-table-column label="操作" width="80">
                <template #default="{ $index }">
                  <el-button type="danger" link :icon="Delete" size="small" @click="removeItem($index)"></el-button>
                </template>
              </el-table-column>
            </el-table>
          </div>
          
          <div class="detail-footer">
            <el-button type="primary" plain :icon="Plus" @click="addItem">添加明细</el-button>
            <div class="total-section">
              <span class="total-label">合计金额：</span>
              <span class="total-amount">¥{{ totalAmount }}</span>
            </div>
          </div>
        </div>
      </el-form>
      
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleSubmit" :loading="submitLoading">
            {{ isEdit ? '保存修改' : '创建采购单' }}
          </el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, nextTick, onUnmounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { ShoppingCart, Search, Refresh, Plus, Edit, Delete, View, Download } from '@element-plus/icons-vue'
import { 
  getPurchaseOrders, createPurchaseOrder, 
  updatePurchaseOrder, deletePurchaseOrder 
} from '../../api/purchase'
import { getSuppliers, getWarehouses, getGoods } from '../../api/basic'
import { createStockIn, confirmStockIn } from '../../api/inventory'

const loading = ref(false)
const submitLoading = ref(false)
const dialogVisible = ref(false)
const isEdit = ref(false)
const formRef = ref(null)
const orderList = ref([])
const supplierList = ref([])
const warehouseList = ref([])
const goodsList = ref([])
const searchKeyword = ref('')
const statusFilter = ref('')
const tableHeight = ref(0)

const form = ref({
  supplier: '',
  warehouse: '',
  order_date: '',
  remark: '',
  items: []
})

const rules = {
  supplier: [{ required: true, message: '请选择供应商', trigger: 'change' }],
  warehouse: [{ required: true, message: '请选择仓库', trigger: 'change' }],
  order_date: [{ required: true, message: '请选择日期', trigger: 'change' }]
}

const getStatusType = (status) => {
  const typeMap = {
    'pending': 'warning',
    'partial': 'info',
    'completed': 'success',
    'cancelled': 'danger'
  }
  return typeMap[status] || ''
}

const getStatusText = (status) => {
  const textMap = {
    'pending': '待入库',
    'partial': '部分入库',
    'completed': '已入库',
    'cancelled': '已取消'
  }
  return textMap[status] || status
}

const formatPrice = (price) => {
  if (price === undefined || price === null) return '0.00'
  return Number(price).toFixed(2)
}

const totalAmount = computed(() => {
  return form.value.items.reduce((sum, item) => {
    return sum + (item.quantity * item.price || 0)
  }, 0).toFixed(2)
})

const loadOrders = async () => {
  loading.value = true
  try {
    const params = {}
    if (searchKeyword.value) {
      params.search = searchKeyword.value
    }
    if (statusFilter.value) {
      params.status = statusFilter.value
    }
    const res = await getPurchaseOrders(params)
    orderList.value = res.data.items || []
  } catch (error) {
    ElMessage.error('加载采购订单失败')
  } finally {
    loading.value = false
  }
}

const loadOptions = async () => {
  try {
    const [suppliersRes, warehousesRes, goodsRes] = await Promise.all([
      getSuppliers(),
      getWarehouses(),
      getGoods()
    ])
    supplierList.value = suppliersRes.data.items || []
    warehouseList.value = warehousesRes.data.items || []
    goodsList.value = goodsRes.data.items || []
  } catch (error) {
    ElMessage.error('加载选项数据失败')
  }
}

const calculateTableHeight = () => {
  nextTick(() => {
    const pageHeader = document.querySelector('.page-header')
    const toolbarCard = document.querySelector('.toolbar-card')
    const pageContent = document.querySelector('.page-content')
    
    if (pageContent) {
      let usedHeight = 0
      if (pageHeader) usedHeight += pageHeader.offsetHeight + 24
      if (toolbarCard) usedHeight += toolbarCard.offsetHeight + 16
      usedHeight += 80
      
      const availableHeight = window.innerHeight - 64 - 48
      tableHeight.value = Math.max(availableHeight - usedHeight, 300)
    }
  })
}

const handleAdd = () => {
  isEdit.value = false
  form.value = {
    supplier: '',
    warehouse: '',
    order_date: '',
    remark: '',
    items: []
  }
  dialogVisible.value = true
}

const handleEdit = (row) => {
  isEdit.value = true
  form.value = {
    id: row.id,
    supplier: row.supplier,
    warehouse: row.warehouse,
    order_date: row.order_date,
    remark: row.remark,
    items: row.items ? [...row.items] : []
  }
  dialogVisible.value = true
}

const handleView = (row) => {
  ElMessage.info('查看采购单功能开发中')
}

const handleStockIn = async (row) => {
  if (row.status === 'completed') {
    ElMessage.warning('该采购单已全部入库')
    return
  }

  try {
    await ElMessageBox.confirm('确定要入库此采购单吗？', '确认入库', {
      confirmButtonText: '确定入库',
      cancelButtonText: '取消',
      type: 'warning'
    })

    const stockInData = {
      purchase_order: row.id,
      warehouse: row.warehouse,
      total_amount: row.total_amount,
      remark: `采购单 ${row.order_no} 入库`
    }
    
    const stockInRes = await createStockIn(stockInData)
    await confirmStockIn(stockInRes.data.id)
    
    ElMessage.success('入库成功')
    loadOrders()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('入库失败')
    }
  }
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm(`确定要删除采购单「${row.order_no}」吗？`, '确认删除', {
      confirmButtonText: '确定删除',
      cancelButtonText: '取消',
      type: 'warning',
      confirmButtonClass: 'el-button--danger'
    })
    await deletePurchaseOrder(row.id)
    ElMessage.success('删除成功')
    loadOrders()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const addItem = () => {
  form.value.items.push({
    goods: '',
    quantity: 1,
    price: 0,
    remark: ''
  })
}

const removeItem = (index) => {
  form.value.items.splice(index, 1)
}

const handleGoodsChange = (row) => {
  const goods = goodsList.value.find(g => g.id === row.goods)
  if (goods) {
    row.price = goods.purchase_price || 0
  }
}

const handleSubmit = async () => {
  try {
    await formRef.value.validate()
    submitLoading.value = true
    
    const data = {
      ...form.value,
      total_amount: parseFloat(totalAmount.value)
    }
    
    if (isEdit.value) {
      await updatePurchaseOrder(form.value.id, data)
      ElMessage.success('更新成功')
    } else {
      await createPurchaseOrder(data)
      ElMessage.success('创建成功')
    }
    
    dialogVisible.value = false
    loadOrders()
  } catch (error) {
    if (error !== false) {
      ElMessage.error(isEdit.value ? '更新失败' : '创建失败')
    }
  } finally {
    submitLoading.value = false
  }
}

const resetForm = () => {
  if (formRef.value) {
    formRef.value.resetFields()
  }
}

onMounted(() => {
  loadOrders()
  loadOptions()
  calculateTableHeight()
  window.addEventListener('resize', calculateTableHeight)
})

onUnmounted(() => {
  window.removeEventListener('resize', calculateTableHeight)
})
</script>

<style scoped>
.purchase-page {
  height: 100%;
  display: flex;
  flex-direction: column;
  gap: var(--spacing-lg);
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  background: linear-gradient(135deg, var(--color-primary-light) 0%, rgba(14, 165, 233, 0.05) 100%);
  padding: var(--spacing-xl);
  border-radius: var(--border-radius-lg);
  border: 1px solid var(--color-primary-light);
}

.header-title-section {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
}

.title-icon {
  width: 56px;
  height: 56px;
  background: linear-gradient(135deg, var(--color-primary) 0%, var(--color-primary-dark) 100%);
  border-radius: var(--border-radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-white);
  box-shadow: var(--shadow-primary);
}

.title-content {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-xs);
}

.page-title {
  margin: 0;
  font-size: var(--font-size-2xl);
  font-weight: 600;
  color: var(--color-text-primary);
  line-height: 1.2;
}

.page-subtitle {
  margin: 0;
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  line-height: 1.4;
}

.header-stats {
  display: flex;
  gap: var(--spacing-lg);
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
}

.stat-value {
  font-size: var(--font-size-3xl);
  font-weight: 700;
  color: var(--color-primary);
  line-height: 1;
}

.stat-label {
  font-size: var(--font-size-sm);
  color: var(--color-text-tertiary);
  margin-top: var(--spacing-xs);
}

.page-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
  overflow: hidden;
}

.toolbar-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background-color: var(--color-white);
  padding: var(--spacing-md) var(--spacing-lg);
  border-radius: var(--border-radius-lg);
  border: 1px solid var(--color-border-light);
  box-shadow: var(--shadow-sm);
}

.toolbar-left,
.toolbar-right {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
}

.search-box {
  position: relative;
  display: flex;
  align-items: center;
}

.search-icon {
  position: absolute;
  left: var(--spacing-md);
  color: var(--color-text-tertiary);
  z-index: 1;
}

.search-input {
  width: 320px;
  padding-left: 40px;
}

.table-card {
  flex: 1;
  background-color: var(--color-white);
  border-radius: var(--border-radius-lg);
  border: 1px solid var(--color-border-light);
  box-shadow: var(--shadow-sm);
  overflow: hidden;
}

.data-table {
  --el-table-header-bg-color: var(--color-bg-light);
}

.order-no-badge {
  display: inline-block;
  padding: 2px 10px;
  background-color: var(--color-bg-light);
  color: var(--color-primary);
  font-weight: 600;
  font-size: var(--font-size-sm);
  border-radius: var(--border-radius-sm);
  font-family: 'Monaco', 'Consolas', monospace;
}

.price-text {
  font-weight: 600;
  font-family: 'Monaco', 'Consolas', monospace;
  color: var(--color-primary);
}

.status-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 4px 12px;
  background-color: var(--color-bg-light);
  color: var(--color-text-secondary);
  font-size: var(--font-size-sm);
  border-radius: 20px;
  font-weight: 500;
}

.status-badge.pending {
  background-color: rgba(245, 158, 11, 0.1);
  color: var(--color-warning);
}

.status-badge.partial {
  background-color: rgba(14, 165, 233, 0.1);
  color: var(--color-primary);
}

.status-badge.completed {
  background-color: rgba(34, 197, 94, 0.1);
  color: var(--color-success);
}

.status-badge.cancelled {
  background-color: rgba(239, 68, 68, 0.1);
  color: var(--color-danger);
}

.status-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background-color: currentColor;
}

.action-buttons {
  display: flex;
  align-items: center;
  gap: var(--spacing-xs);
}

.form-dialog {
  --el-dialog-border-radius: var(--border-radius-lg);
}

.form-dialog :deep(.el-dialog__header) {
  padding: var(--spacing-lg) var(--spacing-xl);
  border-bottom: 1px solid var(--color-border-light);
}

.form-dialog :deep(.el-dialog__body) {
  padding: var(--spacing-lg) var(--spacing-xl);
}

.form-dialog :deep(.el-dialog__footer) {
  padding: var(--spacing-md) var(--spacing-xl);
  border-top: 1px solid var(--color-border-light);
}

.form-section {
  margin-bottom: var(--spacing-lg);
}

.form-section:last-child {
  margin-bottom: 0;
}

.section-title {
  font-size: var(--font-size-base);
  font-weight: 600;
  color: var(--color-text-primary);
  margin-bottom: var(--spacing-md);
  padding-left: var(--spacing-sm);
  border-left: 3px solid var(--color-primary);
}

.detail-table-wrapper {
  border-radius: var(--border-radius-md);
  overflow: hidden;
  border: 1px solid var(--color-border);
}

.detail-table {
  --el-table-header-bg-color: var(--color-bg-light);
}

.detail-price {
  font-weight: 600;
  font-family: 'Monaco', 'Consolas', monospace;
  color: var(--color-primary);
}

.detail-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: var(--spacing-md);
}

.total-section {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
}

.total-label {
  font-size: var(--font-size-base);
  color: var(--color-text-secondary);
}

.total-amount {
  font-size: var(--font-size-xl);
  font-weight: 700;
  color: var(--color-primary);
  font-family: 'Monaco', 'Consolas', monospace;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: var(--spacing-sm);
}
</style>

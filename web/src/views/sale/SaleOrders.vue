<template>
  <div class="sale-page">
    <div class="page-content">
      <div class="toolbar-card">
        <div class="toolbar-left">
          <div class="search-box">
            <el-icon class="search-icon"><Search /></el-icon>
            <el-input
              v-model="searchKeyword"
              placeholder="搜索销售单号、客户"
              class="search-input"
              clearable
              @keyup.enter="loadOrders"
            />
          </div>
          <el-select v-model="statusFilter" placeholder="状态筛选" clearable style="width: 140px" @change="loadOrders">
            <el-option label="全部" :value="''" />
            <el-option label="待出库" value="pending" />
            <el-option label="部分出库" value="partial" />
            <el-option label="已出库" value="completed" />
            <el-option label="已取消" value="cancelled" />
          </el-select>
        </div>
        <div class="toolbar-right">
          <el-button :icon="Refresh" @click="loadOrders">刷新</el-button>
          <el-button type="primary" :icon="Plus" @click="handleAdd">新增销售单</el-button>
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
          <el-table-column prop="order_no" label="销售单号" width="160">
            <template #default="{ row }">
              <span class="order-no-badge">{{ row.order_no }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="customer_name" label="客户" min-width="160" />
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
                <el-button type="success" link :icon="Upload" size="small" @click="handleStockOut(row)" v-if="row.status !== 'completed'">出库</el-button>
                <el-button type="danger" link :icon="Delete" size="small" @click="handleDelete(row)">删除</el-button>
              </div>
            </template>
          </el-table-column>
        </el-table>
        <div class="pagination-wrapper">
          <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :page-sizes="[10, 20, 50, 100]"
            :total="total"
            layout="total, sizes, prev, pager, next, jumper"
            @size-change="loadOrders"
            @current-change="loadOrders"
          />
        </div>
      </div>
    </div>

    <!-- 新增/编辑弹窗 -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? '编辑销售单' : '新增销售单'"
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
              <el-form-item label="客户" prop="customer">
                <el-select v-model="form.customer" placeholder="请选择客户" style="width: 100%" filterable>
                  <el-option 
                    v-for="item in customerList" 
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
          
          <el-form-item label="销售日期" prop="order_date">
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
          <div class="section-title">销售明细</div>
          
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
            {{ isEdit ? '保存修改' : '创建销售单' }}
          </el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, nextTick, onUnmounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { ShoppingBag, Search, Refresh, Plus, Edit, Delete, View, Upload } from '@element-plus/icons-vue'
import { 
  getSaleOrders, createSaleOrder, 
  updateSaleOrder, deleteSaleOrder,
  confirmSaleOrder
} from '../../api/sale'
import { getCustomers, getWarehouses, getGoods } from '../../api/basic'
import { createStockOut } from '../../api/inventory'

const loading = ref(false)
const submitLoading = ref(false)
const dialogVisible = ref(false)
const isEdit = ref(false)
const formRef = ref(null)
const orderList = ref([])
const customerList = ref([])
const warehouseList = ref([])
const goodsList = ref([])
const searchKeyword = ref('')
const statusFilter = ref('')
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)
const tableHeight = ref(0)

const form = ref({
  customer: '',
  warehouse: '',
  order_date: '',
  remark: '',
  items: []
})

const rules = {
  customer: [{ required: true, message: '请选择客户', trigger: 'change' }],
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
    'pending': '待出库',
    'partial': '部分出库',
    'completed': '已出库',
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
    const res = await getSaleOrders(params)
    orderList.value = res.data.items || []
  } catch (error) {
    ElMessage.error('加载销售订单失败')
  } finally {
    loading.value = false
  }
}

const loadOptions = async () => {
  try {
    const [customersRes, warehousesRes, goodsRes] = await Promise.all([
      getCustomers(),
      getWarehouses(),
      getGoods()
    ])
    customerList.value = customersRes.data.items || []
    warehouseList.value = warehousesRes.data.items || []
    goodsList.value = goodsRes.data.items || []
  } catch (error) {
    ElMessage.error('加载选项数据失败')
  }
}

const calculateTableHeight = () => {
  nextTick(() => {
    const toolbarCard = document.querySelector('.toolbar-card')
    const paginationWrapper = document.querySelector('.pagination-wrapper')
    const pageContent = document.querySelector('.page-content')
    
    if (pageContent) {
      let usedHeight = 0
      if (toolbarCard) usedHeight += toolbarCard.offsetHeight + 4
      if (paginationWrapper) usedHeight += paginationWrapper.offsetHeight + 2
      usedHeight += 4
      
      const availableHeight = window.innerHeight - 64 - 16
      tableHeight.value = Math.max(availableHeight - usedHeight, 150)
    }
  })
}

const handleAdd = () => {
  isEdit.value = false
  form.value = {
    customer: '',
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
    customer: row.customer,
    warehouse: row.warehouse,
    order_date: row.order_date,
    remark: row.remark,
    items: row.items ? [...row.items] : []
  }
  dialogVisible.value = true
}

const handleView = (row) => {
  ElMessage.info('查看销售单功能开发中')
}

const handleStockOut = async (row) => {
  if (row.status === 'completed') {
    ElMessage.warning('该销售单已全部出库')
    return
  }

  try {
    await ElMessageBox.confirm('确定要出库此销售单吗？', '确认出库', {
      confirmButtonText: '确定出库',
      cancelButtonText: '取消',
      type: 'warning'
    })

    const stockOutData = {
      sale_order: row.id,
      warehouse: row.warehouse,
      total_amount: row.total_amount,
      remark: `销售单 ${row.order_no} 出库`
    }
    
    await createStockOut(stockOutData)
    await confirmSaleOrder(row.id)
    
    ElMessage.success('出库成功')
    loadOrders()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('出库失败')
    }
  }
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm(`确定要删除销售单「${row.order_no}」吗？`, '确认删除', {
      confirmButtonText: '确定删除',
      cancelButtonText: '取消',
      type: 'warning',
      confirmButtonClass: 'el-button--danger'
    })
    await deleteSaleOrder(row.id)
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
    row.price = goods.sale_price || 0
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
      await updateSaleOrder(form.value.id, data)
      ElMessage.success('更新成功')
    } else {
      await createSaleOrder(data)
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
.sale-page {
  height: 100%;
  width: 100%;
  display: flex;
  flex-direction: column;
  padding: 8px;
  overflow: hidden;
}

.page-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 8px;
  overflow: hidden;
  width: 100%;
}

.toolbar-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background-color: var(--color-white);
  padding: 6px var(--spacing-md);
  border-radius: var(--border-radius-lg);
  border: 1px solid var(--color-border-light);
  box-shadow: var(--shadow-sm);
  flex-shrink: 0;
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
  display: flex;
  flex-direction: column;
  background-color: var(--color-white);
  border-radius: var(--border-radius-lg);
  border: 1px solid var(--color-border-light);
  box-shadow: var(--shadow-sm);
  overflow: hidden;
  min-height: 0;
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

.pagination-wrapper {
  display: flex;
  justify-content: flex-end;
  background-color: var(--color-white);
  border-top: 1px solid var(--color-border-light);
  padding: 4px var(--spacing-md);
  border-radius: 0 0 var(--border-radius-lg) var(--border-radius-lg);
  flex-shrink: 0;
}

.pagination-wrapper :deep(.el-pagination) {
  --el-pagination-button-height: 32px;
  --el-pagination-font-size: 13px;
}

.pagination-wrapper :deep(.el-pagination .btn-prev),
.pagination-wrapper :deep(.el-pagination .btn-next) {
  min-width: 32px;
  padding: 0 8px;
}

.pagination-wrapper :deep(.el-pagination .el-pager li) {
  min-width: 32px;
  height: 32px;
  line-height: 32px;
}

.pagination-wrapper :deep(.el-pagination .el-pagination__sizes) {
  margin-right: 8px;
}

.pagination-wrapper :deep(.el-pagination .el-pagination__jump) {
  margin-left: 8px;
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

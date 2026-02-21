<template>
  <div class="inventory-log-page">
    <div class="page-content">
      <div class="toolbar-card">
        <div class="toolbar-left">
          <div class="search-box">
            <el-icon class="search-icon"><Search /></el-icon>
            <el-input
              v-model="searchKeyword"
              placeholder="搜索商品"
              class="search-input"
              clearable
              @keyup.enter="loadLogs"
            />
          </div>
          <el-select v-model="changeTypeFilter" placeholder="交易类型" clearable style="width: 140px" @change="loadLogs">
            <el-option label="全部" :value="''" />
            <el-option label="采购入库" value="purchase_in" />
            <el-option label="销售出库" value="sale_out" />
            <el-option label="调拨入库" value="transfer_in" />
            <el-option label="调拨出库" value="transfer_out" />
            <el-option label="库存调整" value="adjust" />
          </el-select>
        </div>
        <div class="toolbar-right">
          <el-button :icon="Refresh" @click="loadLogs">刷新</el-button>
        </div>
      </div>

      <div class="table-card">
        <el-table 
          :data="logList" 
          style="width: 100%" 
          v-loading="loading"
          class="data-table"
          stripe
          :height="tableHeight"
          :header-cell-style="{ background: 'var(--color-bg-light)' }"
        >
          <el-table-column label="时间" min-width="130">
            <template #default="{ row }">{{ formatDateTime(row.created_at) }}</template>
          </el-table-column>
          <el-table-column prop="goods_name" label="商品" min-width="120" show-overflow-tooltip />
          <el-table-column prop="warehouse_name" label="仓库" min-width="100" show-overflow-tooltip />
          <el-table-column label="交易类型" min-width="60" align="center">
            <template #default="{ row }">
              <el-tag :type="getTransactionType(row).color" size="small">
                {{ getTransactionType(row).text }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="变动" min-width="50" align="right">
            <template #default="{ row }">
              <span :class="row.change_type === 'inbound' ? 'text-success' : 'text-danger'">
                {{ formatChangeQuantity(row) }}
              </span>
            </template>
          </el-table-column>
          <el-table-column label="前" min-width="50" align="right">
            <template #default="{ row }">{{ formatQuantity(row.before_quantity) }}</template>
          </el-table-column>
          <el-table-column label="后" min-width="50" align="right">
            <template #default="{ row }">{{ formatQuantity(row.after_quantity) }}</template>
          </el-table-column>
          <el-table-column label="备注" min-width="160">
            <template #default="{ row }">
              <span v-html="formatRemark(row.remark)" @click="handleOrderClick($event)"></span>
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
            @size-change="loadLogs"
            @current-change="loadLogs"
          />
        </div>
      </div>
    </div>

    <!-- 订单详情弹窗 -->
    <el-dialog
      v-model="orderDetailVisible"
      :title="orderDetailTitle"
      width="800px"
      class="view-dialog"
      destroy-on-close
    >
      <div v-loading="orderDetailLoading">
        <!-- 采购订单详情 -->
        <template v-if="orderType === 'purchase' && orderDetail">
          <el-descriptions :column="2" border>
            <el-descriptions-item label="采购单号">{{ orderDetail.order_no }}</el-descriptions-item>
            <el-descriptions-item label="状态">
              <div class="status-badge" :class="orderDetail.status">
                <span class="status-dot"></span>
                {{ getStatusText(orderDetail.status) }}
              </div>
            </el-descriptions-item>
            <el-descriptions-item label="供应商">{{ orderDetail.supplier_name }}</el-descriptions-item>
            <el-descriptions-item label="仓库">{{ orderDetail.warehouse_name }}</el-descriptions-item>
            <el-descriptions-item label="采购日期">{{ orderDetail.order_date }}</el-descriptions-item>
            <el-descriptions-item label="总金额">¥{{ formatPrice(orderDetail.total_amount) }}</el-descriptions-item>
            <el-descriptions-item label="创建人">{{ orderDetail.created_by_name || '-' }}</el-descriptions-item>
            <el-descriptions-item label="创建时间">{{ formatDateTime(orderDetail.created_at) }}</el-descriptions-item>
            <el-descriptions-item label="备注" :span="2">{{ orderDetail.remark || '-' }}</el-descriptions-item>
          </el-descriptions>
          <div class="view-items-title">采购明细</div>
          <el-table :data="orderDetail.items || []" border style="width: 100%;">
            <el-table-column type="index" label="#" width="50" align="center" />
            <el-table-column prop="goods_name" label="商品名称" min-width="150" />
            <el-table-column prop="goods_code" label="商品编码" width="100" />
            <el-table-column prop="unit" label="单位" width="70" align="center" />
            <el-table-column prop="quantity" label="数量" width="80" align="right">
              <template #default="{ row }">{{ formatQuantity(row.quantity) }}</template>
            </el-table-column>
            <el-table-column label="单价" width="100" align="right">
              <template #default="{ row }">¥{{ formatPrice(row.price) }}</template>
            </el-table-column>
            <el-table-column label="金额" width="100" align="right">
              <template #default="{ row }">¥{{ formatPrice(row.amount) }}</template>
            </el-table-column>
          </el-table>
        </template>

        <!-- 销售订单详情 -->
        <template v-if="orderType === 'sale' && orderDetail">
          <el-descriptions :column="2" border>
            <el-descriptions-item label="销售单号">{{ orderDetail.order_no }}</el-descriptions-item>
            <el-descriptions-item label="客户">{{ orderDetail.customer_name }}</el-descriptions-item>
            <el-descriptions-item label="仓库">{{ orderDetail.warehouse_name }}</el-descriptions-item>
            <el-descriptions-item label="销售日期">{{ orderDetail.order_date }}</el-descriptions-item>
            <el-descriptions-item label="总金额">¥{{ formatPrice(orderDetail.total_amount) }}</el-descriptions-item>
            <el-descriptions-item label="状态">
              <div class="status-badge" :class="orderDetail.status">
                <span class="status-dot"></span>
                {{ getStatusText(orderDetail.status) }}
              </div>
            </el-descriptions-item>
            <el-descriptions-item label="备注" :span="2">{{ orderDetail.remark || '-' }}</el-descriptions-item>
          </el-descriptions>
          <div class="view-items-title">销售明细</div>
          <el-table :data="orderDetail.items || []" border style="width: 100%;">
            <el-table-column type="index" label="#" width="50" align="center" />
            <el-table-column prop="goods_name" label="商品名称" min-width="150" />
            <el-table-column prop="quantity" label="数量" width="80" align="right">
              <template #default="{ row }">{{ formatQuantity(row.quantity) }}</template>
            </el-table-column>
            <el-table-column label="单价" width="100" align="right">
              <template #default="{ row }">¥{{ formatPrice(row.price) }}</template>
            </el-table-column>
            <el-table-column label="金额" width="100" align="right">
              <template #default="{ row }">¥{{ formatPrice(row.amount) }}</template>
            </el-table-column>
          </el-table>
        </template>

        <!-- 库存调整详情 -->
        <template v-if="orderType === 'adjust' && orderDetail">
          <el-descriptions :column="2" border>
            <el-descriptions-item label="调整单号">{{ orderDetail.order_no }}</el-descriptions-item>
            <el-descriptions-item label="仓库">{{ orderDetail.warehouse_name }}</el-descriptions-item>
            <el-descriptions-item label="调整类型">{{ orderDetail.adjust_type_display }}</el-descriptions-item>
            <el-descriptions-item label="调整原因">{{ orderDetail.reason_display }}</el-descriptions-item>
            <el-descriptions-item label="状态">
              <div class="status-badge" :class="orderDetail.status">
                <span class="status-dot"></span>
                {{ getStatusText(orderDetail.status) }}
              </div>
            </el-descriptions-item>
            <el-descriptions-item label="创建时间">{{ formatDateTime(orderDetail.created_at) }}</el-descriptions-item>
            <el-descriptions-item label="备注" :span="2">{{ orderDetail.remark || '-' }}</el-descriptions-item>
          </el-descriptions>
          <div class="view-items-title">调整明细</div>
          <el-table :data="orderDetail.items || []" border style="width: 100%;">
            <el-table-column type="index" label="#" width="50" align="center" />
            <el-table-column prop="goods_name" label="商品名称" min-width="150" />
            <el-table-column prop="unit" label="单位" width="70" align="center" />
            <el-table-column label="调整前" width="80" align="right">
              <template #default="{ row }">{{ formatQuantity(row.before_quantity) }}</template>
            </el-table-column>
            <el-table-column label="调整数量" width="80" align="right">
              <template #default="{ row }">
                <span :class="row.adjust_quantity >= 0 ? 'text-success' : 'text-danger'">
                  {{ row.adjust_quantity >= 0 ? '+' : '' }}{{ formatQuantity(row.adjust_quantity) }}
                </span>
              </template>
            </el-table-column>
            <el-table-column label="调整后" width="80" align="right">
              <template #default="{ row }">{{ formatQuantity(row.after_quantity) }}</template>
            </el-table-column>
          </el-table>
        </template>

        <!-- 库存调拨详情 -->
        <template v-if="orderType === 'transfer' && orderDetail">
          <el-descriptions :column="2" border>
            <el-descriptions-item label="调拨单号">{{ orderDetail.order_no }}</el-descriptions-item>
            <el-descriptions-item label="调出仓库">{{ orderDetail.from_warehouse_name }}</el-descriptions-item>
            <el-descriptions-item label="调入仓库">{{ orderDetail.to_warehouse_name }}</el-descriptions-item>
            <el-descriptions-item label="状态">
              <div class="status-badge" :class="orderDetail.status">
                <span class="status-dot"></span>
                {{ getStatusText(orderDetail.status) }}
              </div>
            </el-descriptions-item>
            <el-descriptions-item label="创建时间">{{ formatDateTime(orderDetail.created_at) }}</el-descriptions-item>
            <el-descriptions-item label="备注">{{ orderDetail.remark || '-' }}</el-descriptions-item>
          </el-descriptions>
          <div class="view-items-title">调拨明细</div>
          <el-table :data="orderDetail.items || []" border style="width: 100%;">
            <el-table-column type="index" label="#" width="50" align="center" />
            <el-table-column prop="goods_name" label="商品名称" min-width="150" />
            <el-table-column prop="unit" label="单位" width="70" align="center" />
            <el-table-column prop="quantity" label="调拨数量" width="100" align="right">
              <template #default="{ row }">{{ formatQuantity(row.quantity) }}</template>
            </el-table-column>
          </el-table>
        </template>
      </div>
      <template #footer>
        <el-button @click="orderDetailVisible = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Search, Refresh } from '@element-plus/icons-vue'
import { getInventoryLogs, getStockAdjustByNo, getStockTransferByNo } from '../../api/inventory'
import { getPurchaseOrderByNo } from '../../api/purchase'
import { getSaleOrderByNo } from '../../api/sale'

const loading = ref(false)
const logList = ref([])
const searchKeyword = ref('')
const changeTypeFilter = ref('')
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)
const tableHeight = ref(0)

// 订单详情相关
const orderDetailVisible = ref(false)
const orderDetailLoading = ref(false)
const orderDetailTitle = ref('')
const orderDetail = ref(null)
const orderType = ref('')  // purchase, sale, adjust, transfer

/**
 * 格式化日期时间，移除时区信息
 */
const formatDateTime = (datetime) => {
  if (!datetime) return '-'
  
  const date = new Date(datetime)
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  const hours = String(date.getHours()).padStart(2, '0')
  const minutes = String(date.getMinutes()).padStart(2, '0')
  const seconds = String(date.getSeconds()).padStart(2, '0')
  
  return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`
}

/**
 * 格式化数量，去除小数点
 */
const formatQuantity = (value) => {
  if (value === null || value === undefined) return '-'
  const num = Number(value)
  if (isNaN(num)) return '-'
  return Number.isInteger(num) ? num.toString() : num.toFixed(2).replace(/\.?0+$/, '')
}

/**
 * 格式化变动数量，添加正负符号
 */
const formatChangeQuantity = (row) => {
  const value = row.change_quantity
  if (value === null || value === undefined) return '-'
  const num = Number(value)
  if (isNaN(num)) return '-'
  
  const formattedNum = Number.isInteger(num) ? num.toString() : num.toFixed(2).replace(/\.?0+$/, '')
  
  // 入库显示 + 号，出库显示 - 号
  if (row.change_type === 'inbound') {
    return `+${formattedNum}`
  } else {
    return `-${formattedNum}`
  }
}

/**
 * 获取交易类型信息（文字和颜色）
 */
const getTransactionType = (row) => {
  const remark = row.remark || ''
  
  // 根据备注判断具体交易类型
  if (remark.includes('采购入库')) {
    return { text: '采购入库', color: 'success' }
  }
  if (remark.includes('销售出库')) {
    return { text: '销售出库', color: 'danger' }
  }
  if (remark.includes('调拨出库')) {
    return { text: '调拨出库', color: 'warning' }
  }
  if (remark.includes('调拨入库')) {
    return { text: '调拨入库', color: 'primary' }
  }
  if (remark.includes('库存调整')) {
    return { text: '库存调整', color: 'info' }
  }
  
  // 根据变动类型判断
  if (row.change_type === 'inbound') {
    return { text: '入库', color: 'success' }
  }
  if (row.change_type === 'outbound') {
    return { text: '出库', color: 'danger' }
  }
  
  return { text: row.change_type_display || '未知', color: 'info' }
}

/**
 * 格式化备注，将单号转为可点击链接
 */
const formatRemark = (remark) => {
  if (!remark) return '-'
  
  // 匹配单号格式：大写字母+数字组合（如 PO20260220001, SO20260220001 等）
  return remark.replace(/([A-Z]{2,3}\d+)/g, '<span class="order-link" data-order="$1">$1</span>')
}

/**
 * 处理订单号点击事件
 */
const handleOrderClick = async (event) => {
  const target = event.target
  if (!target.classList.contains('order-link')) return
  
  const orderNo = target.dataset.order
  if (!orderNo) return
  
  // 根据单号前缀判断订单类型
  const prefix = orderNo.substring(0, 2).toUpperCase()
  
  orderDetailVisible.value = true
  orderDetailLoading.value = true
  orderDetail.value = null
  orderType.value = ''
  
  try {
    let res = null
    
    if (prefix === 'PO') {
      // 采购订单
      orderDetailTitle.value = '采购订单详情'
      orderType.value = 'purchase'
      res = await getPurchaseOrderByNo(orderNo)
    } else if (prefix === 'SO') {
      // 销售订单
      orderDetailTitle.value = '销售订单详情'
      orderType.value = 'sale'
      res = await getSaleOrderByNo(orderNo)
    } else if (prefix === 'AD') {
      // 库存调整
      orderDetailTitle.value = '库存调整详情'
      orderType.value = 'adjust'
      res = await getStockAdjustByNo(orderNo)
    } else if (prefix === 'TR') {
      // 库存调拨
      orderDetailTitle.value = '库存调拨详情'
      orderType.value = 'transfer'
      res = await getStockTransferByNo(orderNo)
    } else {
      ElMessage.warning('未知的单据类型')
      orderDetailVisible.value = false
      return
    }
    
    orderDetail.value = res.data
  } catch (error) {
    ElMessage.error('获取订单详情失败：' + (error.message || '未知错误'))
    orderDetailVisible.value = false
  } finally {
    orderDetailLoading.value = false
  }
}

/**
 * 获取状态文本
 */
const getStatusText = (status) => {
  const textMap = {
    draft: '草稿',
    pending: '待处理',
    confirmed: '已确认',
    completed: '已完成',
    cancelled: '已取消',
    partial: '部分完成'
  }
  return textMap[status] || status
}

/**
 * 格式化价格
 */
const formatPrice = (value) => {
  if (value === null || value === undefined) return '-'
  const num = Number(value)
  if (isNaN(num)) return '-'
  return num.toFixed(2)
}

const loadLogs = async () => {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      page_size: pageSize.value
    }
    if (changeTypeFilter.value) {
      params.transaction_type = changeTypeFilter.value
    }
    if (searchKeyword.value) {
      params.search = searchKeyword.value
    }
    const res = await getInventoryLogs(params)
    logList.value = res.data.items || res.data.results || []
    total.value = res.data.count || 0
  } catch (error) {
    logList.value = []
    total.value = 0
    ElMessage.error('加载数据失败：' + (error.message || '未知错误'))
  } finally {
    loading.value = false
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

onMounted(() => {
  loadLogs()
  calculateTableHeight()
  window.addEventListener('resize', calculateTableHeight)
})

onUnmounted(() => {
  window.removeEventListener('resize', calculateTableHeight)
})
</script>

<style scoped>
.inventory-log-page {
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

.data-table :deep(.el-table__header-wrapper) {
  position: sticky;
  top: 0;
  z-index: 10;
}

.data-table :deep(.el-table__body-wrapper) {
  overflow-y: auto;
}

.data-table :deep(.el-table__row) {
  height: 48px;
}

.data-table :deep(.el-table__cell) {
  padding: 8px 0;
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

/* 响应式设计 */
@media screen and (max-width: 1400px) {
  .search-input {
    width: 280px;
  }
  
  .data-table :deep(.el-table__row) {
    height: 44px;
  }
}

@media screen and (max-width: 1200px) {
  .search-input {
    width: 240px;
  }
  
  .toolbar-left,
  .toolbar-right {
    gap: var(--spacing-sm);
  }
  
  /* 小屏幕下备注列自适应 */
  .data-table :deep(.el-table__body-wrapper) {
    overflow-x: auto;
  }
}

@media screen and (max-width: 992px) {
  .toolbar-card {
    flex-direction: column;
    gap: var(--spacing-sm);
    padding: var(--spacing-sm);
  }
  
  .toolbar-left,
  .toolbar-right {
    width: 100%;
    justify-content: center;
    flex-wrap: wrap;
  }
  
  .search-input {
    width: 100%;
  }
  
  .data-table :deep(.el-table__row) {
    height: 40px;
  }
  
  .data-table :deep(.el-table__cell) {
    padding: 6px 0;
    font-size: var(--font-size-sm);
  }
}

@media screen and (max-width: 768px) {
  .inventory-log-page {
    padding: 4px;
  }
  
  .page-content {
    gap: 4px;
  }
  
  .toolbar-card,
  .table-card {
    border-radius: var(--border-radius-md);
  }
  
  .pagination-wrapper {
    padding: 4px var(--spacing-sm);
  }
  
  .pagination-wrapper :deep(.el-pagination) {
    flex-wrap: wrap;
    justify-content: center;
  }
  
  /* 移动端表格允许水平滚动 */
  .table-card {
    overflow-x: auto;
  }
  
  .data-table {
    min-width: 700px;
  }
}

/* 数量颜色样式 */
.text-success {
  color: var(--color-success);
  font-weight: 600;
}

.text-danger {
  color: var(--color-danger);
  font-weight: 600;
}

/* 订单号链接样式 - 使用 :deep 以作用于 v-html 生成的内容 */
:deep(.order-link) {
  color: var(--color-primary);
  text-decoration: underline;
  cursor: pointer;
  font-weight: 500;
  transition: color 0.2s;
}

:deep(.order-link:hover) {
  color: var(--color-primary-dark, #4080ff);
}

/* 订单详情弹窗样式 */
.view-dialog :deep(.el-dialog__header) {
  border-bottom: 1px solid var(--color-border-light);
  padding-bottom: var(--spacing-md);
}

.view-dialog :deep(.el-dialog__body) {
  padding: var(--spacing-lg);
}

/* 状态徽章样式 */
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

.status-badge.draft {
  background-color: rgba(245, 158, 11, 0.1);
  color: var(--color-warning);
}

.status-badge.pending {
  background-color: rgba(59, 130, 246, 0.1);
  color: var(--color-primary);
}

.status-badge.confirmed {
  background-color: rgba(34, 197, 94, 0.1);
  color: var(--color-success);
}

.status-badge.completed {
  background-color: rgba(34, 197, 94, 0.1);
  color: var(--color-success);
}

.status-badge.cancelled {
  background-color: rgba(239, 68, 68, 0.1);
  color: var(--color-danger);
}

.status-badge.partial {
  background-color: rgba(245, 158, 11, 0.1);
  color: var(--color-warning);
}

.status-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background-color: currentColor;
}

/* 明细标题样式 */
.view-items-title {
  font-size: 15px;
  font-weight: 600;
  color: var(--color-text-primary);
  margin: var(--spacing-lg) 0 var(--spacing-md);
  padding-left: var(--spacing-sm);
  border-left: 3px solid var(--color-primary);
}
</style>

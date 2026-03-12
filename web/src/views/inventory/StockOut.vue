<template>
  <div class="stock-out-page">
    <div class="page-content">
      <!-- 工具栏 -->
      <div class="toolbar-card">
        <div class="toolbar-left">
          <div class="search-box">
            <el-icon class="search-icon"><Search /></el-icon>
            <el-input
              v-model="searchKeyword"
              placeholder="搜索出库单号"
              class="search-input"
              clearable
              @keyup.enter="loadData"
            />
          </div>
          <el-select v-model="filterWarehouse" placeholder="仓库" clearable style="width: 140px" @change="loadData">
            <el-option label="全部仓库" :value="''" />
            <el-option v-for="item in warehouseList" :key="item.id" :label="item.name" :value="item.id" />
          </el-select>
          <el-select v-model="filterStatus" placeholder="状态" clearable style="width: 120px" @change="loadData">
            <el-option label="全部状态" :value="''" />
            <el-option label="草稿" value="draft" />
            <el-option label="已确认" value="confirmed" />
            <el-option label="已取消" value="cancelled" />
          </el-select>
        </div>
        <div class="toolbar-right">
          <el-button :icon="Refresh" @click="loadData">刷新</el-button>
          <el-button type="warning" :icon="Printer" @click="handleBatchPrint" :disabled="selectedRows.length === 0">
            批量打印送货单
          </el-button>
        </div>
      </div>

      <!-- 表格 -->
      <div class="table-card">
        <el-table 
          :data="tableData" 
          style="width: 100%" 
          v-loading="loading"
          class="data-table"
          stripe
          :height="tableHeight"
          :header-cell-style="{ background: 'var(--color-bg-light)' }"
          @selection-change="handleSelectionChange"
        >
          <el-table-column type="selection" width="55" />
          <el-table-column prop="order_no" label="出库单号" min-width="150" show-overflow-tooltip />
          <el-table-column prop="sale_order_no" label="销售单号" min-width="150" show-overflow-tooltip>
            <template #default="{ row }">{{ row.sale_order_no || '-' }}</template>
          </el-table-column>
          <el-table-column prop="warehouse_name" label="仓库" min-width="120" show-overflow-tooltip />
          <el-table-column prop="total_amount" label="总金额" min-width="120" align="right">
            <template #default="{ row }">¥{{ formatAmount(row.total_amount) }}</template>
          </el-table-column>
          <el-table-column prop="status_display" label="状态" min-width="100" align="center">
            <template #default="{ row }">
              <el-tag :type="getStatusType(row.status)" size="small">{{ row.status_display }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="created_at" label="创建时间" min-width="160">
            <template #default="{ row }">{{ formatDateTime(row.created_at) }}</template>
          </el-table-column>
          <el-table-column label="操作" min-width="220" align="center" fixed="right">
            <template #default="{ row }">
              <div class="action-buttons">
                <el-button type="primary" link size="small" @click="handleView(row)">详情</el-button>
                <el-button type="warning" link size="small" @click="handlePrintDelivery(row)">打印</el-button>
                <el-button type="success" link size="small" @click="handleAdvancedPrint(row)">设计打印</el-button>
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
            @size-change="loadData"
            @current-change="loadData"
          />
        </div>
      </div>
    </div>

    <!-- 详情对话框 -->
    <el-dialog v-model="detailDialogVisible" title="出库单详情" width="900px" class="detail-dialog">
      <div class="order-detail" v-if="currentOrder">
        <div class="detail-header">
          <h3>基本信息</h3>
        </div>
        <div class="info-row">
          <div class="info-item">
            <span class="label">出库单号：</span>
            <span class="value">{{ currentOrder.order_no }}</span>
          </div>
          <div class="info-item">
            <span class="label">销售单号：</span>
            <span class="value">{{ currentOrder.sale_order_no || '-' }}</span>
          </div>
          <div class="info-item">
            <span class="label">状态：</span>
            <el-tag :type="getStatusType(currentOrder.status)" size="small">
              {{ currentOrder.status_display }}
            </el-tag>
          </div>
        </div>
        <div class="info-row">
          <div class="info-item">
            <span class="label">客户名称：</span>
            <span class="value">{{ currentOrder.customer_name || '-' }}</span>
          </div>
          <div class="info-item">
            <span class="label">联系人：</span>
            <span class="value">{{ currentOrder.customer_contact || '-' }}</span>
          </div>
          <div class="info-item">
            <span class="label">联系电话：</span>
            <span class="value">{{ currentOrder.customer_phone || '-' }}</span>
          </div>
        </div>
        <div class="info-row">
          <div class="info-item">
            <span class="label">客户地址：</span>
            <span class="value">{{ currentOrder.customer_address || '-' }}</span>
          </div>
          <div class="info-item">
            <span class="label">仓库：</span>
            <span class="value">{{ currentOrder.warehouse_name }}</span>
          </div>
          <div class="info-item">
            <span class="label">总金额：</span>
            <span class="value">¥{{ formatAmount(currentOrder.total_amount) }}</span>
          </div>
        </div>
        <div class="info-row">
          <div class="info-item full-width">
            <span class="label">备注：</span>
            <span class="value">{{ currentOrder.remark || '-' }}</span>
          </div>
        </div>

        <div class="detail-items">
          <h4>商品明细</h4>
          <el-table :data="currentOrder.items" border stripe max-height="400">
            <el-table-column prop="goods_code" label="商品编码" width="120" />
            <el-table-column prop="goods_name" label="商品名称" min-width="150" />
            <el-table-column prop="goods_spec" label="规格型号" width="120">
              <template #default="{ row }">{{ row.goods_spec || '-' }}</template>
            </el-table-column>
            <el-table-column prop="unit_name" label="单位" width="80" align="center">
              <template #default="{ row }">{{ row.unit_name || row.unit || '-' }}</template>
            </el-table-column>
            <el-table-column prop="quantity" label="数量" width="100" align="right" />
            <el-table-column prop="price" label="单价" width="100" align="right">
              <template #default="{ row }">¥{{ formatAmount(row.price) }}</template>
            </el-table-column>
            <el-table-column prop="amount" label="金额" width="120" align="right">
              <template #default="{ row }">¥{{ formatAmount(row.amount) }}</template>
            </el-table-column>
            <el-table-column prop="remark" label="备注" min-width="120">
              <template #default="{ row }">{{ row.remark || '-' }}</template>
            </el-table-column>
          </el-table>
        </div>
      </div>
      <template #footer>
        <el-button @click="detailDialogVisible = false">关闭</el-button>
        <el-button type="warning" @click="handlePrintDelivery(currentOrder)">打印送货单</el-button>
      </template>
    </el-dialog>

    <!-- 送货单打印组件 -->
    <delivery-note-print
      v-model="printDialogVisible"
      :stockOutData="currentPrintOrder"
    />

    <!-- 高级打印设计器 -->
    <advanced-delivery-print
      v-model="advancedPrintVisible"
      :stockOutData="currentPrintOrder"
    />
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Search, Refresh, Printer } from '@element-plus/icons-vue'
import { getStockOutList, getStockOut } from '../../api/inventory'
import { getWarehouses } from '../../api/basic'
import { DeliveryNotePrint, AdvancedDeliveryPrint } from '../../components/print'

const loading = ref(false)
const tableData = ref([])
const searchKeyword = ref('')
const filterWarehouse = ref('')
const filterStatus = ref('')
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)
const tableHeight = ref(0)
const warehouseList = ref([])
const selectedRows = ref([])

const detailDialogVisible = ref(false)
const currentOrder = ref(null)

const printDialogVisible = ref(false)
const advancedPrintVisible = ref(false)
const currentPrintOrder = ref(null)

const formatAmount = (amount) => {
  if (!amount) return '0.00'
  return Number(amount).toFixed(2)
}

const formatDateTime = (datetime) => {
  if (!datetime) return '-'
  return datetime.replace('T', ' ').substring(0, 19)
}

const getStatusType = (status) => {
  const types = {
    draft: 'info',
    confirmed: 'success',
    cancelled: 'danger'
  }
  return types[status] || 'info'
}

const calculateTableHeight = () => {
  nextTick(() => {
    const toolbarCard = document.querySelector('.toolbar-card')
    const paginationWrapper = document.querySelector('.pagination-wrapper')
    const pageContent = document.querySelector('.page-content')
    
    if (pageContent) {
      let usedHeight = 0
      if (toolbarCard) usedHeight += toolbarCard.offsetHeight + 8
      if (paginationWrapper) usedHeight += paginationWrapper.offsetHeight + 2
      usedHeight += 4
      
      const availableHeight = window.innerHeight - 64 - 16
      tableHeight.value = Math.max(availableHeight - usedHeight, 150)
    }
  })
}

const loadData = async () => {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      page_size: pageSize.value
    }
    if (searchKeyword.value) params.search = searchKeyword.value
    if (filterWarehouse.value) params.warehouse = filterWarehouse.value
    if (filterStatus.value) params.status = filterStatus.value
    
    const res = await getStockOutList(params)
    tableData.value = res.data.items || res.data.results || []
    total.value = res.data.count || 0
  } catch (error) {
    tableData.value = []
    total.value = 0
    ElMessage.error('加载数据失败：' + (error.message || '未知错误'))
  } finally {
    loading.value = false
  }
}

const loadOptions = async () => {
  try {
    const whRes = await getWarehouses()
    warehouseList.value = whRes.data.items || whRes.data.results || []
  } catch (error) {
    console.error('加载选项失败', error)
  }
}

const handleSelectionChange = (rows) => {
  selectedRows.value = rows
}

const handleView = async (row) => {
  try {
    const res = await getStockOut(row.id)
    currentOrder.value = res.data
    detailDialogVisible.value = true
  } catch (error) {
    ElMessage.error('获取详情失败')
  }
}

const handlePrintDelivery = async (row) => {
  try {
    const res = await getStockOut(row.id)
    currentPrintOrder.value = res.data
    printDialogVisible.value = true
  } catch (error) {
    ElMessage.error('获取出库单详情失败')
  }
}

const handleAdvancedPrint = async (row) => {
  try {
    const res = await getStockOut(row.id)
    currentPrintOrder.value = res.data
    advancedPrintVisible.value = true
  } catch (error) {
    ElMessage.error('获取出库单详情失败')
  }
}

const handleBatchPrint = async () => {
  if (selectedRows.value.length === 0) {
    ElMessage.warning('请选择要打印的出库单')
    return
  }
  
  ElMessage.info(`已选择 ${selectedRows.value.length} 个出库单，将依次打印送货单...`)
  
  for (const row of selectedRows.value) {
    try {
      const res = await getStockOut(row.id)
      currentPrintOrder.value = res.data
      printDialogVisible.value = true
      await new Promise(resolve => setTimeout(resolve, 800))
    } catch (error) {
      console.error('打印失败:', error)
    }
  }
}

onMounted(() => {
  loadData()
  loadOptions()
  calculateTableHeight()
  window.addEventListener('resize', calculateTableHeight)
})

onUnmounted(() => {
  window.removeEventListener('resize', calculateTableHeight)
})
</script>

<style scoped>
.stock-out-page {
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
  width: 280px;
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
  flex-shrink: 0;
}

.pagination-wrapper :deep(.el-pagination) {
  --el-pagination-button-height: 32px;
  --el-pagination-font-size: 13px;
}

.detail-dialog .order-detail {
  padding: 10px 0;
}

.detail-header {
  margin-bottom: 15px;
}

.detail-header h3 {
  margin: 0 0 10px 0;
  font-size: 16px;
  color: var(--color-text-primary);
}

.info-row {
  display: flex;
  margin-bottom: 12px;
}

.info-item {
  flex: 1;
  display: flex;
  align-items: center;
}

.info-item.full-width {
  flex: 3;
}

.info-item .label {
  font-weight: bold;
  color: var(--color-text-secondary);
  min-width: 80px;
}

.info-item .value {
  color: var(--color-text-primary);
}

.detail-items {
  margin-top: 20px;
}

.detail-items h4 {
  margin-bottom: 12px;
  font-size: 14px;
  color: var(--color-text-primary);
}

@media screen and (max-width: 1200px) {
  .search-input {
    width: 240px;
  }
  
  .toolbar-left,
  .toolbar-right {
    gap: var(--spacing-sm);
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
</style>

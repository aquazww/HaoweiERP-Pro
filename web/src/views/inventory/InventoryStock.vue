<template>
  <div class="inventory-page">
    <div class="page-content">
      <!-- 统计卡片 -->
      <div class="stats-cards">
        <div class="stat-card">
          <div class="stat-icon total">
            <el-icon><Box /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.total_items }}</div>
            <div class="stat-label">库存品种</div>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon quantity">
            <el-icon><Goods /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ formatNumber(stats.total_quantity) }}</div>
            <div class="stat-label">库存总量</div>
          </div>
        </div>
        <div class="stat-card warning">
          <div class="stat-icon warning">
            <el-icon><Warning /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.out_of_stock }}</div>
            <div class="stat-label">缺货品种</div>
          </div>
        </div>
      </div>

      <!-- 工具栏 -->
      <div class="toolbar-card">
        <div class="toolbar-left">
          <div class="search-box">
            <el-icon class="search-icon"><Search /></el-icon>
            <el-input
              v-model="searchKeyword"
              placeholder="搜索商品名称、编码"
              class="search-input"
              clearable
              @keyup.enter="loadStock"
            />
          </div>
          <el-select v-model="filterWarehouse" placeholder="仓库" clearable style="width: 140px" @change="loadStock">
            <el-option label="全部仓库" :value="''" />
            <el-option v-for="item in warehouseList" :key="item.id" :label="item.name" :value="item.id" />
          </el-select>
          <el-select v-model="filterCategory" placeholder="分类" clearable style="width: 140px" @change="loadStock">
            <el-option label="全部分类" :value="''" />
            <el-option v-for="item in categoryList" :key="item.id" :label="item.name" :value="item.id" />
          </el-select>
          <el-select v-model="filterStatus" placeholder="库存状态" clearable style="width: 130px" @change="loadStock">
            <el-option label="全部状态" :value="''" />
            <el-option label="正常" value="normal" />
            <el-option label="库存不足" value="low" />
            <el-option label="缺货" value="out" />
            <el-option label="库存过剩" value="over" />
          </el-select>
        </div>
        <div class="toolbar-right">
          <el-button :icon="Refresh" @click="loadStock">刷新</el-button>
          <el-button type="warning" :icon="Warning" @click="showWarningDialog">库存预警</el-button>
        </div>
      </div>

      <!-- 表格 -->
      <div class="table-card">
        <el-table 
          :data="stockList" 
          style="width: 100%" 
          v-loading="loading"
          class="data-table"
          stripe
          :height="tableHeight"
          @sort-change="handleSortChange"
        >
          <el-table-column type="index" label="#" width="50" align="center" />
          <el-table-column prop="goods_code" label="商品编码" width="120" sortable="custom" />
          <el-table-column prop="goods_name" label="商品名称" min-width="180" sortable="custom" />
          <el-table-column prop="category_name" label="分类" width="100" />
          <el-table-column prop="warehouse_name" label="仓库" width="100" />
          <el-table-column prop="unit" label="单位" width="70" align="center" />
          <el-table-column prop="quantity" label="库存数量" width="100" align="right" sortable="custom">
            <template #default="{ row }">
              <span :class="getQuantityClass(row)">{{ formatNumber(row.quantity) }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="min_stock" label="安全库存" width="90" align="right">
            <template #default="{ row }">{{ row.min_stock || '-' }}</template>
          </el-table-column>
          <el-table-column prop="max_stock" label="库存上限" width="90" align="right">
            <template #default="{ row }">{{ row.max_stock || '-' }}</template>
          </el-table-column>
          <el-table-column label="状态" width="100" align="center">
            <template #default="{ row }">
              <el-tag :type="getStatusType(row.stock_status?.code)" size="small">
                {{ row.stock_status?.text || '-' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="updated_at" label="更新时间" width="160">
            <template #default="{ row }">{{ formatDateTime(row.updated_at) }}</template>
          </el-table-column>
          <el-table-column label="操作" width="100" align="center" fixed="right">
            <template #default="{ row }">
              <div class="action-buttons">
                <el-button type="primary" link size="small" @click="handleViewLogs(row)">流水</el-button>
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
            @size-change="loadStock"
            @current-change="loadStock"
          />
        </div>
      </div>
    </div>

    <!-- 库存流水弹窗 -->
    <el-dialog v-model="logDialogVisible" title="库存流水" width="900px" class="log-dialog">
      <div class="log-header">
        <span>商品：{{ currentGoods?.goods_name }} ({{ currentGoods?.goods_code }})</span>
        <span>仓库：{{ currentGoods?.warehouse_name }}</span>
      </div>
      <el-table :data="logList" v-loading="logLoading" style="width: 100%;" max-height="400">
        <el-table-column type="index" label="#" width="50" align="center" />
        <el-table-column prop="change_type_display" label="类型" width="80" align="center">
          <template #default="{ row }">
            <el-tag :type="row.change_type === 'inbound' ? 'success' : 'danger'" size="small">
              {{ row.change_type_display }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="change_quantity" label="变动数量" width="100" align="right">
          <template #default="{ row }">
            <span :class="row.change_type === 'inbound' ? 'text-success' : 'text-danger'">
              {{ row.change_type === 'inbound' ? '+' : '-' }}{{ row.change_quantity }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="before_quantity" label="变动前" width="90" align="right" />
        <el-table-column prop="after_quantity" label="变动后" width="90" align="right" />
        <el-table-column prop="related_order_type" label="关联单据" width="120" />
        <el-table-column prop="remark" label="备注" min-width="150" />
        <el-table-column prop="created_at" label="时间" width="160">
          <template #default="{ row }">{{ formatDateTime(row.created_at) }}</template>
        </el-table-column>
      </el-table>
    </el-dialog>

    <!-- 库存预警弹窗 -->
    <el-dialog v-model="warningDialogVisible" title="库存预警" width="800px" class="warning-dialog">
      <el-table :data="warningList" v-loading="warningLoading" style="width: 100%;" max-height="450">
        <el-table-column type="index" label="#" width="50" align="center" />
        <el-table-column prop="goods_code" label="商品编码" width="120" />
        <el-table-column prop="goods_name" label="商品名称" min-width="180" />
        <el-table-column prop="warehouse_name" label="仓库" width="100" />
        <el-table-column prop="quantity" label="当前库存" width="100" align="right">
          <template #default="{ row }">
            <span :class="getWarningClass(row.warning_type)">{{ row.quantity }}</span>
          </template>
        </el-table-column>
        <el-table-column label="预警类型" width="120" align="center">
          <template #default="{ row }">
            <el-tag :type="getWarningType(row.warning_type)" size="small">
              {{ row.warning_text }}
            </el-tag>
          </template>
        </el-table-column>
      </el-table>
      <div class="warning-empty" v-if="!warningLoading && warningList.length === 0">
        <el-empty description="暂无库存预警" />
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Search, Refresh, Box, Goods, Warning } from '@element-plus/icons-vue'
import { getInventory, getInventoryLogs, getInventoryWarning } from '../../api/inventory'
import { getWarehouses, getCategories } from '../../api/basic'

const loading = ref(false)
const stockList = ref([])
const searchKeyword = ref('')
const filterWarehouse = ref('')
const filterCategory = ref('')
const filterStatus = ref('')
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)
const tableHeight = ref(0)
const stats = ref({ total_items: 0, total_quantity: 0, out_of_stock: 0 })
const warehouseList = ref([])
const categoryList = ref([])
const sortField = ref('')
const sortOrder = ref('')

const logDialogVisible = ref(false)
const logLoading = ref(false)
const logList = ref([])
const currentGoods = ref(null)

const warningDialogVisible = ref(false)
const warningLoading = ref(false)
const warningList = ref([])

const formatNumber = (num) => {
  if (num === null || num === undefined) return '0'
  const n = Number(num)
  if (isNaN(n)) return '0'
  if (Number.isInteger(n)) return String(n)
  return n.toFixed(2)
}

const formatDateTime = (datetime) => {
  if (!datetime) return '-'
  return datetime.replace('T', ' ').substring(0, 19)
}

const getQuantityClass = (row) => {
  const status = row.stock_status?.code
  if (status === 'out') return 'quantity-out'
  if (status === 'low') return 'quantity-low'
  if (status === 'over') return 'quantity-over'
  return ''
}

const getStatusType = (code) => {
  const types = { normal: 'success', low: 'warning', out: 'danger', over: 'info' }
  return types[code] || 'info'
}

const getWarningType = (type) => {
  const types = { out: 'danger', low: 'warning', over: 'info' }
  return types[type] || 'info'
}

const getWarningClass = (type) => {
  if (type === 'out') return 'quantity-out'
  if (type === 'low') return 'quantity-low'
  return ''
}

const handleSortChange = ({ prop, order }) => {
  sortField.value = prop || ''
  sortOrder.value = order === 'ascending' ? '' : '-'
  loadStock()
}

const calculateTableHeight = () => {
  nextTick(() => {
    const statsCards = document.querySelector('.stats-cards')
    const toolbarCard = document.querySelector('.toolbar-card')
    const paginationWrapper = document.querySelector('.pagination-wrapper')
    const pageContent = document.querySelector('.page-content')
    
    if (pageContent) {
      let usedHeight = 0
      if (statsCards) usedHeight += statsCards.offsetHeight + 8
      if (toolbarCard) usedHeight += toolbarCard.offsetHeight + 4
      if (paginationWrapper) usedHeight += paginationWrapper.offsetHeight + 2
      usedHeight += 4
      
      const availableHeight = window.innerHeight - 64 - 16
      tableHeight.value = Math.max(availableHeight - usedHeight, 150)
    }
  })
}

const loadStock = async () => {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      page_size: pageSize.value
    }
    if (searchKeyword.value) params.search = searchKeyword.value
    if (filterWarehouse.value) params.warehouse = filterWarehouse.value
    if (filterCategory.value) params.category = filterCategory.value
    if (filterStatus.value) params.stock_status = filterStatus.value
    if (sortField.value) params.ordering = sortOrder.value + sortField.value
    
    const res = await getInventory(params)
    stockList.value = res.data.items || res.data.results || []
    total.value = res.data.count || 0
    
    if (res.data.stats) {
      stats.value = res.data.stats
    }
  } catch (error) {
    stockList.value = []
    total.value = 0
    ElMessage.error('加载数据失败：' + (error.message || '未知错误'))
  } finally {
    loading.value = false
  }
}

const loadOptions = async () => {
  try {
    const [whRes, catRes] = await Promise.all([
      getWarehouses(),
      getCategories()
    ])
    warehouseList.value = whRes.data.items || whRes.data.results || []
    categoryList.value = catRes.data.items || catRes.data.results || []
  } catch (error) {
    console.error('加载选项失败', error)
  }
}

const handleViewLogs = async (row) => {
  currentGoods.value = row
  logDialogVisible.value = true
  logLoading.value = true
  
  try {
    const res = await getInventoryLogs({ goods: row.goods, warehouse: row.warehouse, page_size: 50 })
    logList.value = res.data.items || res.data.results || []
  } catch (error) {
    logList.value = []
    ElMessage.error('加载流水失败')
  } finally {
    logLoading.value = false
  }
}

const showWarningDialog = async () => {
  warningDialogVisible.value = true
  warningLoading.value = true
  
  try {
    const res = await getInventoryWarning()
    warningList.value = res.data || []
  } catch (error) {
    warningList.value = []
    ElMessage.error('加载预警失败')
  } finally {
    warningLoading.value = false
  }
}

onMounted(() => {
  loadStock()
  loadOptions()
  calculateTableHeight()
  window.addEventListener('resize', calculateTableHeight)
})

onUnmounted(() => {
  window.removeEventListener('resize', calculateTableHeight)
})
</script>

<style scoped>
.inventory-page {
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

.stats-cards {
  display: flex;
  gap: 16px;
  flex-shrink: 0;
}

.stat-card {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 12px;
  background-color: var(--color-white);
  padding: 12px 16px;
  border-radius: var(--border-radius-lg);
  border: 1px solid var(--color-border-light);
  box-shadow: var(--shadow-sm);
}

.stat-card.warning {
  border-left: 3px solid var(--color-danger);
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
}

.stat-icon.total {
  background-color: rgba(59, 130, 246, 0.1);
  color: var(--color-primary);
}

.stat-icon.quantity {
  background-color: rgba(34, 197, 94, 0.1);
  color: var(--color-success);
}

.stat-icon.warning {
  background-color: rgba(239, 68, 68, 0.1);
  color: var(--color-danger);
}

.stat-info {
  display: flex;
  flex-direction: column;
}

.stat-value {
  font-size: 24px;
  font-weight: 700;
  color: var(--color-text-primary);
  font-family: 'Monaco', 'Consolas', monospace;
}

.stat-label {
  font-size: 13px;
  color: var(--color-text-secondary);
  margin-top: 2px;
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

.quantity-out {
  color: var(--color-danger);
  font-weight: 600;
}

.quantity-low {
  color: var(--color-warning);
  font-weight: 600;
}

.quantity-over {
  color: var(--color-primary);
  font-weight: 600;
}

.text-success {
  color: var(--color-success);
}

.text-danger {
  color: var(--color-danger);
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

.log-dialog .log-header {
  display: flex;
  gap: 24px;
  margin-bottom: 16px;
  padding: 12px 16px;
  background-color: var(--color-bg-light);
  border-radius: var(--border-radius-md);
  font-size: 14px;
  color: var(--color-text-secondary);
}

.warning-dialog .warning-empty {
  padding: 24px;
}
</style>

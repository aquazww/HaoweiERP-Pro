<template>
  <div class="finance-page">
    <div class="page-content">
      <div class="toolbar-card">
        <div class="toolbar-left">
          <div class="search-box">
            <el-icon class="search-icon"><Search /></el-icon>
            <el-input
              v-model="searchKeyword"
              placeholder="搜索单号"
              class="search-input"
              clearable
              @keyup.enter="loadPayments"
            />
          </div>
          <el-select v-model="query.type" placeholder="类型" clearable style="width: 140px" @change="loadPayments">
            <el-option label="全部" :value="''" />
            <el-option label="应付" value="payable" />
            <el-option label="应收" value="receivable" />
          </el-select>
          <el-select v-model="query.status" placeholder="状态" clearable style="width: 140px" @change="loadPayments">
            <el-option label="全部" :value="''" />
            <el-option label="未付款" value="pending" />
            <el-option label="部分付款" value="partial" />
            <el-option label="已付款" value="paid" />
          </el-select>
        </div>
        <div class="toolbar-right">
          <el-button :icon="Refresh" @click="loadPayments">刷新</el-button>
          <el-button type="primary" :icon="Plus" @click="handleAdd">新增收付款</el-button>
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
        >
          <el-table-column type="index" label="#" width="50" align="center" />
          <el-table-column prop="order_no" label="单号" min-width="150" />
          <el-table-column label="类型" width="90" align="center">
            <template #default="{ row }">
              <el-tag :type="row.type === 'payable' ? 'warning' : 'primary'" size="small">
                {{ row.type === 'payable' ? '应付' : '应收' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="related_order_no" label="关联单号" min-width="140" />
          <el-table-column label="金额" width="130" align="right">
            <template #default="{ row }">
              <span class="price-amount">¥{{ formatPrice(row.amount) }}</span>
            </template>
          </el-table-column>
          <el-table-column label="已付金额" width="130" align="right">
            <template #default="{ row }">
              <span class="price-paid">¥{{ formatPrice(row.paid_amount) }}</span>
            </template>
          </el-table-column>
          <el-table-column label="状态" width="90" align="center">
            <template #default="{ row }">
              <el-tag :type="getStatusType(row.status)" size="small">{{ getStatusText(row.status) }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="payment_date" label="付款日期" width="110" />
          <el-table-column label="操作" width="210" align="center" fixed="right">
            <template #default="{ row }">
              <div class="action-buttons">
                <el-button type="primary" link size="small" @click="handleView(row)">查看</el-button>
                <el-button type="success" link size="small" @click="handlePay(row)">付款</el-button>
                <el-button type="danger" link size="small" @click="handleDelete(row)">删除</el-button>
              </div>
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
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick, onUnmounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Refresh, Plus } from '@element-plus/icons-vue'
import { getPayments, deletePayment } from '../../api/finance'

const loading = ref(false)
const paymentList = ref([])
const searchKeyword = ref('')
const query = ref({
  type: '',
  status: '',
  page: 1,
  pageSize: 20,
  total: 0
})
const tableHeight = ref(0)

const getStatusType = (status) => {
  const typeMap = {
    'pending': 'warning',
    'partial': 'info',
    'paid': 'success'
  }
  return typeMap[status] || ''
}

const getStatusText = (status) => {
  const textMap = {
    'pending': '未付款',
    'partial': '部分付款',
    'paid': '已付款'
  }
  return textMap[status] || status
}

const formatPrice = (price) => {
  if (price === undefined || price === null) return '0.00'
  return Number(price).toFixed(2)
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

const loadPayments = async () => {
  loading.value = true
  try {
    const params = {
      page: query.value.page,
      page_size: query.value.pageSize
    }
    if (query.value.type) {
      params.type = query.value.type
    }
    if (query.value.status) {
      params.status = query.value.status
    }
    if (searchKeyword.value) {
      params.search = searchKeyword.value
    }
    const res = await getPayments(params)
    paymentList.value = res.data.items || res.data.results || []
    query.value.total = res.data.count || 0
  } catch (error) {
    paymentList.value = []
    query.value.total = 0
    ElMessage.error('加载数据失败：' + (error.message || '未知错误'))
  } finally {
    loading.value = false
  }
}

const handleAdd = () => {
  ElMessage.info('新增收付款功能开发中')
}

const handleView = (row) => {
  ElMessage.info('查看收付款功能开发中')
}

const handlePay = (row) => {
  ElMessage.info('收付款功能开发中')
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm('确定要删除该收付款单吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await deletePayment(row.id)
    ElMessage.success('删除成功')
    loadPayments()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
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
.finance-page {
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

.action-buttons {
  display: flex;
  align-items: center;
  gap: var(--spacing-xs);
}

.price-amount {
  font-weight: 600;
  color: var(--color-warning);
  font-family: 'Monaco', 'Consolas', monospace;
}

.price-paid {
  font-weight: 600;
  color: var(--color-primary);
  font-family: 'Monaco', 'Consolas', monospace;
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
</style>

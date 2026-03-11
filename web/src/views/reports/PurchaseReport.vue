<template>
  <div class="common-page report-page">
    <div class="page-content">
      <div class="table-card">
        <div class="card-header">
          <span class="card-title">采购报表</span>
          <el-button type="primary" :icon="Download" @click="handleExport">导出</el-button>
        </div>
        
        <div class="filter-section">
          <el-form :inline="true" :model="queryForm">
            <el-form-item label="日期范围">
              <el-date-picker
                v-model="dateRange"
                type="daterange"
                range-separator="至"
                start-placeholder="开始日期"
                end-placeholder="结束日期"
                value-format="YYYY-MM-DD"
                @change="handleDateChange"
              />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="loadReport">查询</el-button>
            </el-form-item>
          </el-form>
        </div>
        
        <div class="summary-section">
          <div class="summary-card">
            <div class="summary-item">
              <span class="label">总金额</span>
              <span class="value">¥{{ (reportData.summary?.total_amount !== undefined && reportData.summary?.total_amount !== null) ? reportData.summary.total_amount.toFixed(2) : '0.00' }}</span>
            </div>
          </div>
          <div class="summary-card">
            <div class="summary-item">
              <span class="label">订单数</span>
              <span class="value">{{ reportData.summary?.order_count || 0 }}</span>
            </div>
          </div>
        </div>
        
        <el-table :data="reportData.orders || []" style="width: 100%" v-loading="loading" class="data-table">
          <el-table-column prop="order_no" label="采购单号" min-width="150" />
          <el-table-column prop="supplier_name" label="供应商" min-width="180" />
          <el-table-column prop="order_date" label="日期" min-width="120" />
          <el-table-column prop="total_amount" label="金额" min-width="120" align="right">
            <template #default="{ row }">
              ¥{{ (row.total_amount !== undefined && row.total_amount !== null) ? row.total_amount.toFixed(2) : '0.00' }}
            </template>
          </el-table-column>
          <el-table-column prop="status" label="状态" min-width="100" align="center" />
        </el-table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Download } from '@element-plus/icons-vue'
import { getPurchaseReport } from '../../api/reports'
import { exportToExcel } from '../../utils/export'

const loading = ref(false)
const dateRange = ref([])
const queryForm = ref({
  start_date: '',
  end_date: ''
})

const reportData = ref({
  summary: {
    total_amount: 0,
    order_count: 0
  },
  orders: []
})

const handleDateChange = (val) => {
  if (val && val.length === 2) {
    queryForm.value.start_date = val[0]
    queryForm.value.end_date = val[1]
  } else {
    queryForm.value.start_date = ''
    queryForm.value.end_date = ''
  }
}

const loadReport = async () => {
  loading.value = true
  try {
    const params = {}
    if (queryForm.value.start_date) {
      params.start_date = queryForm.value.start_date
    }
    if (queryForm.value.end_date) {
      params.end_date = queryForm.value.end_date
    }
    const res = await getPurchaseReport(params)
    reportData.value = res.data
  } catch (error) {
    ElMessage.error('加载报表失败')
  } finally {
    loading.value = false
  }
}

const handleExport = () => {
  if (!reportData.value.orders || reportData.value.orders.length === 0) {
    ElMessage.warning('暂无数据可导出')
    return
  }
  
  const columns = [
    { key: 'order_no', title: '采购单号' },
    { key: 'supplier_name', title: '供应商' },
    { key: 'order_date', title: '日期' },
    { key: 'total_amount', title: '金额' },
    { key: 'status', title: '状态' }
  ]
  
  const exportData = reportData.value.orders.map(item => ({
    ...item,
    total_amount: '¥' + ((item.total_amount !== undefined && item.total_amount !== null) ? item.total_amount.toFixed(2) : '0.00')
  }))
  
  const filename = `采购报表_${new Date().getTime()}`
  exportToExcel(exportData, columns, filename)
  ElMessage.success('导出成功')
}

onMounted(() => {
  loadReport()
})
</script>

<style scoped>
.report-page .card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--spacing-md) var(--spacing-lg);
  border-bottom: 1px solid var(--color-border-light);
}

.report-page .card-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--color-text-primary);
}

.report-page .filter-section {
  padding: var(--spacing-md) var(--spacing-lg);
  border-bottom: 1px solid var(--color-border-light);
}

.report-page .summary-section {
  display: flex;
  gap: var(--spacing-lg);
  padding: var(--spacing-lg);
}

.report-page .summary-card {
  flex: 1;
  background: linear-gradient(135deg, #f0f5ff 0%, #e6f4ff 100%);
  border: 1px solid #bae0ff;
  border-radius: var(--border-radius-lg);
  padding: var(--spacing-lg);
}

.report-page .summary-item {
  text-align: center;
}

.report-page .summary-item .label {
  font-size: 14px;
  color: var(--color-text-secondary);
  display: block;
  margin-bottom: var(--spacing-xs);
}

.report-page .summary-item .value {
  font-size: 28px;
  font-weight: 700;
  color: var(--color-primary);
  font-family: 'Monaco', 'Consolas', monospace;
}
</style>

<template>
  <div class="common-page finance-report">
    <div class="page-content">
      <div class="table-card">
        <div class="card-header">
          <span class="card-title">财务报表</span>
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
            <el-form-item label="收付款类型">
              <el-select v-model="queryForm.payment_type" placeholder="全部" clearable style="width: 150px;">
                <el-option label="收款" value="income" />
                <el-option label="付款" value="expense" />
              </el-select>
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="handleSearch">查询</el-button>
              <el-button @click="handleReset">重置</el-button>
            </el-form-item>
          </el-form>
        </div>

        <div class="stats-section">
          <div class="stat-card income">
            <div class="stat-content">
              <div class="stat-value">¥{{ (reportData.summary?.income !== undefined && reportData.summary?.income !== null) ? reportData.summary.income.toFixed(2) : '0.00' }}</div>
              <div class="stat-label">总收入</div>
            </div>
          </div>
          <div class="stat-card expense">
            <div class="stat-content">
              <div class="stat-value">¥{{ (reportData.summary?.expense !== undefined && reportData.summary?.expense !== null) ? reportData.summary.expense.toFixed(2) : '0.00' }}</div>
              <div class="stat-label">总支出</div>
            </div>
          </div>
          <div class="stat-card profit">
            <div class="stat-content">
              <div class="stat-value">¥{{ (reportData.summary?.net_profit !== undefined && reportData.summary?.net_profit !== null) ? reportData.summary.net_profit.toFixed(2) : '0.00' }}</div>
              <div class="stat-label">净利润</div>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-content">
              <div class="stat-value">{{ reportData.summary?.payment_count || 0 }}</div>
              <div class="stat-label">收付款笔数</div>
            </div>
          </div>
        </div>

        <el-table :data="reportData.payments || []" style="width: 100%" v-loading="loading" class="data-table">
          <el-table-column prop="payment_no" label="收付款单号" min-width="150" />
          <el-table-column prop="payment_type" label="类型" width="100" align="center">
            <template #default="{ row }">
              <el-tag :type="row.payment_type === '收款' ? 'success' : 'danger'">
                {{ row.payment_type }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="related_party_name" label="往来单位" min-width="150" />
          <el-table-column prop="amount" label="金额" min-width="100" align="right">
            <template #default="{ row }">
              <span :style="{ color: row.payment_type === '收款' ? '#67c23a' : '#f56c6c' }">
                {{ row.payment_type === '收款' ? '+' : '-' }}¥{{ (row.amount !== undefined && row.amount !== null) ? row.amount.toFixed(2) : '0.00' }}
              </span>
            </template>
          </el-table-column>
          <el-table-column prop="payment_date" label="日期" min-width="100" />
          <el-table-column prop="payment_method" label="支付方式" min-width="100" />
          <el-table-column prop="remark" label="备注" min-width="150" show-overflow-tooltip />
        </el-table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { Download } from '@element-plus/icons-vue'
import { getFinanceReport } from '../../api/reports'
import { ElMessage } from 'element-plus'
import { exportToExcel } from '../../utils/export'

const loading = ref(false)
const dateRange = ref([])

const queryForm = ref({
  start_date: '',
  end_date: '',
  payment_type: ''
})

const reportData = ref({
  summary: {
    total_payment: 0,
    income: 0,
    expense: 0,
    net_profit: 0,
    payment_count: 0
  },
  payments: []
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
    if (queryForm.value.payment_type) {
      params.payment_type = queryForm.value.payment_type
    }
    const res = await getFinanceReport(params)
    reportData.value = res.data
  } catch (error) {
    ElMessage.error('加载报表失败')
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  loadReport()
}

const handleReset = () => {
  queryForm.value = {
    start_date: '',
    end_date: '',
    payment_type: ''
  }
  dateRange.value = []
  loadReport()
}

const handleExport = () => {
  if (!reportData.value.payments || reportData.value.payments.length === 0) {
    ElMessage.warning('暂无数据可导出')
    return
  }
  
  const columns = [
    { key: 'payment_no', title: '收付款单号' },
    { key: 'payment_type', title: '类型' },
    { key: 'related_party_name', title: '往来单位' },
    { key: 'amount', title: '金额' },
    { key: 'payment_date', title: '日期' },
    { key: 'payment_method', title: '支付方式' },
    { key: 'remark', title: '备注' }
  ]
  
  const exportData = reportData.value.payments.map(item => ({
    ...item,
    amount: (item.payment_type === '收款' ? '+' : '-') + '¥' + ((item.amount !== undefined && item.amount !== null) ? item.amount.toFixed(2) : '0.00')
  }))
  
  const filename = `财务报表_${new Date().getTime()}`
  exportToExcel(exportData, columns, filename)
  ElMessage.success('导出成功')
}

onMounted(() => {
  loadReport()
})
</script>

<style scoped>
.finance-report .card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--spacing-md) var(--spacing-lg);
  border-bottom: 1px solid var(--color-border-light);
}

.finance-report .card-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--color-text-primary);
}

.finance-report .filter-section {
  padding: var(--spacing-md) var(--spacing-lg);
  border-bottom: 1px solid var(--color-border-light);
}

.finance-report .stats-section {
  display: flex;
  gap: var(--spacing-lg);
  padding: var(--spacing-lg);
}

.finance-report .stat-card {
  flex: 1;
  text-align: center;
  background: linear-gradient(135deg, #f5f7fa 0%, #e4e7ed 100%);
  border: 1px solid var(--color-border-light);
  border-radius: var(--border-radius-lg);
  padding: var(--spacing-lg);
}

.finance-report .stat-card.income {
  background: linear-gradient(135deg, #f0fff4 0%, #dcffe4 100%);
  border-color: #bbf7d0;
}

.finance-report .stat-card.income .stat-value {
  color: var(--color-success);
}

.finance-report .stat-card.expense {
  background: linear-gradient(135deg, #fff1f0 0%, #ffccc7 100%);
  border-color: #ffccc7;
}

.finance-report .stat-card.expense .stat-value {
  color: var(--color-danger);
}

.finance-report .stat-card.profit {
  background: linear-gradient(135deg, #f0f5ff 0%, #e6f4ff 100%);
  border-color: #bae0ff;
}

.finance-report .stat-card.profit .stat-value {
  color: var(--color-primary);
}

.finance-report .stat-content {
  padding: var(--spacing-sm);
}

.finance-report .stat-value {
  font-size: 28px;
  font-weight: 700;
  margin-bottom: var(--spacing-xs);
  font-family: 'Monaco', 'Consolas', monospace;
}

.finance-report .stat-label {
  font-size: 14px;
  color: var(--color-text-secondary);
}
</style>

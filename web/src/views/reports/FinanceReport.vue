<template>
  <div class="finance-report">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>财务报表</span>
          <el-button type="primary" :icon="Download" @click="handleExport">导出</el-button>
        </div>
      </template>
      
      <el-form :inline="true" :model="queryForm" class="search-form">
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

      <el-row :gutter="20" style="margin-bottom: 20px;">
        <el-col :span="6">
          <el-card class="stat-card income">
            <div class="stat-content">
              <div class="stat-value">¥{{ (reportData.summary?.income !== undefined && reportData.summary?.income !== null) ? reportData.summary.income.toFixed(2) : '0.00' }}</div>
              <div class="stat-label">总收入</div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stat-card expense">
            <div class="stat-content">
              <div class="stat-value">¥{{ (reportData.summary?.expense !== undefined && reportData.summary?.expense !== null) ? reportData.summary.expense.toFixed(2) : '0.00' }}</div>
              <div class="stat-label">总支出</div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stat-card profit">
            <div class="stat-content">
              <div class="stat-value">¥{{ (reportData.summary?.net_profit !== undefined && reportData.summary?.net_profit !== null) ? reportData.summary.net_profit.toFixed(2) : '0.00' }}</div>
              <div class="stat-label">净利润</div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-value">{{ reportData.summary?.payment_count || 0 }}</div>
              <div class="stat-label">收付款笔数</div>
            </div>
          </el-card>
        </el-col>
      </el-row>

      <el-table :data="reportData.payments || []" border style="width: 100%" v-loading="loading">
        <el-table-column prop="payment_no" label="收付款单号" width="180" />
        <el-table-column prop="payment_type" label="类型" width="100">
          <template #default="{ row }">
            <el-tag :type="row.payment_type === '收款' ? 'success' : 'danger'">
              {{ row.payment_type }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="related_party_name" label="往来单位" width="180" />
        <el-table-column prop="amount" label="金额" width="120">
          <template #default="{ row }">
            <span :style="{ color: row.payment_type === '收款' ? '#67c23a' : '#f56c6c' }">
              {{ row.payment_type === '收款' ? '+' : '-' }}¥{{ (row.amount !== undefined && row.amount !== null) ? row.amount.toFixed(2) : '0.00' }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="payment_date" label="日期" width="120" />
        <el-table-column prop="payment_method" label="支付方式" width="120" />
        <el-table-column prop="remark" label="备注" />
      </el-table>
    </el-card>
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
.finance-report {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.search-form {
  margin-bottom: 20px;
}

.stat-card {
  text-align: center;
}

.stat-card.income .stat-value {
  color: #67c23a;
}

.stat-card.expense .stat-value {
  color: #f56c6c;
}

.stat-card.profit .stat-value {
  color: #409EFF;
}

.stat-content {
  padding: 10px;
}

.stat-value {
  font-size: 28px;
  font-weight: bold;
  margin-bottom: 10px;
}

.stat-label {
  font-size: 14px;
  color: #666;
}
</style>

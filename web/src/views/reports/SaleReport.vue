<template>
  <div class="report-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>销售报表</span>
          <el-button type="primary" :icon="Download" @click="handleExport">导出</el-button>
        </div>
      </template>
      
      <el-form :inline="true" :model="queryForm" style="margin-bottom: 20px;">
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
      
      <el-row :gutter="20" style="margin-bottom: 20px;">
        <el-col :span="12">
          <el-card class="summary-card">
            <div class="summary-item">
              <span class="label">总金额：</span>
              <span class="value">¥{{ (reportData.summary?.total_amount !== undefined && reportData.summary?.total_amount !== null) ? reportData.summary.total_amount.toFixed(2) : '0.00' }}</span>
            </div>
          </el-card>
        </el-col>
        <el-col :span="12">
          <el-card class="summary-card">
            <div class="summary-item">
              <span class="label">订单数：</span>
              <span class="value">{{ reportData.summary?.order_count || 0 }}</span>
            </div>
          </el-card>
        </el-col>
      </el-row>
      
      <el-table :data="reportData.orders || []" style="width: 100%" v-loading="loading">
        <el-table-column prop="order_no" label="销售单号" width="150" />
        <el-table-column prop="customer_name" label="客户" width="200" />
        <el-table-column prop="order_date" label="日期" width="150" />
        <el-table-column prop="total_amount" label="金额" width="150">
          <template #default="{ row }">
            ¥{{ (row.total_amount !== undefined && row.total_amount !== null) ? row.total_amount.toFixed(2) : '0.00' }}
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100" />
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Download } from 'element-plus'
import { getSaleReport } from '../../api/reports'
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
    const res = await getSaleReport(params)
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
    { key: 'order_no', title: '销售单号' },
    { key: 'customer_name', title: '客户' },
    { key: 'order_date', title: '日期' },
    { key: 'total_amount', title: '金额' },
    { key: 'status', title: '状态' }
  ]
  
  const exportData = reportData.value.orders.map(item => ({
    ...item,
    total_amount: '¥' + ((item.total_amount !== undefined && item.total_amount !== null) ? item.total_amount.toFixed(2) : '0.00')
  }))
  
  const filename = `销售报表_${new Date().getTime()}`
  exportToExcel(exportData, columns, filename)
  ElMessage.success('导出成功')
}

onMounted(() => {
  loadReport()
})
</script>

<style scoped>
.report-page {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.summary-card {
  margin-bottom: 20px;
}

.summary-item {
  text-align: center;
}

.summary-item .label {
  font-size: 14px;
  color: #666;
  margin-right: 10px;
}

.summary-item .value {
  font-size: 24px;
  font-weight: bold;
  color: #409EFF;
}
</style>

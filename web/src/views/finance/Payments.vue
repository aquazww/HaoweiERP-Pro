<template>
  <div class="finance-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>收付款管理</span>
          <el-button type="primary" @click="handleAdd">新增收付款</el-button>
        </div>
      </template>
      
      <el-form :inline="true" :model="queryForm" style="margin-bottom: 20px;">
        <el-form-item label="类型">
          <el-select v-model="queryForm.type" placeholder="请选择" clearable style="width: 150px;">
            <el-option label="应付" value="payable" />
            <el-option label="应收" value="receivable" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="queryForm.status" placeholder="请选择" clearable style="width: 150px;">
            <el-option label="未付款" value="pending" />
            <el-option label="部分付款" value="partial" />
            <el-option label="已付款" value="paid" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="loadPayments">查询</el-button>
        </el-form-item>
      </el-form>
      
      <el-table :data="paymentList" style="width: 100%" v-loading="loading">
        <el-table-column prop="order_no" label="单号" width="150" />
        <el-table-column prop="type" label="类型" width="100">
          <template #default="{ row }">
            <el-tag :type="row.type === 'payable' ? 'warning' : 'primary'">
              {{ row.type === 'payable' ? '应付' : '应收' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="related_order_no" label="关联单号" width="150" />
        <el-table-column prop="amount" label="金额" width="120" />
        <el-table-column prop="paid_amount" label="已付金额" width="120" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">{{ getStatusText(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="payment_date" label="付款日期" width="120" />
        <el-table-column label="操作" width="200">
          <template #default="{ row }">
            <el-button type="primary" link @click="handleView(row)">查看</el-button>
            <el-button type="success" link @click="handlePay(row)">付款</el-button>
            <el-button type="danger" link @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getPayments, deletePayment } from '../../api/finance'

const loading = ref(false)
const paymentList = ref([])
const queryForm = ref({
  type: '',
  status: ''
})

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

const loadPayments = async () => {
  loading.value = true
  try {
    const params = {}
    if (queryForm.value.type) {
      params.type = queryForm.value.type
    }
    if (queryForm.value.status) {
      params.status = queryForm.value.status
    }
    const res = await getPayments(params)
    paymentList.value = res.data.items || []
  } catch (error) {
    ElMessage.error('加载收付款列表失败')
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
})
</script>

<style scoped>
.finance-page {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>

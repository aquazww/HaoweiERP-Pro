<template>
  <el-dialog
    :model-value="modelValue"
    @update:model-value="$emit('update:modelValue', $event)"
    title="付款详情"
    width="700px"
    destroy-on-close
  >
    <el-descriptions :column="2" border>
      <el-descriptions-item label="付款单号">{{ viewData.order_no }}</el-descriptions-item>
      <el-descriptions-item label="往来单位">{{ viewData.related_party_name }}</el-descriptions-item>
      <el-descriptions-item label="类型">
        <el-tag :type="viewData.type === 'pay' ? 'danger' : 'success'" size="small">
          {{ viewData.type === 'pay' ? '付款' : '收款' }}
        </el-tag>
      </el-descriptions-item>
      <el-descriptions-item label="状态">
        <el-tag :type="getStatusType(viewData.status)">{{ getStatusText(viewData.status) }}</el-tag>
      </el-descriptions-item>
      <el-descriptions-item label="总金额">¥{{ formatPrice(viewData.total_amount) }}</el-descriptions-item>
      <el-descriptions-item label="已付金额">¥{{ formatPrice(viewData.paid_amount || 0) }}</el-descriptions-item>
      <el-descriptions-item label="未付金额">
        <span class="unpaid-amount">¥{{ formatPrice((viewData.total_amount || 0) - (viewData.paid_amount || 0)) }}</span>
      </el-descriptions-item>
      <el-descriptions-item label="创建时间">{{ viewData.created_at }}</el-descriptions-item>
    </el-descriptions>
    
    <el-divider content-position="left">付款记录</el-divider>
    
    <el-table :data="viewData.records || []" border size="small">
      <el-table-column prop="payment_date" label="付款日期" width="120" align="center" />
      <el-table-column label="付款金额" width="120" align="right">
        <template #default="{ row }">¥{{ formatPrice(row.amount) }}</template>
      </el-table-column>
      <el-table-column prop="payment_method" label="付款方式" width="100" align="center">
        <template #default="{ row }">{{ getPaymentMethodText(row.payment_method) }}</template>
      </el-table-column>
      <el-table-column prop="remark" label="备注" min-width="150" />
      <el-table-column prop="created_by_name" label="操作人" width="100" align="center" />
    </el-table>
    
    <template #footer>
      <el-button @click="$emit('update:modelValue', false)">关闭</el-button>
      <el-button type="primary" @click="$emit('edit')" v-if="canEdit && viewData.status !== 'paid'">付款</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { formatPrice } from '@/utils/format'

defineProps({
  modelValue: { type: Boolean, default: false },
  viewData: { type: Object, default: () => ({}) },
  recordsExpanded: { type: Boolean, default: false },
  canEdit: { type: Boolean, default: false }
})

defineEmits(['update:modelValue', 'edit', 'delete'])

const getStatusText = (status) => {
  const map = { pending: '待付款', partial: '部分付款', paid: '已付款' }
  return map[status] || status
}

const getStatusType = (status) => {
  const map = { pending: 'danger', partial: 'warning', paid: 'success' }
  return map[status] || 'info'
}

const getPaymentMethodText = (method) => {
  const map = { cash: '现金', bank: '银行转账', check: '支票', other: '其他' }
  return map[method] || method
}
</script>

<style scoped>
.unpaid-amount {
  color: #f56c6c;
  font-weight: 500;
}
</style>

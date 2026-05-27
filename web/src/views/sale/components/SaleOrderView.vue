<template>
  <el-dialog
    :model-value="modelValue"
    @update:model-value="$emit('update:modelValue', $event)"
    title="销售单详情"
    width="800px"
    destroy-on-close
    class="sale-view-dialog"
  >
    <el-descriptions :column="2" border>
      <el-descriptions-item label="销售单号">{{ viewData.order_no }}</el-descriptions-item>
      <el-descriptions-item label="客户名称">{{ viewData.customer_name }}</el-descriptions-item>
      <el-descriptions-item label="仓库名称">{{ viewData.warehouse_name }}</el-descriptions-item>
      <el-descriptions-item label="订单状态">
        <el-tag :type="getStatusType(viewData.status)">{{ getStatusText(viewData.status) }}</el-tag>
      </el-descriptions-item>
      <el-descriptions-item label="订单金额">¥{{ formatPrice(viewData.total_amount) }}</el-descriptions-item>
      <el-descriptions-item label="创建时间">{{ viewData.created_at }}</el-descriptions-item>
      <el-descriptions-item label="备注" :span="2">{{ viewData.remark || '-' }}</el-descriptions-item>
    </el-descriptions>
    
    <el-divider content-position="left">销售明细</el-divider>
    
    <el-table :data="viewData.items" border size="small">
      <el-table-column prop="goods_code" label="商品编码" width="120" />
      <el-table-column prop="goods_name" label="商品名称" min-width="180" />
      <el-table-column prop="unit_name" label="单位" width="80" align="center" />
      <el-table-column prop="quantity" label="数量" width="80" align="center" />
      <el-table-column label="单价" width="100" align="right">
        <template #default="{ row }">¥{{ formatPrice(row.price) }}</template>
      </el-table-column>
      <el-table-column label="金额" width="100" align="right">
        <template #default="{ row }">¥{{ formatPrice(row.amount) }}</template>
      </el-table-column>
      <el-table-column prop="shipped_quantity" label="已出库" width="80" align="center" />
    </el-table>
    
    <template #footer>
      <el-button @click="$emit('update:modelValue', false)">关闭</el-button>
      <el-button type="warning" @click="$emit('cancel')" v-if="canCancel && viewData.status !== 'completed' && viewData.status !== 'cancelled'">取消单据</el-button>
      <el-button type="primary" @click="$emit('edit')" v-if="canEdit && viewData.status === 'pending'">编辑</el-button>
      <el-button type="success" @click="$emit('stock-out')" v-if="canStockOut && viewData.status !== 'completed' && viewData.status !== 'cancelled'">出库</el-button>
      <el-button type="danger" @click="$emit('delete')" v-if="canDelete && viewData.status === 'pending'">删除</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { formatPrice } from '@/utils/format'

defineProps({
  modelValue: { type: Boolean, default: false },
  viewData: { type: Object, default: () => ({}) },
  canEdit: { type: Boolean, default: false },
  canStockOut: { type: Boolean, default: false },
  canDelete: { type: Boolean, default: false },
  canCancel: { type: Boolean, default: false }
})

defineEmits(['update:modelValue', 'edit', 'stock-out', 'delete', 'cancel'])

const getStatusText = (status) => {
  const map = { pending: '待出库', partial: '部分出库', completed: '已出库', cancelled: '已取消' }
  return map[status] || status
}

const getStatusType = (status) => {
  const map = { pending: 'warning', partial: 'info', completed: 'success', cancelled: 'danger' }
  return map[status] || 'info'
}
</script>

<style scoped>
.sale-view-dialog :deep(.el-dialog__body) { padding: 16px 20px; }
.sale-view-dialog :deep(.el-descriptions__label) { font-weight: 600; color: var(--color-text-secondary); }
.sale-view-dialog :deep(.el-descriptions__content) { font-weight: 500; color: var(--color-text-primary); }
.sale-view-dialog .detail-table { margin-top: 8px; }
.sale-view-dialog .detail-table :deep(.el-table__header th) { background: var(--color-bg-light); font-weight: 600; }
.sale-view-dialog .detail-table :deep(.el-table__body td) { font-size: 13px; }
.sale-view-dialog .dialog-footer { display: flex; justify-content: flex-end; gap: 10px; }
</style>

<template>
  <el-dialog 
    v-model="dialogVisible" 
    title="采购单详情" 
    width="800px"
    class="purchase-order-view-dialog"
  >
    <div class="view-content" v-if="viewData">
      <div class="info-section">
        <div class="info-row">
          <div class="info-item">
            <span class="info-label">采购单号</span>
            <span class="info-value">{{ viewData.order_no || '-' }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">状态</span>
            <el-tag :type="getStatusType(viewData.status)">{{ getStatusText(viewData.status) }}</el-tag>
          </div>
        </div>
        <div class="info-row">
          <div class="info-item">
            <span class="info-label">供应商</span>
            <span class="info-value">{{ viewData.supplier_name || '-' }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">仓库</span>
            <span class="info-value">{{ viewData.warehouse_name || '-' }}</span>
          </div>
        </div>
        <div class="info-row">
          <div class="info-item">
            <span class="info-label">采购日期</span>
            <span class="info-value">{{ viewData.order_date || '-' }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">总金额</span>
            <span class="info-value amount">¥{{ formatPrice(viewData.total_amount) }}</span>
          </div>
        </div>
        <div class="info-row">
          <div class="info-item">
            <span class="info-label">入库时间</span>
            <span class="info-value">{{ viewData.stock_in_time ? formatDateTime(viewData.stock_in_time) : '-' }}</span>
          </div>
        </div>
        <div class="info-row">
          <div class="info-item">
            <span class="info-label">创建人</span>
            <span class="info-value">{{ viewData.created_by_name || '-' }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">创建时间</span>
            <span class="info-value">{{ formatDateTime(viewData.created_at) }}</span>
          </div>
        </div>
      </div>
      
      <div class="remark-box" v-if="viewData.remark">
        <div class="remark-header">
          <el-icon class="remark-icon"><Document /></el-icon>
          <span>采购备注</span>
        </div>
        <div class="remark-text">{{ viewData.remark }}</div>
      </div>
      
      <div class="remark-box stock-in-remark" v-if="viewData.stock_in_remark">
        <div class="remark-header">
          <el-icon class="remark-icon"><Finished /></el-icon>
          <span>入库备注</span>
        </div>
        <div class="remark-text">{{ viewData.stock_in_remark }}</div>
      </div>
      
      <div class="items-section">
        <div class="items-header" @click="itemsExpanded = !itemsExpanded">
          <div class="header-left">
            <el-icon class="expand-icon" :class="{ expanded: itemsExpanded }"><ArrowRight /></el-icon>
            <span class="header-title">采购明细</span>
            <span class="header-count">{{ viewData.items?.length || 0 }}项</span>
          </div>
          <span class="expand-hint">{{ itemsExpanded ? '收起' : '展开' }}</span>
        </div>
        <el-collapse-transition>
          <div class="items-body" v-show="itemsExpanded">
            <el-table :data="viewData?.items || []" border size="small" class="detail-table">
              <el-table-column prop="goods_name" label="商品名称" min-width="140">
                <template #default="{ row }">
                  <span class="goods-name">{{ row.goods_name }}</span>
                </template>
              </el-table-column>
              <el-table-column prop="goods_spec" label="规格" min-width="80" align="center">
                <template #default="{ row }">
                  <span class="spec-text">{{ row.goods_spec || '-' }}</span>
                </template>
              </el-table-column>
              <el-table-column prop="quantity" label="数量" min-width="90" align="center">
                <template #default="{ row }">
                  <span class="quantity-cell">{{ formatQuantity(row.quantity) }}</span>
                  <span class="unit-text">{{ row.unit || '-' }}</span>
                </template>
              </el-table-column>
              <el-table-column prop="price" label="单价" width="85" align="right">
                <template #default="{ row }">¥{{ formatPrice(row.price) }}</template>
              </el-table-column>
              <el-table-column prop="amount" label="金额" width="95" align="right">
                <template #default="{ row }">
                  <span class="amount-cell">¥{{ formatPrice(row.amount) }}</span>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </el-collapse-transition>
      </div>
    </div>

    <template #footer>
      <div class="dialog-footer">
        <el-button @click="dialogVisible = false">关闭</el-button>
        <el-button 
          v-if="canEdit && viewData?.status === 'pending'"
          type="primary" 
          @click="handleEdit"
        >
          编辑
        </el-button>
        <el-button 
          v-if="canStockIn && viewData?.status !== 'completed' && viewData?.status !== 'cancelled'"
          type="success" 
          @click="handleStockIn"
        >
          入库
        </el-button>
        <el-button 
          v-if="canDelete && viewData?.status === 'pending'"
          type="danger" 
          @click="handleDelete"
        >
          删除
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, watch } from 'vue'
import { Document, ArrowRight, Finished } from '@element-plus/icons-vue'
import { formatPrice, formatQuantity } from '../../../utils/format'

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  },
  viewData: {
    type: Object,
    default: null
  },
  canEdit: {
    type: Boolean,
    default: false
  },
  canStockIn: {
    type: Boolean,
    default: false
  },
  canDelete: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:modelValue', 'edit', 'stock-in', 'delete'])

const dialogVisible = ref(props.modelValue)
const itemsExpanded = ref(true)

watch(() => props.modelValue, (val) => {
  dialogVisible.value = val
})

watch(dialogVisible, (val) => {
  emit('update:modelValue', val)
})

const getStatusText = (status) => {
  const textMap = {
    pending: '待入库',
    partial: '部分入库',
    completed: '已入库',
    cancelled: '已取消'
  }
  return textMap[status] || status
}

const getStatusType = (status) => {
  const typeMap = {
    pending: 'warning',
    partial: 'info',
    completed: 'success',
    cancelled: 'danger'
  }
  return typeMap[status] || 'info'
}

const formatDateTime = (datetime) => {
  if (!datetime) return '-'
  const date = new Date(datetime)
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  const hours = String(date.getHours()).padStart(2, '0')
  const minutes = String(date.getMinutes()).padStart(2, '0')
  const seconds = String(date.getSeconds()).padStart(2, '0')
  return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`
}

const handleEdit = () => {
  emit('edit')
}

const handleStockIn = () => {
  emit('stock-in')
}

const handleDelete = () => {
  emit('delete')
}
</script>

<style scoped>
.purchase-order-view-dialog :deep(.el-dialog__body) {
  padding: 20px;
}

.view-content {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.info-section {
  background: #f5f7fa;
  border-radius: 8px;
  padding: 16px;
}

.info-row {
  display: flex;
  gap: 20px;
  margin-bottom: 12px;
}

.info-row:last-child {
  margin-bottom: 0;
}

.info-item {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 8px;
}

.info-label {
  font-size: 13px;
  color: #909399;
  min-width: 70px;
}

.info-value {
  font-size: 14px;
  color: #303133;
  font-weight: 500;
}

.info-value.amount {
  color: #f56c6c;
  font-size: 16px;
}

.remark-box {
  background: #fdf6ec;
  border-radius: 8px;
  padding: 12px 16px;
}

.remark-box.stock-in-remark {
  background: #f0f9eb;
}

.remark-header {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 8px;
  font-size: 13px;
  color: #606266;
  font-weight: 500;
}

.remark-icon {
  font-size: 16px;
  color: #e6a23c;
}

.stock-in-remark .remark-icon {
  color: #67c23a;
}

.remark-text {
  font-size: 13px;
  color: #606266;
  line-height: 1.6;
  padding-left: 22px;
}

.items-section {
  border: 1px solid #ebeef5;
  border-radius: 8px;
  overflow: hidden;
}

.items-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: #f5f7fa;
  cursor: pointer;
  user-select: none;
}

.items-header:hover {
  background: #ecf5ff;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 8px;
}

.expand-icon {
  font-size: 14px;
  color: #909399;
  transition: transform 0.2s;
}

.expand-icon.expanded {
  transform: rotate(90deg);
}

.header-title {
  font-size: 14px;
  font-weight: 500;
  color: #303133;
}

.header-count {
  font-size: 12px;
  color: #909399;
  background: #fff;
  padding: 2px 8px;
  border-radius: 10px;
}

.expand-hint {
  font-size: 12px;
  color: #909399;
}

.items-body {
  padding: 16px;
}

.detail-table .goods-name {
  font-weight: 500;
  color: #303133;
}

.detail-table .spec-text {
  color: #909399;
}

.detail-table .quantity-cell {
  font-weight: 500;
  color: #409eff;
}

.detail-table .unit-text {
  color: #909399;
  margin-left: 4px;
  font-size: 12px;
}

.detail-table .amount-cell {
  font-weight: 500;
  color: #f56c6c;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}
</style>

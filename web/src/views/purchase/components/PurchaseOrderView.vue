<template>
  <el-dialog 
    v-model="dialogVisible" 
    title="采购单详情" 
    width="720px"
    class="purchase-order-view-dialog"
    :close-on-click-modal="false"
  >
    <div class="view-content" v-if="viewData">
      <!-- 状态横幅 -->
      <div class="status-banner" :class="getStatusClass(viewData.status)">
        <div class="status-left">
          <el-icon class="status-icon"><DocumentCopy /></el-icon>
          <div class="status-info">
            <div class="order-no">{{ viewData.order_no }}</div>
            <div class="status-text">{{ getStatusText(viewData.status) }}</div>
          </div>
        </div>
        <div class="status-right">
          <span class="amount-label">总金额</span>
          <span class="amount-value">¥{{ formatPrice(viewData.total_amount) }}</span>
        </div>
      </div>

      <!-- 基础信息 -->
      <div class="info-section">
        <div class="info-row">
          <div class="info-item">
            <span class="label">供应商</span>
            <span class="value">{{ viewData.supplier_name || '-' }}</span>
          </div>
          <div class="info-item">
            <span class="label">入库仓库</span>
            <span class="value">{{ viewData.warehouse_name || '-' }}</span>
          </div>
        </div>
        <div class="info-row">
          <div class="info-item">
            <span class="label">采购日期</span>
            <span class="value">{{ viewData.order_date || '-' }}</span>
          </div>
          <div class="info-item">
            <span class="label">明细项数</span>
            <span class="value primary">{{ viewData.items?.length || 0 }} 项</span>
          </div>
        </div>
        <div class="info-row">
          <div class="info-item">
            <span class="label">创建人</span>
            <span class="value">{{ viewData.created_by_name || '-' }}</span>
          </div>
          <div class="info-item">
            <span class="label">创建时间</span>
            <span class="value">{{ formatDateTime(viewData.created_at) }}</span>
          </div>
        </div>
        <div class="info-row" v-if="viewData.stock_in_time">
          <div class="info-item">
            <span class="label">入库时间</span>
            <span class="value success">{{ formatDateTime(viewData.stock_in_time) }}</span>
          </div>
          <div class="info-item">
            <span class="label">入库状态</span>
            <span class="value success">已完成</span>
          </div>
        </div>
      </div>

      <!-- 备注信息 -->
      <div class="remark-section" v-if="viewData.remark || viewData.stock_in_remark">
        <div class="remark-item" v-if="viewData.remark">
          <span class="remark-label"><el-icon><EditPen /></el-icon> 采购备注</span>
          <span class="remark-text">{{ viewData.remark }}</span>
        </div>
        <div class="remark-item" v-if="viewData.stock_in_remark">
          <span class="remark-label success"><el-icon><CircleCheck /></el-icon> 入库备注</span>
          <span class="remark-text">{{ viewData.stock_in_remark }}</span>
        </div>
      </div>

      <!-- 采购明细 -->
      <div class="items-section">
        <div class="section-header" @click="itemsExpanded = !itemsExpanded">
          <div class="header-left">
            <el-icon class="expand-icon" :class="{ expanded: itemsExpanded }"><ArrowRight /></el-icon>
            <span>采购明细</span>
            <el-tag size="small" type="info">{{ viewData.items?.length || 0 }}项</el-tag>
          </div>
          <div class="header-right">
            <span>合计 {{ formatQuantity(totalQuantity) }} 件</span>
            <span class="total-amount">¥{{ formatPrice(viewData.total_amount) }}</span>
          </div>
        </div>
        <el-collapse-transition>
          <div class="items-body" v-show="itemsExpanded">
            <el-table :data="viewData?.items || []" border size="small">
              <el-table-column type="index" label="序号" width="50" align="center" />
              <el-table-column prop="goods_name" label="商品名称" min-width="120">
                <template #default="{ row }">
                  <span class="goods-name">{{ row.goods_name }}</span>
                  <span class="goods-code" v-if="row.goods_code">（{{ row.goods_code }}）</span>
                </template>
              </el-table-column>
              <el-table-column prop="goods_spec" label="规格" width="70" align="center" show-overflow-tooltip>
                <template #default="{ row }">{{ row.goods_spec || '-' }}</template>
              </el-table-column>
              <el-table-column label="数量" width="85" align="center">
                <template #default="{ row }">
                  <span class="qty">{{ formatQuantity(row.quantity) }}</span>
                  <span class="unit">{{ row.unit || '' }}</span>
                </template>
              </el-table-column>
              <el-table-column label="单价" width="80" align="right">
                <template #default="{ row }">¥{{ formatPrice(row.price) }}</template>
              </el-table-column>
              <el-table-column label="金额" width="90" align="right">
                <template #default="{ row }">
                  <span class="amount">¥{{ formatPrice(row.amount) }}</span>
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
          v-if="canCancel && viewData?.status !== 'completed' && viewData?.status !== 'cancelled'"
          type="warning" :icon="CircleClose" @click="handleCancel">取消单据</el-button>
        <el-button 
          v-if="canEdit && viewData?.status === 'pending'"
          type="primary" :icon="Edit" @click="handleEdit">编辑</el-button>
        <el-button 
          v-if="canStockIn && viewData?.status !== 'completed' && viewData?.status !== 'cancelled'"
          type="success" :icon="Upload" @click="handleStockIn">入库</el-button>
        <el-button 
          v-if="canDelete && viewData?.status === 'pending'"
          type="danger" :icon="Delete" @click="handleDelete">删除</el-button>
      </div>
    </template>

    <StockInDialog v-model="stockInDialogVisible" :purchase-order="viewData" @success="handleStockInSuccess" />
  </el-dialog>
</template>

<script setup>
/**
 * 采购单详情弹窗组件
 */
import { ref, watch, computed } from 'vue'
import { DocumentCopy, ArrowRight, Edit, Upload, Delete, EditPen, CircleCheck, CircleClose } from '@element-plus/icons-vue'
import { formatPrice, formatQuantity } from '../../../utils/format'
import StockInDialog from './StockInDialog.vue'

const props = defineProps({
  modelValue: { type: Boolean, default: false },
  viewData: { type: Object, default: null },
  canEdit: { type: Boolean, default: false },
  canStockIn: { type: Boolean, default: false },
  canDelete: { type: Boolean, default: false },
  canCancel: { type: Boolean, default: false }
})

const emit = defineEmits(['update:modelValue', 'edit', 'stock-in', 'delete', 'cancel', 'refresh'])

const dialogVisible = ref(props.modelValue)
const itemsExpanded = ref(true)
const stockInDialogVisible = ref(false)

watch(() => props.modelValue, (val) => { dialogVisible.value = val })
watch(dialogVisible, (val) => { emit('update:modelValue', val) })

const totalQuantity = computed(() => {
  if (!props.viewData?.items) return 0
  return props.viewData.items.reduce((sum, item) => sum + (Number(item.quantity) || 0), 0)
})

const getStatusText = (status) => {
  const map = { pending: '待入库', partial: '部分入库', completed: '已入库', cancelled: '已取消' }
  return map[status] || status
}

const getStatusClass = (status) => {
  const map = { pending: 'status-pending', partial: 'status-partial', completed: 'status-completed', cancelled: 'status-cancelled' }
  return map[status] || ''
}

const formatDateTime = (datetime) => {
  if (!datetime) return '-'
  const d = new Date(datetime)
  return `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}-${String(d.getDate()).padStart(2,'0')} ${String(d.getHours()).padStart(2,'0')}:${String(d.getMinutes()).padStart(2,'0')}`
}

const handleEdit = () => { emit('edit') }
const handleStockIn = () => { stockInDialogVisible.value = true }
const handleStockInSuccess = () => { emit('refresh'); emit('update:modelValue', false) }
const handleDelete = () => { emit('delete') }
const handleCancel = () => { emit('cancel') }
</script>

<style scoped>
.purchase-order-view-dialog :deep(.el-dialog__body) {
  padding: 16px 20px;
}

.view-content {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

/* 状态横幅 */
.status-banner {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  border-radius: 8px;
  color: #fff;
}
.status-banner.status-pending { background: linear-gradient(135deg, #e6a23c, #f5c26b); }
.status-banner.status-partial { background: linear-gradient(135deg, #409eff, #79bbff); }
.status-banner.status-completed { background: linear-gradient(135deg, #67c23a, #95d475); }
.status-banner.status-cancelled { background: linear-gradient(135deg, #909399, #b4b6ba); }

.status-left { display: flex; align-items: center; gap: 12px; }
.status-icon { font-size: 32px; opacity: 0.9; }
.status-info { display: flex; flex-direction: column; gap: 2px; }
.order-no { font-size: 18px; font-weight: 600; }
.status-text { font-size: 13px; opacity: 0.9; }
.status-right { display: flex; flex-direction: column; align-items: flex-end; gap: 2px; }
.amount-label { font-size: 12px; opacity: 0.9; }
.amount-value { font-size: 20px; font-weight: 600; }

/* 基础信息 */
.info-section {
  background: #fafbfc;
  border-radius: 8px;
  padding: 4px 16px;
}

.info-row {
  display: flex;
  padding: 10px 0;
}

.info-row:not(:last-child) {
  border-bottom: 1px dashed #ebeef5;
}

.info-item {
  flex: 1;
  display: flex;
  align-items: center;
}

.info-item .label {
  width: 70px;
  font-size: 13px;
  color: #909399;
  flex-shrink: 0;
}

.info-item .value {
  font-size: 14px;
  color: #303133;
  font-weight: 500;
}

.info-item .value.primary { color: #409eff; }
.info-item .value.success { color: #67c23a; }

/* 备注信息 */
.remark-section {
  display: flex;
  gap: 16px;
}

.remark-item {
  flex: 1;
  display: flex;
  align-items: flex-start;
  gap: 8px;
  padding: 10px 12px;
  background: #fdf6ec;
  border-radius: 6px;
}

.remark-label {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: #e6a23c;
  white-space: nowrap;
  flex-shrink: 0;
}

.remark-label.success { color: #67c23a; }

.remark-text {
  font-size: 13px;
  color: #606266;
  line-height: 1.5;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

/* 采购明细 */
.items-section {
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  overflow: hidden;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 14px;
  background: #f5f7fa;
  cursor: pointer;
  user-select: none;
}

.section-header:hover { background: #ecf5ff; }

.header-left {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 14px;
  font-weight: 500;
  color: #303133;
}

.expand-icon {
  font-size: 12px;
  color: #909399;
  transition: transform 0.2s;
}

.expand-icon.expanded { transform: rotate(90deg); }

.header-right {
  display: flex;
  align-items: center;
  gap: 16px;
  font-size: 13px;
  color: #606266;
}

.total-amount {
  font-size: 15px;
  font-weight: 600;
  color: #f56c6c;
}

.items-body { padding: 12px; }

.detail-table .goods-name { font-weight: 500; color: #303133; }
.detail-table .goods-code { font-size: 11px; color: #909399; margin-left: 2px; }
.detail-table .qty { font-weight: 500; color: #409eff; }
.detail-table .unit { font-size: 11px; color: #909399; margin-left: 2px; }
.detail-table .amount { font-weight: 500; color: #f56c6c; }

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

@media screen and (max-width: 768px) {
  .remark-section { flex-direction: column; gap: 8px; }
}
</style>

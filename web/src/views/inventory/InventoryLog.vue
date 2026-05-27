<template>
  <div class="common-page inventory-log-page">
    <div class="page-content">
      <div class="toolbar-card">
        <div class="toolbar-left">
          <div class="search-box">
            <el-icon class="search-icon"><Search /></el-icon>
            <el-input
              v-model="searchKeyword"
              placeholder="搜索商品名称、仓库"
              class="search-input"
              clearable
              @keyup.enter="loadLogs"
            />
          </div>
          <el-select v-model="changeTypeFilter" placeholder="变动类型" clearable style="width: 140px" @change="loadLogs">
            <el-option label="全部" :value="''" />
            <el-option label="采购入库" value="purchase_in" />
            <el-option label="销售出库" value="sale_out" />
            <el-option label="调拨入库" value="transfer_in" />
            <el-option label="调拨出库" value="transfer_out" />
            <el-option label="库存调整" value="adjust" />
          </el-select>
        </div>
        <div class="toolbar-right">
          <el-button :icon="Refresh" @click="loadLogs">刷新</el-button>
        </div>
      </div>

      <div class="table-card">
        <el-table 
          :data="logList" 
          style="width: 100%" 
          v-loading="loading"
          :height="tableHeight"
          class="data-table"
          stripe
          @cell-click="handleOrderClick"
        >
          <el-table-column prop="goods_name" label="商品名称" min-width="180" show-overflow-tooltip />
          <el-table-column prop="warehouse_name" label="仓库" min-width="120" align="center" />
          <el-table-column prop="transaction_type" label="变动类型" width="100" align="center">
            <template #default="{ row }">
              <el-tag :type="getTransactionType(row).color" size="small">
                {{ getTransactionType(row).text }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="quantity_change" label="变动数量" width="100" align="center">
            <template #default="{ row }">
              <span :class="row.change_type === 'inbound' ? 'quantity-in' : 'quantity-out'">
                {{ formatChangeQuantity(row) }}
              </span>
            </template>
          </el-table-column>
          <el-table-column prop="balance_after" label="结存数量" width="100" align="center">
            <template #default="{ row }">
              <span class="balance-text">{{ formatQuantity(row.balance_after) }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="order_no" label="关联单号" min-width="150" align="center">
            <template #default="{ row }">
              <span 
                v-if="row.order_no" 
                class="order-link"
                :data-order-id="row.order_id"
                :data-order-type="row.order_type"
              >
                {{ row.order_no }}
              </span>
              <span v-else>-</span>
            </template>
          </el-table-column>
          <el-table-column prop="remark" label="备注" min-width="150" show-overflow-tooltip>
            <template #default="{ row }">
              {{ formatRemark(row.remark) }}
            </template>
          </el-table-column>
          <el-table-column prop="created_at" label="变动时间" width="160" align="center">
            <template #default="{ row }">
              {{ formatDateTime(row.created_at) }}
            </template>
          </el-table-column>
        </el-table>
        <div class="pagination-wrapper">
          <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :page-sizes="[20, 50, 100]"
            :total="total"
            layout="total, sizes, prev, pager, next, jumper"
            @size-change="loadLogs"
            @current-change="loadLogs"
          />
        </div>
      </div>
    </div>

    <!-- 订单详情弹窗 -->
    <el-dialog 
      v-model="orderDetailVisible" 
      :title="orderDetailTitle" 
      width="700px"
      class="order-detail-dialog"
    >
      <div class="order-detail-content" v-if="orderDetail">
        <div class="detail-section">
          <div class="detail-row">
            <span class="detail-label">单号</span>
            <span class="detail-value">{{ orderDetail.order_no }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">状态</span>
            <el-tag :type="getStatusType(orderDetail.status)">{{ getStatusText(orderDetail.status) }}</el-tag>
          </div>
        </div>
        <div class="detail-section">
          <div class="detail-header">明细信息</div>
          <el-table :data="orderDetail.items" border size="small">
            <el-table-column prop="goods_name" label="商品名称" min-width="150" />
            <el-table-column prop="quantity" label="数量" width="80" align="center" />
            <el-table-column prop="unit" label="单位" width="60" align="center" />
            <el-table-column prop="price" label="单价" width="80" align="right">
              <template #default="{ row }">¥{{ formatQuantity(row.price) }}</template>
            </el-table-column>
          </el-table>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { Refresh, Search } from '@element-plus/icons-vue'
import { useInventoryLog } from '@/composables/useInventoryLog'

const {
  loading,
  logList,
  searchKeyword,
  changeTypeFilter,
  currentPage,
  pageSize,
  total,
  tableHeight,
  orderDetailVisible,
  orderDetail,
  orderDetailTitle,
  getTransactionType,
  getStatusText,
  formatDateTime,
  formatChangeQuantity,
  formatQuantity,
  formatRemark,
  handleOrderClick,
  loadLogs
} = useInventoryLog()

const getStatusType = (status) => {
  const typeMap = {
    pending: 'warning',
    partial: 'info',
    completed: 'success',
    cancelled: 'danger'
  }
  return typeMap[status] || 'info'
}

onMounted(() => {
  loadLogs()
})
</script>

<style scoped>
.inventory-log-page .quantity-in { color: var(--color-success); font-weight: 600; }
.inventory-log-page .quantity-out { color: var(--color-danger); font-weight: 600; }
.inventory-log-page .balance-text { color: var(--color-primary); font-weight: 500; }
.inventory-log-page .order-link { color: var(--color-primary); cursor: pointer; font-weight: 500; }
.inventory-log-page .order-link:hover { color: var(--color-primary-dark); text-decoration: underline; }
.inventory-log-page .order-detail-content { display: flex; flex-direction: column; gap: 16px; }
.inventory-log-page .detail-section {
  background: var(--color-bg-light); border-radius: var(--border-radius-md); padding: 12px;
  border: 1px solid var(--color-border-light);
}
.inventory-log-page .detail-row { display: flex; align-items: center; gap: 12px; margin-bottom: 8px; }
.inventory-log-page .detail-row:last-child { margin-bottom: 0; }
.inventory-log-page .detail-label { font-size: 13px; color: var(--color-text-tertiary); min-width: 60px; }
.inventory-log-page .detail-value { font-size: 14px; color: var(--color-text-primary); font-weight: 500; }
.inventory-log-page .detail-header { font-size: 15px; font-weight: 600; color: var(--color-text-primary); margin-bottom: 12px; }
</style>

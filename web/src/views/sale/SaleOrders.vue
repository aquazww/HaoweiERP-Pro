<template>
  <div class="sale-page">
    <div class="page-content">
      <div class="toolbar-card">
        <div class="toolbar-left">
          <div class="search-box">
            <el-icon class="search-icon"><Search /></el-icon>
            <el-input
              v-model="searchKeyword"
              placeholder="搜索销售单号、客户"
              class="search-input"
              clearable
              @keyup.enter="loadOrders"
            />
          </div>
          <el-select v-model="statusFilter" placeholder="状态筛选" clearable style="width: 140px" @change="loadOrders">
            <el-option label="全部" :value="''" />
            <el-option label="待出库" value="pending" />
            <el-option label="部分出库" value="partial" />
            <el-option label="已出库" value="completed" />
            <el-option label="已取消" value="cancelled" />
          </el-select>
        </div>
        <div class="toolbar-right">
          <el-button :icon="Refresh" @click="loadOrders">刷新</el-button>
          <el-button type="primary" :icon="Plus" @click="handleAdd" v-if="canAddSale">新增销售单</el-button>
        </div>
      </div>

      <div class="table-card">
        <el-table 
          :data="orderList" 
          style="width: 100%" 
          v-loading="loading"
          :height="tableHeight"
          class="data-table"
          stripe
        >
          <el-table-column prop="customer_name" label="客户名称" min-width="180" show-overflow-tooltip />
          <el-table-column prop="warehouse_name" label="仓库名称" min-width="120" align="center" />
          <el-table-column prop="item_count" label="明细项数" min-width="90" align="center">
            <template #default="{ row }">
              <span class="item-count-badge">{{ row.items?.length || 0 }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="total_amount" label="订单总金额" min-width="120" align="right">
            <template #default="{ row }">
              <span class="price-text">¥{{ formatPrice(row.total_amount) }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="status" label="订单状态" min-width="100" align="center">
            <template #default="{ row }">
              <el-tag :type="getStatusType(row.status)">{{ getStatusText(row.status) }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="order_no" label="销售单号" min-width="150" align="center">
            <template #default="{ row }">
              <span class="order-no-link" @click="handleView(row)">{{ row.order_no }}</span>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="200" align="center" fixed="right">
            <template #default="{ row }">
              <el-button type="primary" link size="small" @click="handleView(row)">查看</el-button>
              <el-button type="primary" link size="small" @click="handleEdit(row)" v-if="canEditSale && row.status === 'pending'">编辑</el-button>
              <el-button type="success" link size="small" @click="handleStockOut(row)" v-if="canStockOut && row.status !== 'completed'">出库</el-button>
              <el-button type="danger" link size="small" @click="handleDelete(row)" v-if="canDeleteSale && row.status === 'pending'">删除</el-button>
            </template>
          </el-table-column>
        </el-table>
        <div class="pagination-wrapper">
          <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :page-sizes="[10, 20, 50, 100]"
            :total="total"
            layout="total, sizes, prev, pager, next, jumper"
            @size-change="loadOrders"
            @current-change="loadOrders"
          />
        </div>
      </div>
    </div>

    <!-- 销售单表单弹窗 -->
    <SaleOrderForm
      v-model="dialogVisible"
      :dialog-title="isEdit ? '编辑销售单' : '新增销售单'"
      :is-edit="isEdit"
      :form="form"
      :rules="rules"
      :customer-list="customerList"
      :warehouse-list="warehouseList"
      :goods-list="goodsList"
      :total-quantity="totalQuantity"
      :total-amount="totalAmount"
      :submit-loading="submitLoading"
      @submit="handleSubmit"
      @add-item="addItem"
      @remove-item="removeItem"
      @goods-change="handleGoodsChange"
      @quantity-input="handleQuantityInput"
      @price-input="handlePriceInput"
      @dialog-close="handleDialogClose"
    />

    <!-- 销售单详情弹窗 -->
    <SaleOrderView
      v-model="viewDialogVisible"
      :view-data="viewData"
      :can-edit="canEditSale"
      :can-stock-out="canStockOut"
      :can-delete="canDeleteSale"
      @edit="handleEditFromView"
      @stock-out="handleStockOutFromView"
      @delete="handleDeleteFromView"
    />
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { Plus, Refresh, Search } from '@element-plus/icons-vue'
import { useSaleOrders } from '@/composables/useSaleOrders'
import SaleOrderForm from './components/SaleOrderForm.vue'
import SaleOrderView from './components/SaleOrderView.vue'
import { formatPrice } from '@/utils/format'
import { canAdd, canEdit, canDelete } from '@/utils/permission'

const canAddSale = canAdd('sale')
const canEditSale = canEdit('sale')
const canDeleteSale = canDelete('sale')
const canStockOut = canEdit('inventory')

const {
  loading,
  orderList,
  searchKeyword,
  statusFilter,
  currentPage,
  pageSize,
  total,
  tableHeight,
  dialogVisible,
  isEdit,
  submitLoading,
  viewDialogVisible,
  viewData,
  customerList,
  warehouseList,
  goodsList,
  form,
  rules,
  totalQuantity,
  totalAmount,
  getStatusText,
  loadOrders,
  handleAdd,
  handleEdit,
  handleView,
  handleEditFromView,
  handleDeleteFromView,
  addItem,
  removeItem,
  handleGoodsChange,
  handleQuantityInput,
  handlePriceInput,
  handleSubmit,
  handleDialogClose
} = useSaleOrders()

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
  loadOrders()
})
</script>

<style scoped>
.sale-page {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.page-content {
  flex: 1;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 16px;
  overflow: hidden;
}

.toolbar-card {
  background: #fff;
  border-radius: 8px;
  padding: 16px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.08);
}

.toolbar-left {
  display: flex;
  gap: 12px;
  align-items: center;
}

.search-box {
  position: relative;
  width: 280px;
}

.search-icon {
  position: absolute;
  left: 10px;
  top: 50%;
  transform: translateY(-50%);
  color: #909399;
}

.search-input :deep(.el-input__wrapper) {
  padding-left: 30px;
}

.toolbar-right {
  display: flex;
  gap: 10px;
}

.table-card {
  flex: 1;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.08);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.data-table {
  flex: 1;
}

.item-count-badge {
  background: #f0f5ff;
  color: #165DFF;
  padding: 2px 10px;
  border-radius: 10px;
  font-size: 12px;
  font-weight: 500;
}

.price-text {
  color: #f56c6c;
  font-weight: 500;
}

.order-no-link {
  color: #409eff;
  cursor: pointer;
  text-decoration: underline;
}

.pagination-wrapper {
  padding: 12px 16px;
  border-top: 1px solid #f0f0f0;
  display: flex;
  justify-content: flex-end;
}
</style>

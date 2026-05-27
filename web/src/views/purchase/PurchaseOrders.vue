<template>
  <div class="common-page purchase-page">
    <div class="page-content">
      <div class="toolbar-card">
        <div class="toolbar-left">
          <div class="search-box">
            <el-icon class="search-icon"><Search /></el-icon>
            <el-input
              v-model="searchKeyword"
              placeholder="搜索采购单号、供应商"
              class="search-input"
              clearable
              @keyup.enter="loadOrders"
            />
          </div>
          <el-select v-model="statusFilter" placeholder="状态筛选" clearable style="width: 140px" @change="loadOrders">
            <el-option label="全部" :value="''" />
            <el-option label="待入库" value="pending" />
            <el-option label="部分入库" value="partial" />
            <el-option label="已入库" value="completed" />
            <el-option label="已取消" value="cancelled" />
          </el-select>
        </div>
        <div class="toolbar-right">
          <el-button :icon="Refresh" @click="loadOrders">刷新</el-button>
          <el-button type="primary" :icon="Plus" @click="handleAdd" v-if="canAddPurchase">新增采购单</el-button>
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
          <el-table-column prop="supplier_name" label="供应商名称" min-width="180" show-overflow-tooltip />
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
          <el-table-column prop="order_no" label="采购单号" min-width="150" align="center">
            <template #default="{ row }">
              <span class="order-no-link" @click="handleView(row)">{{ row.order_no }}</span>
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

    <!-- 新增/编辑弹窗 -->
    <PurchaseOrderForm
      ref="purchaseFormRef"
      v-model="dialogVisible"
      :dialog-title="isEdit ? '编辑采购单' : '新增采购单'"
      :is-edit="isEdit"
      :form="form"
      :rules="rules"
      :supplier-list="supplierList"
      :warehouse-list="warehouseList"
      :goods-list="goodsList"
      :category-list="categoryList"
      :available-goods="availableGoods"
      :total-quantity="totalQuantity"
      :total-amount="totalAmount"
      :submit-loading="submitLoading"
      @submit="handleSubmit"
      @add-item="addItem"
      @remove-item="removeItem"
      @goods-change="handleGoodsChange"
      @code-change="handleCodeChange"
      @spec-change="handleSpecChange"
      @quantity-input="handleQuantityInput"
      @quantity-blur="handleQuantityBlur"
      @price-input="handlePriceInput"
      @price-blur="handlePriceBlur"
      @dialog-close="handleDialogClose"
    />

    <!-- 详情弹窗 -->
    <PurchaseOrderView
      v-model="viewDialogVisible"
      :view-data="viewData"
      :can-edit="canEditPurchase"
      :can-stock-in="canStockIn"
      :can-delete="canDeletePurchase"
      :can-cancel="canEditPurchase"
      @edit="handleEditFromView"
      @stock-in="handleStockInFromView"
      @delete="handleDeleteFromView"
      @cancel="handleCancelFromView"
      @refresh="handleRefresh"
    />
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { Plus, Refresh, Search } from '@element-plus/icons-vue'
import { usePurchaseOrders } from '@/composables/usePurchaseOrders'
import PurchaseOrderForm from './components/PurchaseOrderForm.vue'
import PurchaseOrderView from './components/PurchaseOrderView.vue'
import { formatPrice } from '@/utils/format'
import { canAdd, canEdit, canDelete } from '@/utils/permission'

const canAddPurchase = canAdd('purchase')
const canEditPurchase = canEdit('purchase')
const canDeletePurchase = canDelete('purchase')
const canStockIn = canEdit('inventory')

const purchaseFormRef = ref(null)

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
  formRef,
  supplierList,
  warehouseList,
  goodsList,
  categoryList,
  form,
  rules,
  availableGoods,
  totalQuantity,
  totalAmount,
  getStatusText,
  loadOrders,
  handleAdd,
  handleEdit,
  handleView,
  handleEditFromView,
  handleDeleteFromView,
  handleCancelFromView,
  handleRefresh,
  addItem,
  removeItem,
  handleGoodsChange,
  handleCodeChange,
  handleSpecChange,
  handleQuantityInput,
  handleQuantityBlur,
  handlePriceInput,
  handlePriceBlur,
  handleSubmit,
  handleDialogClose
} = usePurchaseOrders(purchaseFormRef)

const getStatusType = (status) => {
  const typeMap = {
    pending: 'warning',
    partial: 'info',
    completed: 'success',
    cancelled: 'danger'
  }
  return typeMap[status] || 'info'
}

const handleStockInFromView = () => {
  loadOrders()
}

onMounted(() => {
  loadOrders()
})
</script>

<style scoped>
.purchase-page .item-count-badge {
  background: var(--color-primary-lighter);
  color: var(--color-primary);
  padding: 2px 10px; border-radius: 10px;
  font-size: 12px; font-weight: 500;
}
.purchase-page .price-text { color: var(--color-danger); font-weight: 600; font-family: 'SF Mono','Monaco','Consolas',monospace; }
.purchase-page .order-no-link { color: var(--color-primary); cursor: pointer; font-weight: 500; }
.purchase-page .order-no-link:hover { color: var(--color-primary-dark); text-decoration: underline; }
</style>

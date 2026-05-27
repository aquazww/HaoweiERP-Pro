<template>
  <div class="common-page sale-page">
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
      :can-cancel="canEditSale"
      @edit="handleEditFromView"
      @stock-out="handleStockOutFromView"
      @delete="handleDeleteFromView"
      @cancel="handleCancelFromView"
    />
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Refresh, Search } from '@element-plus/icons-vue'
import { useSaleOrders } from '@/composables/useSaleOrders'
import SaleOrderForm from './components/SaleOrderForm.vue'
import SaleOrderView from './components/SaleOrderView.vue'
import { formatPrice } from '@/utils/format'
import { canAdd, canEdit, canDelete } from '@/utils/permission'
import { confirmSaleOrder } from '@/api/sale'

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
  handleCancelFromView,
  addItem,
  removeItem,
  handleGoodsChange,
  handleQuantityInput,
  handlePriceInput,
  handleSubmit,
  handleDialogClose
} = useSaleOrders()

const handleStockOutFromView = async () => {
  if (!viewData.value) return
  
  try {
    await ElMessageBox.confirm(
      `确认对销售单「${viewData.value.order_no}」执行出库操作？`,
      '出库确认',
      { confirmButtonText: '确认出库', cancelButtonText: '取消', type: 'warning' }
    )
    
    await confirmSaleOrder(viewData.value.id)
    ElMessage.success('出库成功')
    viewDialogVisible.value = false
    loadOrders()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error(error.response?.data?.msg || error.message || '出库失败')
    }
    // 无论成功失败，刷新列表确保显示最新状态
    viewDialogVisible.value = false
    loadOrders()
  }
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

onMounted(() => {
  loadOrders()
})
</script>

<style scoped>
.sale-page .item-count-badge {
  background: var(--color-primary-lighter);
  color: var(--color-primary);
  padding: 2px 10px; border-radius: 10px;
  font-size: 12px; font-weight: 500;
}
.sale-page .price-text { color: var(--color-danger); font-weight: 600; font-family: 'SF Mono','Monaco','Consolas',monospace; }
.sale-page .order-no-link { color: var(--color-primary); cursor: pointer; font-weight: 500; }
.sale-page .order-no-link:hover { color: var(--color-primary-dark); text-decoration: underline; }
</style>

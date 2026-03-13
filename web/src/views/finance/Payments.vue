<template>
  <div class="payments-page">
    <div class="page-content">
      <div class="toolbar-card">
        <div class="toolbar-left">
          <div class="search-box">
            <el-icon class="search-icon"><Search /></el-icon>
            <el-input
              v-model="searchKeyword"
              placeholder="搜索付款单号、往来单位"
              class="search-input"
              clearable
              @keyup.enter="loadPayments"
            />
          </div>
          <el-select v-model="query.type" placeholder="类型筛选" clearable style="width: 120px" @change="loadPayments">
            <el-option label="全部" :value="''" />
            <el-option label="付款" value="pay" />
            <el-option label="收款" value="receive" />
          </el-select>
          <el-select v-model="query.status" placeholder="状态筛选" clearable style="width: 120px" @change="loadPayments">
            <el-option label="全部" :value="''" />
            <el-option label="待付款" value="pending" />
            <el-option label="部分付款" value="partial" />
            <el-option label="已付款" value="paid" />
          </el-select>
        </div>
        <div class="toolbar-right">
          <el-button :icon="Refresh" @click="loadPayments">刷新</el-button>
          <el-button type="primary" :icon="Plus" @click="handleAdd" v-if="canAddFinance">新增付款</el-button>
        </div>
      </div>

      <div class="table-card">
        <el-table 
          :data="paymentList" 
          style="width: 100%" 
          v-loading="loading"
          :height="tableHeight"
          class="data-table"
          stripe
        >
          <el-table-column prop="order_no" label="付款单号" min-width="150" align="center" />
          <el-table-column prop="related_party_name" label="往来单位" min-width="180" show-overflow-tooltip />
          <el-table-column prop="type" label="类型" width="80" align="center">
            <template #default="{ row }">
              <el-tag :type="row.type === 'pay' ? 'danger' : 'success'" size="small">
                {{ row.type === 'pay' ? '付款' : '收款' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="total_amount" label="总金额" min-width="120" align="right">
            <template #default="{ row }">
              <span class="price-text">¥{{ formatPrice(row.total_amount) }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="paid_amount" label="已付金额" min-width="120" align="right">
            <template #default="{ row }">
              <span class="price-text success">¥{{ formatPrice(row.paid_amount || 0) }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="status" label="状态" width="100" align="center">
            <template #default="{ row }">
              <el-tag :type="getStatusType(row.status)">{{ getStatusText(row.status) }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="payment_date" label="付款日期" width="120" align="center" />
          <el-table-column label="操作" width="150" align="center" fixed="right">
            <template #default="{ row }">
              <el-button type="primary" link size="small" @click="handleView(row)">查看</el-button>
              <el-button type="primary" link size="small" @click="handleEdit(row)" v-if="canEditFinance && row.status !== 'paid'">付款</el-button>
            </template>
          </el-table-column>
        </el-table>
        <div class="pagination-wrapper">
          <el-pagination
            v-model:current-page="query.page"
            v-model:page-size="query.pageSize"
            :page-sizes="[10, 20, 50, 100]"
            :total="total"
            layout="total, sizes, prev, pager, next, jumper"
            @size-change="loadPayments"
            @current-change="loadPayments"
          />
        </div>
      </div>
    </div>

    <!-- 付款表单弹窗 -->
    <PaymentForm
      v-model="dialogVisible"
      :dialog-title="dialogTitle"
      :is-edit="isEdit"
      :form="form"
      :rules="rules"
      :submit-loading="submitLoading"
      @submit="handleSubmit"
      @dialog-close="handleDialogClose"
    />

    <!-- 付款详情弹窗 -->
    <PaymentView
      v-model="viewDialogVisible"
      :view-data="viewData"
      :records-expanded="recordsExpanded"
      :can-edit="canEditFinance"
      @edit="handlePayFromView"
      @delete="handleDeleteFromView"
    />
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { Plus, Refresh, Search } from '@element-plus/icons-vue'
import { usePayments } from '@/composables/usePayments'
import PaymentForm from './components/PaymentForm.vue'
import PaymentView from './components/PaymentView.vue'
import { formatPrice } from '@/utils/format'

const {
  loading,
  paymentList,
  searchKeyword,
  query,
  total,
  tableHeight,
  dialogVisible,
  dialogTitle,
  isEdit,
  submitLoading,
  viewDialogVisible,
  viewData,
  recordsExpanded,
  formRef,
  canAddFinance,
  canEditFinance,
  canDeleteFinance,
  form,
  rules,
  getStatusText,
  loadPayments,
  handleAdd,
  handleEdit,
  handleView,
  handlePayFromView,
  handleDeleteFromView,
  handleSubmit,
  handleDialogClose
} = usePayments()

const getStatusType = (status) => {
  const typeMap = {
    pending: 'danger',
    partial: 'warning',
    paid: 'success'
  }
  return typeMap[status] || 'info'
}

onMounted(() => {
  loadPayments()
})
</script>

<style scoped>
.payments-page {
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

.price-text {
  color: #f56c6c;
  font-weight: 500;
}

.price-text.success {
  color: #67c23a;
}

.pagination-wrapper {
  padding: 12px 16px;
  border-top: 1px solid #f0f0f0;
  display: flex;
  justify-content: flex-end;
}
</style>

<template>
  <div class="params-page">
    <div class="page-content">
      <el-tabs v-model="activeTab" class="params-tabs">
        <el-tab-pane label="计量单位" name="units">
          <UnitsTab
            :unit-list="unitList"
            :unit-loading="unitLoading"
            :unit-search="unitSearch"
            :selected-unit="selectedUnit"
            :unit-dialog-visible="unitDialogVisible"
            :unit-dialog-title="unitDialogTitle"
            :unit-form="unitForm"
            :unit-rules="unitRules"
            :unit-submit-loading="unitSubmitLoading"
            :unit-toggle-loading="unitToggleLoading"
            :filtered-unit-list="filteredUnitList"
            @search="loadUnits"
            @add="handleAddUnit"
            @edit="handleEditUnit"
            @delete="handleDeleteUnit"
            @toggle-status="handleToggleUnitStatus"
            @click="handleUnitClick"
            @submit="handleUnitSubmit"
            @dialog-close="unitDialogVisible = false"
          />
        </el-tab-pane>
        
        <el-tab-pane label="仓库信息" name="warehouses">
          <WarehousesTab
            :warehouse-list="warehouseList"
            :warehouse-loading="warehouseLoading"
            :warehouse-search="warehouseSearch"
            :selected-warehouse="selectedWarehouse"
            :warehouse-dialog-visible="warehouseDialogVisible"
            :warehouse-dialog-title="warehouseDialogTitle"
            :warehouse-form="warehouseForm"
            :warehouse-rules="warehouseRules"
            :warehouse-submit-loading="warehouseSubmitLoading"
            :warehouse-toggle-loading="warehouseToggleLoading"
            :filtered-warehouse-list="filteredWarehouseList"
            @search="loadWarehouses"
            @add="handleAddWarehouse"
            @edit="handleEditWarehouse"
            @delete="handleDeleteWarehouse"
            @toggle-status="handleToggleWarehouseStatus"
            @click="handleWarehouseClick"
            @submit="handleWarehouseSubmit"
            @dialog-close="warehouseDialogVisible = false"
          />
        </el-tab-pane>
        
        <el-tab-pane label="公司信息" name="company">
          <CompanyTab
            :company-form="companyForm"
            :company-rules="companyRules"
            :company-loading="companyLoading"
            :company-submit-loading="companySubmitLoading"
            :company-error-fields="companyErrorFields"
            @save="handleSaveCompany"
            @clear-error="clearFieldError"
            @logo-upload="handleLogoUpload"
            @stamp-upload="handleStampUpload"
          />
        </el-tab-pane>
      </el-tabs>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useUnits } from '@/composables/useUnits'
import { useWarehouses } from '@/composables/useWarehouses'
import { useCompany } from '@/composables/useCompany'
import UnitsTab from './components/UnitsTab.vue'
import WarehousesTab from './components/WarehousesTab.vue'
import CompanyTab from './components/CompanyTab.vue'

const activeTab = ref('units')

const {
  unitList,
  unitLoading,
  unitSearch,
  unitDialogVisible,
  unitDialogTitle,
  unitFormRef,
  unitSubmitLoading,
  unitToggleLoading,
  selectedUnit,
  unitForm,
  unitRules,
  filteredUnitList,
  handleUnitClick,
  loadUnits,
  handleAddUnit,
  handleEditUnit,
  handleUnitSubmit,
  handleToggleUnitStatus,
  handleDeleteUnit
} = useUnits()

const {
  warehouseList,
  warehouseLoading,
  warehouseSearch,
  warehouseDialogVisible,
  warehouseDialogTitle,
  warehouseFormRef,
  warehouseSubmitLoading,
  warehouseToggleLoading,
  selectedWarehouse,
  warehouseForm,
  warehouseRules,
  filteredWarehouseList,
  handleWarehouseClick,
  loadWarehouses,
  handleAddWarehouse,
  handleEditWarehouse,
  handleWarehouseSubmit,
  handleToggleWarehouseStatus,
  handleDeleteWarehouse
} = useWarehouses()

const {
  companyLoading,
  companySubmitLoading,
  companyFormRef,
  companyErrorFields,
  companyForm,
  companyRules,
  clearFieldError,
  loadCompanyInfo,
  handleSaveCompany,
  handleLogoUpload,
  handleStampUpload
} = useCompany()

onMounted(() => {
  loadUnits()
  loadWarehouses()
  loadCompanyInfo()
})
</script>

<style scoped>
.params-page {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.page-content {
  flex: 1;
  padding: 16px;
  overflow: hidden;
}

.params-tabs {
  height: 100%;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.08);
}

.params-tabs :deep(.el-tabs__header) {
  margin: 0;
  padding: 0 16px;
  background: #f5f7fa;
  border-radius: 8px 8px 0 0;
}

.params-tabs :deep(.el-tabs__content) {
  height: calc(100% - 40px);
  overflow-y: auto;
  padding: 16px;
}
</style>

<template>
  <div class="goods-page">
    <div class="page-content">
      <div class="dual-card-container">
        <!-- 左侧分类树卡片 -->
        <GoodsCategoryTree
          :category-tree-data="categoryTreeData"
          :selected-category-id="selectedCategoryId"
          :expanded-categories="expandedCategories"
          :can-add-goods="canAddGoods"
          :can-edit-goods="canEditGoods"
          @add-category="handleAddCategoryItem"
          @manage-category="handleManageCategory"
          @category-click="handleCategoryItemClick"
          @select-category="handleSelectCategory"
        />
        
        <!-- 右侧商品列表卡片 -->
        <div class="goods-card">
          <div class="toolbar-card">
            <div class="toolbar-left">
              <div class="search-box">
                <el-icon class="search-icon"><Search /></el-icon>
                <el-input
                  v-model="searchKeyword"
                  placeholder="搜索商品编码、名称"
                  class="search-input"
                  clearable
                  @keyup.enter="loadGoods"
                />
              </div>
              <el-select v-model="statusFilter" placeholder="状态筛选" clearable style="width: 140px" @change="loadGoods">
                <el-option label="全部" :value="''" />
                <el-option label="启用" :value="1" />
                <el-option label="停用" :value="0" />
              </el-select>
            </div>
            <div class="toolbar-right">
              <el-button type="primary" :icon="Plus" @click="handleAdd" v-if="canAddGoods">新增商品</el-button>
            </div>
          </div>
          
          <el-table 
            :data="goodsList" 
            v-loading="loading"
            :height="tableHeight"
            border
            stripe
            highlight-current-row
            @row-dblclick="handleEdit"
          >
            <el-table-column prop="code" label="商品编码" min-width="120" />
            <el-table-column prop="name" label="商品名称" min-width="180" />
            <el-table-column prop="category_name" label="分类" min-width="100" />
            <el-table-column prop="unit_name" label="单位" width="80" align="center" />
            <el-table-column prop="spec" label="规格" min-width="100" />
            <el-table-column label="进货价" width="100" align="right">
              <template #default="{ row }">¥{{ formatPrice(row.purchase_price) }}</template>
            </el-table-column>
            <el-table-column label="销售价" width="100" align="right">
              <template #default="{ row }">¥{{ formatPrice(row.sale_price) }}</template>
            </el-table-column>
            <el-table-column label="状态" width="80" align="center">
              <template #default="{ row }">
                <el-switch
                  v-model="row.status"
                  :active-value="1"
                  :inactive-value="0"
                  @change="handleToggleStatus(row)"
                  :loading="toggleLoading === row.id"
                  :disabled="!canEditGoods"
                />
              </template>
            </el-table-column>
            <el-table-column label="操作" width="120" align="center" fixed="right">
              <template #default="{ row }">
                <el-button type="primary" link size="small" @click="handleEdit(row)" v-if="canEditGoods">编辑</el-button>
                <el-button type="danger" link size="small" @click="handleDelete(row)" v-if="canDeleteGoods">删除</el-button>
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
              @size-change="loadGoods"
              @current-change="loadGoods"
            />
          </div>
        </div>
      </div>
    </div>
    
    <!-- 商品表单弹窗 -->
    <GoodsForm
      v-model="dialogVisible"
      :dialog-title="dialogTitle"
      :is-edit="isEdit"
      :form="form"
      :rules="rules"
      :price-errors="priceErrors"
      :category-options="goodsCategoryOptions"
      :unit-list="unitList"
      :submit-loading="submitLoading"
      @submit="handleSubmit"
      @price-input="handlePriceInput"
      @price-blur="handlePriceBlur"
      @dialog-close="handleDialogClose"
    />
    
    <!-- 分类管理弹窗 -->
    <CategoryManageDialog
      v-model="categoryDialogVisible"
      :category-tree-data="categoryTreeData"
      @refresh="loadCategories"
    />
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { Plus, Search } from '@element-plus/icons-vue'
import { useGoodsCategory } from '@/composables/useGoodsCategory'
import { useGoods } from '@/composables/useGoods'
import GoodsCategoryTree from './components/GoodsCategoryTree.vue'
import GoodsForm from './components/GoodsForm.vue'
import CategoryManageDialog from './components/CategoryManageDialog.vue'
import { formatPrice } from '@/utils/format'

const {
  categoryTreeData,
  selectedCategoryId,
  selectedCategoryIncludeChildren,
  expandedCategories,
  categoryDialogVisible,
  goodsCategoryOptions,
  loadCategories,
  handleCategoryItemClick,
  handleSelectCategory,
  handleManageCategory,
  handleAddCategoryItem
} = useGoodsCategory()

const {
  loading,
  toggleLoading,
  goodsList,
  searchKeyword,
  statusFilter,
  currentPage,
  pageSize,
  total,
  tableHeight,
  unitList,
  dialogVisible,
  dialogTitle,
  isEdit,
  submitLoading,
  formRef,
  canAddGoods,
  canEditGoods,
  canDeleteGoods,
  priceErrors,
  form,
  rules,
  loadGoods,
  loadUnits,
  handleAdd,
  handleEdit,
  handleSubmit,
  handleDelete,
  handleToggleStatus,
  handlePriceInput,
  handlePriceBlur,
  handleDialogClose
} = useGoods(selectedCategoryId, selectedCategoryIncludeChildren)

watch(selectedCategoryId, () => {
  loadGoods()
})

onMounted(() => {
  loadCategories()
  loadUnits()
})
</script>

<style scoped>
.goods-page {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.page-content {
  flex: 1;
  padding: 16px;
  overflow: hidden;
}

.dual-card-container {
  display: flex;
  gap: 16px;
  height: 100%;
}

.goods-card {
  flex: 1;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.08);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.toolbar-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  border-bottom: 1px solid #f0f0f0;
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

.pagination-wrapper {
  padding: 12px 16px;
  border-top: 1px solid #f0f0f0;
  display: flex;
  justify-content: flex-end;
}
</style>

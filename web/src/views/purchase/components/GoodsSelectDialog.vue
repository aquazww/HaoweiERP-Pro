<template>
  <el-dialog
    v-model="dialogVisible"
    title="选择商品"
    width="800px"
    :close-on-click-modal="false"
    class="goods-select-dialog"
  >
    <div class="goods-select-content">
      <div class="category-section">
        <div class="section-title">商品分类</div>
        <div class="category-list">
          <div
            v-for="category in categoryList"
            :key="category.id"
            class="category-item"
            :class="{ active: selectedCategory === category.id }"
            @click="handleCategorySelect(category.id)"
          >
            <span class="category-name">{{ category.name }}</span>
            <span class="category-count">{{ getCategoryGoodsCount(category.id) }}</span>
          </div>
        </div>
      </div>
      
      <div class="goods-section">
        <div class="section-header">
          <div class="section-title">
            {{ selectedCategoryName ? selectedCategoryName + ' - 商品列表' : '商品列表' }}
          </div>
          <el-input
            v-model="searchKeyword"
            placeholder="搜索商品编码、名称"
            clearable
            style="width: 200px"
            @input="handleSearch"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
        </div>
        
        <el-table
          ref="goodsTableRef"
          :data="filteredGoodsList"
          v-loading="loading"
          border
          stripe
          highlight-current-row
          height="350px"
          @current-change="handleCurrentChange"
          @row-dblclick="handleRowDblClick"
        >
          <el-table-column prop="code" label="商品编码" width="120" show-overflow-tooltip />
          <el-table-column prop="name" label="商品名称" min-width="150" show-overflow-tooltip />
          <el-table-column prop="spec" label="规格" width="120" show-overflow-tooltip>
            <template #default="{ row }">
              <span>{{ row.spec || '-' }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="unit_name" label="单位" width="80" align="center" />
          <el-table-column label="进货价" width="100" align="right">
            <template #default="{ row }">
              <span class="price-text">¥{{ formatPrice(row.purchase_price) }}</span>
            </template>
          </el-table-column>
        </el-table>
        
        <div class="selected-info" v-if="selectedGoods">
          <span class="info-label">已选择：</span>
          <span class="info-value">{{ selectedGoods.code }} - {{ selectedGoods.name }}</span>
        </div>
      </div>
    </div>
    
    <template #footer>
      <div class="dialog-footer">
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleConfirm" :disabled="!selectedGoods">确认选择</el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup>
/**
 * 商品选择弹窗组件
 * 支持按分类筛选商品并选择
 */
import { ref, computed, watch } from 'vue'
import { Search } from '@element-plus/icons-vue'
import { formatPrice } from '@/utils/format'

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  },
  goodsList: {
    type: Array,
    default: () => []
  },
  categoryList: {
    type: Array,
    default: () => []
  },
  excludeIds: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['update:modelValue', 'select'])

const dialogVisible = ref(props.modelValue)
const loading = ref(false)
const searchKeyword = ref('')
const selectedCategory = ref(null)
const selectedGoods = ref(null)
const goodsTableRef = ref(null)

watch(() => props.modelValue, (val) => {
  dialogVisible.value = val
  if (val) {
    selectedCategory.value = null
    selectedGoods.value = null
    searchKeyword.value = ''
  }
})

watch(dialogVisible, (val) => {
  emit('update:modelValue', val)
})

/**
 * 计算选中的分类名称
 */
const selectedCategoryName = computed(() => {
  if (!selectedCategory.value) return ''
  const category = props.categoryList.find(c => c.id === selectedCategory.value)
  return category?.name || ''
})

/**
 * 过滤后的商品列表
 */
const filteredGoodsList = computed(() => {
  let list = props.goodsList.filter(g => !props.excludeIds.includes(g.id))
  
  if (selectedCategory.value) {
    list = list.filter(g => g.category_id === selectedCategory.value || g.category === selectedCategory.value)
  }
  
  if (searchKeyword.value) {
    const keyword = searchKeyword.value.toLowerCase()
    list = list.filter(g => 
      g.code?.toLowerCase().includes(keyword) ||
      g.name?.toLowerCase().includes(keyword)
    )
  }
  
  return list
})

/**
 * 获取分类下的商品数量
 */
const getCategoryGoodsCount = (categoryId) => {
  return props.goodsList.filter(g => 
    (g.category_id === categoryId || g.category === categoryId) &&
    !props.excludeIds.includes(g.id)
  ).length
}

/**
 * 处理分类选择
 */
const handleCategorySelect = (categoryId) => {
  selectedCategory.value = selectedCategory.value === categoryId ? null : categoryId
  selectedGoods.value = null
}

/**
 * 处理搜索
 */
const handleSearch = () => {
  selectedGoods.value = null
}

/**
 * 处理表格行选中变化
 */
const handleCurrentChange = (row) => {
  selectedGoods.value = row
}

/**
 * 处理双击行
 */
const handleRowDblClick = (row) => {
  if (row) {
    selectedGoods.value = row
    handleConfirm()
  }
}

/**
 * 确认选择
 */
const handleConfirm = () => {
  if (selectedGoods.value) {
    emit('select', selectedGoods.value)
    dialogVisible.value = false
  }
}

defineExpose({
  selectedGoods
})
</script>

<style scoped>
.goods-select-dialog :deep(.el-dialog__body) {
  padding: 0;
}

.goods-select-content {
  display: flex;
  height: 450px;
}

.category-section {
  width: 180px;
  border-right: 1px solid #ebeef5;
  display: flex;
  flex-direction: column;
}

.section-title {
  padding: 12px 16px;
  font-size: 14px;
  font-weight: 600;
  color: #303133;
  background: #fafafa;
  border-bottom: 1px solid #ebeef5;
}

.category-list {
  flex: 1;
  overflow-y: auto;
  padding: 8px 0;
}

.category-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 16px;
  cursor: pointer;
  transition: all 0.2s;
}

.category-item:hover {
  background: #f5f7fa;
}

.category-item.active {
  background: #ecf5ff;
  color: #409eff;
}

.category-name {
  font-size: 13px;
}

.category-count {
  font-size: 12px;
  color: #909399;
  background: #f0f2f5;
  padding: 2px 6px;
  border-radius: 10px;
}

.category-item.active .category-count {
  background: #409eff;
  color: #fff;
}

.goods-section {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: #fafafa;
  border-bottom: 1px solid #ebeef5;
}

.section-header .section-title {
  padding: 0;
  background: transparent;
  border-bottom: none;
}

.goods-section :deep(.el-table) {
  flex: 1;
}

.price-text {
  color: #f56c6c;
  font-weight: 500;
}

.selected-info {
  padding: 10px 16px;
  background: #f5f7fa;
  border-top: 1px solid #ebeef5;
  font-size: 13px;
}

.info-label {
  color: #909399;
}

.info-value {
  color: #409eff;
  font-weight: 500;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}
</style>

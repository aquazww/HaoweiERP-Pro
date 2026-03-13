<template>
  <div class="category-card">
    <div class="category-header">
      <span class="category-title">商品分类</span>
      <div class="category-actions">
        <el-button type="primary" link :icon="Plus" size="small" @click="handleAddCategory" v-if="canAddGoods">添加</el-button>
        <el-button type="primary" link :icon="Setting" size="small" @click="handleManageCategory" v-if="canEditGoods">管理</el-button>
      </div>
    </div>
    <div class="category-tree-wrapper">
      <div class="category-tree">
        <div 
          v-for="(category, index) in categoryTreeData" 
          :key="category.id"
          class="category-node level-1"
          :class="{ 
            active: selectedCategoryId === category.id,
            expanded: expandedCategories.includes(category.id),
            'has-children': category.children && category.children.length > 0,
            'last-child': index === categoryTreeData.length - 1
          }"
        >
          <div 
            class="category-item"
            @click="handleCategoryItemClick(category)"
          >
            <div class="tree-line"></div>
            <div class="item-content">
              <el-icon 
                class="expand-icon" 
                :class="{ expanded: expandedCategories.includes(category.id) }"
                v-if="category.children && category.children.length > 0"
              >
                <ArrowRight />
              </el-icon>
              <span class="expand-placeholder" v-else></span>
              <el-icon class="category-icon folder"><Folder /></el-icon>
              <span class="category-name">{{ category.name }}</span>
            </div>
            <span class="category-count" v-if="getCategoryTotalGoods(category) > 0">{{ getCategoryTotalGoods(category) }}</span>
          </div>
          
          <el-collapse-transition>
            <div 
              class="children-container" 
              v-show="expandedCategories.includes(category.id) && category.children && category.children.length > 0"
            >
              <div 
                v-for="(sub, subIndex) in category.children" 
                :key="sub.id"
                class="category-node level-2"
                :class="{ 
                  active: selectedCategoryId === sub.id,
                  'last-child': subIndex === category.children.length - 1
                }"
              >
                <div 
                  class="category-item"
                  @click.stop="handleSelectCategory(sub.id)"
                >
                  <div class="tree-line"></div>
                  <div class="item-content">
                    <span class="line-connector"></span>
                    <el-icon class="category-icon leaf"><Document /></el-icon>
                    <span class="category-name">{{ sub.name }}</span>
                  </div>
                  <span class="category-count" v-if="sub.goods_count > 0">{{ sub.goods_count }}</span>
                </div>
              </div>
            </div>
          </el-collapse-transition>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { Plus, Setting, Folder, Document, ArrowRight } from '@element-plus/icons-vue'

defineProps({
  categoryTreeData: {
    type: Array,
    default: () => []
  },
  selectedCategoryId: {
    type: [Number, String, null],
    default: null
  },
  expandedCategories: {
    type: Array,
    default: () => []
  },
  canAddGoods: {
    type: Boolean,
    default: false
  },
  canEditGoods: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['add-category', 'manage-category', 'select-category', 'category-click'])

const handleAddCategory = () => {
  emit('add-category')
}

const handleManageCategory = () => {
  emit('manage-category')
}

const handleCategoryItemClick = (category) => {
  emit('category-click', category)
}

const handleSelectCategory = (categoryId) => {
  emit('select-category', categoryId)
}

const getCategoryTotalGoods = (category) => {
  let total = category.goods_count || 0
  if (category.children && category.children.length > 0) {
    category.children.forEach(child => {
      total += child.goods_count || 0
    })
  }
  return total
}
</script>

<style scoped>
.category-card {
  width: 260px;
  flex-shrink: 0;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.08);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.category-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 14px 16px;
  border-bottom: 1px solid #f0f0f0;
  background: linear-gradient(135deg, #fafbfc 0%, #f5f7fa 100%);
}

.category-title {
  font-size: 15px;
  font-weight: 600;
  color: #303133;
}

.category-actions {
  display: flex;
  gap: 8px;
}

.category-tree-wrapper {
  flex: 1;
  overflow-y: auto;
  padding: 8px 0;
}

.category-tree {
  display: flex;
  flex-direction: column;
}

.category-node {
  position: relative;
}

.category-node.level-1 {
  margin-bottom: 2px;
}

.category-node.level-2 {
  position: relative;
}

.category-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 12px;
  cursor: pointer;
  transition: all 0.2s ease-in-out;
  border-radius: 6px;
  user-select: none;
  position: relative;
}

.category-item:hover {
  background: #f0f5ff;
}

.category-item.active {
  background: #e6f4ff;
  color: #165DFF;
  font-weight: 600;
}

.category-item .tree-line {
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 3px;
  background: transparent;
  border-radius: 3px 0 0 3px;
  transition: background 0.2s;
}

.category-item.active .tree-line {
  background: #165DFF;
}

.category-item .item-content {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1;
}

.category-item .expand-icon {
  font-size: 12px;
  color: #909399;
  transition: transform 0.2s ease-in-out;
  width: 16px;
  flex-shrink: 0;
}

.category-item .expand-icon.expanded {
  transform: rotate(90deg);
  color: #165DFF;
}

.category-item .expand-placeholder {
  width: 16px;
  flex-shrink: 0;
}

.category-item .category-icon {
  font-size: 16px;
  flex-shrink: 0;
}

.category-item .category-icon.folder {
  color: #faad14;
}

.category-item .category-icon.leaf {
  color: #165DFF;
}

.category-item .category-name {
  font-size: 14px;
  color: #303133;
  flex: 1;
}

.category-item.active .category-name {
  color: #165DFF;
  font-weight: 600;
}

.category-item .category-count {
  font-size: 12px;
  color: #909399;
  background: #f0f2f5;
  padding: 2px 8px;
  border-radius: 10px;
  flex-shrink: 0;
}

.category-item.active .category-count {
  background: #d9e8ff;
  color: #165DFF;
}

.children-container {
  position: relative;
  padding-left: 24px;
}

.children-container::before {
  content: '';
  position: absolute;
  left: 18px;
  top: 0;
  bottom: 12px;
  width: 1px;
  background: #d9d9d9;
}

.category-node.level-2 .category-item {
  padding: 8px 12px;
  position: relative;
}

.category-node.level-2 .category-item::before {
  content: '';
  position: absolute;
  left: -6px;
  top: 50%;
  width: 12px;
  height: 1px;
  background: #d9d9d9;
}

.category-node.level-2.last-child .category-item::after {
  content: '';
  position: absolute;
  left: -7px;
  top: 50%;
  bottom: 0;
  width: 3px;
  background: #fff;
}

.category-node.level-2 .line-connector {
  display: none;
}

.category-node.level-2 .category-icon.leaf {
  color: #165DFF;
}
</style>

<template>
  <el-dialog
    :model-value="modelValue"
    @update:model-value="$emit('update:modelValue', $event)"
    title="分类管理"
    width="500px"
    destroy-on-close
  >
    <div class="category-manage">
      <el-tree
        ref="treeRef"
        :data="categoryTreeData"
        :props="{ label: 'name', children: 'children' }"
        node-key="id"
        default-expand-all
        :expand-on-click-node="false"
        draggable
        :allow-drop="allowDrop"
        :allow-drag="allowDrag"
        @node-drop="handleNodeDrop"
      >
        <template #default="{ node, data }">
          <div class="tree-node" @click="handleNodeClick(node, $event)">
            <div class="node-left">
              <span 
                class="expand-trigger" 
                v-if="data.children && data.children.length > 0"
                @click.stop="handleToggleExpand(node)"
              >
                <el-icon :class="{ 'is-expanded': node.expanded }">
                  <ArrowRight />
                </el-icon>
              </span>
              <span class="expand-placeholder" v-else></span>
              <el-icon class="node-icon" :class="{ 'is-folder': data.children && data.children.length > 0 }">
                <Folder v-if="data.children && data.children.length > 0" />
                <Document v-else />
              </el-icon>
              <span class="node-label">{{ node.label }}</span>
            </div>
            <span class="node-actions">
              <el-button type="primary" link size="small" @click.stop="handleEditCategory(data)">编辑</el-button>
              <el-button type="danger" link size="small" @click.stop="handleDeleteCategory(data)">删除</el-button>
            </span>
          </div>
        </template>
      </el-tree>
    </div>
    <template #footer>
      <div class="dialog-footer">
        <el-button type="primary" :icon="Plus" @click="handleAddCategory">新增分类</el-button>
        <el-button @click="$emit('update:modelValue', false)">关闭</el-button>
      </div>
    </template>
  </el-dialog>
  
  <Teleport to="body">
    <el-dialog
      v-model="categoryFormVisible"
      :title="categoryFormTitle"
      width="400px"
      destroy-on-close
      :z-index="3000"
    >
      <el-form :model="categoryForm" label-width="80px">
        <el-form-item label="分类名称" required>
          <el-input v-model="categoryForm.name" placeholder="请输入分类名称" />
        </el-form-item>
        <el-form-item label="上级分类">
          <el-cascader
            v-model="categoryForm.parent_id"
            :options="categoryOptions"
            :props="{ value: 'id', label: 'name', checkStrictly: true, emitPath: false }"
            clearable
            placeholder="选择上级分类（可选）"
            style="width: 100%"
            teleported
            popper-class="category-cascader-popper"
          />
        </el-form-item>
        <el-form-item label="商品数量" v-if="categoryForm.id">
          <div class="goods-count-info">
            <el-tag type="info" size="large">
              已关联商品：<span class="count-number">{{ categoryForm.goods_count || 0 }}</span> 个
            </el-tag>
          </div>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="categoryFormVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSaveCategory" :loading="saveLoading">保存</el-button>
      </template>
    </el-dialog>
  </Teleport>
</template>

<script setup>
import { ref, computed } from 'vue'
import { Plus, Folder, Document, ArrowRight } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { createCategory, updateCategory, deleteCategory, batchUpdateCategorySort } from '@/api/basic'

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  },
  categoryTreeData: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['update:modelValue', 'refresh'])

const treeRef = ref(null)
const categoryFormVisible = ref(false)
const categoryFormTitle = ref('新增分类')
const saveLoading = ref(false)
const categoryForm = ref({
  id: null,
  name: '',
  parent_id: null
})

const categoryOptions = computed(() => {
  return JSON.parse(JSON.stringify(props.categoryTreeData))
})

/**
 * 判断节点是否可拖拽
 */
const allowDrag = (draggingNode) => {
  return true
}

/**
 * 判断节点是否可放置
 */
const allowDrop = (draggingNode, dropNode, type) => {
  if (type === 'inner') {
    return dropNode.data.level < 5
  }
  return true
}

/**
 * 处理节点拖拽完成
 */
const handleNodeDrop = async (draggingNode, dropNode, dropType, ev) => {
  const sortList = []
  
  const collectSortData = (nodes, parentId = null) => {
    nodes.forEach((node, index) => {
      sortList.push({
        id: node.id,
        sort_order: index,
        parent: parentId
      })
      if (node.children && node.children.length > 0) {
        collectSortData(node.children, node.id)
      }
    })
  }
  
  collectSortData(props.categoryTreeData)
  
  try {
    await batchUpdateCategorySort({ sort_list: sortList })
    ElMessage.success('排序已更新')
    emit('refresh')
  } catch (error) {
    ElMessage.error('排序更新失败：' + (error.response?.data?.msg || error.message || '未知错误'))
    emit('refresh')
  }
}

/**
 * 处理节点点击（切换展开/折叠）
 */
const handleNodeClick = (node, event) => {
  if (node.data.children && node.data.children.length > 0) {
    node.expanded = !node.expanded
  }
}

/**
 * 处理展开/折叠按钮点击
 */
const handleToggleExpand = (node) => {
  node.expanded = !node.expanded
}

const handleAddCategory = () => {
  categoryFormTitle.value = '新增分类'
  categoryForm.value = {
    id: null,
    name: '',
    parent_id: null
  }
  categoryFormVisible.value = true
}

const handleEditCategory = (data) => {
  categoryFormTitle.value = '编辑分类'
  categoryForm.value = {
    id: data.id,
    name: data.name,
    parent_id: data.parent || null,
    goods_count: data.goods_count || 0
  }
  categoryFormVisible.value = true
}

const handleDeleteCategory = async (data) => {
  try {
    await ElMessageBox.confirm(`确定删除分类「${data.name}」？`, '提示', { type: 'warning' })
    await deleteCategory(data.id)
    ElMessage.success('删除成功')
    emit('refresh')
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error(error.response?.data?.message || '删除失败')
    }
  }
}

const handleSaveCategory = async () => {
  if (!categoryForm.value.name.trim()) {
    ElMessage.warning('请输入分类名称')
    return
  }
  
  saveLoading.value = true
  try {
    const data = {
      name: categoryForm.value.name,
      parent: categoryForm.value.parent_id || null
    }
    
    if (categoryForm.value.id) {
      await updateCategory(categoryForm.value.id, data)
      ElMessage.success('更新成功')
    } else {
      await createCategory(data)
      ElMessage.success('创建成功')
    }
    
    categoryFormVisible.value = false
    emit('refresh')
  } catch (error) {
    ElMessage.error(error.response?.data?.message || '保存失败')
  } finally {
    saveLoading.value = false
  }
}
</script>

<style scoped>
.category-manage {
  max-height: 400px;
  overflow-y: auto;
}

.tree-node {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 4px 8px;
  margin: 2px 0;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.tree-node:hover {
  background-color: #f5f7fa;
}

.node-left {
  display: flex;
  align-items: center;
  gap: 6px;
}

.expand-trigger {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  margin-left: -4px;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.expand-trigger:hover {
  background-color: #e4e7ed;
}

.expand-trigger .el-icon {
  font-size: 12px;
  color: #909399;
  transition: transform 0.2s ease-in-out;
}

.expand-trigger .el-icon.is-expanded {
  transform: rotate(90deg);
  color: #409eff;
}

.expand-placeholder {
  width: 20px;
}

.node-icon {
  font-size: 16px;
  color: #909399;
}

.node-icon.is-folder {
  color: #faad14;
}

.node-label {
  font-size: 14px;
  color: #303133;
}

.node-actions {
  opacity: 0;
  transition: opacity 0.2s;
}

.tree-node:hover .node-actions {
  opacity: 1;
}

.goods-count-info {
  display: flex;
  align-items: center;
}

.count-number {
  font-size: 16px;
  font-weight: 600;
  color: #409eff;
  margin: 0 4px;
}

.dialog-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>

<style>
.category-cascader-popper {
  z-index: 4000 !important;
}

.category-manage .el-tree-node__expand-icon {
  display: none !important;
}
</style>

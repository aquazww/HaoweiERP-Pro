<template>
  <el-dialog
    :model-value="modelValue"
    @update:model-value="$emit('update:modelValue', $event)"
    title="分类管理"
    width="500px"
    destroy-on-close
  >
    <div class="category-manage">
      <div class="category-toolbar">
        <el-button type="primary" size="small" :icon="Plus" @click="handleAddCategory">新增分类</el-button>
      </div>
      
      <el-tree
        ref="treeRef"
        :data="categoryTreeData"
        :props="{ label: 'name', children: 'children' }"
        node-key="id"
        default-expand-all
        :expand-on-click-node="false"
      >
        <template #default="{ node, data }">
          <div class="tree-node">
            <span class="node-label">{{ node.label }}</span>
            <span class="node-actions">
              <el-button type="primary" link size="small" @click.stop="handleEditCategory(data)">编辑</el-button>
              <el-button type="danger" link size="small" @click.stop="handleDeleteCategory(data)">删除</el-button>
            </span>
          </div>
        </template>
      </el-tree>
    </div>
    
    <el-dialog
      v-model="categoryFormVisible"
      :title="categoryFormTitle"
      width="400px"
      append-to-body
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
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="categoryFormVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSaveCategory" :loading="saveLoading">保存</el-button>
      </template>
    </el-dialog>
  </el-dialog>
</template>

<script setup>
import { ref, computed } from 'vue'
import { Plus } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getCategories, createCategory, updateCategory, deleteCategory } from '@/api/basic'

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
  const options = structuredClone(props.categoryTreeData)
  return options
})

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
    parent_id: data.parent_id || null
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
      parent_id: categoryForm.value.parent_id || null
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

.category-toolbar {
  margin-bottom: 12px;
}

.tree-node {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-right: 8px;
}

.node-label {
  font-size: 14px;
}

.node-actions {
  opacity: 0;
  transition: opacity 0.2s;
}

.tree-node:hover .node-actions {
  opacity: 1;
}
</style>

<template>
  <div class="params-page">
    <div class="page-content">
      <div class="table-card">
        <el-tabs v-model="activeTab" class="params-tabs">
          <el-tab-pane label="计量单位" name="units">
            <div class="tab-header">
              <div class="search-box">
                <el-input v-model="unitSearch" placeholder="搜索单位名称" clearable @keyup.enter="loadUnits" style="width: 200px" />
              </div>
              <el-button type="primary" :icon="Plus" @click="handleAddUnit">新增单位</el-button>
            </div>
            <el-table :data="unitList" v-loading="unitLoading" style="width: 100%;" class="data-table" stripe>
              <el-table-column type="index" label="#" width="60" align="center" />
              <el-table-column prop="name" label="单位名称" min-width="200" />
              <el-table-column label="状态" width="100">
                <template #default="{ row }">
                  <el-tag :type="row.is_active ? 'success' : 'info'" size="small">{{ row.is_active ? '启用' : '禁用' }}</el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="created_at" label="创建时间" width="180">
                <template #default="{ row }">{{ formatDateTime(row.created_at) }}</template>
              </el-table-column>
              <el-table-column label="操作" width="150" fixed="right">
                <template #default="{ row }">
                  <el-button type="primary" link size="small" @click="handleEditUnit(row)">编辑</el-button>
                  <el-button type="danger" link size="small" @click="handleDeleteUnit(row)">删除</el-button>
                </template>
              </el-table-column>
            </el-table>
          </el-tab-pane>

          <el-tab-pane label="仓库信息" name="warehouses">
            <div class="tab-header">
              <div class="search-box">
                <el-input v-model="warehouseSearch" placeholder="搜索仓库名称" clearable @keyup.enter="loadWarehouses" style="width: 200px" />
              </div>
              <el-button type="primary" :icon="Plus" @click="handleAddWarehouse">新增仓库</el-button>
            </div>
            <el-table :data="warehouseList" v-loading="warehouseLoading" style="width: 100%;" class="data-table" stripe>
              <el-table-column type="index" label="#" width="60" align="center" />
              <el-table-column prop="name" label="仓库名称" min-width="150" />
              <el-table-column prop="address" label="仓库地址" min-width="200" />
              <el-table-column prop="contact" label="联系人" width="120" />
              <el-table-column prop="phone" label="联系电话" width="140" />
              <el-table-column label="状态" width="100">
                <template #default="{ row }">
                  <el-tag :type="row.is_active ? 'success' : 'info'" size="small">{{ row.is_active ? '启用' : '禁用' }}</el-tag>
                </template>
              </el-table-column>
              <el-table-column label="操作" width="150" fixed="right">
                <template #default="{ row }">
                  <el-button type="primary" link size="small" @click="handleEditWarehouse(row)">编辑</el-button>
                  <el-button type="danger" link size="small" @click="handleDeleteWarehouse(row)">删除</el-button>
                </template>
              </el-table-column>
            </el-table>
          </el-tab-pane>

          <el-tab-pane label="商品分类" name="categories">
            <div class="tab-header">
              <div class="search-box">
                <el-input v-model="categorySearch" placeholder="搜索分类名称" clearable @keyup.enter="loadCategories" style="width: 200px" />
              </div>
              <el-button type="primary" :icon="Plus" @click="handleAddCategory">新增分类</el-button>
            </div>
            <el-table :data="categoryList" v-loading="categoryLoading" style="width: 100%;" class="data-table" stripe row-key="id" default-expand-all>
              <el-table-column type="index" label="#" width="60" align="center" />
              <el-table-column prop="name" label="分类名称" min-width="180" />
              <el-table-column label="父分类" width="120">
                <template #default="{ row }">
                  <span v-if="row.parent_name">{{ row.parent_name }}</span>
                  <span v-else class="text-muted">顶级分类</span>
                </template>
              </el-table-column>
              <el-table-column prop="sort_order" label="排序" width="80" align="center" />
              <el-table-column label="状态" width="80" align="center">
                <template #default="{ row }">
                  <el-tag :type="row.is_active ? 'success' : 'info'" size="small">{{ row.is_active ? '启用' : '禁用' }}</el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="created_at" label="创建时间" width="160">
                <template #default="{ row }">{{ formatDateTime(row.created_at) }}</template>
              </el-table-column>
              <el-table-column label="操作" width="140" fixed="right">
                <template #default="{ row }">
                  <el-button type="primary" link size="small" @click="handleEditCategory(row)">编辑</el-button>
                  <el-button type="danger" link size="small" @click="handleDeleteCategory(row)">删除</el-button>
                </template>
              </el-table-column>
            </el-table>
          </el-tab-pane>
        </el-tabs>
      </div>
    </div>

    <!-- 计量单位弹窗 -->
    <el-dialog v-model="unitDialogVisible" :title="unitDialogTitle" width="400px" class="form-dialog" destroy-on-close>
      <el-form :model="unitForm" :rules="unitRules" ref="unitFormRef" label-width="100px">
        <el-form-item label="单位名称" prop="name">
          <el-input v-model="unitForm.name" placeholder="请输入单位名称" maxlength="50" />
        </el-form-item>
        <el-form-item label="状态">
          <el-switch v-model="unitForm.is_active" active-text="启用" inactive-text="禁用" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="unitDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleUnitSubmit" :loading="unitSubmitLoading">确定</el-button>
      </template>
    </el-dialog>

    <!-- 仓库弹窗 -->
    <el-dialog v-model="warehouseDialogVisible" :title="warehouseDialogTitle" width="500px" class="form-dialog" destroy-on-close>
      <el-form :model="warehouseForm" :rules="warehouseRules" ref="warehouseFormRef" label-width="100px">
        <el-form-item label="仓库名称" prop="name">
          <el-input v-model="warehouseForm.name" placeholder="请输入仓库名称" maxlength="100" />
        </el-form-item>
        <el-form-item label="仓库地址">
          <el-input v-model="warehouseForm.address" placeholder="请输入仓库地址" maxlength="200" />
        </el-form-item>
        <el-form-item label="联系人">
          <el-input v-model="warehouseForm.contact" placeholder="请输入联系人" maxlength="50" />
        </el-form-item>
        <el-form-item label="联系电话">
          <el-input v-model="warehouseForm.phone" placeholder="请输入联系电话" maxlength="20" />
        </el-form-item>
        <el-form-item label="状态">
          <el-switch v-model="warehouseForm.is_active" active-text="启用" inactive-text="禁用" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="warehouseDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleWarehouseSubmit" :loading="warehouseSubmitLoading">确定</el-button>
      </template>
    </el-dialog>

    <!-- 商品分类弹窗 -->
    <el-dialog v-model="categoryDialogVisible" :title="categoryDialogTitle" width="450px" class="form-dialog" destroy-on-close>
      <el-form :model="categoryForm" :rules="categoryRules" ref="categoryFormRef" label-width="100px">
        <el-form-item label="分类名称" prop="name">
          <el-input v-model="categoryForm.name" placeholder="请输入分类名称" maxlength="100" />
        </el-form-item>
        <el-form-item label="父分类">
          <el-tree-select
            v-model="categoryForm.parent"
            :data="categoryTreeData"
            :props="{ label: 'name', value: 'id', children: 'children' }"
            placeholder="请选择父分类（可选）"
            clearable
            check-strictly
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="排序">
          <el-input-number v-model="categoryForm.sort_order" :min="0" :max="9999" style="width: 100%" />
        </el-form-item>
        <el-form-item label="状态">
          <el-switch v-model="categoryForm.is_active" active-text="启用" inactive-text="禁用" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="categoryDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleCategorySubmit" :loading="categorySubmitLoading">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { getUnits, createUnit, updateUnit, deleteUnit, getWarehouses, createWarehouse, updateWarehouse, deleteWarehouse, getCategories, createCategory, updateCategory, deleteCategory } from '../../api/basic'

const parseErrorMessage = (error) => {
  const errorData = error.response?.data
  if (!errorData) return error.message || '网络错误，请稍后重试'
  
  if (errorData.msg && typeof errorData.msg === 'string') {
    return errorData.msg
  }
  
  if (typeof errorData === 'object') {
    const messages = []
    for (const [field, msg] of Object.entries(errorData)) {
      if (field === 'msg' || field === 'code' || field === 'data') continue
      
      let message = ''
      if (Array.isArray(msg)) {
        message = msg.map(item => {
          if (typeof item === 'object' && item.string) {
            return item.string
          }
          return String(item)
        }).join('；')
      } else if (typeof msg === 'object' && msg.string) {
        message = msg.string
      } else if (typeof msg === 'string') {
        message = msg
      }
      
      if (message) {
        messages.push(message)
      }
    }
    
    if (messages.length > 0) {
      return messages.join('；')
    }
  }
  
  return '操作失败，请稍后重试'
}

const activeTab = ref('units')

const formatDateTime = (datetime) => {
  if (!datetime) return '-'
  return datetime.replace('T', ' ').substring(0, 19)
}

// 计量单位
const unitList = ref([])
const unitLoading = ref(false)
const unitSearch = ref('')
const unitDialogVisible = ref(false)
const unitDialogTitle = ref('')
const unitFormRef = ref(null)
const unitSubmitLoading = ref(false)
const unitEditingId = ref(null)
const unitForm = ref({ name: '', is_active: true })
const unitRules = { name: [{ required: true, message: '请输入单位名称', trigger: 'blur' }] }

const loadUnits = async () => {
  unitLoading.value = true
  try {
    const params = { page_size: 1000 }
    if (unitSearch.value) params.search = unitSearch.value
    const res = await getUnits(params)
    unitList.value = res.data.items || res.data.results || []
  } catch (error) {
    ElMessage.error('加载计量单位失败')
  } finally {
    unitLoading.value = false
  }
}

const handleAddUnit = () => {
  unitDialogTitle.value = '新增计量单位'
  unitEditingId.value = null
  unitForm.value = { name: '', is_active: true }
  unitDialogVisible.value = true
}

const handleEditUnit = (row) => {
  unitDialogTitle.value = '编辑计量单位'
  unitEditingId.value = row.id
  unitForm.value = { name: row.name, is_active: row.is_active }
  unitDialogVisible.value = true
}

const handleDeleteUnit = async (row) => {
  try {
    await ElMessageBox.confirm(`确定删除计量单位「${row.name}」？`, '确认删除', { type: 'warning' })
    await deleteUnit(row.id)
    ElMessage.success('删除成功')
    loadUnits()
  } catch (error) {
    if (error === 'cancel') return
    const errorData = error.response?.data
    if (errorData?.data?.goods_list) {
      const goodsList = errorData.data.goods_list
      const suggestion = errorData.data.suggestion || ''
      ElMessageBox.alert(
        `<div style="line-height: 1.8;">
          <p style="margin-bottom: 12px; color: #303133;"><strong>${errorData.msg}</strong></p>
          <p style="margin-bottom: 8px; color: #606266;">关联商品：</p>
          <ul style="margin: 0 0 12px 20px; padding: 0; color: #909399;">
            ${goodsList.map(g => `<li>${g}</li>`).join('')}
          </ul>
          <p style="color: #E6A23C; font-size: 13px;">${suggestion}</p>
        </div>`,
        '删除失败',
        {
          dangerouslyUseHTMLString: true,
          confirmButtonText: '我知道了',
          type: 'warning'
        }
      )
    } else if (errorData?.msg) {
      ElMessage.error(errorData.msg)
    } else {
      ElMessage.error('删除失败：' + (error.message || '网络错误，请稍后重试'))
    }
  }
}

const handleUnitSubmit = async () => {
  try { await unitFormRef.value.validate() } catch { return }
  unitSubmitLoading.value = true
  try {
    if (unitEditingId.value) {
      await updateUnit(unitEditingId.value, unitForm.value)
      ElMessage.success('更新成功')
    } else {
      await createUnit(unitForm.value)
      ElMessage.success('创建成功')
    }
    unitDialogVisible.value = false
    loadUnits()
  } catch (error) {
    ElMessage.error(parseErrorMessage(error))
  } finally {
    unitSubmitLoading.value = false
  }
}

// 仓库信息
const warehouseList = ref([])
const warehouseLoading = ref(false)
const warehouseSearch = ref('')
const warehouseDialogVisible = ref(false)
const warehouseDialogTitle = ref('')
const warehouseFormRef = ref(null)
const warehouseSubmitLoading = ref(false)
const warehouseEditingId = ref(null)
const warehouseForm = ref({ name: '', address: '', contact: '', phone: '', is_active: true })
const warehouseRules = { name: [{ required: true, message: '请输入仓库名称', trigger: 'blur' }] }

const loadWarehouses = async () => {
  warehouseLoading.value = true
  try {
    const params = { page_size: 1000 }
    if (warehouseSearch.value) params.search = warehouseSearch.value
    const res = await getWarehouses(params)
    warehouseList.value = res.data.items || res.data.results || []
  } catch (error) {
    ElMessage.error('加载仓库信息失败')
  } finally {
    warehouseLoading.value = false
  }
}

const handleAddWarehouse = () => {
  warehouseDialogTitle.value = '新增仓库'
  warehouseEditingId.value = null
  warehouseForm.value = { name: '', address: '', contact: '', phone: '', is_active: true }
  warehouseDialogVisible.value = true
}

const handleEditWarehouse = (row) => {
  warehouseDialogTitle.value = '编辑仓库'
  warehouseEditingId.value = row.id
  warehouseForm.value = { name: row.name, address: row.address || '', contact: row.contact || '', phone: row.phone || '', is_active: row.is_active }
  warehouseDialogVisible.value = true
}

const handleDeleteWarehouse = async (row) => {
  try {
    await ElMessageBox.confirm(`确定删除仓库「${row.name}」？`, '确认删除', { type: 'warning' })
    await deleteWarehouse(row.id)
    ElMessage.success('删除成功')
    loadWarehouses()
  } catch (error) {
    if (error === 'cancel') return
    const errorData = error.response?.data
    if (errorData?.data?.goods_list) {
      const goodsList = errorData.data.goods_list
      const suggestion = errorData.data.suggestion || ''
      ElMessageBox.alert(
        `<div style="line-height: 1.8;">
          <p style="margin-bottom: 12px; color: #303133;"><strong>${errorData.msg}</strong></p>
          <p style="margin-bottom: 8px; color: #606266;">库存记录：</p>
          <ul style="margin: 0 0 12px 20px; padding: 0; color: #909399;">
            ${goodsList.map(g => `<li>${g}</li>`).join('')}
          </ul>
          <p style="color: #E6A23C; font-size: 13px;">${suggestion}</p>
        </div>`,
        '删除失败',
        {
          dangerouslyUseHTMLString: true,
          confirmButtonText: '我知道了',
          type: 'warning'
        }
      )
    } else if (errorData?.msg) {
      ElMessage.error(errorData.msg)
    } else {
      ElMessage.error('删除失败：' + (error.message || '网络错误，请稍后重试'))
    }
  }
}

const handleWarehouseSubmit = async () => {
  try { await warehouseFormRef.value.validate() } catch { return }
  warehouseSubmitLoading.value = true
  try {
    if (warehouseEditingId.value) {
      await updateWarehouse(warehouseEditingId.value, warehouseForm.value)
      ElMessage.success('更新成功')
    } else {
      await createWarehouse(warehouseForm.value)
      ElMessage.success('创建成功')
    }
    warehouseDialogVisible.value = false
    loadWarehouses()
  } catch (error) {
    ElMessage.error(parseErrorMessage(error))
  } finally {
    warehouseSubmitLoading.value = false
  }
}

// 商品分类
const categoryList = ref([])
const categoryLoading = ref(false)
const categorySearch = ref('')
const categoryDialogVisible = ref(false)
const categoryDialogTitle = ref('')
const categoryFormRef = ref(null)
const categorySubmitLoading = ref(false)
const categoryEditingId = ref(null)
const categoryForm = ref({ name: '', parent: null, sort_order: 0, is_active: true })
const categoryRules = { name: [{ required: true, message: '请输入分类名称', trigger: 'blur' }] }

const categoryTreeData = computed(() => {
  const buildTree = (items, parentId = null) => {
    return items
      .filter(item => item.parent === parentId)
      .map(item => ({
        ...item,
        children: buildTree(items, item.id)
      }))
  }
  return buildTree(categoryList.value)
})

const loadCategories = async () => {
  categoryLoading.value = true
  try {
    const params = { page_size: 1000 }
    if (categorySearch.value) params.search = categorySearch.value
    const res = await getCategories(params)
    categoryList.value = res.data.items || res.data.results || []
  } catch (error) {
    ElMessage.error('加载商品分类失败')
  } finally {
    categoryLoading.value = false
  }
}

const handleAddCategory = () => {
  categoryDialogTitle.value = '新增商品分类'
  categoryEditingId.value = null
  categoryForm.value = { name: '', parent: null, sort_order: 0, is_active: true }
  categoryDialogVisible.value = true
}

const handleEditCategory = (row) => {
  categoryDialogTitle.value = '编辑商品分类'
  categoryEditingId.value = row.id
  categoryForm.value = { 
    name: row.name, 
    parent: row.parent || null, 
    sort_order: row.sort_order || 0, 
    is_active: row.is_active 
  }
  categoryDialogVisible.value = true
}

const handleDeleteCategory = async (row) => {
  const hasChildren = categoryList.value.some(item => item.parent === row.id)
  if (hasChildren) {
    ElMessage.warning('该分类下有子分类，请先删除子分类')
    return
  }
  try {
    await ElMessageBox.confirm(`确定删除商品分类「${row.name}」？`, '确认删除', { type: 'warning' })
    await deleteCategory(row.id)
    ElMessage.success('删除成功')
    loadCategories()
  } catch (error) {
    if (error === 'cancel') return
    const errorData = error.response?.data
    if (errorData?.data?.goods_list) {
      const goodsList = errorData.data.goods_list
      const suggestion = errorData.data.suggestion || ''
      ElMessageBox.alert(
        `<div style="line-height: 1.8;">
          <p style="margin-bottom: 12px; color: #303133;"><strong>${errorData.msg}</strong></p>
          <p style="margin-bottom: 8px; color: #606266;">关联商品：</p>
          <ul style="margin: 0 0 12px 20px; padding: 0; color: #909399;">
            ${goodsList.map(g => `<li>${g}</li>`).join('')}
          </ul>
          <p style="color: #E6A23C; font-size: 13px;">${suggestion}</p>
        </div>`,
        '删除失败',
        {
          dangerouslyUseHTMLString: true,
          confirmButtonText: '我知道了',
          type: 'warning'
        }
      )
    } else if (errorData?.msg) {
      ElMessage.error(errorData.msg)
    } else {
      ElMessage.error('删除失败：' + (error.message || '网络错误，请稍后重试'))
    }
  }
}

const handleCategorySubmit = async () => {
  try { await categoryFormRef.value.validate() } catch { return }
  categorySubmitLoading.value = true
  try {
    const submitData = {
      name: categoryForm.value.name,
      parent: categoryForm.value.parent || null,
      sort_order: categoryForm.value.sort_order,
      is_active: categoryForm.value.is_active
    }
    if (categoryEditingId.value) {
      await updateCategory(categoryEditingId.value, submitData)
      ElMessage.success('更新成功')
    } else {
      await createCategory(submitData)
      ElMessage.success('创建成功')
    }
    categoryDialogVisible.value = false
    loadCategories()
  } catch (error) {
    const errorData = error.response?.data
    if (errorData && typeof errorData === 'object' && !errorData.msg) {
      const fieldNames = {
        'name': '分类名称',
        'parent': '父分类',
        'sort_order': '排序',
        'is_active': '状态'
      }
      const errorMessages = Object.entries(errorData)
        .map(([field, msg]) => {
          let message = ''
          if (Array.isArray(msg)) {
            message = msg.map(item => {
              if (typeof item === 'object' && item.string) {
                return item.string
              }
              return String(item)
            }).join('；')
          } else if (typeof msg === 'object' && msg.string) {
            message = msg.string
          } else {
            message = String(msg)
          }
          const fieldName = fieldNames[field] || field
          return `${fieldName}：${message}`
        })
        .join('；')
      ElMessage.error(errorMessages || '操作失败，请检查输入内容')
    } else if (errorData?.msg) {
      ElMessage.error(errorData.msg)
    } else {
      ElMessage.error('操作失败：' + (error.message || '网络错误，请稍后重试'))
    }
  } finally {
    categorySubmitLoading.value = false
  }
}

onMounted(() => {
  loadUnits()
  loadWarehouses()
  loadCategories()
})
</script>

<style scoped>
.params-page {
  height: 100%;
  width: 100%;
  display: flex;
  flex-direction: column;
  padding: 8px;
  overflow: hidden;
}

.page-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  width: 100%;
}

.table-card {
  flex: 1;
  display: flex;
  flex-direction: column;
  background-color: var(--color-white);
  border-radius: var(--border-radius-lg);
  border: 1px solid var(--color-border-light);
  box-shadow: var(--shadow-sm);
  overflow: hidden;
  min-height: 0;
}

.params-tabs {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.params-tabs :deep(.el-tabs__header) {
  margin: 0;
  padding: 0 var(--spacing-lg);
  background-color: var(--color-bg-light);
}

.params-tabs :deep(.el-tabs__content) {
  flex: 1;
  overflow: auto;
  padding: var(--spacing-lg);
}

.tab-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-md);
}

.search-box {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
}

.data-table {
  --el-table-header-bg-color: var(--color-bg-light);
}

.form-dialog :deep(.el-dialog__header) {
  border-bottom: 1px solid var(--color-border-light);
  padding: var(--spacing-lg) var(--spacing-xl);
}

.form-dialog :deep(.el-dialog__body) {
  padding: var(--spacing-xl);
}

.form-dialog :deep(.el-dialog__footer) {
  border-top: 1px solid var(--color-border-light);
  padding: var(--spacing-lg) var(--spacing-xl);
}

.text-muted {
  color: var(--color-text-placeholder, #9ca3af);
  font-style: italic;
}
</style>

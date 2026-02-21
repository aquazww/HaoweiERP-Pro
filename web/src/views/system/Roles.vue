<template>
  <div class="roles-page">
    <div class="page-content">
      <div class="toolbar-card">
        <div class="toolbar-left">
          <div class="search-box">
            <el-icon class="search-icon"><Search /></el-icon>
            <el-input
              v-model="searchKeyword"
              placeholder="搜索角色名称"
              class="search-input"
              clearable
              @keyup.enter="loadData"
            />
          </div>
        </div>
        <div class="toolbar-right">
          <el-button :icon="Refresh" @click="loadData">刷新</el-button>
          <el-button type="primary" :icon="Plus" @click="handleAdd">新增角色</el-button>
        </div>
      </div>

      <div class="table-card">
        <el-table 
          :data="tableData" 
          style="width: 100%" 
          v-loading="loading"
          class="data-table"
          stripe
          :height="tableHeight"
        >
          <el-table-column type="index" label="#" width="60" align="center" />
          <el-table-column prop="name" label="角色名称" width="200" />
          <el-table-column prop="description" label="描述" />
          <el-table-column label="创建时间" width="160">
            <template #default="{ row }">{{ formatDateTime(row.created_at) }}</template>
          </el-table-column>
          <el-table-column label="操作" width="140" align="center">
            <template #default="{ row }">
              <div class="action-buttons">
                <el-button type="primary" link :icon="Edit" size="small" @click="handleEdit(row)">编辑</el-button>
                <el-button type="danger" link :icon="Delete" size="small" @click="handleDelete(row)">删除</el-button>
              </div>
            </template>
          </el-table-column>
        </el-table>
        <div class="pagination-wrapper">
          <el-pagination
            v-model:current-page="pagination.page"
            v-model:page-size="pagination.pageSize"
            :page-sizes="[10, 20, 50, 100]"
            :total="pagination.total"
            layout="total, sizes, prev, pager, next, jumper"
            @size-change="loadData"
            @current-change="loadData"
          />
        </div>
      </div>
    </div>

    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="600px">
      <el-form :model="form" :rules="rules" ref="formRef" label-width="100px">
        <el-form-item label="角色名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入角色名称" />
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input v-model="form.description" type="textarea" placeholder="请输入描述" :rows="3" />
        </el-form-item>
        <el-form-item label="权限配置" prop="permissions">
          <el-checkbox-group v-model="permissionsList">
            <el-checkbox label="basic">基础资料</el-checkbox>
            <el-checkbox label="purchase">采购管理</el-checkbox>
            <el-checkbox label="sale">销售管理</el-checkbox>
            <el-checkbox label="inventory">库存管理</el-checkbox>
            <el-checkbox label="finance">财务管理</el-checkbox>
            <el-checkbox label="reports">报表中心</el-checkbox>
            <el-checkbox label="system">系统管理</el-checkbox>
          </el-checkbox-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick, onUnmounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Refresh, Plus, Edit, Delete } from '@element-plus/icons-vue'
import { getRoles, createRole, updateRole, deleteRole } from '../../api/system'

const loading = ref(false)
const tableData = ref([])
const formRef = ref(null)
const dialogVisible = ref(false)
const dialogTitle = ref('')
const editingId = ref(null)
const searchKeyword = ref('')
const tableHeight = ref(0)

const permissionsList = ref([])

const form = ref({
  name: '',
  description: '',
  permissions: {}
})

const rules = {
  name: [{ required: true, message: '请输入角色名称', trigger: 'blur' }]
}

const pagination = ref({
  page: 1,
  pageSize: 20,
  total: 0
})

/**
 * 格式化日期时间，移除时区信息
 */
const formatDateTime = (datetime) => {
  if (!datetime) return '-'
  
  const date = new Date(datetime)
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  const hours = String(date.getHours()).padStart(2, '0')
  const minutes = String(date.getMinutes()).padStart(2, '0')
  const seconds = String(date.getSeconds()).padStart(2, '0')
  
  return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`
}

const calculateTableHeight = () => {
  nextTick(() => {
    const toolbarCard = document.querySelector('.toolbar-card')
    const paginationWrapper = document.querySelector('.pagination-wrapper')
    const pageContent = document.querySelector('.page-content')
    
    if (pageContent) {
      let usedHeight = 0
      if (toolbarCard) usedHeight += toolbarCard.offsetHeight + 4
      if (paginationWrapper) usedHeight += paginationWrapper.offsetHeight + 2
      usedHeight += 4
      
      const availableHeight = window.innerHeight - 64 - 16
      tableHeight.value = Math.max(availableHeight - usedHeight, 150)
    }
  })
}

const loadData = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.value.page,
      page_size: pagination.value.pageSize
    }
    if (searchKeyword.value) {
      params.search = searchKeyword.value
    }
    const res = await getRoles(params)
    tableData.value = res.data.results || res.data.items || []
    pagination.value.total = res.data.count || 0
  } catch (error) {
    tableData.value = []
    pagination.value.total = 0
    ElMessage.error('加载数据失败：' + (error.message || '未知错误'))
  } finally {
    loading.value = false
  }
}

const handleAdd = () => {
  dialogTitle.value = '新增角色'
  editingId.value = null
  form.value = { name: '', description: '', permissions: {} }
  permissionsList.value = []
  dialogVisible.value = true
}

const handleEdit = (row) => {
  dialogTitle.value = '编辑角色'
  editingId.value = row.id
  form.value = { ...row }
  permissionsList.value = Object.keys(row.permissions || {}).filter(key => row.permissions[key])
  dialogVisible.value = true
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm('确定要删除该角色吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await deleteRole(row.id)
    ElMessage.success('删除成功')
    loadData()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const handleSubmit = async () => {
  await formRef.value.validate()
  
  const permissions = {}
  permissionsList.value.forEach(key => {
    permissions[key] = true
  })
  
  try {
    if (editingId.value) {
      await updateRole(editingId.value, { ...form.value, permissions })
      ElMessage.success('更新成功')
    } else {
      await createRole({ ...form.value, permissions })
      ElMessage.success('创建成功')
    }
    dialogVisible.value = false
    loadData()
  } catch (error) {
    ElMessage.error('操作失败')
  }
}

onMounted(() => {
  loadData()
  calculateTableHeight()
  window.addEventListener('resize', calculateTableHeight)
})

onUnmounted(() => {
  window.removeEventListener('resize', calculateTableHeight)
})
</script>

<style scoped>
.roles-page {
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
  gap: 8px;
  overflow: hidden;
  width: 100%;
}

.toolbar-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background-color: var(--color-white);
  padding: 6px var(--spacing-md);
  border-radius: var(--border-radius-lg);
  border: 1px solid var(--color-border-light);
  box-shadow: var(--shadow-sm);
  flex-shrink: 0;
}

.toolbar-left,
.toolbar-right {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
}

.search-box {
  position: relative;
  display: flex;
  align-items: center;
}

.search-icon {
  position: absolute;
  left: var(--spacing-md);
  color: var(--color-text-tertiary);
  z-index: 1;
}

.search-input {
  width: 320px;
  padding-left: 40px;
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

.data-table {
  --el-table-header-bg-color: var(--color-bg-light);
}

.action-buttons {
  display: flex;
  align-items: center;
  gap: var(--spacing-xs);
}

.pagination-wrapper {
  display: flex;
  justify-content: flex-end;
  background-color: var(--color-white);
  border-top: 1px solid var(--color-border-light);
  padding: 4px var(--spacing-md);
  border-radius: 0 0 var(--border-radius-lg) var(--border-radius-lg);
  flex-shrink: 0;
}

.pagination-wrapper :deep(.el-pagination) {
  --el-pagination-button-height: 32px;
  --el-pagination-font-size: 13px;
}

.pagination-wrapper :deep(.el-pagination .btn-prev),
.pagination-wrapper :deep(.el-pagination .btn-next) {
  min-width: 32px;
  padding: 0 8px;
}

.pagination-wrapper :deep(.el-pagination .el-pager li) {
  min-width: 32px;
  height: 32px;
  line-height: 32px;
}

.pagination-wrapper :deep(.el-pagination .el-pagination__sizes) {
  margin-right: 8px;
}

.pagination-wrapper :deep(.el-pagination .el-pagination__jump) {
  margin-left: 8px;
}
</style>

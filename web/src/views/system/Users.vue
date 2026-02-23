<template>
  <div class="users-page">
    <div class="page-content">
      <div class="toolbar-card">
        <div class="toolbar-left">
          <div class="search-box">
            <el-icon class="search-icon"><Search /></el-icon>
            <el-input
              v-model="searchKeyword"
              placeholder="搜索用户名、手机号"
              class="search-input"
              clearable
              @keyup.enter="loadData"
            />
          </div>
          <el-select v-model="statusFilter" placeholder="状态筛选" clearable style="width: 120px" @change="loadData">
            <el-option label="全部" :value="''" />
            <el-option label="启用" :value="true" />
            <el-option label="禁用" :value="false" />
          </el-select>
        </div>
        <div class="toolbar-right">
          <el-button :icon="Refresh" @click="loadData">刷新</el-button>
          <el-button type="primary" :icon="Plus" @click="handleAdd" v-if="canAddUser">新增用户</el-button>
        </div>
      </div>

      <div class="table-card">
        <el-table 
          :data="tableData" 
          style="width: 100%" 
          v-loading="loading"
          class="data-table"
          :height="tableHeight"
          stripe
        >
          <el-table-column prop="username" label="用户名" min-width="120">
            <template #default="{ row }">
              <div class="user-info">
                <el-avatar :size="32" class="user-avatar">{{ (row.name || row.username)?.charAt(0)?.toUpperCase() }}</el-avatar>
                <div class="user-detail">
                  <span class="username">{{ row.username }}</span>
                  <span class="name" v-if="row.name">{{ row.name }}</span>
                </div>
              </div>
            </template>
          </el-table-column>
          <el-table-column prop="phone" label="手机号" min-width="130">
            <template #default="{ row }">{{ row.phone || '-' }}</template>
          </el-table-column>
          <el-table-column label="权限" min-width="150">
            <template #default="{ row }">
              <div class="permission-tags">
                <el-tag 
                  v-for="(perm, key) in getPermissionSummary(row.permissions)" 
                  :key="key"
                  size="small"
                  type="info"
                  class="perm-tag"
                >
                  {{ perm }}
                </el-tag>
                <span v-if="!hasAnyPermission(row.permissions)" class="text-muted">未配置</span>
              </div>
            </template>
          </el-table-column>
          <el-table-column label="状态" width="100" align="center">
            <template #default="{ row }">
              <el-switch
                v-model="row.is_active"
                active-color="#165DFF"
                inactive-color="#9ca3af"
                :loading="toggleLoading === row.id"
                @change="handleToggleStatus(row)"
                :disabled="row.username === 'admin'"
              />
            </template>
          </el-table-column>
          <el-table-column prop="created_at" label="创建时间" width="180">
            <template #default="{ row }">{{ formatDateTime(row.created_at) }}</template>
          </el-table-column>
          <el-table-column label="操作" width="220" fixed="right" align="center">
            <template #default="{ row }">
              <div class="action-buttons">
                <el-button type="primary" link :icon="Edit" size="small" @click="handleEdit(row)" v-if="canEditUser">编辑</el-button>
                <el-button type="warning" link size="small" @click="handleResetPassword(row)" v-if="canEditUser">重置密码</el-button>
                <el-button type="danger" link :icon="Delete" size="small" @click="handleDelete(row)" :disabled="row.username === 'admin'" v-if="canDeleteUser">删除</el-button>
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

    <!-- 新增/编辑弹窗 -->
    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="680px" class="form-dialog user-dialog" destroy-on-close>
      <el-form :model="form" :rules="rules" ref="formRef" label-width="80px" label-position="right">
        <div class="form-section">
          <div class="section-title">基本信息</div>
          <div class="section-content">
            <el-row :gutter="16">
              <el-col :span="12">
                <el-form-item label="用户名" prop="username">
                  <el-input v-model="form.username" placeholder="请输入用户名" :disabled="!!editingId" maxlength="50" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="姓名" prop="name">
                  <el-input v-model="form.name" placeholder="请输入姓名" maxlength="50" />
                </el-form-item>
              </el-col>
            </el-row>
            <el-row :gutter="16">
              <el-col :span="12">
                <el-form-item label="密码" prop="password" v-if="!editingId">
                  <el-input v-model="form.password" type="password" placeholder="至少6位字符" show-password maxlength="50" />
                </el-form-item>
                <el-form-item label="手机号" prop="phone" v-else>
                  <el-input v-model="form.phone" placeholder="请输入手机号" maxlength="11" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="确认密码" prop="password_confirm" v-if="!editingId">
                  <el-input v-model="form.password_confirm" type="password" placeholder="再次输入密码" show-password maxlength="50" />
                </el-form-item>
              </el-col>
            </el-row>
            <el-row :gutter="16" v-if="!editingId">
              <el-col :span="12">
                <el-form-item label="手机号" prop="phone">
                  <el-input v-model="form.phone" placeholder="请输入手机号" maxlength="11" />
                </el-form-item>
              </el-col>
            </el-row>
          </div>
        </div>
        
        <div class="form-section">
          <div class="section-title">权限配置</div>
          <div class="permission-grid">
            <div class="permission-card" v-for="(module, key) in permissionModules" :key="key">
              <div class="card-header">
                <el-checkbox 
                  v-model="moduleCheckAll[key]" 
                  :indeterminate="moduleIndeterminate[key]"
                  @change="handleModuleCheckAllChange(key, $event)"
                >
                  {{ module.name }}
                </el-checkbox>
              </div>
              <div class="card-body">
                <el-checkbox-group v-model="form.permissions[key]" size="small">
                  <el-checkbox 
                    v-for="action in module.actions" 
                    :key="action" 
                    :label="action"
                    :disabled="action === 'view' && isViewDisabled(key)"
                    @change="handlePermissionChange(key, action)"
                  >
                    {{ getActionLabel(action) }}
                  </el-checkbox>
                </el-checkbox-group>
              </div>
            </div>
          </div>
        </div>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleSubmit" :loading="submitLoading">确定</el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 重置密码弹窗 -->
    <el-dialog v-model="resetPasswordVisible" title="重置密码" width="400px" class="form-dialog" destroy-on-close>
      <el-form :model="resetPasswordForm" :rules="resetPasswordRules" ref="resetPasswordRef" label-width="100px">
        <el-form-item label="用户">
          <el-input :value="resetPasswordForm.username" disabled />
        </el-form-item>
        <el-form-item label="新密码" prop="new_password">
          <el-input v-model="resetPasswordForm.new_password" type="password" placeholder="请输入新密码（至少6位）" show-password maxlength="50" />
        </el-form-item>
        <el-form-item label="确认密码" prop="confirm_password">
          <el-input v-model="resetPasswordForm.confirm_password" type="password" placeholder="请再次输入新密码" show-password maxlength="50" />
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="resetPasswordVisible = false">取消</el-button>
          <el-button type="primary" @click="handleConfirmResetPassword" :loading="resetLoading">确定</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, nextTick, onUnmounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Refresh, Plus, Edit, Delete } from '@element-plus/icons-vue'
import { getUsers, createUser, updateUser, deleteUser, resetPassword, getPermissionModules } from '../../api/system'
import { canAdd, canEdit, canDelete } from '../../utils/permission'

const loading = ref(false)
const submitLoading = ref(false)
const resetLoading = ref(false)
const toggleLoading = ref(null)
const tableData = ref([])
const permissionModules = ref({})
const formRef = ref(null)
const resetPasswordRef = ref(null)
const dialogVisible = ref(false)
const resetPasswordVisible = ref(false)
const dialogTitle = ref('')
const editingId = ref(null)
const searchKeyword = ref('')
const statusFilter = ref('')
const tableHeight = ref(0)

const canAddUser = computed(() => canAdd('system'))
const canEditUser = computed(() => canEdit('system'))
const canDeleteUser = computed(() => canDelete('system'))

const form = ref({
  username: '',
  name: '',
  password: '',
  password_confirm: '',
  phone: '',
  permissions: {},
  is_active: true
})

const moduleCheckAll = reactive({})
const moduleIndeterminate = reactive({})

const resetPasswordForm = ref({
  id: null,
  username: '',
  new_password: '',
  confirm_password: ''
})

const validatePassword = (rule, value, callback) => {
  if (!value && !editingId.value) {
    callback(new Error('请输入密码'))
  } else if (value && value.length < 6) {
    callback(new Error('密码长度不能少于6位'))
  } else {
    if (form.value.password_confirm) {
      formRef.value?.validateField('password_confirm')
    }
    callback()
  }
}

const validatePasswordConfirm = (rule, value, callback) => {
  if (form.value.password && !value) {
    callback(new Error('请再次输入密码以确认'))
  } else if (value && value !== form.value.password) {
    callback(new Error('两次输入的密码不一致，请确保两次输入的密码相同'))
  } else {
    callback()
  }
}

const validateConfirmPassword = (rule, value, callback) => {
  if (!value) {
    callback(new Error('请再次输入密码'))
  } else if (value !== resetPasswordForm.value.new_password) {
    callback(new Error('两次输入的密码不一致'))
  } else {
    callback()
  }
}

const validatePhone = (rule, value, callback) => {
  if (value && !/^1[3-9]\d{9}$/.test(value)) {
    callback(new Error('请输入有效的手机号'))
  } else {
    callback()
  }
}

const rules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 2, max: 50, message: '用户名长度为2-50个字符', trigger: 'blur' }
  ],
  name: [
    { max: 50, message: '姓名不能超过50个字符', trigger: 'blur' }
  ],
  password: [
    { validator: validatePassword, trigger: 'blur' }
  ],
  password_confirm: [
    { validator: validatePasswordConfirm, trigger: 'blur' }
  ],
  phone: [{ validator: validatePhone, trigger: 'blur' }]
}

const resetPasswordRules = {
  new_password: [{ required: true, validator: validatePassword, trigger: 'blur' }],
  confirm_password: [{ required: true, validator: validateConfirmPassword, trigger: 'blur' }]
}

const pagination = ref({
  page: 1,
  pageSize: 20,
  total: 0
})

const formatDateTime = (datetime) => {
  if (!datetime) return '-'
  return datetime.replace('T', ' ').substring(0, 19)
}

const getActionLabel = (action) => {
  const labels = { view: '查看', add: '新增', edit: '编辑', delete: '删除' }
  return labels[action] || action
}

const getPermissionSummary = (permissions) => {
  if (!permissions || Object.keys(permissions).length === 0) return {}
  const summary = {}
  const moduleNames = {
    basic: '基础资料', purchase: '采购管理', sale: '销售管理',
    inventory: '库存管理', finance: '财务管理', reports: '报表中心', system: '系统管理'
  }
  for (const [key, actions] of Object.entries(permissions)) {
    if (actions && Object.values(actions).some(v => v)) {
      summary[key] = moduleNames[key] || key
    }
  }
  return summary
}

const hasAnyPermission = (permissions) => {
  if (!permissions) return false
  return Object.values(permissions).some(actions => 
    actions && Object.values(actions).some(v => v)
  )
}

const initPermissionForm = () => {
  const perms = {}
  for (const key of Object.keys(permissionModules.value)) {
    perms[key] = []
    moduleCheckAll[key] = false
    moduleIndeterminate[key] = false
  }
  return perms
}

const handleModuleCheckAllChange = (moduleKey, checked) => {
  const actions = permissionModules.value[moduleKey]?.actions || []
  if (checked) {
    form.value.permissions[moduleKey] = [...actions]
  } else {
    form.value.permissions[moduleKey] = []
  }
  moduleIndeterminate[moduleKey] = false
}

const handlePermissionChange = (moduleKey, action) => {
  const perms = form.value.permissions[moduleKey] || []
  const hasAdd = perms.includes('add')
  const hasEdit = perms.includes('edit')
  const hasDelete = perms.includes('delete')
  const hasActionPerms = hasAdd || hasEdit || hasDelete
  
  if (hasActionPerms && !perms.includes('view')) {
    if (!perms.includes('view')) {
      perms.push('view')
      form.value.permissions[moduleKey] = perms
    }
  }
  
  const actions = permissionModules.value[moduleKey]?.actions || []
  const checkedCount = form.value.permissions[moduleKey]?.length || 0
  moduleCheckAll[moduleKey] = checkedCount === actions.length
  moduleIndeterminate[moduleKey] = checkedCount > 0 && checkedCount < actions.length
}

const isViewDisabled = (moduleKey) => {
  const perms = form.value.permissions[moduleKey] || []
  const hasAdd = perms.includes('add')
  const hasEdit = perms.includes('edit')
  const hasDelete = perms.includes('delete')
  return hasAdd || hasEdit || hasDelete
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
    if (searchKeyword.value) params.search = searchKeyword.value
    if (statusFilter.value !== '') params.is_active = statusFilter.value
    
    const res = await getUsers(params)
    tableData.value = res.data.items || res.data.results || []
    pagination.value.total = res.data.count || 0
  } catch (error) {
    tableData.value = []
    pagination.value.total = 0
    const errorMsg = error.response?.data?.msg || error.message || '未知错误'
    if (error.response?.status === 403 || errorMsg.includes('权限')) {
      ElMessage.warning('您没有系统管理的查看权限，请联系管理员')
    } else {
      ElMessage.error('加载数据失败：' + errorMsg)
    }
  } finally {
    loading.value = false
  }
}

const loadPermissionModules = async () => {
  try {
    const res = await getPermissionModules()
    permissionModules.value = res.data || {}
  } catch (error) {
    console.error('加载权限模块失败')
  }
}

const handleAdd = () => {
  dialogTitle.value = '新增用户'
  editingId.value = null
  form.value = { 
    username: '', 
    name: '', 
    password: '', 
    password_confirm: '', 
    phone: '', 
    permissions: initPermissionForm(), 
    is_active: true 
  }
  dialogVisible.value = true
}

const handleEdit = (row) => {
  dialogTitle.value = '编辑用户'
  editingId.value = row.id
  const perms = initPermissionForm()
  
  if (row.permissions) {
    for (const [key, actions] of Object.entries(row.permissions)) {
      if (actions && typeof actions === 'object') {
        perms[key] = Object.entries(actions).filter(([, v]) => v).map(([k]) => k)
      }
    }
  }
  
  form.value = { 
    username: row.username, 
    name: row.name || '', 
    phone: row.phone || '', 
    permissions: perms
  }
  
  for (const key of Object.keys(perms)) {
    const actions = permissionModules.value[key]?.actions || []
    const checkedCount = perms[key]?.length || 0
    moduleCheckAll[key] = checkedCount === actions.length && actions.length > 0
    moduleIndeterminate[key] = checkedCount > 0 && checkedCount < actions.length
  }
  
  dialogVisible.value = true
}

const handleDelete = async (row) => {
  if (row.username === 'admin') {
    ElMessage.warning('不能删除管理员账户')
    return
  }
  
  try {
    await ElMessageBox.confirm(`确定要删除用户「${row.username}」吗？`, '确认删除', {
      confirmButtonText: '确定删除',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    await deleteUser(row.id)
    ElMessage.success('删除成功')
    loadData()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败：' + (error.response?.data?.msg || error.message || '未知错误'))
    }
  }
}

const handleToggleStatus = async (row) => {
  if (row.username === 'admin') {
    ElMessage.warning('不能禁用管理员账户')
    row.is_active = true
    return
  }
  
  const originalStatus = !row.is_active
  try {
    await ElMessageBox.confirm(
      `确定要${row.is_active ? '启用' : '禁用'}用户「${row.username}」吗？`,
      '提示',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    toggleLoading.value = row.id
    await updateUser(row.id, { is_active: row.is_active })
    ElMessage.success('操作成功')
    loadData()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('操作失败：' + (error.response?.data?.msg || error.message || '未知错误'))
    }
    row.is_active = originalStatus
  } finally {
    toggleLoading.value = null
  }
}

const handleResetPassword = (row) => {
  resetPasswordForm.value = {
    id: row.id,
    username: row.username,
    new_password: '',
    confirm_password: ''
  }
  resetPasswordVisible.value = true
}

const handleConfirmResetPassword = async () => {
  try {
    await resetPasswordRef.value.validate()
  } catch (error) {
    return
  }
  
  resetLoading.value = true
  try {
    await resetPassword(resetPasswordForm.value.id, {
      new_password: resetPasswordForm.value.new_password
    })
    ElMessage.success('密码重置成功')
    resetPasswordVisible.value = false
  } catch (error) {
    ElMessage.error('密码重置失败：' + (error.response?.data?.msg || error.message || '未知错误'))
  } finally {
    resetLoading.value = false
  }
}

const handleSubmit = async () => {
  try {
    await formRef.value.validate()
  } catch (error) {
    return
  }
  
  submitLoading.value = true
  try {
    const permsData = {}
    for (const [key, actions] of Object.entries(form.value.permissions)) {
      permsData[key] = {}
      const allActions = permissionModules.value[key]?.actions || []
      for (const action of allActions) {
        permsData[key][action] = actions.includes(action)
      }
    }
    
    if (editingId.value) {
      const submitData = {
        username: form.value.username,
        name: form.value.name,
        phone: form.value.phone,
        permissions: permsData
      }
      await updateUser(editingId.value, submitData)
      ElMessage.success('更新成功')
    } else {
      await createUser({ 
        ...form.value, 
        permissions: permsData 
      })
      ElMessage.success('创建成功')
    }
    dialogVisible.value = false
    loadData()
  } catch (error) {
    ElMessage.error('操作失败：' + (error.response?.data?.msg || error.message || '未知错误'))
  } finally {
    submitLoading.value = false
  }
}

onMounted(() => {
  loadData()
  loadPermissionModules()
  calculateTableHeight()
  window.addEventListener('resize', calculateTableHeight)
})

onUnmounted(() => {
  window.removeEventListener('resize', calculateTableHeight)
})
</script>

<style scoped>
.users-page {
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
  width: 280px;
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

.user-info {
  display: flex;
  align-items: center;
  gap: 10px;
}

.user-avatar {
  background: linear-gradient(135deg, var(--color-primary) 0%, var(--color-primary-dark) 100%);
  color: white;
  font-weight: 600;
  flex-shrink: 0;
}

.user-detail {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.username {
  font-weight: 500;
}

.name {
  font-size: 12px;
  color: var(--color-text-tertiary);
}

.text-muted {
  color: var(--color-text-tertiary);
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
  flex-shrink: 0;
}

.form-dialog :deep(.el-dialog__header) {
  border-bottom: 1px solid var(--color-border-light);
  padding: 16px 20px;
}

.form-dialog :deep(.el-dialog__body) {
  padding: 16px 20px;
  max-height: 65vh;
  overflow-y: auto;
}

.form-dialog :deep(.el-dialog__footer) {
  border-top: 1px solid var(--color-border-light);
  padding: 12px 20px;
}

.user-dialog .form-section {
  margin-bottom: 16px;
}

.user-dialog .form-section:last-child {
  margin-bottom: 0;
}

.user-dialog .section-title {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 14px;
  font-weight: 600;
  color: #303133;
  padding: 8px 12px;
  background: linear-gradient(135deg, #f5f7fa 0%, #eef1f5 100%);
  border-radius: 6px;
  margin-bottom: 12px;
}

.user-dialog .section-content {
  padding: 0 4px;
}

.user-dialog .el-form-item {
  margin-bottom: 16px;
}

.user-dialog .el-form-item:last-child {
  margin-bottom: 0;
}

.user-dialog .el-input {
  width: 100%;
}

.permission-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 10px;
}

.permission-card {
  border: 1px solid #e4e7ed;
  border-radius: 6px;
  overflow: hidden;
  transition: all 0.2s;
}

.permission-card:hover {
  border-color: #165DFF;
  box-shadow: 0 2px 8px rgba(22, 93, 255, 0.1);
}

.permission-card .card-header {
  background: #fafbfc;
  padding: 6px 10px;
  border-bottom: 1px solid #e4e7ed;
}

.permission-card .card-header .el-checkbox {
  font-weight: 600;
  font-size: 13px;
}

.permission-card .card-body {
  padding: 8px 10px;
}

.permission-card .card-body .el-checkbox-group {
  display: flex;
  flex-wrap: wrap;
  gap: 4px 12px;
}

.permission-card .card-body .el-checkbox {
  margin-right: 0;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

.permission-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

.perm-tag {
  font-size: 11px;
}
</style>

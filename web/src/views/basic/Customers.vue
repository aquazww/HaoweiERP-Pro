<template>
  <div class="customers-page">
    <div class="page-content">
      <div class="toolbar-card">
        <div class="toolbar-left">
          <div class="search-box">
            <el-icon class="search-icon"><Search /></el-icon>
            <el-input
              v-model="searchKeyword"
              placeholder="搜索编码、名称、联系人、电话"
              class="search-input"
              clearable
              @keyup.enter="loadCustomers"
            />
          </div>
          <el-select v-model="statusFilter" placeholder="状态筛选" clearable style="width: 140px" @change="loadCustomers">
            <el-option label="全部" :value="''" />
            <el-option label="启用" :value="1" />
            <el-option label="禁用" :value="0" />
          </el-select>
        </div>
        <div class="toolbar-right">
          <el-button :icon="Refresh" @click="loadCustomers">刷新</el-button>
          <el-button type="primary" :icon="Plus" @click="handleAdd" v-if="canAddBasic">新增客户</el-button>
        </div>
      </div>

      <div class="table-card">
        <el-table 
          :data="customersList" 
          style="width: 100%" 
          v-loading="loading"
          class="data-table"
          stripe
          :height="tableHeight"
        >
          <el-table-column prop="code" label="编码" width="120">
            <template #default="{ row }">
              <span class="code-badge">{{ row.code }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="name" label="公司名称" min-width="180">
            <template #default="{ row }">
              <div class="name-cell">
                <div class="company-initials">{{ getCompanyInitials(row.name) }}</div>
                <div class="company-info">
                  <div class="company-name">{{ row.name }}</div>
                  <div class="company-contact" v-if="row.contact">{{ row.contact }} · {{ row.phone }}</div>
                </div>
              </div>
            </template>
          </el-table-column>
          <el-table-column prop="tax_no" label="税号" width="170" show-overflow-tooltip />
          <el-table-column prop="bank_name" label="开户银行" min-width="140" show-overflow-tooltip />
          <el-table-column label="状态" width="100" align="center">
            <template #default="{ row }">
              <el-switch
                v-model="row.status"
                active-color="#165DFF"
                inactive-color="#9ca3af"
                :active-value="1"
                :inactive-value="0"
                :loading="toggleLoading === row.id"
                @change="handleToggleStatus(row)"
              />
            </template>
          </el-table-column>
          <el-table-column label="操作" width="140" align="center">
            <template #default="{ row }">
              <div class="action-buttons">
                <el-button type="primary" link :icon="Edit" size="small" @click="handleEdit(row)" v-if="canEditBasic">编辑</el-button>
                <el-button type="danger" link :icon="Delete" size="small" @click="handleDelete(row)" v-if="canDeleteBasic">删除</el-button>
              </div>
            </template>
          </el-table-column>
        </el-table>
        <div class="pagination-wrapper">
          <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :page-sizes="[10, 20, 50, 100]"
            :total="total"
            layout="total, sizes, prev, pager, next, jumper"
            @size-change="loadCustomers"
            @current-change="loadCustomers"
          />
        </div>
      </div>
    </div>

    <!-- 新增/编辑客户对话框 -->
    <el-dialog 
      v-model="dialogVisible" 
      :title="dialogTitle" 
      width="720px"
      :close-on-click-modal="false"
      @close="handleDialogClose"
    >
      <el-form 
        ref="formRef" 
        :model="form" 
        :rules="rules" 
        label-width="100px"
        label-position="right"
        class="customer-form"
      >
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="客户编码" prop="code">
              <el-input 
                v-model="form.code" 
                placeholder="请输入客户编码"
                maxlength="50"
                show-word-limit
                :disabled="isEdit"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="公司名称" prop="name">
              <el-input 
                v-model="form.name" 
                placeholder="请输入公司名称"
                maxlength="100"
                show-word-limit
              />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="税号" prop="tax_no">
              <el-input 
                v-model="form.tax_no" 
                placeholder="请输入纳税人识别号"
                maxlength="50"
                show-word-limit
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="公司地址" prop="address">
              <el-input 
                v-model="form.address" 
                placeholder="请输入公司地址"
                maxlength="200"
              />
            </el-form-item>
          </el-col>
        </el-row>

        <el-divider content-position="left">联系信息</el-divider>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="联系人" prop="contact">
              <el-input 
                v-model="form.contact" 
                placeholder="请输入联系人姓名"
                maxlength="50"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="联系电话" prop="phone">
              <el-input 
                v-model="form.phone" 
                placeholder="请输入联系电话"
                maxlength="20"
              />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="24">
            <el-form-item label="公司邮箱" prop="email">
              <el-input 
                v-model="form.email" 
                placeholder="请输入公司邮箱"
                maxlength="254"
              />
            </el-form-item>
          </el-col>
        </el-row>

        <el-divider content-position="left">银行信息</el-divider>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="开户银行" prop="bank_name">
              <el-input 
                v-model="form.bank_name" 
                placeholder="请输入开户银行名称"
                maxlength="100"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="银行账号" prop="bank_account">
              <el-input 
                v-model="form.bank_account" 
                placeholder="请输入银行账号"
                maxlength="50"
              />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="支行行号" prop="bank_branch_no">
              <el-input 
                v-model="form.bank_branch_no" 
                placeholder="请输入支行行号（选填）"
                maxlength="50"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="状态" prop="status">
              <el-radio-group v-model="form.status">
                <el-radio :value="1">启用</el-radio>
                <el-radio :value="0">禁用</el-radio>
              </el-radio-group>
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="备注" prop="remark">
          <el-input 
            v-model="form.remark" 
            type="textarea" 
            :rows="3"
            placeholder="请输入备注信息（选填）"
            maxlength="500"
            show-word-limit
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <div class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleSubmit" :loading="submitLoading">
            {{ isEdit ? '保存修改' : '确认新增' }}
          </el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, nextTick, onUnmounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Refresh, Plus, Edit, Delete } from '@element-plus/icons-vue'
import { getCustomers, createCustomer, deleteCustomer, updateCustomer } from '../../api/basic'
import { canAdd, canEdit, canDelete } from '../../utils/permission'

const canAddBasic = computed(() => canAdd('basic'))
const canEditBasic = computed(() => canEdit('basic'))
const canDeleteBasic = computed(() => canDelete('basic'))

const loading = ref(false)
const toggleLoading = ref(null)
const customersList = ref([])
const searchKeyword = ref('')
const statusFilter = ref('')
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)
const tableHeight = ref(0)

const dialogVisible = ref(false)
const dialogTitle = ref('新增客户')
const isEdit = ref(false)
const submitLoading = ref(false)
const formRef = ref(null)

const form = reactive({
  id: null,
  code: '',
  name: '',
  tax_no: '',
  address: '',
  contact: '',
  phone: '',
  email: '',
  bank_name: '',
  bank_account: '',
  bank_branch_no: '',
  balance: 0,
  remark: '',
  status: 1
})

const validateCode = (rule, value, callback) => {
  if (!value || !value.trim()) {
    callback(new Error('请输入客户编码'))
  } else if (value.length > 50) {
    callback(new Error('客户编码不能超过50个字符'))
  } else if (!/^[A-Za-z0-9_-]+$/.test(value)) {
    callback(new Error('客户编码只能包含字母、数字、下划线和横线'))
  } else {
    callback()
  }
}

const validateName = (rule, value, callback) => {
  if (!value || !value.trim()) {
    callback(new Error('请输入公司名称'))
  } else if (value.length > 100) {
    callback(new Error('公司名称不能超过100个字符'))
  } else {
    callback()
  }
}

const validateTaxNo = (rule, value, callback) => {
  if (!value || !value.trim()) {
    callback(new Error('请输入纳税人识别号'))
  } else if (value.length > 50) {
    callback(new Error('税号不能超过50个字符'))
  } else if (!/^[A-Za-z0-9]+$/.test(value)) {
    callback(new Error('税号只能包含字母和数字'))
  } else {
    callback()
  }
}

const validateAddress = (rule, value, callback) => {
  if (!value || !value.trim()) {
    callback(new Error('请输入公司地址'))
  } else if (value.length > 200) {
    callback(new Error('地址不能超过200个字符'))
  } else {
    callback()
  }
}

const validatePhone = (rule, value, callback) => {
  if (value && value.trim()) {
    const phoneRegex = /^[\d\-+()]+$/
    if (!phoneRegex.test(value)) {
      callback(new Error('请输入有效的电话号码'))
    } else {
      callback()
    }
  } else {
    callback()
  }
}

const validateEmail = (rule, value, callback) => {
  if (value && value.trim()) {
    const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/
    if (!emailRegex.test(value)) {
      callback(new Error('请输入有效的邮箱地址'))
    } else {
      callback()
    }
  } else {
    callback()
  }
}

const rules = {
  code: [
    { required: true, validator: validateCode, trigger: 'blur' }
  ],
  name: [
    { required: true, validator: validateName, trigger: 'blur' }
  ],
  tax_no: [
    { required: true, validator: validateTaxNo, trigger: 'blur' }
  ],
  address: [
    { required: true, validator: validateAddress, trigger: 'blur' }
  ],
  phone: [
    { validator: validatePhone, trigger: 'blur' }
  ],
  email: [
    { validator: validateEmail, trigger: 'blur' }
  ]
}

const getCompanyInitials = (name) => {
  if (!name) return ''
  return name.slice(0, 2).toUpperCase()
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

const loadCustomers = async () => {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      page_size: pageSize.value
    }
    if (searchKeyword.value) {
      params.search = searchKeyword.value
    }
    if (statusFilter.value !== '') {
      params.status = statusFilter.value
    }
    const res = await getCustomers(params)
    customersList.value = res.data.items || res.data.results || []
    total.value = res.data.count || 0
  } catch (error) {
    customersList.value = []
    total.value = 0
    ElMessage.error('加载数据失败：' + (error.message || '未知错误'))
  } finally {
    loading.value = false
  }
}

const resetForm = () => {
  form.id = null
  form.code = ''
  form.name = ''
  form.tax_no = ''
  form.address = ''
  form.contact = ''
  form.phone = ''
  form.email = ''
  form.bank_name = ''
  form.bank_account = ''
  form.bank_branch_no = ''
  form.balance = 0
  form.remark = ''
  form.status = 1
}

const handleAdd = () => {
  resetForm()
  isEdit.value = false
  dialogTitle.value = '新增客户'
  dialogVisible.value = true
}

const handleEdit = (row) => {
  resetForm()
  isEdit.value = true
  dialogTitle.value = '编辑客户'
  
  form.id = row.id
  form.code = row.code
  form.name = row.name
  form.tax_no = row.tax_no
  form.address = row.address
  form.contact = row.contact || ''
  form.phone = row.phone || ''
  form.email = row.email || ''
  form.bank_name = row.bank_name || ''
  form.bank_account = row.bank_account || ''
  form.bank_branch_no = row.bank_branch_no || ''
  form.balance = row.balance || 0
  form.remark = row.remark || ''
  form.status = row.status
  
  dialogVisible.value = true
}

const handleDialogClose = () => {
  formRef.value?.resetFields()
}

const handleSubmit = async () => {
  if (!formRef.value) return
  
  try {
    await formRef.value.validate()
  } catch (error) {
    ElMessage.warning('请检查表单填写是否正确')
    return
  }
  
  submitLoading.value = true
  
  try {
    const submitData = {
      code: form.code.trim().toUpperCase(),
      name: form.name.trim(),
      tax_no: form.tax_no.trim().toUpperCase(),
      address: form.address.trim(),
      contact: form.contact?.trim() || '',
      phone: form.phone?.trim() || '',
      email: form.email?.trim() || '',
      bank_name: form.bank_name?.trim() || '',
      bank_account: form.bank_account?.trim() || '',
      bank_branch_no: form.bank_branch_no?.trim() || '',
      balance: form.balance || 0,
      remark: form.remark?.trim() || '',
      status: form.status
    }
    
    if (isEdit.value) {
      await updateCustomer(form.id, submitData)
      ElMessage.success('客户修改成功')
    } else {
      await createCustomer(submitData)
      ElMessage.success('客户新增成功')
    }
    
    dialogVisible.value = false
    loadCustomers()
  } catch (error) {
    const errorMsg = error.response?.data?.msg || error.message || '操作失败'
    
    if (error.response?.data?.data) {
      const errors = error.response.data.data
      const errorMessages = Object.values(errors).flat().join('；')
      ElMessage.error(errorMessages)
    } else {
      ElMessage.error(errorMsg)
    }
  } finally {
    submitLoading.value = false
  }
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm(`确定要删除客户「${row.name}」吗？`, '确认删除', {
      confirmButtonText: '确定删除',
      cancelButtonText: '取消',
      type: 'warning',
      confirmButtonClass: 'el-button--danger'
    })
    await deleteCustomer(row.id)
    ElMessage.success('删除成功')
    loadCustomers()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const handleToggleStatus = async (row) => {
  const originalStatus = row.status === 1 ? 0 : 1
  try {
    await ElMessageBox.confirm(`确定要${row.status === 1 ? '启用' : '禁用'}客户「${row.name}」吗？`, '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    toggleLoading.value = row.id
    await updateCustomer(row.id, { ...row, status: row.status })
    ElMessage.success('操作成功')
    loadCustomers()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('操作失败')
    }
    row.status = originalStatus
  } finally {
    toggleLoading.value = null
  }
}

onMounted(() => {
  loadCustomers()
  calculateTableHeight()
  window.addEventListener('resize', calculateTableHeight)
})

onUnmounted(() => {
  window.removeEventListener('resize', calculateTableHeight)
})
</script>

<style scoped>
.customers-page {
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

.code-badge {
  display: inline-block;
  padding: 2px 10px;
  background-color: var(--color-bg-light);
  color: var(--color-primary);
  font-weight: 500;
  font-size: var(--font-size-sm);
  border-radius: var(--border-radius-sm);
  font-family: 'Monaco', 'Consolas', monospace;
}

.name-cell {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
}

.company-initials {
  width: 36px;
  height: 36px;
  background: linear-gradient(135deg, var(--color-primary-light) 0%, var(--color-primary) 100%);
  border-radius: var(--border-radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-white);
  font-weight: 600;
  font-size: var(--font-size-sm);
  flex-shrink: 0;
}

.company-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
  overflow: hidden;
}

.company-name {
  font-weight: 500;
  color: var(--color-text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.company-contact {
  font-size: var(--font-size-xs);
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

.customer-form {
  padding: 10px 20px;
}

.customer-form :deep(.el-divider__text) {
  font-weight: 500;
  color: var(--color-text-secondary);
}

.customer-form :deep(.el-form-item__label) {
  font-weight: 500;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}
</style>

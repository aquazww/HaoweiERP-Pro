<template>
  <div class="customers-page">
    <div class="page-header">
      <div class="header-title-section">
        <div class="title-icon">
          <el-icon :size="24"><UserFilled /></el-icon>
        </div>
        <div class="title-content">
          <h1 class="page-title">客户管理</h1>
          <p class="page-subtitle">管理和维护所有客户信息</p>
        </div>
      </div>
      <div class="header-stats">
        <div class="stat-item">
          <div class="stat-value">{{ total }}</div>
          <div class="stat-label">客户总数</div>
        </div>
        <div class="stat-item">
          <div class="stat-value active">{{ activeCount }}</div>
          <div class="stat-label">启用</div>
        </div>
      </div>
    </div>

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
          <el-select v-model="statusFilter" placeholder="状态筛选" clearable @change="loadCustomers">
            <el-option label="全部" :value="''" />
            <el-option label="启用" :value="1" />
            <el-option label="禁用" :value="0" />
          </el-select>
        </div>
        <div class="toolbar-right">
          <el-button :icon="Refresh" @click="loadCustomers">刷新</el-button>
          <el-button type="primary" :icon="Plus" @click="handleAdd">新增客户</el-button>
        </div>
      </div>

      <div class="table-card">
        <el-table 
          :data="customersList" 
          style="width: 100%" 
          v-loading="loading"
          :height="tableHeight"
          class="data-table"
          stripe
        >
          <el-table-column type="index" label="#" width="60" align="center" />
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
          <el-table-column label="状态" width="90">
            <template #default="{ row }">
              <div class="status-badge" :class="{ active: row.status === 1 }">
                <span class="status-dot"></span>
                {{ row.status === 1 ? '启用' : '禁用' }}
              </div>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="140" fixed="right">
            <template #default="{ row }">
              <div class="action-buttons">
                <el-button type="primary" link :icon="Edit" size="small" @click="handleEdit(row)">编辑</el-button>
                <el-button type="danger" link :icon="Delete" size="small" @click="handleDelete(row)">删除</el-button>
              </div>
            </template>
          </el-table-column>
        </el-table>
      </div>

      <div class="pagination-card">
        <div class="pagination-info">
          <span>共 <strong>{{ total }}</strong> 条记录</span>
        </div>
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="total"
          layout="prev, pager, next, jumper, sizes"
          @size-change="loadCustomers"
          @current-change="loadCustomers"
        />
      </div>
    </div>

    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? '编辑客户' : '新增客户'"
      width="720px"
      class="form-dialog"
      @close="resetForm"
    >
      <el-form ref="formRef" :model="formData" :rules="formRules" label-width="100px">
        <div class="form-section">
          <div class="section-title">基础信息</div>
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="客户编码" prop="code">
                <el-input v-model="formData.code" placeholder="请输入客户编码" :disabled="isEdit" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="公司名称" prop="name">
                <el-input v-model="formData.name" placeholder="请输入公司名称" />
              </el-form-item>
            </el-col>
          </el-row>
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="税号" prop="tax_no">
                <el-input v-model="formData.tax_no" placeholder="请输入税号" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="状态" prop="status">
                <el-select v-model="formData.status" placeholder="请选择状态" style="width: 100%">
                  <el-option label="启用" :value="1" />
                  <el-option label="禁用" :value="0" />
                </el-select>
              </el-form-item>
            </el-col>
          </el-row>
          <el-form-item label="公司地址" prop="address">
            <el-input v-model="formData.address" placeholder="请输入公司地址" />
          </el-form-item>
        </div>

        <div class="form-section">
          <div class="section-title">联系方式</div>
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="联系人" prop="contact">
                <el-input v-model="formData.contact" placeholder="请输入联系人" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="联系电话" prop="phone">
                <el-input v-model="formData.phone" placeholder="请输入联系电话" />
              </el-form-item>
            </el-col>
          </el-row>
          <el-form-item label="公司邮箱" prop="email">
            <el-input v-model="formData.email" placeholder="请输入公司邮箱" />
          </el-form-item>
        </div>

        <div class="form-section">
          <div class="section-title">银行信息</div>
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="开户银行" prop="bank_name">
                <el-input v-model="formData.bank_name" placeholder="请输入开户银行" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="银行账号" prop="bank_account">
                <el-input v-model="formData.bank_account" placeholder="请输入银行账号" />
              </el-form-item>
            </el-col>
          </el-row>
          <el-form-item label="支行行号" prop="bank_branch_no">
            <el-input v-model="formData.bank_branch_no" placeholder="请输入支行行号" />
          </el-form-item>
        </div>

        <div class="form-section">
          <div class="section-title">备注信息</div>
          <el-form-item label="备注" prop="remark">
            <el-input v-model="formData.remark" type="textarea" :rows="3" placeholder="请输入备注信息" />
          </el-form-item>
        </div>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleSubmit" :loading="submitLoading">
            {{ isEdit ? '保存修改' : '创建客户' }}
          </el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick, onUnmounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { UserFilled, Search, Refresh, Plus, Edit, Delete } from '@element-plus/icons-vue'
import { getCustomers, createCustomer, updateCustomer, deleteCustomer } from '../../api/basic'

const loading = ref(false)
const submitLoading = ref(false)
const customersList = ref([])
const searchKeyword = ref('')
const statusFilter = ref('')
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)
const dialogVisible = ref(false)
const isEdit = ref(false)
const formRef = ref(null)
const tableHeight = ref(0)

const formData = ref({
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
  remark: '',
  status: 1
})

const formRules = {
  code: [
    { required: true, message: '请输入客户编码', trigger: 'blur' }
  ],
  name: [
    { required: true, message: '请输入公司名称', trigger: 'blur' }
  ],
  tax_no: [
    { required: true, message: '请输入税号', trigger: 'blur' }
  ],
  address: [
    { required: true, message: '请输入公司地址', trigger: 'blur' }
  ],
  status: [
    { required: true, message: '请选择状态', trigger: 'change' }
  ],
  email: [
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
  ]
}

const activeCount = computed(() => {
  return customersList.value.filter(item => item.status === 1).length
})

const getCompanyInitials = (name) => {
  if (!name) return ''
  return name.slice(0, 2).toUpperCase()
}

const loadCustomers = async () => {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      page_size: pageSize.value,
      search: searchKeyword.value
    }
    if (statusFilter.value !== '') {
      params.status = statusFilter.value
    }
    const res = await getCustomers(params)
    customersList.value = res.data.items || []
    total.value = res.data.count || 0
  } catch (error) {
    ElMessage.error('加载客户列表失败')
  } finally {
    loading.value = false
  }
}

const calculateTableHeight = () => {
  nextTick(() => {
    const pageHeader = document.querySelector('.page-header')
    const toolbarCard = document.querySelector('.toolbar-card')
    const paginationCard = document.querySelector('.pagination-card')
    const pageContent = document.querySelector('.page-content')
    
    if (pageContent) {
      let usedHeight = 0
      if (pageHeader) usedHeight += pageHeader.offsetHeight + 24
      if (toolbarCard) usedHeight += toolbarCard.offsetHeight + 16
      if (paginationCard) usedHeight += paginationCard.offsetHeight + 16
      usedHeight += 80
      
      const availableHeight = window.innerHeight - 64 - 48
      tableHeight.value = Math.max(availableHeight - usedHeight, 300)
    }
  })
}

const handleAdd = () => {
  isEdit.value = false
  dialogVisible.value = true
}

const handleEdit = (row) => {
  isEdit.value = true
  formData.value = { ...row }
  dialogVisible.value = true
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

const handleSubmit = async () => {
  if (!formRef.value) return
  
  try {
    await formRef.value.validate()
    submitLoading.value = true
    
    if (isEdit.value) {
      await updateCustomer(formData.value.id, formData.value)
      ElMessage.success('编辑成功')
    } else {
      await createCustomer(formData.value)
      ElMessage.success('新增成功')
    }
    
    dialogVisible.value = false
    loadCustomers()
  } catch (error) {
    if (error !== false) {
      ElMessage.error(isEdit.value ? '编辑失败' : '新增失败')
    }
  } finally {
    submitLoading.value = false
  }
}

const resetForm = () => {
  if (formRef.value) {
    formRef.value.resetFields()
  }
  formData.value = {
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
    remark: '',
    status: 1
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
  display: flex;
  flex-direction: column;
  gap: var(--spacing-lg);
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  background: linear-gradient(135deg, var(--color-primary-light) 0%, rgba(14, 165, 233, 0.05) 100%);
  padding: var(--spacing-xl);
  border-radius: var(--border-radius-lg);
  border: 1px solid var(--color-primary-light);
}

.header-title-section {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
}

.title-icon {
  width: 56px;
  height: 56px;
  background: linear-gradient(135deg, var(--color-primary) 0%, var(--color-primary-dark) 100%);
  border-radius: var(--border-radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-white);
  box-shadow: var(--shadow-primary);
}

.title-content {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-xs);
}

.page-title {
  margin: 0;
  font-size: var(--font-size-2xl);
  font-weight: 600;
  color: var(--color-text-primary);
  line-height: 1.2;
}

.page-subtitle {
  margin: 0;
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  line-height: 1.4;
}

.header-stats {
  display: flex;
  gap: var(--spacing-lg);
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
}

.stat-value {
  font-size: var(--font-size-3xl);
  font-weight: 700;
  color: var(--color-primary);
  line-height: 1;
}

.stat-value.active {
  color: var(--color-success);
}

.stat-label {
  font-size: var(--font-size-sm);
  color: var(--color-text-tertiary);
  margin-top: var(--spacing-xs);
}

.page-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
  overflow: hidden;
}

.toolbar-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background-color: var(--color-white);
  padding: var(--spacing-md) var(--spacing-lg);
  border-radius: var(--border-radius-lg);
  border: 1px solid var(--color-border-light);
  box-shadow: var(--shadow-sm);
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
  background-color: var(--color-white);
  border-radius: var(--border-radius-lg);
  border: 1px solid var(--color-border-light);
  box-shadow: var(--shadow-sm);
  overflow: hidden;
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

.status-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 4px 12px;
  background-color: var(--color-bg-light);
  color: var(--color-text-secondary);
  font-size: var(--font-size-sm);
  border-radius: 20px;
  font-weight: 500;
}

.status-badge.active {
  background-color: rgba(34, 197, 94, 0.1);
  color: var(--color-success);
}

.status-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background-color: var(--color-text-tertiary);
}

.status-badge.active .status-dot {
  background-color: var(--color-success);
}

.action-buttons {
  display: flex;
  align-items: center;
  gap: var(--spacing-xs);
}

.pagination-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background-color: var(--color-white);
  padding: var(--spacing-md) var(--spacing-lg);
  border-radius: var(--border-radius-lg);
  border: 1px solid var(--color-border-light);
  box-shadow: var(--shadow-sm);
}

.pagination-info {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
}

.pagination-info strong {
  color: var(--color-primary);
  font-weight: 600;
}

.form-dialog {
  --el-dialog-border-radius: var(--border-radius-lg);
}

.form-dialog :deep(.el-dialog__header) {
  padding: var(--spacing-lg) var(--spacing-xl);
  border-bottom: 1px solid var(--color-border-light);
}

.form-dialog :deep(.el-dialog__body) {
  padding: var(--spacing-lg) var(--spacing-xl);
}

.form-dialog :deep(.el-dialog__footer) {
  padding: var(--spacing-md) var(--spacing-xl);
  border-top: 1px solid var(--color-border-light);
}

.form-section {
  margin-bottom: var(--spacing-lg);
}

.form-section:last-child {
  margin-bottom: 0;
}

.section-title {
  font-size: var(--font-size-base);
  font-weight: 600;
  color: var(--color-text-primary);
  margin-bottom: var(--spacing-md);
  padding-left: var(--spacing-sm);
  border-left: 3px solid var(--color-primary);
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: var(--spacing-sm);
}
</style>

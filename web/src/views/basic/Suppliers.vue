<template>
  <div class="suppliers-page">
    <div class="page-header">
      <div class="header-title-section">
        <div class="title-icon">
          <el-icon :size="24"><OfficeBuilding /></el-icon>
        </div>
        <div class="title-content">
          <h1 class="page-title">供应商管理</h1>
          <p class="page-subtitle">管理和维护所有供应商信息</p>
        </div>
      </div>
      <div class="header-stats">
        <div class="stat-item">
          <div class="stat-value">{{ total }}</div>
          <div class="stat-label">供应商总数</div>
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
              @keyup.enter="loadSuppliers"
            />
          </div>
          <el-select v-model="statusFilter" placeholder="状态筛选" clearable @change="loadSuppliers">
            <el-option label="全部" :value="''" />
            <el-option label="启用" :value="1" />
            <el-option label="禁用" :value="0" />
          </el-select>
        </div>
        <div class="toolbar-right">
          <el-button :icon="Refresh" @click="loadSuppliers">刷新</el-button>
          <el-button type="primary" :icon="Plus" @click="handleAdd">新增供应商</el-button>
        </div>
      </div>

      <div class="table-card">
        <el-table 
          :data="displayList" 
          style="width: 100%" 
          v-loading="loading"
          class="data-table"
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
          <el-table-column label="状态" width="100" align="center">
            <template #default="{ row }">
              <el-switch
                v-model="row.status"
                active-color="#165DFF"
                inactive-color="#9ca3af"
                :active-value="1"
                :inactive-value="0"
                @change="handleToggleStatus(row)"
              />
            </template>
          </el-table-column>
          <el-table-column label="操作" width="140" fixed="right" align="center">
            <template #default="{ row }">
              <div class="action-buttons">
                <el-button type="primary" link :icon="Edit" size="small" @click="handleEdit(row)">编辑</el-button>
                <el-button type="danger" link :icon="Delete" size="small" @click="handleDelete(row)">删除</el-button>
              </div>
            </template>
          </el-table-column>
        </el-table>
      </div>

      <div class="pagination-wrapper">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="loadSuppliers"
          @current-change="loadSuppliers"
        />
      </div>
    </div>

    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? '编辑供应商' : '新增供应商'"
      width="720px"
      class="form-dialog"
      @close="resetForm"
    >
      <el-form ref="formRef" :model="formData" :rules="formRules" label-width="100px">
        <div class="form-section">
          <div class="section-title">基础信息</div>
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="供应商编码" prop="code">
                <el-input v-model="formData.code" placeholder="请输入供应商编码" :disabled="isEdit" />
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
          <el-form-item label="地址" prop="address">
            <el-input v-model="formData.address" placeholder="请输入地址" />
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
            {{ isEdit ? '保存修改' : '创建供应商' }}
          </el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { OfficeBuilding, Search, Refresh, Plus, Edit, Delete } from '@element-plus/icons-vue'
import { getSuppliers, createSupplier, updateSupplier, deleteSupplier } from '../../api/basic'

const loading = ref(false)
const submitLoading = ref(false)
const suppliersList = ref([])
const searchKeyword = ref('')
const statusFilter = ref('')
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)
const dialogVisible = ref(false)
const isEdit = ref(false)
const formRef = ref(null)
const useMockData = ref(true)

const mockSuppliers = ref([
  { id: 1, code: 'SUP001', name: '北京原材料供应有限公司', tax_no: '911100001234567890', address: '北京市朝阳区建国路88号', contact: '张经理', phone: '13800138001', email: 'zhang@bjmaterials.com', bank_name: '中国工商银行北京分行', bank_account: '6222020012345678901', bank_branch_no: '10210000001', status: 1, remark: '长期合作供应商' },
  { id: 2, code: 'SUP002', name: '上海电子科技有限公司', tax_no: '913100000987654321', address: '上海市浦东新区张江高科技园区', contact: '李总', phone: '13900139002', email: 'li@shanghaitech.com', bank_name: '招商银行上海分行', bank_account: '6226090098765432109', bank_branch_no: '30829000001', status: 1, remark: '主要电子元件供应商' },
  { id: 3, code: 'SUP003', name: '广州化工原料厂', tax_no: '914400001122334455', address: '广州市黄埔区化工园区', contact: '王厂长', phone: '13700137003', email: 'wang@gzchemical.com', bank_name: '中国银行广州分行', bank_account: '6216610011223344556', bank_branch_no: '10458100000', status: 0, remark: '暂停合作' },
  { id: 4, code: 'SUP004', name: '深圳精密机械制造', tax_no: '914403005566778899', address: '深圳市宝安区沙井街道', contact: '陈工', phone: '13600136004', email: 'chen@szprecision.com', bank_name: '建设银行深圳分行', bank_account: '6217007200012345678', bank_branch_no: '10558400000', status: 1, remark: '机械部件供应商' },
  { id: 5, code: 'SUP005', name: '杭州包装材料有限公司', tax_no: '913301009988776655', address: '杭州市余杭区仓前街道', contact: '刘经理', phone: '13500135005', email: 'liu@hzpack.com', bank_name: '农业银行杭州分行', bank_account: '6228480310012345678', bank_branch_no: '10333100000', status: 1, remark: '' }
])

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
    { required: true, message: '请输入供应商编码', trigger: 'blur' }
  ],
  name: [
    { required: true, message: '请输入公司名称', trigger: 'blur' }
  ],
  tax_no: [
    { required: true, message: '请输入税号', trigger: 'blur' }
  ],
  address: [
    { required: true, message: '请输入地址', trigger: 'blur' }
  ],
  status: [
    { required: true, message: '请选择状态', trigger: 'change' }
  ],
  email: [
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
  ]
}

const displayList = computed(() => {
  let list = suppliersList.value.length > 0 ? suppliersList.value : mockSuppliers.value
  
  if (searchKeyword.value) {
    const keyword = searchKeyword.value.toLowerCase()
    list = list.filter(item => 
      item.code.toLowerCase().includes(keyword) ||
      item.name.toLowerCase().includes(keyword) ||
      (item.contact && item.contact.toLowerCase().includes(keyword)) ||
      (item.phone && item.phone.includes(keyword))
    )
  }
  
  if (statusFilter.value !== '') {
    list = list.filter(item => item.status === statusFilter.value)
  }
  
  total.value = list.length
  
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return list.slice(start, end)
})

const activeCount = computed(() => {
  const list = suppliersList.value.length > 0 ? suppliersList.value : mockSuppliers.value
  return list.filter(item => item.status === 1).length
})

const getCompanyInitials = (name) => {
  if (!name) return ''
  return name.slice(0, 2).toUpperCase()
}

const loadSuppliers = async () => {
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
    const res = await getSuppliers(params)
    suppliersList.value = res.data.items || []
    total.value = res.data.count || 0
    useMockData.value = false
  } catch (error) {
    useMockData.value = true
    total.value = mockSuppliers.value.length
    ElMessage.info('使用模拟数据展示')
  } finally {
    loading.value = false
  }
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
    await ElMessageBox.confirm(`确定要删除供应商「${row.name}」吗？`, '确认删除', {
      confirmButtonText: '确定删除',
      cancelButtonText: '取消',
      type: 'warning',
      confirmButtonClass: 'el-button--danger'
    })
    if (useMockData.value) {
      const index = mockSuppliers.value.findIndex(item => item.id === row.id)
      if (index > -1) {
        mockSuppliers.value.splice(index, 1)
      }
      ElMessage.success('删除成功')
    } else {
      await deleteSupplier(row.id)
      ElMessage.success('删除成功')
      loadSuppliers()
    }
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const handleToggleStatus = async (row) => {
  try {
    await ElMessageBox.confirm(`确定要${row.status === 1 ? '启用' : '禁用'}供应商「${row.name}」吗？`, '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    if (useMockData.value) {
      const index = mockSuppliers.value.findIndex(item => item.id === row.id)
      if (index > -1) {
        mockSuppliers.value[index].status = row.status
      }
      ElMessage.success('操作成功')
    } else {
      await updateSupplier(row.id, { ...row, status: row.status })
      ElMessage.success('操作成功')
      loadSuppliers()
    }
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('操作失败')
      row.status = row.status === 1 ? 0 : 1
    } else {
      row.status = row.status === 1 ? 0 : 1
    }
  }
}

const handleSubmit = async () => {
  if (!formRef.value) return
  
  try {
    await formRef.value.validate()
    submitLoading.value = true
    
    if (isEdit.value) {
      if (useMockData.value) {
        const index = mockSuppliers.value.findIndex(item => item.id === formData.value.id)
        if (index > -1) {
          mockSuppliers.value[index] = { ...formData.value }
        }
        ElMessage.success('编辑成功')
      } else {
        await updateSupplier(formData.value.id, formData.value)
        ElMessage.success('编辑成功')
        loadSuppliers()
      }
    } else {
      if (useMockData.value) {
        const newId = Math.max(...mockSuppliers.value.map(item => item.id)) + 1
        mockSuppliers.value.push({ ...formData.value, id: newId })
        ElMessage.success('新增成功')
      } else {
        await createSupplier(formData.value)
        ElMessage.success('新增成功')
        loadSuppliers()
      }
    }
    
    dialogVisible.value = false
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
  loadSuppliers()
})
</script>

<style scoped>
.suppliers-page {
  height: 100%;
  display: flex;
  flex-direction: column;
  gap: var(--spacing-lg);
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  background: linear-gradient(135deg, var(--color-primary-light) 0%, rgba(22, 93, 255, 0.05) 100%);
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

.action-buttons {
  display: flex;
  align-items: center;
  gap: var(--spacing-xs);
}

.pagination-wrapper {
  display: flex;
  justify-content: flex-end;
  padding: var(--spacing-md) 0;
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

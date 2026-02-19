<template>
  <div class="users-page">
    <div class="page-header">
      <div class="header-title-section">
        <div class="title-icon">
          <el-icon :size="24"><User /></el-icon>
        </div>
        <div class="title-content">
          <h1 class="page-title">用户管理</h1>
          <p class="page-subtitle">管理和维护系统用户账户</p>
        </div>
      </div>
      <div class="header-actions">
        <el-button type="primary" :icon="Plus" @click="handleAdd">新增用户</el-button>
      </div>
    </div>

    <div class="page-content">
      <div class="table-card">
        <el-table 
          :data="tableData" 
          style="width: 100%" 
          v-loading="loading"
          class="data-table"
        >
          <el-table-column prop="username" label="用户名" min-width="140" />
          <el-table-column prop="role_name" label="角色" min-width="120" />
          <el-table-column prop="phone" label="手机号" min-width="130" />
          <el-table-column label="状态" width="100" align="center">
            <template #default="{ row }">
              <el-switch
                v-model="row.is_active"
                active-color="#165DFF"
                inactive-color="#9ca3af"
                @change="handleToggleStatus(row)"
              />
            </template>
          </el-table-column>
          <el-table-column prop="created_at" label="创建时间" width="180" />
          <el-table-column label="操作" width="160" fixed="right" align="center">
            <template #default="{ row }">
              <el-button type="primary" link :icon="Edit" size="small" @click="handleEdit(row)">编辑</el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>

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

    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="500px" class="form-dialog">
      <el-form :model="form" :rules="rules" ref="formRef" label-width="100px">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="form.username" placeholder="请输入用户名" :disabled="!!editingId" />
        </el-form-item>
        <el-form-item label="密码" prop="password" v-if="!editingId">
          <el-input v-model="form.password" type="password" placeholder="请输入密码" show-password />
        </el-form-item>
        <el-form-item label="角色" prop="role">
          <el-select v-model="form.role" placeholder="请选择角色" style="width: 100%;">
            <el-option v-for="role in roles" :key="role.id" :label="role.name" :value="role.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="手机号" prop="phone">
          <el-input v-model="form.phone" placeholder="请输入手机号" />
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
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { User, Plus, Edit } from '@element-plus/icons-vue'
import { getUsers, createUser, updateUser } from '../../api/system'
import { getRoles } from '../../api/system'

const tableData = ref([])
const roles = ref([])
const formRef = ref(null)
const dialogVisible = ref(false)
const dialogTitle = ref('')
const editingId = ref(null)
const loading = ref(false)

const form = ref({
  username: '',
  password: '',
  role: null,
  phone: '',
  is_active: true
})

const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
  role: [{ required: true, message: '请选择角色', trigger: 'change' }]
}

const pagination = ref({
  page: 1,
  pageSize: 20,
  total: 0
})

const loadData = async () => {
  loading.value = true
  try {
    const res = await getUsers({
      page: pagination.value.page,
      page_size: pagination.value.pageSize
    })
    tableData.value = res.data.results || []
    pagination.value.total = res.data.count || 0
  } catch (error) {
    ElMessage.error('加载数据失败')
  } finally {
    loading.value = false
  }
}

const loadRoles = async () => {
  try {
    const res = await getRoles({ page_size: 1000 })
    roles.value = res.data.results || []
  } catch (error) {
    ElMessage.error('加载角色列表失败')
  }
}

const handleAdd = () => {
  dialogTitle.value = '新增用户'
  editingId.value = null
  form.value = { username: '', password: '', role: null, phone: '', is_active: true }
  dialogVisible.value = true
}

const handleEdit = (row) => {
  dialogTitle.value = '编辑用户'
  editingId.value = row.id
  form.value = { ...row, role: row.role?.id || null }
  dialogVisible.value = true
}

const handleToggleStatus = async (row) => {
  try {
    await ElMessageBox.confirm(`确定要${row.is_active ? '启用' : '禁用'}该用户吗？`, '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await updateUser(row.id, { ...row, is_active: row.is_active })
    ElMessage.success('操作成功')
    loadData()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('操作失败')
      row.is_active = !row.is_active
    }
  }
}

const handleSubmit = async () => {
  await formRef.value.validate()
  
  try {
    if (editingId.value) {
      const { password, ...data } = form.value
      await updateUser(editingId.value, data)
      ElMessage.success('更新成功')
    } else {
      await createUser(form.value)
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
  loadRoles()
})
</script>

<style scoped>
.users-page {
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

.header-actions {
  display: flex;
  gap: var(--spacing-sm);
}

.page-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
  overflow: hidden;
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

.pagination-wrapper {
  display: flex;
  justify-content: flex-end;
  padding: var(--spacing-md) 0;
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
</style>

<template>
  <div class="roles-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>角色管理</span>
          <el-button type="primary" @click="handleAdd">新增角色</el-button>
        </div>
      </template>

      <el-table :data="tableData" border style="width: 100%">
        <el-table-column prop="name" label="角色名称" width="200" />
        <el-table-column prop="description" label="描述" />
        <el-table-column prop="created_at" label="创建时间" width="180" />
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click="handleEdit(row)">编辑</el-button>
            <el-button type="danger" size="small" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.pageSize"
        :page-sizes="[10, 20, 50, 100]"
        :total="pagination.total"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="loadData"
        @current-change="loadData"
        style="margin-top: 20px; justify-content: flex-end"
      />
    </el-card>

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
import { ref, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getRoles, createRole, updateRole, deleteRole } from '../../api/system'

const tableData = ref([])
const formRef = ref(null)
const dialogVisible = ref(false)
const dialogTitle = ref('')
const editingId = ref(null)

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

const loadData = async () => {
  try {
    const res = await getRoles({
      page: pagination.value.page,
      page_size: pagination.value.pageSize
    })
    tableData.value = res.data.results || []
    pagination.value.total = res.data.count || 0
  } catch (error) {
    ElMessage.error('加载数据失败')
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
})
</script>

<style scoped>
.roles-page {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>

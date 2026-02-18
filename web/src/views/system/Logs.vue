<template>
  <div class="logs-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>操作日志</span>
        </div>
      </template>

      <el-form :inline="true" :model="queryForm" class="search-form">
        <el-form-item label="操作类型">
          <el-select v-model="queryForm.action" placeholder="全部" clearable style="width: 150px;">
            <el-option label="创建" value="create" />
            <el-option label="更新" value="update" />
            <el-option label="删除" value="delete" />
            <el-option label="登录" value="login" />
            <el-option label="登出" value="logout" />
            <el-option label="其他" value="other" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">查询</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>

      <el-table :data="tableData" border style="width: 100%">
        <el-table-column prop="username" label="操作用户" width="150" />
        <el-table-column label="操作类型" width="100">
          <template #default="{ row }">
            <el-tag :type="getActionType(row.action)">
              {{ getActionText(row.action) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="module" label="操作模块" width="150" />
        <el-table-column prop="detail" label="操作详情" />
        <el-table-column prop="ip_address" label="IP 地址" width="150" />
        <el-table-column prop="created_at" label="操作时间" width="180" />
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
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getLogs } from '../../api/system'
import { ElMessage } from 'element-plus'

const queryForm = ref({
  action: ''
})

const tableData = ref([])

const pagination = ref({
  page: 1,
  pageSize: 20,
  total: 0
})

const getActionType = (action) => {
  const typeMap = {
    create: 'success',
    update: 'primary',
    delete: 'danger',
    login: 'info',
    logout: 'warning',
    other: ''
  }
  return typeMap[action] || ''
}

const getActionText = (action) => {
  const textMap = {
    create: '创建',
    update: '更新',
    delete: '删除',
    login: '登录',
    logout: '登出',
    other: '其他'
  }
  return textMap[action] || action
}

const loadData = async () => {
  try {
    const res = await getLogs({
      ...queryForm.value,
      page: pagination.value.page,
      page_size: pagination.value.pageSize
    })
    tableData.value = res.data.results || []
    pagination.value.total = res.data.count || 0
  } catch (error) {
    ElMessage.error('加载数据失败')
  }
}

const handleSearch = () => {
  pagination.value.page = 1
  loadData()
}

const handleReset = () => {
  queryForm.value = { action: '' }
  pagination.value.page = 1
  loadData()
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.logs-page {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.search-form {
  margin-bottom: 20px;
}
</style>

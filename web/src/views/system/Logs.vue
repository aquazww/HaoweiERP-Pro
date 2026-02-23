<template>
  <div class="logs-page">
    <div class="page-content">
      <div class="toolbar-card">
        <div class="toolbar-left">
          <div class="search-box">
            <el-icon class="search-icon"><Search /></el-icon>
            <el-input
              v-model="searchKeyword"
              placeholder="搜索操作详情"
              class="search-input"
              clearable
              @keyup.enter="loadData"
            />
          </div>
          <el-select v-model="queryForm.action" placeholder="操作类型" clearable style="width: 140px" @change="handleSearch">
            <el-option label="全部" :value="''" />
            <el-option label="创建" value="create" />
            <el-option label="更新" value="update" />
            <el-option label="删除" value="delete" />
            <el-option label="登录" value="login" />
            <el-option label="登出" value="logout" />
            <el-option label="其他" value="other" />
          </el-select>
        </div>
        <div class="toolbar-right">
          <el-button :icon="Refresh" @click="handleReset">重置</el-button>
          <el-button type="primary" :icon="Search" @click="handleSearch">查询</el-button>
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
          <el-table-column label="操作用户" width="150">
            <template #default="{ row }">
              {{ row.user_name || row.username }}
            </template>
          </el-table-column>
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
          <el-table-column label="操作时间" width="160">
            <template #default="{ row }">
              {{ formatDateTime(row.created_at) }}
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
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick, onUnmounted } from 'vue'
import { getLogs } from '../../api/system'
import { ElMessage } from 'element-plus'
import { Search, Refresh } from '@element-plus/icons-vue'

const loading = ref(false)
const searchKeyword = ref('')
const tableHeight = ref(0)

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
      ...queryForm.value,
      page: pagination.value.page,
      page_size: pagination.value.pageSize
    }
    if (searchKeyword.value) {
      params.search = searchKeyword.value
    }
    const res = await getLogs(params)
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

const handleSearch = () => {
  pagination.value.page = 1
  loadData()
}

const handleReset = () => {
  queryForm.value = { action: '' }
  searchKeyword.value = ''
  pagination.value.page = 1
  loadData()
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
.logs-page {
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

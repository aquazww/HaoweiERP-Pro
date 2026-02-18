<template>
  <div class="goods-page">
    <div class="page-header">
      <div class="header-title-section">
        <div class="title-icon">
          <el-icon :size="24"><Goods /></el-icon>
        </div>
        <div class="title-content">
          <h1 class="page-title">商品管理</h1>
          <p class="page-subtitle">管理和维护所有商品信息</p>
        </div>
      </div>
      <div class="header-stats">
        <div class="stat-item">
          <div class="stat-value">{{ goodsList.length }}</div>
          <div class="stat-label">商品总数</div>
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
              placeholder="搜索商品编码、名称"
              class="search-input"
              clearable
              @keyup.enter="loadGoods"
            />
          </div>
        </div>
        <div class="toolbar-right">
          <el-button :icon="Refresh" @click="loadGoods">刷新</el-button>
          <el-button type="primary" :icon="Plus" @click="handleAdd">新增商品</el-button>
        </div>
      </div>

      <div class="table-card">
        <el-table 
          :data="goodsList" 
          style="width: 100%" 
          v-loading="loading"
          :height="tableHeight"
          class="data-table"
          stripe
        >
          <el-table-column type="index" label="#" width="60" align="center" />
          <el-table-column prop="code" label="商品编码" width="140">
            <template #default="{ row }">
              <span class="code-badge">{{ row.code }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="name" label="商品名称" min-width="200">
            <template #default="{ row }">
              <div class="name-cell">
                <div class="goods-initials">{{ getGoodsInitials(row.name) }}</div>
                <div class="goods-info">
                  <div class="goods-name">{{ row.name }}</div>
                  <div class="goods-category" v-if="row.category_name">{{ row.category_name }}</div>
                </div>
              </div>
            </template>
          </el-table-column>
          <el-table-column prop="unit" label="单位" width="80" align="center" />
          <el-table-column prop="purchase_price" label="进货价" width="120" align="right">
            <template #default="{ row }">
              <span class="price-text purchase">¥{{ formatPrice(row.purchase_price) }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="sale_price" label="销售价" width="120" align="right">
            <template #default="{ row }">
              <span class="price-text sale">¥{{ formatPrice(row.sale_price) }}</span>
            </template>
          </el-table-column>
          <el-table-column label="利润" width="120" align="right">
            <template #default="{ row }">
              <span class="price-text profit">¥{{ formatPrice(calculateProfit(row)) }}</span>
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
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick, onUnmounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Goods, Search, Refresh, Plus, Edit, Delete } from '@element-plus/icons-vue'
import { getGoods, deleteGoods } from '../../api/basic'

const loading = ref(false)
const goodsList = ref([])
const searchKeyword = ref('')
const tableHeight = ref(0)

const loadGoods = async () => {
  loading.value = true
  try {
    const params = {}
    if (searchKeyword.value) {
      params.search = searchKeyword.value
    }
    const res = await getGoods(params)
    goodsList.value = res.data.items || []
  } catch (error) {
    ElMessage.error('加载商品列表失败')
  } finally {
    loading.value = false
  }
}

const calculateTableHeight = () => {
  nextTick(() => {
    const pageHeader = document.querySelector('.page-header')
    const toolbarCard = document.querySelector('.toolbar-card')
    const pageContent = document.querySelector('.page-content')
    
    if (pageContent) {
      let usedHeight = 0
      if (pageHeader) usedHeight += pageHeader.offsetHeight + 24
      if (toolbarCard) usedHeight += toolbarCard.offsetHeight + 16
      usedHeight += 80
      
      const availableHeight = window.innerHeight - 64 - 48
      tableHeight.value = Math.max(availableHeight - usedHeight, 300)
    }
  })
}

const getGoodsInitials = (name) => {
  if (!name) return ''
  return name.slice(0, 2)
}

const formatPrice = (price) => {
  if (price === undefined || price === null) return '0.00'
  return Number(price).toFixed(2)
}

const calculateProfit = (row) => {
  const purchase = Number(row.purchase_price) || 0
  const sale = Number(row.sale_price) || 0
  return sale - purchase
}

const handleAdd = () => {
  ElMessage.info('新增商品功能开发中')
}

const handleEdit = (row) => {
  ElMessage.info('编辑商品功能开发中')
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm(`确定要删除商品「${row.name}」吗？`, '确认删除', {
      confirmButtonText: '确定删除',
      cancelButtonText: '取消',
      type: 'warning',
      confirmButtonClass: 'el-button--danger'
    })
    await deleteGoods(row.id)
    ElMessage.success('删除成功')
    loadGoods()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

onMounted(() => {
  loadGoods()
  calculateTableHeight()
  window.addEventListener('resize', calculateTableHeight)
})

onUnmounted(() => {
  window.removeEventListener('resize', calculateTableHeight)
})
</script>

<style scoped>
.goods-page {
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

.goods-initials {
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

.goods-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
  overflow: hidden;
}

.goods-name {
  font-weight: 500;
  color: var(--color-text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.goods-category {
  font-size: var(--font-size-xs);
  color: var(--color-text-tertiary);
}

.price-text {
  font-weight: 600;
  font-family: 'Monaco', 'Consolas', monospace;
}

.price-text.purchase {
  color: var(--color-warning);
}

.price-text.sale {
  color: var(--color-primary);
}

.price-text.profit {
  color: var(--color-success);
}

.action-buttons {
  display: flex;
  align-items: center;
  gap: var(--spacing-xs);
}
</style>

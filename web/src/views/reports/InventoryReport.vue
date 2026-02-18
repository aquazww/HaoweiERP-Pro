<template>
  <div class="inventory-report">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>库存报表</span>
          <el-button type="primary" :icon="Download" @click="handleExport">导出</el-button>
        </div>
      </template>
      
      <el-form :inline="true" :model="queryForm" class="search-form">
        <el-form-item label="商品">
          <el-input v-model="queryForm.goods_name" placeholder="请输入商品名称" clearable />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">查询</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>

      <el-table :data="tableData" border style="width: 100%">
        <el-table-column prop="goods_name" label="商品名称" />
        <el-table-column prop="goods_code" label="商品编码" width="120" />
        <el-table-column prop="specification" label="规格型号" width="120" />
        <el-table-column prop="unit_name" label="单位" width="80" />
        <el-table-column prop="category_name" label="分类" width="120" />
        <el-table-column prop="quantity" label="库存数量" width="120">
          <template #default="{ row }">
            <span :class="{ 'low-stock': row.quantity <= (row.min_stock || 0) }">
              {{ row.quantity }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="avg_price" label="平均成本" width="120">
          <template #default="{ row }">
            ¥{{ (row.avg_price !== undefined && row.avg_price !== null) ? row.avg_price.toFixed(2) : '0.00' }}
          </template>
        </el-table-column>
        <el-table-column prop="total_value" label="库存总值" width="120">
          <template #default="{ row }">
            ¥{{ (row.total_value !== undefined && row.total_value !== null) ? row.total_value.toFixed(2) : '0.00' }}
          </template>
        </el-table-column>
        <el-table-column prop="min_stock" label="预警库存" width="100" />
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
import { Download } from 'element-plus'
import { getInventoryReport } from '../../api/reports'
import { ElMessage } from 'element-plus'
import { exportToExcel } from '../../utils/export'

const queryForm = ref({
  goods_name: ''
})

const tableData = ref([])

const pagination = ref({
  page: 1,
  pageSize: 20,
  total: 0
})

const loadData = async () => {
  try {
    const res = await getInventoryReport({
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
  queryForm.value = {
    goods_name: ''
  }
  pagination.value.page = 1
  loadData()
}

const handleExport = async () => {
  if (tableData.value.length === 0) {
    ElMessage.warning('暂无数据可导出')
    return
  }
  
  const allData = []
  let page = 1
  
  try {
    while (true) {
      const res = await getInventoryReport({
        ...queryForm.value,
        page: page,
        page_size: 100
      })
      const results = res.data.results || []
      allData.push(...results)
      if (results.length < 100) break
      page++
    }
  } catch (error) {
    ElMessage.error('获取全部数据失败')
    return
  }
  
  const columns = [
    { key: 'goods_name', title: '商品名称' },
    { key: 'goods_code', title: '商品编码' },
    { key: 'specification', title: '规格型号' },
    { key: 'unit_name', title: '单位' },
    { key: 'category_name', title: '分类' },
    { key: 'quantity', title: '库存数量' },
    { key: 'avg_price', title: '平均成本' },
    { key: 'total_value', title: '库存总值' },
    { key: 'min_stock', title: '预警库存' }
  ]
  
  const exportData = allData.map(item => ({
    ...item,
    avg_price: '¥' + ((item.avg_price !== undefined && item.avg_price !== null) ? item.avg_price.toFixed(2) : '0.00'),
    total_value: '¥' + ((item.total_value !== undefined && item.total_value !== null) ? item.total_value.toFixed(2) : '0.00')
  }))
  
  const filename = `库存报表_${new Date().getTime()}`
  exportToExcel(exportData, columns, filename)
  ElMessage.success('导出成功')
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.inventory-report {
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

.low-stock {
  color: #f56c6c;
  font-weight: bold;
}
</style>

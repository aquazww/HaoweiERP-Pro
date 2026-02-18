<template>
  <div class="inventory-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>库存查询</span>
        </div>
      </template>
      
      <el-table :data="stockList" style="width: 100%" v-loading="loading">
        <el-table-column prop="goods_name" label="商品" width="200" />
        <el-table-column prop="warehouse_name" label="仓库" width="150" />
        <el-table-column prop="quantity" label="库存数量" width="120" />
        <el-table-column label="操作" width="150">
          <template #default="{ row }">
            <el-button type="primary" link @click="handleViewLogs(row)">流水</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getInventory } from '../../api/inventory'

const loading = ref(false)
const stockList = ref([])

const loadStock = async () => {
  loading.value = true
  try {
    const res = await getInventory()
    stockList.value = res.data.items || []
  } catch (error) {
    ElMessage.error('加载库存失败')
  } finally {
    loading.value = false
  }
}

const handleViewLogs = (row) => {
  ElMessage.info('库存流水功能开发中')
}

onMounted(() => {
  loadStock()
})
</script>

<style scoped>
.inventory-page {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>

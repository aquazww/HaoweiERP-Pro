<template>
  <div class="inventory-log-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>库存流水</span>
        </div>
      </template>
      
      <el-form :inline="true" :model="queryForm" style="margin-bottom: 20px;">
        <el-form-item label="商品">
          <el-input v-model="queryForm.goods" placeholder="请输入商品名称" clearable />
        </el-form-item>
        <el-form-item label="变动类型">
          <el-select v-model="queryForm.change_type" placeholder="请选择" clearable style="width: 150px;">
            <el-option label="入库" value="in" />
            <el-option label="出库" value="out" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="loadLogs">查询</el-button>
        </el-form-item>
      </el-form>
      
      <el-table :data="logList" style="width: 100%" v-loading="loading">
        <el-table-column prop="created_at" label="时间" width="180" />
        <el-table-column prop="goods_name" label="商品" width="200" />
        <el-table-column prop="warehouse_name" label="仓库" width="150" />
        <el-table-column prop="change_type_display" label="变动类型" width="100">
          <template #default="{ row }">
            <el-tag :type="row.change_type === 'in' ? 'success' : 'danger'">
              {{ row.change_type_display }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="change_quantity" label="变动数量" width="120" />
        <el-table-column prop="before_quantity" label="变动前" width="120" />
        <el-table-column prop="after_quantity" label="变动后" width="120" />
        <el-table-column prop="remark" label="备注" min-width="200" />
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getInventoryLogs } from '../../api/inventory'

const loading = ref(false)
const logList = ref([])
const queryForm = ref({
  goods: '',
  change_type: ''
})

const loadLogs = async () => {
  loading.value = true
  try {
    const params = {}
    if (queryForm.value.change_type) {
      params.change_type = queryForm.value.change_type
    }
    const res = await getInventoryLogs(params)
    logList.value = res.data.items || []
  } catch (error) {
    ElMessage.error('加载库存流水失败')
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadLogs()
})
</script>

<style scoped>
.inventory-log-page {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>

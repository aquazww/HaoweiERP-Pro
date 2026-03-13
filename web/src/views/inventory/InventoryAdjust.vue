<template>
  <div class="inventory-adjust-page">
    <div class="page-content">
      <div class="toolbar-card">
        <div class="toolbar-left">
          <div class="search-box">
            <el-icon class="search-icon"><Search /></el-icon>
            <el-input
              v-model="searchKeyword"
              placeholder="搜索商品名称、仓库"
              class="search-input"
              clearable
              @keyup.enter="loadAdjusts"
            />
          </div>
          <el-select v-model="statusFilter" placeholder="状态筛选" clearable style="width: 140px" @change="loadAdjusts">
            <el-option label="全部" :value="''" />
            <el-option label="待审核" value="pending" />
            <el-option label="已通过" value="approved" />
            <el-option label="已拒绝" value="rejected" />
          </el-select>
        </div>
        <div class="toolbar-right">
          <el-button :icon="Refresh" @click="loadAdjusts">刷新</el-button>
          <el-button type="primary" :icon="Plus" @click="handleAdd" v-if="canAddAdjust">新增调整</el-button>
        </div>
      </div>

      <div class="table-card">
        <el-table 
          :data="adjustList" 
          style="width: 100%" 
          v-loading="loading"
          :height="tableHeight"
          class="data-table"
          stripe
        >
          <el-table-column prop="warehouse_name" label="仓库" min-width="120" align="center" />
          <el-table-column prop="goods_name" label="商品名称" min-width="180" show-overflow-tooltip />
          <el-table-column prop="original_quantity" label="原库存" width="100" align="center">
            <template #default="{ row }">
              <span class="quantity-text">{{ formatQuantity(row.original_quantity) }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="adjust_quantity" label="调整数量" width="100" align="center">
            <template #default="{ row }">
              <span :class="row.adjust_quantity >= 0 ? 'quantity-in' : 'quantity-out'">
                {{ row.adjust_quantity >= 0 ? '+' : '' }}{{ formatQuantity(row.adjust_quantity) }}
              </span>
            </template>
          </el-table-column>
          <el-table-column prop="new_quantity" label="新库存" width="100" align="center">
            <template #default="{ row }">
              <span class="quantity-text new">{{ formatQuantity(row.new_quantity) }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="status" label="状态" width="100" align="center">
            <template #default="{ row }">
              <el-tag :type="getStatusType(row.status)">{{ getStatusText(row.status) }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="reason" label="调整原因" min-width="150" show-overflow-tooltip />
          <el-table-column prop="created_at" label="创建时间" width="160" align="center">
            <template #default="{ row }">
              {{ formatDateTime(row.created_at) }}
            </template>
          </el-table-column>
          <el-table-column label="操作" width="150" align="center" fixed="right">
            <template #default="{ row }">
              <el-button 
                type="success" 
                link 
                size="small" 
                @click="handleApprove(row)" 
                v-if="canApprove && row.status === 'pending'"
              >
                通过
              </el-button>
              <el-button 
                type="danger" 
                link 
                size="small" 
                @click="handleReject(row)" 
                v-if="canApprove && row.status === 'pending'"
              >
                拒绝
              </el-button>
              <el-button 
                type="danger" 
                link 
                size="small" 
                @click="handleDelete(row)" 
                v-if="canDeleteAdjust && row.status === 'pending'"
              >
                删除
              </el-button>
            </template>
          </el-table-column>
        </el-table>
        <div class="pagination-wrapper">
          <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :page-sizes="[20, 50, 100]"
            :total="total"
            layout="total, sizes, prev, pager, next, jumper"
            @size-change="loadAdjusts"
            @current-change="loadAdjusts"
          />
        </div>
      </div>
    </div>

    <!-- 新增调整弹窗 -->
    <el-dialog 
      v-model="dialogVisible" 
      title="新增库存调整" 
      width="600px"
      :close-on-click-modal="false"
    >
      <el-form 
        ref="formRef" 
        :model="form" 
        :rules="rules" 
        label-width="100px"
        class="adjust-form"
      >
        <el-form-item label="仓库" prop="warehouse">
          <el-select v-model="form.warehouse" placeholder="请选择仓库" style="width: 100%">
            <el-option 
              v-for="item in warehouseList" 
              :key="item.id" 
              :label="item.name" 
              :value="item.id" 
            />
          </el-select>
        </el-form-item>
        <el-form-item label="商品" prop="goods">
          <el-select 
            v-model="form.goods" 
            placeholder="请选择商品" 
            style="width: 100%"
            filterable
            @change="handleGoodsChange"
          >
            <el-option 
              v-for="item in goodsList" 
              :key="item.id" 
              :label="item.name" 
              :value="item.id" 
            />
          </el-select>
        </el-form-item>
        <el-form-item label="当前库存">
          <span class="current-stock">{{ formatQuantity(currentStock) }}</span>
        </el-form-item>
        <el-form-item label="调整后库存" prop="new_quantity">
          <el-input-number 
            v-model="form.new_quantity" 
            :min="0"
            :max="999999999"
            style="width: 100%"
            @change="handleQuantityChange"
          />
        </el-form-item>
        <el-form-item label="调整数量">
          <span :class="adjustQuantity >= 0 ? 'quantity-in' : 'quantity-out'">
            {{ adjustQuantity >= 0 ? '+' : '' }}{{ formatQuantity(adjustQuantity) }}
          </span>
        </el-form-item>
        <el-form-item label="调整原因" prop="reason">
          <el-input 
            v-model="form.reason" 
            type="textarea" 
            :rows="3"
            placeholder="请输入调整原因"
            maxlength="500"
            show-word-limit
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleSubmit" :loading="submitLoading">确定</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { Plus, Refresh, Search } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getStockAdjustList, getStockAdjust, createStockIn, confirmStockIn, deleteInventory } from '@/api/inventory'
import { getWarehouses, getGoods } from '@/api/basic'
import { formatQuantity } from '@/utils/format'
import { canAdd, canEdit, canDelete } from '@/utils/permission'

const canAddAdjust = canAdd('inventory')
const canDeleteAdjust = canDelete('inventory')
const canApprove = canEdit('inventory')

const loading = ref(false)
const adjustList = ref([])
const searchKeyword = ref('')
const statusFilter = ref('')
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)
const tableHeight = ref(0)

const dialogVisible = ref(false)
const submitLoading = ref(false)
const formRef = ref(null)
const warehouseList = ref([])
const goodsList = ref([])

const form = reactive({
  warehouse: null,
  goods: null,
  new_quantity: 0,
  reason: ''
})

const rules = {
  warehouse: [{ required: true, message: '请选择仓库', trigger: 'change' }],
  goods: [{ required: true, message: '请选择商品', trigger: 'change' }],
  new_quantity: [{ required: true, message: '请输入调整后库存', trigger: 'blur' }],
  reason: [{ required: true, message: '请输入调整原因', trigger: 'blur' }]
}

const currentStock = ref(0)

const adjustQuantity = computed(() => {
  return form.new_quantity - currentStock.value
})

const getStatusText = (status) => {
  const textMap = {
    pending: '待审核',
    approved: '已通过',
    rejected: '已拒绝'
  }
  return textMap[status] || status
}

const getStatusType = (status) => {
  const typeMap = {
    pending: 'warning',
    approved: 'success',
    rejected: 'danger'
  }
  return typeMap[status] || 'info'
}

const formatDateTime = (datetime) => {
  if (!datetime) return '-'
  return datetime.replace('T', ' ').substring(0, 19)
}

const loadAdjusts = async () => {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      page_size: pageSize.value
    }
    if (searchKeyword.value) {
      params.search = searchKeyword.value
    }
    if (statusFilter.value) {
      params.status = statusFilter.value
    }
    
    const res = await getStockAdjustList(params)
    adjustList.value = res.data?.items || res.data?.results || []
    total.value = res.data?.count || 0
  } catch (error) {
    ElMessage.error('加载数据失败')
  } finally {
    loading.value = false
  }
}

const loadWarehouses = async () => {
  try {
    const res = await getWarehouses({ page_size: 1000, is_active: true })
    warehouseList.value = res.data?.items || res.data?.results || []
  } catch (error) {
    warehouseList.value = []
  }
}

const loadGoods = async () => {
  try {
    const res = await getGoods({ page_size: 1000, status: 1 })
    goodsList.value = res.data?.items || res.data?.results || []
  } catch (error) {
    goodsList.value = []
  }
}

const handleAdd = () => {
  form.warehouse = null
  form.goods = null
  form.new_quantity = 0
  form.reason = ''
  currentStock.value = 0
  dialogVisible.value = true
}

const handleGoodsChange = async () => {
  if (!form.warehouse || !form.goods) {
    currentStock.value = 0
    return
  }
  
  try {
    const res = await getInventoryStock({
      warehouse: form.warehouse,
      goods: form.goods
    })
    currentStock.value = res.data?.quantity || 0
    form.new_quantity = currentStock.value
  } catch (error) {
    currentStock.value = 0
  }
}

const handleQuantityChange = () => {
  // 调整数量自动计算
}

const handleSubmit = async () => {
  if (!formRef.value) return
  
  try {
    await formRef.value.validate()
  } catch (error) {
    return
  }
  
  submitLoading.value = true
  try {
    const data = {
      warehouse: form.warehouse,
      goods: form.goods,
      new_quantity: form.new_quantity,
      reason: form.reason
    }
    
    await createStockIn(data)
    ElMessage.success('新增成功')
    dialogVisible.value = false
    loadAdjusts()
  } catch (error) {
    ElMessage.error('新增失败')
  } finally {
    submitLoading.value = false
  }
}

const handleApprove = async (row) => {
  try {
    await ElMessageBox.confirm('确定通过此调整申请？', '提示', { type: 'warning' })
    await confirmStockIn(row.id)
    ElMessage.success('已通过')
    loadAdjusts()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('操作失败')
    }
  }
}

const handleReject = async (row) => {
  try {
    await ElMessageBox.confirm('确定拒绝此调整申请？', '提示', { type: 'warning' })
    await deleteInventory(row.id)
    ElMessage.success('已拒绝')
    loadAdjusts()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('操作失败')
    }
  }
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm('确定删除此调整记录？', '确认删除', { type: 'warning' })
    await deleteInventory(row.id)
    ElMessage.success('删除成功')
    loadAdjusts()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

onMounted(() => {
  loadWarehouses()
  loadGoods()
  loadAdjusts()
})
</script>

<style scoped>
.inventory-adjust-page {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.page-content {
  flex: 1;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 16px;
  overflow: hidden;
}

.toolbar-card {
  background: #fff;
  border-radius: 8px;
  padding: 16px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.08);
}

.toolbar-left {
  display: flex;
  gap: 12px;
  align-items: center;
}

.search-box {
  position: relative;
  width: 280px;
}

.search-icon {
  position: absolute;
  left: 10px;
  top: 50%;
  transform: translateY(-50%);
  color: #909399;
}

.search-input :deep(.el-input__wrapper) {
  padding-left: 30px;
}

.toolbar-right {
  display: flex;
  gap: 10px;
}

.table-card {
  flex: 1;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.08);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.data-table {
  flex: 1;
}

.quantity-text {
  color: #606266;
  font-weight: 500;
}

.quantity-text.new {
  color: #409eff;
}

.quantity-in {
  color: #67c23a;
  font-weight: 500;
}

.quantity-out {
  color: #f56c6c;
  font-weight: 500;
}

.pagination-wrapper {
  padding: 12px 16px;
  border-top: 1px solid #f0f0f0;
  display: flex;
  justify-content: flex-end;
}

.adjust-form {
  padding: 10px 20px;
}

.current-stock {
  font-size: 16px;
  font-weight: 500;
  color: #409eff;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}
</style>

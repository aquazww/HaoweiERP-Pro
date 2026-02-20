<template>
  <div class="transfer-page">
    <div class="page-content">
      <div class="toolbar-card">
        <div class="toolbar-left">
          <div class="search-box">
            <el-icon class="search-icon"><Search /></el-icon>
            <el-input v-model="searchKeyword" placeholder="搜索调拨单号" class="search-input" clearable @keyup.enter="loadTransfers" />
          </div>
          <el-select v-model="statusFilter" placeholder="状态筛选" clearable style="width: 120px" @change="loadTransfers">
            <el-option label="全部" :value="''" />
            <el-option label="草稿" value="draft" />
            <el-option label="已确认" value="confirmed" />
          </el-select>
        </div>
        <div class="toolbar-right">
          <el-button :icon="Refresh" @click="loadTransfers">刷新</el-button>
          <el-button type="primary" :icon="Plus" @click="handleAdd">新增调拨单</el-button>
        </div>
      </div>

      <div class="table-card">
        <el-table :data="transferList" style="width: 100%" v-loading="loading" :height="tableHeight" class="data-table" stripe>
          <el-table-column type="index" label="#" width="50" align="center" />
          <el-table-column prop="order_no" label="调拨单号" width="160">
            <template #default="{ row }">
              <span class="order-no-badge">{{ row.order_no }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="from_warehouse_name" label="调出仓库" width="120" />
          <el-table-column width="50" align="center">
            <template #default>
              <el-icon class="transfer-icon"><Right /></el-icon>
            </template>
          </el-table-column>
          <el-table-column prop="to_warehouse_name" label="调入仓库" width="120" />
          <el-table-column label="调拨明细" min-width="200">
            <template #default="{ row }">
              <span class="items-preview">{{ getItemsPreview(row.items) }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="status" label="状态" width="90">
            <template #default="{ row }">
              <div class="status-badge" :class="row.status">
                <span class="status-dot"></span>
                {{ getStatusText(row.status) }}
              </div>
            </template>
          </el-table-column>
          <el-table-column prop="created_at" label="创建时间" width="160">
            <template #default="{ row }">{{ formatDateTime(row.created_at) }}</template>
          </el-table-column>
          <el-table-column label="操作" width="180" fixed="right">
            <template #default="{ row }">
              <div class="action-buttons">
                <el-button type="primary" link :icon="View" size="small" @click="handleView(row)">查看</el-button>
                <el-button type="success" link size="small" @click="handleConfirm(row)" v-if="row.status === 'draft'">确认</el-button>
                <el-button type="danger" link :icon="Delete" size="small" @click="handleDelete(row)" v-if="row.status === 'draft'">删除</el-button>
              </div>
            </template>
          </el-table-column>
        </el-table>
        <div class="pagination-wrapper">
          <el-pagination v-model:current-page="currentPage" v-model:page-size="pageSize" :page-sizes="[10, 20, 50, 100]" :total="total" layout="total, sizes, prev, pager, next, jumper" @size-change="loadTransfers" @current-change="loadTransfers" />
        </div>
      </div>
    </div>

    <!-- 新增弹窗 -->
    <el-dialog v-model="dialogVisible" title="新增库存调拨单" width="900px" class="form-dialog" destroy-on-close @close="resetForm">
      <el-form :model="form" :rules="rules" ref="formRef" label-width="100px">
        <div class="form-section">
          <div class="section-title">基本信息</div>
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="调出仓库" prop="from_warehouse">
                <el-select v-model="form.from_warehouse" placeholder="请选择调出仓库" style="width: 100%" @change="loadCurrentStock">
                  <el-option v-for="item in warehouseList" :key="item.id" :label="item.name" :value="item.id" :disabled="item.id === form.to_warehouse" />
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="调入仓库" prop="to_warehouse">
                <el-select v-model="form.to_warehouse" placeholder="请选择调入仓库" style="width: 100%">
                  <el-option v-for="item in warehouseList" :key="item.id" :label="item.name" :value="item.id" :disabled="item.id === form.from_warehouse" />
                </el-select>
              </el-form-item>
            </el-col>
          </el-row>
          <el-form-item label="备注">
            <el-input v-model="form.remark" type="textarea" :rows="2" placeholder="请输入备注" />
          </el-form-item>
        </div>

        <div class="form-section">
          <div class="section-title">调拨明细</div>
          <div class="detail-table-wrapper">
            <el-table :data="form.items" border style="width: 100%;" class="detail-table">
              <el-table-column prop="goods" label="商品" min-width="200">
                <template #default="{ row }">
                  <el-select v-model="row.goods" placeholder="选择商品" style="width: 100%" filterable @change="handleGoodsChange(row)">
                    <el-option v-for="item in goodsList" :key="item.id" :label="item.name" :value="item.id" />
                  </el-select>
                </template>
              </el-table-column>
              <el-table-column label="当前库存" width="100" align="right">
                <template #default="{ row }">{{ row.current_quantity || '-' }}</template>
              </el-table-column>
              <el-table-column prop="quantity" label="调拨数量" width="150">
                <template #default="{ row }">
                  <div class="input-cell" :class="{ 'has-error': row._quantityError }">
                    <el-input :model-value="formatInputNumber(row.quantity, true)" @input="(val) => handleQuantityInput(row, val)" @blur="handleQuantityBlur(row)" placeholder="请输入" class="number-input" :class="{ 'is-error': row._quantityError }" />
                    <div class="error-tip" v-if="row._quantityError">{{ row._quantityError }}</div>
                  </div>
                </template>
              </el-table-column>
              <el-table-column label="操作" width="70" align="center">
                <template #default="{ $index }">
                  <el-button type="danger" link :icon="Delete" size="small" @click="removeItem($index)"></el-button>
                </template>
              </el-table-column>
            </el-table>
          </div>
          <div class="detail-footer">
            <el-button type="primary" plain :icon="Plus" @click="addItem">添加明细</el-button>
          </div>
        </div>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleSubmit" :loading="submitLoading">创建调拨单</el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 查看弹窗 -->
    <el-dialog v-model="viewDialogVisible" title="调拨单详情" width="800px" class="view-dialog" destroy-on-close>
      <el-descriptions :column="2" border class="view-descriptions">
        <el-descriptions-item label="调拨单号">{{ viewData.order_no }}</el-descriptions-item>
        <el-descriptions-item label="调出仓库">{{ viewData.from_warehouse_name }}</el-descriptions-item>
        <el-descriptions-item label="调入仓库">{{ viewData.to_warehouse_name }}</el-descriptions-item>
        <el-descriptions-item label="状态">
          <div class="status-badge" :class="viewData.status">
            <span class="status-dot"></span>
            {{ getStatusText(viewData.status) }}
          </div>
        </el-descriptions-item>
        <el-descriptions-item label="创建时间">{{ formatDateTime(viewData.created_at) }}</el-descriptions-item>
        <el-descriptions-item label="备注">{{ viewData.remark || '-' }}</el-descriptions-item>
      </el-descriptions>
      <div class="view-items-title">调拨明细</div>
      <el-table :data="viewData.items" border style="width: 100%;">
        <el-table-column type="index" label="#" width="50" align="center" />
        <el-table-column prop="goods_name" label="商品名称" min-width="180" />
        <el-table-column prop="quantity" label="调拨数量" width="120" align="right" />
      </el-table>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick, onUnmounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Refresh, Plus, Delete, View, Right } from '@element-plus/icons-vue'
import { getWarehouses, getGoods } from '../../api/basic'
import { getInventory } from '../../api/inventory'
import { formatInputNumber, parseInputNumber } from '../../utils/format'
import request from '../../api/index'

const loading = ref(false)
const submitLoading = ref(false)
const dialogVisible = ref(false)
const viewDialogVisible = ref(false)
const formRef = ref(null)
const transferList = ref([])
const warehouseList = ref([])
const goodsList = ref([])
const searchKeyword = ref('')
const statusFilter = ref('')
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)
const tableHeight = ref(0)

const viewData = ref({ items: [] })

const form = ref({
  from_warehouse: '',
  to_warehouse: '',
  remark: '',
  items: []
})

const rules = {
  from_warehouse: [{ required: true, message: '请选择调出仓库', trigger: 'change' }],
  to_warehouse: [{ required: true, message: '请选择调入仓库', trigger: 'change' }]
}

const getStatusText = (status) => {
  const textMap = { 'draft': '草稿', 'confirmed': '已确认', 'cancelled': '已取消' }
  return textMap[status] || status
}

const formatDateTime = (datetime) => {
  if (!datetime) return '-'
  return datetime.replace('T', ' ').substring(0, 19)
}

const getItemsPreview = (items) => {
  if (!items || items.length === 0) return '-'
  const names = items.slice(0, 3).map(i => i.goods_name).join('、')
  return items.length > 3 ? `${names}等${items.length}项` : names
}

const loadCurrentStock = async () => {
  if (!form.value.from_warehouse) return
  for (const item of form.value.items) {
    if (item.goods) {
      await handleGoodsChange(item)
    }
  }
}

const handleGoodsChange = async (row) => {
  if (form.value.from_warehouse && row.goods) {
    try {
      const res = await getInventory({ goods: row.goods, warehouse: form.value.from_warehouse })
      const items = res.data.items || res.data.results || []
      row.current_quantity = items.length > 0 ? items[0].quantity : 0
    } catch (error) {
      row.current_quantity = 0
    }
  }
}

const handleQuantityInput = (row, value) => {
  row._quantityError = ''
  const num = parseInputNumber(value)
  row.quantity = num
}

const handleQuantityBlur = (row) => {
  if (row.quantity === null || row.quantity === undefined || row.quantity === '') {
    row._quantityError = '请输入数量'
    return
  }
  if (row.quantity <= 0) {
    row._quantityError = '数量必须大于0'
    return
  }
  if (row.current_quantity !== undefined && row.quantity > row.current_quantity) {
    row._quantityError = '调拨数量不能超过当前库存'
    return
  }
  row._quantityError = ''
}

const loadTransfers = async () => {
  loading.value = true
  try {
    const params = { page: currentPage.value, page_size: pageSize.value }
    if (searchKeyword.value) params.search = searchKeyword.value
    if (statusFilter.value) params.status = statusFilter.value
    const res = await request.get('/inventory/transfer/', { params })
    transferList.value = res.data.items || res.data.results || []
    total.value = res.data.count || 0
  } catch (error) {
    transferList.value = []
    total.value = 0
    ElMessage.error('加载数据失败')
  } finally {
    loading.value = false
  }
}

const loadOptions = async () => {
  try {
    const [whRes, goodsRes] = await Promise.all([getWarehouses(), getGoods()])
    warehouseList.value = whRes.data.items || whRes.data.results || []
    goodsList.value = goodsRes.data.items || goodsRes.data.results || []
  } catch (error) {
    ElMessage.error('加载选项失败')
  }
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

const handleAdd = () => {
  form.value = { from_warehouse: '', to_warehouse: '', remark: '', items: [] }
  dialogVisible.value = true
}

const handleView = async (row) => {
  try {
    const res = await request.get(`/inventory/transfer/${row.id}/`)
    viewData.value = res.data.data || res.data
    viewDialogVisible.value = true
  } catch (error) {
    ElMessage.error('加载详情失败')
  }
}

const handleConfirm = async (row) => {
  try {
    await ElMessageBox.confirm('确认此调拨单？确认后将更新库存。', '确认调拨', { type: 'warning' })
    await request.post(`/inventory/transfer/${row.id}/confirm/`)
    ElMessage.success('确认成功')
    loadTransfers()
  } catch (error) {
    if (error !== 'cancel') ElMessage.error('确认失败')
  }
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm(`确定删除调拨单「${row.order_no}」？`, '确认删除', { type: 'warning' })
    await request.delete(`/inventory/transfer/${row.id}/`)
    ElMessage.success('删除成功')
    loadTransfers()
  } catch (error) {
    if (error !== 'cancel') ElMessage.error('删除失败')
  }
}

const addItem = () => {
  form.value.items.push({ goods: '', current_quantity: 0, quantity: null, _quantityError: '' })
}

const removeItem = (index) => {
  form.value.items.splice(index, 1)
}

const handleSubmit = async () => {
  try {
    await formRef.value.validate()
  } catch (error) {
    ElMessage.warning('请检查表单')
    return
  }
  
  if (form.value.items.length === 0) {
    ElMessage.warning('请添加调拨明细')
    return
  }
  
  const hasError = form.value.items.some(item => item._quantityError || !item.goods || !item.quantity)
  if (hasError) {
    ElMessage.warning('请检查明细数据')
    return
  }
  
  submitLoading.value = true
  try {
    const data = {
      from_warehouse: form.value.from_warehouse,
      to_warehouse: form.value.to_warehouse,
      remark: form.value.remark,
      items: form.value.items.map(item => ({ goods: item.goods, quantity: item.quantity }))
    }
    await request.post('/inventory/transfer/', data)
    ElMessage.success('创建成功')
    dialogVisible.value = false
    loadTransfers()
  } catch (error) {
    ElMessage.error('创建失败：' + (error.response?.data?.msg || error.message || '未知错误'))
  } finally {
    submitLoading.value = false
  }
}

const resetForm = () => {
  if (formRef.value) formRef.value.resetFields()
}

onMounted(() => {
  loadTransfers()
  loadOptions()
  calculateTableHeight()
  window.addEventListener('resize', calculateTableHeight)
})

onUnmounted(() => {
  window.removeEventListener('resize', calculateTableHeight)
})
</script>

<style scoped>
@import './inventory-common.css';
.transfer-icon {
  color: var(--color-primary);
  font-size: 16px;
}
</style>

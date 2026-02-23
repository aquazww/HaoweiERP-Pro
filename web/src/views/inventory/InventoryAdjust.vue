<template>
  <div class="adjust-page">
    <div class="page-content">
      <div class="toolbar-card">
        <div class="toolbar-left">
          <div class="search-box">
            <el-icon class="search-icon"><Search /></el-icon>
            <el-input
              v-model="searchKeyword"
              placeholder="搜索调整单号"
              class="search-input"
              clearable
              @keyup.enter="loadAdjusts"
            />
          </div>
          <el-select v-model="statusFilter" placeholder="状态筛选" clearable style="width: 120px" @change="loadAdjusts">
            <el-option label="全部" :value="''" />
            <el-option label="草稿" value="draft" />
            <el-option label="已确认" value="confirmed" />
          </el-select>
        </div>
        <div class="toolbar-right">
          <el-button :icon="Refresh" @click="loadAdjusts">刷新</el-button>
          <el-button type="primary" :icon="Plus" @click="handleAdd" v-if="canAddInventory">新增调整单</el-button>
        </div>
      </div>

      <div class="table-card">
        <el-table :data="adjustList" style="width: 100%" v-loading="loading" :height="tableHeight" class="data-table" stripe :header-cell-style="{ background: 'var(--color-bg-light)' }">
          <el-table-column prop="order_no" label="调整单号" min-width="150" align="center">
            <template #default="{ row }">
              <span class="order-no-badge">{{ row.order_no }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="warehouse_name" label="仓库" min-width="100" show-overflow-tooltip />
          <el-table-column prop="adjust_type_display" label="调整类型" min-width="90" align="center">
            <template #default="{ row }">
              <el-tag :type="row.adjust_type === 'increase' ? 'success' : 'danger'" size="small">
                {{ row.adjust_type_display }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="reason_display" label="调整原因" min-width="90" show-overflow-tooltip />
          <el-table-column label="调整明细" min-width="180" show-overflow-tooltip>
            <template #default="{ row }">
              <span class="items-preview">{{ getItemsPreview(row.items) }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="status" label="状态" min-width="80" align="center">
            <template #default="{ row }">
              <div class="status-badge" :class="row.status">
                <span class="status-dot"></span>
                {{ getStatusText(row.status) }}
              </div>
            </template>
          </el-table-column>
          <el-table-column label="创建时间" min-width="140">
            <template #default="{ row }">{{ formatDateTime(row.created_at) }}</template>
          </el-table-column>
          <el-table-column label="操作" min-width="160" align="center">
            <template #default="{ row }">
              <div class="action-buttons">
                <el-button type="primary" link :icon="View" size="small" @click="handleView(row)">查看</el-button>
                <el-button type="success" link size="small" @click="handleConfirm(row)" v-if="canEditInventory && row.status === 'draft'">确认</el-button>
                <el-button type="danger" link :icon="Delete" size="small" @click="handleDelete(row)" v-if="canDeleteInventory && row.status === 'draft'">删除</el-button>
              </div>
            </template>
          </el-table-column>
        </el-table>
        <div class="pagination-wrapper">
          <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :page-sizes="[10, 20, 50, 100]"
            :total="total"
            layout="total, sizes, prev, pager, next, jumper"
            @size-change="loadAdjusts"
            @current-change="loadAdjusts"
          />
        </div>
      </div>
    </div>

    <!-- 新增弹窗 -->
    <el-dialog v-model="dialogVisible" title="新增库存调整单" width="900px" class="form-dialog" destroy-on-close @close="resetForm">
      <el-form :model="form" :rules="rules" ref="formRef" label-width="100px">
        <div class="form-section">
          <div class="section-title">基本信息</div>
          <el-row :gutter="20">
            <el-col :span="8">
              <el-form-item label="仓库" prop="warehouse">
                <el-select v-model="form.warehouse" placeholder="请选择仓库" style="width: 100%">
                  <el-option v-for="item in warehouseList" :key="item.id" :label="item.name" :value="item.id" />
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item label="调整类型" prop="adjust_type">
                <el-select v-model="form.adjust_type" placeholder="请选择" style="width: 100%">
                  <el-option label="库存增加" value="increase" />
                  <el-option label="库存减少" value="decrease" />
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item label="调整原因" prop="reason">
                <el-select v-model="form.reason" placeholder="请选择" style="width: 100%">
                  <el-option label="盘点调整" value="check" />
                  <el-option label="商品损耗" value="damage" />
                  <el-option label="退货入库" value="return" />
                  <el-option label="其他原因" value="other" />
                </el-select>
              </el-form-item>
            </el-col>
          </el-row>
          <el-form-item label="备注">
            <el-input v-model="form.remark" type="textarea" :rows="2" placeholder="请输入备注" />
          </el-form-item>
        </div>

        <div class="form-section">
          <div class="section-title">调整明细</div>
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
              <el-table-column prop="adjust_quantity" label="调整数量" width="150">
                <template #default="{ row }">
                  <div class="input-cell" :class="{ 'has-error': row._quantityError }">
                    <el-input
                      :model-value="formatInputNumber(row.adjust_quantity, true)"
                      @input="(val) => handleQuantityInput(row, val)"
                      @blur="handleQuantityBlur(row)"
                      placeholder="请输入"
                      class="number-input"
                      :class="{ 'is-error': row._quantityError }"
                    />
                    <div class="error-tip" v-if="row._quantityError">{{ row._quantityError }}</div>
                  </div>
                </template>
              </el-table-column>
              <el-table-column label="调整后" width="100" align="right">
                <template #default="{ row }">
                  <span :class="getAfterQuantityClass(row)">{{ getAfterQuantity(row) }}</span>
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
          <el-button type="primary" @click="handleSubmit" :loading="submitLoading">创建调整单</el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 查看弹窗 -->
    <el-dialog
      v-model="viewDialogVisible"
      width="700px"
      class="view-dialog"
      :show-close="false"
    >
      <template #header>
        <div class="dialog-header">
          <span class="dialog-title">调整单详情</span>
          <div class="status-badge small" :class="viewData?.status" v-if="viewData">
            <span class="status-dot"></span>
            {{ getStatusText(viewData?.status) }}
          </div>
        </div>
        <span class="close-btn" @click="viewDialogVisible = false">×</span>
      </template>
      
      <div class="detail-container" v-if="viewData">
        <div class="info-section">
          <div class="info-row highlight-row">
            <div class="info-item-group">
              <span class="info-label">仓库</span>
              <span class="info-value">{{ viewData.warehouse_name }}</span>
            </div>
            <div class="info-item-group">
              <span class="info-label">调整单号</span>
              <span class="info-value primary">{{ viewData.order_no }}</span>
            </div>
          </div>
          <div class="info-row highlight-row">
            <div class="info-item-group">
              <span class="info-label">调整类型</span>
              <span class="info-value">{{ viewData.adjust_type_display }}</span>
            </div>
            <div class="info-item-group">
              <span class="info-label">调整原因</span>
              <span class="info-value">{{ viewData.reason_display }}</span>
            </div>
          </div>
          <div class="info-row">
            <div class="info-item">
              <span class="info-label">创建时间</span>
              <span class="info-value">{{ formatDateTime(viewData.created_at) }}</span>
            </div>
          </div>
        </div>
        
        <div class="remark-box" v-if="viewData.remark">
          <div class="remark-header">
            <el-icon class="remark-icon"><Document /></el-icon>
            <span>备注</span>
          </div>
          <div class="remark-text">{{ viewData.remark }}</div>
        </div>
        
        <div class="items-section">
          <div class="items-header" @click="itemsExpanded = !itemsExpanded">
            <div class="header-left">
              <el-icon class="expand-icon" :class="{ expanded: itemsExpanded }"><ArrowRight /></el-icon>
              <span class="header-title">调整明细</span>
              <span class="header-count">{{ viewData.items?.length || 0 }}项</span>
            </div>
            <span class="expand-hint">{{ itemsExpanded ? '收起' : '展开' }}</span>
          </div>
          <el-collapse-transition>
            <div class="items-body" v-show="itemsExpanded">
              <el-table :data="viewData.items" border size="small" class="detail-table">
                <el-table-column prop="goods_name" label="商品" min-width="140">
                  <template #default="{ row }">
                    <div class="goods-cell">
                      <span class="goods-name">{{ row.goods_name }}</span>
                      <span class="goods-spec">{{ row.goods_spec || '-' }}</span>
                    </div>
                  </template>
                </el-table-column>
                <el-table-column prop="before_quantity" label="调整前" width="75" align="center" />
                <el-table-column prop="adjust_quantity" label="调整量" width="75" align="center">
                  <template #default="{ row }">
                    <span :class="row.adjust_quantity >= 0 ? 'quantity-cell increase' : 'quantity-cell decrease'">
                      {{ row.adjust_quantity >= 0 ? '+' : '' }}{{ row.adjust_quantity }}
                    </span>
                  </template>
                </el-table-column>
                <el-table-column prop="after_quantity" label="调整后" width="75" align="center" />
              </el-table>
            </div>
          </el-collapse-transition>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick, onUnmounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Refresh, Plus, Delete, View, Document, ArrowRight } from '@element-plus/icons-vue'
import { getWarehouses, getGoods } from '../../api/basic'
import { getInventory } from '../../api/inventory'
import { formatInputNumber, parseInputNumber } from '../../utils/format'
import { canAdd, canEdit, canDelete } from '../../utils/permission'
import request from '../../api/index'

const canAddInventory = computed(() => canAdd('inventory'))
const canEditInventory = computed(() => canEdit('inventory'))
const canDeleteInventory = computed(() => canDelete('inventory'))

const loading = ref(false)
const submitLoading = ref(false)
const dialogVisible = ref(false)
const viewDialogVisible = ref(false)
const formRef = ref(null)
const adjustList = ref([])
const warehouseList = ref([])
const goodsList = ref([])
const searchKeyword = ref('')
const statusFilter = ref('')
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)
const tableHeight = ref(0)
const itemsExpanded = ref(false)

const viewData = ref({ items: [] })

const form = ref({
  warehouse: '',
  adjust_type: 'increase',
  reason: '',
  remark: '',
  items: []
})

const rules = {
  warehouse: [{ required: true, message: '请选择仓库', trigger: 'change' }],
  adjust_type: [{ required: true, message: '请选择调整类型', trigger: 'change' }],
  reason: [{ required: true, message: '请选择调整原因', trigger: 'change' }]
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

const getAfterQuantity = (row) => {
  const current = Number(row.current_quantity) || 0
  const adjust = Number(row.adjust_quantity) || 0
  const type = form.value.adjust_type
  return type === 'increase' ? (current + adjust) : (current - adjust)
}

const getAfterQuantityClass = (row) => {
  const after = getAfterQuantity(row)
  return after < 0 ? 'text-danger' : ''
}

const handleGoodsChange = async (row) => {
  if (form.value.warehouse && row.goods) {
    try {
      const res = await getInventory({ goods: row.goods, warehouse: form.value.warehouse })
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
  row.adjust_quantity = num
}

const handleQuantityBlur = (row) => {
  if (row.adjust_quantity === null || row.adjust_quantity === undefined || row.adjust_quantity === '') {
    row._quantityError = '请输入数量'
    return
  }
  if (row.adjust_quantity <= 0) {
    row._quantityError = '数量必须大于0'
    return
  }
  if (form.value.adjust_type === 'decrease') {
    const after = getAfterQuantity(row)
    if (after < 0) {
      row._quantityError = '调整后库存不能为负数'
      return
    }
  }
  row._quantityError = ''
}

const loadAdjusts = async () => {
  loading.value = true
  try {
    const params = { page: currentPage.value, page_size: pageSize.value }
    if (searchKeyword.value) params.search = searchKeyword.value
    if (statusFilter.value) params.status = statusFilter.value
    const res = await request.get('/inventory/adjust/', { params })
    adjustList.value = res.data.items || res.data.results || []
    total.value = res.data.count || 0
  } catch (error) {
    adjustList.value = []
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
  form.value = { warehouse: '', adjust_type: 'increase', reason: '', remark: '', items: [] }
  dialogVisible.value = true
}

const handleView = async (row) => {
  try {
    const res = await request.get(`/inventory/adjust/${row.id}/`)
    viewData.value = res.data.data || res.data
    viewDialogVisible.value = true
  } catch (error) {
    ElMessage.error('加载详情失败')
  }
}

const handleConfirm = async (row) => {
  try {
    await ElMessageBox.confirm('确认此调整单？确认后将更新库存。', '确认调整', { type: 'warning' })
    await request.post(`/inventory/adjust/${row.id}/confirm/`)
    ElMessage.success('确认成功')
    loadAdjusts()
  } catch (error) {
    if (error !== 'cancel') ElMessage.error('确认失败')
  }
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm(`确定删除调整单「${row.order_no}」？`, '确认删除', { type: 'warning' })
    await request.delete(`/inventory/adjust/${row.id}/`)
    ElMessage.success('删除成功')
    loadAdjusts()
  } catch (error) {
    if (error !== 'cancel') ElMessage.error('删除失败')
  }
}

const addItem = () => {
  form.value.items.push({ goods: '', current_quantity: 0, adjust_quantity: null, _quantityError: '' })
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
    ElMessage.warning('请添加调整明细')
    return
  }
  
  const hasError = form.value.items.some(item => item._quantityError || !item.goods || !item.adjust_quantity)
  if (hasError) {
    ElMessage.warning('请检查明细数据')
    return
  }
  
  submitLoading.value = true
  try {
    const data = {
      warehouse: form.value.warehouse,
      adjust_type: form.value.adjust_type,
      reason: form.value.reason,
      remark: form.value.remark,
      items: form.value.items.map(item => ({ goods: item.goods, adjust_quantity: item.adjust_quantity }))
    }
    await request.post('/inventory/adjust/', data)
    ElMessage.success('创建成功')
    dialogVisible.value = false
    loadAdjusts()
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
  loadAdjusts()
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

.view-dialog :deep(.el-dialog__header) {
  padding: 0;
  margin: 0;
  position: relative;
}

.view-dialog :deep(.el-dialog__body) {
  padding: 12px 16px;
}

.dialog-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 14px 16px;
  background: linear-gradient(135deg, #f0f5ff 0%, #e6f4ff 100%);
  border-bottom: 1px solid #bae0ff;
  border-radius: var(--el-dialog-border-radius) var(--el-dialog-border-radius) 0 0;
  padding-right: 50px;
}

.dialog-title {
  font-size: 16px;
  font-weight: 600;
  color: #333;
}

.close-btn {
  position: absolute;
  top: 0;
  right: 0;
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  font-weight: 300;
  color: #999;
  cursor: pointer;
  line-height: 1;
  transition: all 0.2s;
  border-radius: 0 var(--el-dialog-border-radius) 0 6px;
  background: transparent;
}

.close-btn:hover {
  color: #333;
  background: rgba(0, 0, 0, 0.04);
}

.detail-container {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.info-section {
  background: #fafafa;
  border-radius: 6px;
  padding: 0;
  border: 1px solid #e8e8e8;
  overflow: hidden;
}

.info-row {
  display: flex;
  gap: 0;
  padding: 8px 12px;
  border-bottom: 1px solid #f0f0f0;
}

.info-row:last-child {
  border-bottom: none;
}

.info-row.highlight-row {
  background: linear-gradient(135deg, #f0f5ff 0%, #f5f9ff 100%);
  border-bottom: 1px solid #e6f0ff;
}

.info-item {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1;
}

.info-item-group {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1;
  padding: 4px 8px;
}

.info-label {
  font-size: 12px;
  color: #999;
  min-width: 56px;
}

.info-value {
  font-size: 13px;
  color: #333;
  font-weight: 500;
}

.info-value.primary {
  font-weight: 700;
  color: var(--color-primary);
  font-family: 'Monaco', 'Consolas', monospace;
}

.remark-box {
  background: #fffbe6;
  border: 1px solid #ffe58f;
  border-radius: 6px;
  padding: 10px 12px;
}

.remark-header {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: #d48806;
  font-weight: 600;
  margin-bottom: 6px;
}

.remark-icon {
  font-size: 14px;
}

.remark-text {
  font-size: 13px;
  color: #614700;
  line-height: 1.6;
  padding-left: 20px;
}

.items-section {
  border: 1px solid #e8e8e8;
  border-radius: 6px;
  overflow: hidden;
}

.items-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 12px;
  background: #f5f5f5;
  cursor: pointer;
  transition: background 0.2s;
}

.items-header:hover {
  background: #efefef;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 8px;
}

.expand-icon {
  font-size: 12px;
  color: #999;
  transition: transform 0.2s;
}

.expand-icon.expanded {
  transform: rotate(90deg);
}

.header-title {
  font-size: 13px;
  font-weight: 600;
  color: #333;
}

.header-count {
  font-size: 12px;
  color: #999;
}

.expand-hint {
  font-size: 12px;
  color: #999;
}

.items-body {
  border-top: 1px solid #e8e8e8;
}

.detail-table {
  --el-table-header-bg-color: #f5f7fa;
  --el-table-border-color: #ebeef5;
  --el-table-row-hover-bg-color: #f0f5ff;
}

.detail-table :deep(.el-table__header th) {
  font-weight: 600;
  font-size: 12px;
  color: #606266;
  padding: 10px 0;
  background: linear-gradient(180deg, #f8fafc 0%, #f0f4f8 100%);
  border-bottom: 2px solid #e0e6ed;
}

.detail-table :deep(.el-table__body td) {
  padding: 10px 0;
  border-bottom: 1px solid #f0f2f5;
}

.goods-cell {
  display: flex;
  flex-direction: row;
  align-items: center;
  gap: 8px;
}

.goods-cell .goods-name {
  font-size: 13px;
  color: #303133;
  font-weight: 500;
}

.goods-cell .goods-spec {
  font-size: 10px;
  color: #909399;
  font-family: 'Monaco', 'Consolas', monospace;
  background: #f4f4f5;
  padding: 0 4px;
  border-radius: 2px;
  white-space: nowrap;
  line-height: 1.4;
}

.quantity-cell {
  font-weight: 600;
  font-family: 'Monaco', 'Consolas', monospace;
}

.quantity-cell.increase {
  color: #52c41a;
}

.quantity-cell.decrease {
  color: #f5222d;
}
</style>

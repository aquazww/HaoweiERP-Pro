<template>
  <div class="purchase-page">
    <div class="page-content">
      <div class="toolbar-card">
        <div class="toolbar-left">
          <div class="search-box">
            <el-icon class="search-icon"><Search /></el-icon>
            <el-input
              v-model="searchKeyword"
              placeholder="搜索采购单号、供应商"
              class="search-input"
              clearable
              @keyup.enter="loadOrders"
            />
          </div>
          <el-select v-model="statusFilter" placeholder="状态筛选" clearable style="width: 140px" @change="loadOrders">
            <el-option label="全部" :value="''" />
            <el-option label="待入库" value="pending" />
            <el-option label="部分入库" value="partial" />
            <el-option label="已入库" value="completed" />
            <el-option label="已取消" value="cancelled" />
          </el-select>
        </div>
        <div class="toolbar-right">
          <el-button :icon="Refresh" @click="loadOrders">刷新</el-button>
          <el-button type="primary" :icon="Plus" @click="handleAdd">新增采购单</el-button>
        </div>
      </div>

      <div class="table-card">
        <el-table 
          :data="orderList" 
          style="width: 100%" 
          v-loading="loading"
          :height="tableHeight"
          class="data-table"
          stripe
        >
          <el-table-column type="index" label="#" width="60" align="center" />
          <el-table-column prop="order_no" label="采购单号" width="160">
            <template #default="{ row }">
              <span class="order-no-badge">{{ row.order_no }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="supplier_name" label="供应商" min-width="160" />
          <el-table-column prop="warehouse_name" label="仓库" width="130" />
          <el-table-column prop="total_amount" label="总金额" width="140" align="right">
            <template #default="{ row }">
              <span class="price-text">¥{{ formatPrice(row.total_amount) }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="status" label="状态" width="110">
            <template #default="{ row }">
              <div class="status-badge" :class="row.status">
                <span class="status-dot"></span>
                {{ getStatusText(row.status) }}
              </div>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="260" fixed="right">
            <template #default="{ row }">
              <div class="action-buttons">
                <el-button type="primary" link :icon="View" size="small" @click="handleView(row)">查看</el-button>
                <el-button type="warning" link :icon="Edit" size="small" @click="handleEdit(row)" v-if="row.status === 'pending'">编辑</el-button>
                <el-button type="success" link :icon="Download" size="small" @click="handleStockIn(row)" v-if="row.status !== 'completed' && row.status !== 'cancelled'">入库</el-button>
                <el-button type="danger" link :icon="Delete" size="small" @click="handleDelete(row)" v-if="row.status === 'pending'">删除</el-button>
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
            @size-change="loadOrders"
            @current-change="loadOrders"
          />
        </div>
      </div>
    </div>

    <!-- 新增/编辑弹窗 -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? '编辑采购单' : '新增采购单'"
      width="1100px"
      class="form-dialog"
      destroy-on-close
      @close="resetForm"
    >
      <el-form :model="form" :rules="rules" ref="formRef" label-width="100px">
        <div class="form-section">
          <div class="section-title">基本信息</div>
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="供应商" prop="supplier">
                <el-select v-model="form.supplier" placeholder="请选择供应商" style="width: 100%" filterable>
                  <el-option 
                    v-for="item in supplierList" 
                    :key="item.id" 
                    :label="item.name" 
                    :value="item.id" 
                  />
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :span="12">
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
            </el-col>
          </el-row>
          
          <el-form-item label="采购日期" prop="order_date">
            <el-date-picker
              v-model="form.order_date"
              type="date"
              placeholder="选择日期"
              style="width: 100%"
              value-format="YYYY-MM-DD"
            />
          </el-form-item>

          <el-form-item label="备注">
            <el-input v-model="form.remark" type="textarea" :rows="2" placeholder="请输入备注" maxlength="500" show-word-limit />
          </el-form-item>
        </div>

        <div class="form-section">
          <div class="section-title">
            采购明细
            <span class="item-count" v-if="form.items.length > 0">({{ form.items.length }}项)</span>
          </div>
          
          <div class="detail-table-wrapper">
            <el-table :data="form.items" border style="width: 100%;" class="detail-table">
              <el-table-column type="index" label="#" width="50" align="center" />
              <el-table-column prop="goods" label="商品" min-width="200">
                <template #default="{ row, $index }">
                  <el-select 
                    v-model="row.goods" 
                    placeholder="请选择商品" 
                    style="width: 100%" 
                    filterable 
                    @change="handleGoodsChange(row, $index)"
                  >
                    <el-option 
                      v-for="item in availableGoods($index)" 
                      :key="item.id" 
                      :label="`${item.name} (${item.code})`" 
                      :value="item.id" 
                    />
                  </el-select>
                </template>
              </el-table-column>
              <el-table-column prop="unit" label="单位" width="70" align="center">
                <template #default="{ row }">
                  <span class="unit-text">{{ getGoodsUnit(row.goods) }}</span>
                </template>
              </el-table-column>
              <el-table-column prop="quantity" label="数量" width="150">
                <template #default="{ row, $index }">
                  <div class="input-cell" :class="{ 'has-error': row._quantityError }">
                    <el-input
                      :model-value="formatInputNumber(row.quantity, true)"
                      @input="(val) => handleQuantityInput(row, val)"
                      @blur="handleQuantityBlur(row)"
                      placeholder="请输入"
                      class="number-input"
                      :class="{ 'is-error': row._quantityError }"
                    >
                      <template #suffix>
                        <span class="input-suffix" v-if="row.quantity">件</span>
                      </template>
                    </el-input>
                    <div class="error-tip" v-if="row._quantityError">{{ row._quantityError }}</div>
                  </div>
                </template>
              </el-table-column>
              <el-table-column prop="price" label="单价(元)" width="150">
                <template #default="{ row, $index }">
                  <div class="input-cell" :class="{ 'has-error': row._priceError }">
                    <el-input
                      :model-value="formatInputNumber(row.price)"
                      @input="(val) => handlePriceInput(row, val)"
                      @blur="handlePriceBlur(row)"
                      placeholder="请输入"
                      class="number-input price-input"
                      :class="{ 'is-error': row._priceError }"
                    >
                      <template #prefix>
                        <span class="input-prefix">¥</span>
                      </template>
                    </el-input>
                    <div class="error-tip" v-if="row._priceError">{{ row._priceError }}</div>
                  </div>
                </template>
              </el-table-column>
              <el-table-column prop="amount" label="金额(元)" width="130" align="right">
                <template #default="{ row }">
                  <div class="amount-display">
                    <span class="amount-symbol">¥</span>
                    <span class="amount-value">{{ calculateItemAmount(row) }}</span>
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
            <div class="total-section">
              <div class="total-info">
                <span class="total-items">共 <strong>{{ form.items.length }}</strong> 项</span>
                <span class="total-divider">|</span>
                <span class="total-quantity">合计数量: <strong>{{ totalQuantity }}</strong></span>
              </div>
              <div class="total-amount-wrapper">
                <span class="total-label">合计金额：</span>
                <span class="total-amount">¥{{ totalAmount }}</span>
              </div>
            </div>
          </div>
        </div>
      </el-form>
      
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleSubmit" :loading="submitLoading">
            {{ isEdit ? '保存修改' : '创建采购单' }}
          </el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 查看详情弹窗 -->
    <el-dialog
      v-model="viewDialogVisible"
      title="采购单详情"
      width="900px"
      class="view-dialog"
    >
      <el-descriptions :column="2" border v-if="viewData">
        <el-descriptions-item label="采购单号">{{ viewData.order_no }}</el-descriptions-item>
        <el-descriptions-item label="状态">
          <div class="status-badge" :class="viewData.status">
            <span class="status-dot"></span>
            {{ getStatusText(viewData.status) }}
          </div>
        </el-descriptions-item>
        <el-descriptions-item label="供应商">{{ viewData.supplier_name }}</el-descriptions-item>
        <el-descriptions-item label="仓库">{{ viewData.warehouse_name }}</el-descriptions-item>
        <el-descriptions-item label="采购日期">{{ viewData.order_date }}</el-descriptions-item>
        <el-descriptions-item label="总金额">¥{{ formatPrice(viewData.total_amount) }}</el-descriptions-item>
        <el-descriptions-item label="创建人">{{ viewData.created_by_name || '-' }}</el-descriptions-item>
        <el-descriptions-item label="创建时间">{{ viewData.created_at }}</el-descriptions-item>
        <el-descriptions-item label="备注" :span="2">{{ viewData.remark || '-' }}</el-descriptions-item>
      </el-descriptions>
      
      <div class="view-items-title">采购明细</div>
      <el-table :data="viewData?.items || []" border style="width: 100%;">
        <el-table-column type="index" label="#" width="60" align="center" />
        <el-table-column prop="goods_name" label="商品名称" min-width="180" />
        <el-table-column prop="goods_code" label="商品编码" width="120" />
        <el-table-column prop="unit" label="单位" width="70" align="center" />
        <el-table-column prop="quantity" label="数量" width="100" align="right">
          <template #default="{ row }">{{ formatQuantity(row.quantity) }}</template>
        </el-table-column>
        <el-table-column prop="price" label="单价" width="120" align="right">
          <template #default="{ row }">¥{{ formatPrice(row.price) }}</template>
        </el-table-column>
        <el-table-column prop="amount" label="金额" width="120" align="right">
          <template #default="{ row }">¥{{ formatPrice(row.amount) }}</template>
        </el-table-column>
      </el-table>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, nextTick, onUnmounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Refresh, Plus, Edit, Delete, View, Download } from '@element-plus/icons-vue'
import { 
  getPurchaseOrders, createPurchaseOrder, 
  updatePurchaseOrder, deletePurchaseOrder,
  getPurchaseOrder
} from '../../api/purchase'
import { getSuppliers, getWarehouses, getGoods } from '../../api/basic'
import { createStockIn, confirmStockIn } from '../../api/inventory'
import { formatPrice, formatQuantity, formatInputNumber, parseInputNumber, calculateAmount } from '../../utils/format'

const loading = ref(false)
const submitLoading = ref(false)
const dialogVisible = ref(false)
const viewDialogVisible = ref(false)
const isEdit = ref(false)
const formRef = ref(null)
const orderList = ref([])
const supplierList = ref([])
const warehouseList = ref([])
const goodsList = ref([])
const searchKeyword = ref('')
const statusFilter = ref('')
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)
const tableHeight = ref(0)
const viewData = ref(null)

const form = ref({
  supplier: '',
  warehouse: '',
  order_date: '',
  remark: '',
  items: []
})

const rules = {
  supplier: [{ required: true, message: '请选择供应商', trigger: 'change' }],
  warehouse: [{ required: true, message: '请选择仓库', trigger: 'change' }],
  order_date: [{ required: true, message: '请选择采购日期', trigger: 'change' }]
}

const getStatusText = (status) => {
  const textMap = {
    'pending': '待入库',
    'partial': '部分入库',
    'completed': '已入库',
    'cancelled': '已取消'
  }
  return textMap[status] || status
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
  if (row.quantity > 999999.99) {
    row._quantityError = '数量超出范围'
    return
  }
  row._quantityError = ''
}

const handlePriceInput = (row, value) => {
  row._priceError = ''
  const num = parseInputNumber(value)
  row.price = num
}

const handlePriceBlur = (row) => {
  if (row.price === null || row.price === undefined || row.price === '') {
    row._priceError = '请输入单价'
    return
  }
  if (row.price <= 0) {
    row._priceError = '单价必须大于0'
    return
  }
  if (row.price > 99999999.99) {
    row._priceError = '单价超出范围'
    return
  }
  row._priceError = ''
}

const calculateItemAmount = (row) => {
  return calculateAmount(row.quantity, row.price)
}

const totalQuantity = computed(() => {
  const total = form.value.items.reduce((sum, item) => {
    return sum + (Number(item.quantity) || 0)
  }, 0)
  if (Number.isInteger(total)) return String(total)
  return total.toString()
})

const totalAmount = computed(() => {
  return form.value.items.reduce((sum, item) => {
    return sum + ((Number(item.quantity) || 0) * (Number(item.price) || 0))
  }, 0).toFixed(2)
})

const getGoodsUnit = (goodsId) => {
  const goods = goodsList.value.find(g => g.id === goodsId)
  return goods?.unit || '-'
}

const availableGoods = (currentIndex) => {
  const selectedGoodsIds = form.value.items
    .filter((_, index) => index !== currentIndex)
    .map(item => item.goods)
    .filter(id => id)
  
  return goodsList.value.filter(goods => !selectedGoodsIds.includes(goods.id))
}

const loadOrders = async () => {
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
    const res = await getPurchaseOrders(params)
    orderList.value = res.data.items || res.data.results || []
    total.value = res.data.count || 0
  } catch (error) {
    orderList.value = []
    total.value = 0
    ElMessage.error('加载采购订单失败：' + (error.message || '未知错误'))
  } finally {
    loading.value = false
  }
}

const loadOptions = async () => {
  try {
    const [suppliersRes, warehousesRes, goodsRes] = await Promise.all([
      getSuppliers(),
      getWarehouses(),
      getGoods()
    ])
    supplierList.value = suppliersRes.data.items || suppliersRes.data.results || []
    warehouseList.value = warehousesRes.data.items || warehousesRes.data.results || []
    goodsList.value = goodsRes.data.items || goodsRes.data.results || []
  } catch (error) {
    ElMessage.error('加载选项数据失败')
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
  isEdit.value = false
  form.value = {
    supplier: '',
    warehouse: '',
    order_date: new Date().toISOString().split('T')[0],
    remark: '',
    items: []
  }
  dialogVisible.value = true
}

const handleEdit = async (row) => {
  if (row.status !== 'pending') {
    ElMessage.warning('只有待入库状态的订单才能编辑')
    return
  }
  
  isEdit.value = true
  
  try {
    const res = await getPurchaseOrder(row.id)
    const data = res.data.data || res.data
    
    form.value = {
      id: data.id,
      supplier: data.supplier,
      warehouse: data.warehouse,
      order_date: data.order_date,
      remark: data.remark || '',
      items: (data.items || []).map(item => ({
        goods: item.goods,
        quantity: Number(item.quantity),
        price: Number(item.price),
        remark: item.remark || '',
        _quantityError: '',
        _priceError: ''
      }))
    }
    dialogVisible.value = true
  } catch (error) {
    ElMessage.error('获取订单详情失败')
  }
}

const handleView = async (row) => {
  try {
    const res = await getPurchaseOrder(row.id)
    viewData.value = res.data.data || res.data
    viewDialogVisible.value = true
  } catch (error) {
    ElMessage.error('获取订单详情失败')
  }
}

const handleStockIn = async (row) => {
  if (row.status === 'completed') {
    ElMessage.warning('该采购单已全部入库')
    return
  }
  
  if (row.status === 'cancelled') {
    ElMessage.warning('该采购单已取消，无法入库')
    return
  }

  try {
    await ElMessageBox.confirm(
      `确定要将采购单「${row.order_no}」入库吗？入库后将更新库存。`,
      '确认入库',
      {
        confirmButtonText: '确定入库',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    const stockInData = {
      purchase_order: row.id,
      warehouse: row.warehouse,
      total_amount: row.total_amount,
      remark: `采购单 ${row.order_no} 入库`
    }
    
    const stockInRes = await createStockIn(stockInData)
    await confirmStockIn(stockInRes.data.id || stockInRes.data.data?.id)
    
    ElMessage.success('入库成功')
    loadOrders()
  } catch (error) {
    if (error !== 'cancel') {
      const errorMsg = error.response?.data?.msg || error.message || '入库失败'
      ElMessage.error(errorMsg)
    }
  }
}

const handleDelete = async (row) => {
  if (row.status !== 'pending') {
    ElMessage.warning('只有待入库状态的订单才能删除')
    return
  }
  
  try {
    await ElMessageBox.confirm(`确定要删除采购单「${row.order_no}」吗？`, '确认删除', {
      confirmButtonText: '确定删除',
      cancelButtonText: '取消',
      type: 'warning',
      confirmButtonClass: 'el-button--danger'
    })
    await deletePurchaseOrder(row.id)
    ElMessage.success('删除成功')
    loadOrders()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const addItem = () => {
  form.value.items.push({
    goods: '',
    quantity: null,
    price: null,
    remark: '',
    _quantityError: '',
    _priceError: ''
  })
}

const removeItem = (index) => {
  form.value.items.splice(index, 1)
}

const handleGoodsChange = (row, index) => {
  const goods = goodsList.value.find(g => g.id === row.goods)
  if (goods) {
    row.price = goods.purchase_price ? Number(goods.purchase_price) : null
    row._priceError = ''
  }
}

const validateItems = () => {
  if (form.value.items.length === 0) {
    ElMessage.warning('请至少添加一条采购明细')
    return false
  }
  
  let hasError = false
  
  for (let i = 0; i < form.value.items.length; i++) {
    const item = form.value.items[i]
    
    if (!item.goods) {
      ElMessage.warning(`第${i + 1}条明细：请选择商品`)
      hasError = true
      continue
    }
    
    if (item.quantity === null || item.quantity === undefined || item.quantity === '') {
      item._quantityError = '请输入数量'
      hasError = true
    } else if (item.quantity <= 0) {
      item._quantityError = '数量必须大于0'
      hasError = true
    }
    
    if (item.price === null || item.price === undefined || item.price === '') {
      item._priceError = '请输入单价'
      hasError = true
    } else if (item.price <= 0) {
      item._priceError = '单价必须大于0'
      hasError = true
    }
  }
  
  if (hasError) {
    return false
  }
  
  const goodsIds = form.value.items.map(item => item.goods)
  const uniqueIds = new Set(goodsIds)
  if (goodsIds.length !== uniqueIds.size) {
    ElMessage.warning('采购明细中存在重复商品，请检查')
    return false
  }
  
  return true
}

const handleSubmit = async () => {
  if (!formRef.value) return
  
  try {
    await formRef.value.validate()
  } catch (error) {
    ElMessage.warning('请检查基本信息是否填写完整')
    return
  }
  
  if (!validateItems()) {
    return
  }
  
  submitLoading.value = true
  
  try {
    const data = {
      supplier: form.value.supplier,
      warehouse: form.value.warehouse,
      order_date: form.value.order_date,
      remark: form.value.remark || '',
      items: form.value.items.map(item => ({
        goods: item.goods,
        quantity: item.quantity,
        price: item.price,
        remark: item.remark || ''
      }))
    }
    
    if (isEdit.value) {
      await updatePurchaseOrder(form.value.id, data)
      ElMessage.success('修改成功')
    } else {
      await createPurchaseOrder(data)
      ElMessage.success('创建成功')
    }
    
    dialogVisible.value = false
    loadOrders()
  } catch (error) {
    const errorMsg = error.response?.data?.msg || error.response?.data?.data || error.message || '操作失败'
    
    if (typeof errorMsg === 'object') {
      const messages = Object.values(errorMsg).flat().join('；')
      ElMessage.error(messages)
    } else {
      ElMessage.error(errorMsg)
    }
  } finally {
    submitLoading.value = false
  }
}

const resetForm = () => {
  if (formRef.value) {
    formRef.value.resetFields()
  }
  form.value.items = []
}

onMounted(() => {
  loadOrders()
  loadOptions()
  calculateTableHeight()
  window.addEventListener('resize', calculateTableHeight)
})

onUnmounted(() => {
  window.removeEventListener('resize', calculateTableHeight)
})
</script>

<style scoped>
.purchase-page {
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

.order-no-badge {
  display: inline-block;
  padding: 2px 10px;
  background-color: var(--color-bg-light);
  color: var(--color-primary);
  font-weight: 600;
  font-size: var(--font-size-sm);
  border-radius: var(--border-radius-sm);
  font-family: 'Monaco', 'Consolas', monospace;
}

.price-text {
  font-weight: 600;
  font-family: 'Monaco', 'Consolas', monospace;
  color: var(--color-primary);
}

.status-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 4px 12px;
  background-color: var(--color-bg-light);
  color: var(--color-text-secondary);
  font-size: var(--font-size-sm);
  border-radius: 20px;
  font-weight: 500;
}

.status-badge.pending {
  background-color: rgba(245, 158, 11, 0.1);
  color: var(--color-warning);
}

.status-badge.partial {
  background-color: rgba(14, 165, 233, 0.1);
  color: var(--color-primary);
}

.status-badge.completed {
  background-color: rgba(34, 197, 94, 0.1);
  color: var(--color-success);
}

.status-badge.cancelled {
  background-color: rgba(239, 68, 68, 0.1);
  color: var(--color-danger);
}

.status-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background-color: currentColor;
}

.action-buttons {
  display: flex;
  align-items: center;
  gap: var(--spacing-xs);
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

.form-dialog {
  --el-dialog-border-radius: var(--border-radius-lg);
}

.form-dialog :deep(.el-dialog__header) {
  padding: var(--spacing-lg) var(--spacing-xl);
  border-bottom: 1px solid var(--color-border-light);
}

.form-dialog :deep(.el-dialog__body) {
  padding: var(--spacing-lg) var(--spacing-xl);
  max-height: 65vh;
  overflow-y: auto;
}

.form-dialog :deep(.el-dialog__footer) {
  padding: var(--spacing-md) var(--spacing-xl);
  border-top: 1px solid var(--color-border-light);
}

.form-section {
  margin-bottom: var(--spacing-lg);
}

.form-section:last-child {
  margin-bottom: 0;
}

.section-title {
  font-size: var(--font-size-base);
  font-weight: 600;
  color: var(--color-text-primary);
  margin-bottom: var(--spacing-md);
  padding-left: var(--spacing-sm);
  border-left: 3px solid var(--color-primary);
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
}

.item-count {
  font-weight: 400;
  color: var(--color-text-secondary);
  font-size: var(--font-size-sm);
}

.detail-table-wrapper {
  border-radius: var(--border-radius-md);
  overflow: hidden;
  border: 1px solid var(--color-border);
}

.detail-table {
  --el-table-header-bg-color: var(--color-bg-light);
}

.unit-text {
  color: var(--color-text-secondary);
  font-size: var(--font-size-sm);
}

.input-cell {
  position: relative;
}

.input-cell.has-error .number-input :deep(.el-input__wrapper) {
  border-color: var(--color-danger);
  box-shadow: 0 0 0 1px var(--color-danger) inset;
}

.number-input :deep(.el-input__wrapper) {
  padding: 0 8px;
}

.number-input.is-error :deep(.el-input__wrapper) {
  border-color: var(--color-danger);
}

.number-input.price-input :deep(.el-input__inner) {
  text-align: right;
}

.input-prefix {
  color: var(--color-primary);
  font-weight: 600;
}

.input-suffix {
  color: var(--color-text-tertiary);
  font-size: var(--font-size-xs);
}

.error-tip {
  position: absolute;
  top: 100%;
  left: 0;
  font-size: 11px;
  color: var(--color-danger);
  white-space: nowrap;
  padding-top: 2px;
  z-index: 10;
}

.amount-display {
  display: flex;
  align-items: baseline;
  justify-content: flex-end;
  gap: 2px;
}

.amount-symbol {
  color: var(--color-primary);
  font-weight: 600;
  font-size: var(--font-size-sm);
}

.amount-value {
  font-weight: 700;
  font-family: 'Monaco', 'Consolas', monospace;
  color: var(--color-primary);
  font-size: var(--font-size-base);
}

.detail-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: var(--spacing-md);
  padding: var(--spacing-sm) 0;
}

.total-section {
  display: flex;
  align-items: center;
  gap: var(--spacing-xl);
}

.total-info {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  color: var(--color-text-secondary);
  font-size: var(--font-size-sm);
}

.total-info strong {
  color: var(--color-text-primary);
  font-weight: 600;
}

.total-divider {
  color: var(--color-border);
}

.total-amount-wrapper {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
}

.total-label {
  font-size: var(--font-size-base);
  color: var(--color-text-secondary);
}

.total-amount {
  font-size: var(--font-size-xl);
  font-weight: 700;
  color: var(--color-primary);
  font-family: 'Monaco', 'Consolas', monospace;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: var(--spacing-sm);
}

.view-dialog :deep(.el-dialog__body) {
  padding: var(--spacing-lg) var(--spacing-xl);
}

.view-items-title {
  font-size: var(--font-size-base);
  font-weight: 600;
  color: var(--color-text-primary);
  margin: var(--spacing-lg) 0 var(--spacing-md);
  padding-left: var(--spacing-sm);
  border-left: 3px solid var(--color-primary);
}
</style>

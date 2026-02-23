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
          <el-button type="primary" :icon="Plus" @click="handleAdd" v-if="canAddPurchase">新增采购单</el-button>
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
          :header-cell-style="{ background: 'var(--color-bg-light)' }"
        >
          <el-table-column prop="order_no" label="采购单号" min-width="150" align="center">
            <template #default="{ row }">
              <span class="order-no-badge">{{ row.order_no }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="supplier_name" label="供应商" min-width="180" show-overflow-tooltip />
          <el-table-column prop="warehouse_name" label="仓库" min-width="120" align="center" show-overflow-tooltip />
          <el-table-column prop="total_amount" label="总金额" min-width="120" align="right">
            <template #default="{ row }">
              <span class="price-text">¥{{ formatPrice(row.total_amount) }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="status" label="状态" min-width="100" align="center">
            <template #default="{ row }">
              <div class="status-badge small" :class="row.status">
                <span class="status-dot"></span>
                {{ getStatusText(row.status) }}
              </div>
            </template>
          </el-table-column>
          <el-table-column label="操作" min-width="240" align="center">
            <template #default="{ row }">
              <div class="action-buttons">
                <el-button type="primary" link :icon="View" size="small" @click="handleView(row)">查看</el-button>
                <el-button type="warning" link :icon="Edit" size="small" @click="handleEdit(row)" v-if="canEditPurchase && row.status === 'pending'">编辑</el-button>
                <el-button type="success" link :icon="Download" size="small" @click="handleStockIn(row)" v-if="canStockIn && row.status !== 'completed' && row.status !== 'cancelled'">入库</el-button>
                <el-button type="danger" link :icon="Delete" size="small" @click="handleDelete(row)" v-if="canDeletePurchase && row.status === 'pending'">删除</el-button>
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
      width="700px"
      class="form-dialog"
      destroy-on-close
      :show-close="false"
      @close="resetForm"
    >
      <template #header>
        <div class="dialog-header">
          <span class="dialog-title">{{ isEdit ? '编辑采购单' : '新增采购单' }}</span>
        </div>
        <span class="close-btn" @click="dialogVisible = false">×</span>
      </template>
      
      <div class="form-container">
        <div class="form-section-card">
          <div class="form-section-header">
            <span class="section-title">基本信息</span>
          </div>
          <div class="form-section-body">
            <div class="form-row">
              <div class="form-item">
                <span class="form-label required">供应商</span>
                <el-select v-model="form.supplier" placeholder="请选择供应商" style="width: 100%" filterable>
                  <el-option 
                    v-for="item in supplierList" 
                    :key="item.id" 
                    :label="item.name" 
                    :value="item.id" 
                  />
                </el-select>
              </div>
              <div class="form-item">
                <span class="form-label required">仓库</span>
                <el-select v-model="form.warehouse" placeholder="请选择仓库" style="width: 100%">
                  <el-option 
                    v-for="item in warehouseList" 
                    :key="item.id" 
                    :label="item.name" 
                    :value="item.id" 
                  />
                </el-select>
              </div>
            </div>
            <div class="form-row">
              <div class="form-item">
                <span class="form-label required">采购日期</span>
                <el-date-picker
                  v-model="form.order_date"
                  type="date"
                  placeholder="选择日期"
                  style="width: 100%"
                  value-format="YYYY-MM-DD"
                />
              </div>
              <div class="form-item">
                <span class="form-label">备注</span>
                <el-input v-model="form.remark" placeholder="请输入备注（可选）" maxlength="500" />
              </div>
            </div>
          </div>
        </div>
        
        <div class="form-section-card">
          <div class="form-section-header">
            <span class="section-title">采购明细</span>
            <span class="item-count-badge" v-if="form.items.length > 0">{{ form.items.length }}项</span>
          </div>
          <div class="form-section-body no-padding">
            <el-table :data="form.items" border size="small" class="form-table">
              <el-table-column prop="goods" label="商品" min-width="160">
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
                      :label="item.name" 
                      :value="item.id" 
                    >
                      <div class="goods-option">
                        <span class="goods-name">{{ item.name }}</span>
                        <span class="goods-spec">{{ item.spec || '-' }}</span>
                      </div>
                    </el-option>
                  </el-select>
                </template>
              </el-table-column>
              <el-table-column prop="quantity" label="数量" width="120" align="center">
                <template #default="{ row }">
                  <el-input
                    :model-value="formatInputNumber(row.quantity, true)"
                    @input="(val) => handleQuantityInput(row, val)"
                    @blur="handleQuantityBlur(row)"
                    placeholder="数量"
                    size="small"
                    :class="{ 'is-error': row._quantityError }"
                  >
                    <template #suffix>
                      <span class="input-suffix" v-if="row.quantity">{{ getGoodsUnit(row.goods) }}</span>
                    </template>
                  </el-input>
                </template>
              </el-table-column>
              <el-table-column prop="price" label="单价" width="100" align="right">
                <template #default="{ row }">
                  <el-input
                    :model-value="formatInputNumber(row.price)"
                    @input="(val) => handlePriceInput(row, val)"
                    @blur="handlePriceBlur(row)"
                    placeholder="单价"
                    size="small"
                    :class="{ 'is-error': row._priceError }"
                  >
                    <template #prefix>¥</template>
                  </el-input>
                </template>
              </el-table-column>
              <el-table-column prop="amount" label="金额" width="100" align="right">
                <template #default="{ row }">
                  <span class="amount-cell">¥{{ calculateItemAmount(row) }}</span>
                </template>
              </el-table-column>
              <el-table-column label="" width="45" align="center">
                <template #default="{ $index }">
                  <el-button type="danger" link :icon="Delete" size="small" @click="removeItem($index)"></el-button>
                </template>
              </el-table-column>
            </el-table>
            
            <div class="table-footer">
              <el-button type="primary" plain :icon="Plus" size="small" @click="addItem">添加商品</el-button>
              <div class="total-display">
                <span class="total-item">共 <strong>{{ form.items.length }}</strong> 项</span>
                <span class="total-divider">|</span>
                <span class="total-item">合计数量: <strong>{{ totalQuantity }}</strong></span>
                <span class="total-amount-display">
                  <span class="label">合计金额</span>
                  <span class="value">¥{{ totalAmount }}</span>
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
      
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
      width="700px"
      class="view-dialog"
      :show-close="false"
    >
      <template #header>
        <div class="dialog-header">
          <span class="dialog-title">采购单详情</span>
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
              <span class="info-label">供应商</span>
              <span class="info-value">{{ viewData.supplier_name }}</span>
            </div>
            <div class="info-item-group">
              <span class="info-label">采购单号</span>
              <span class="info-value primary">{{ viewData.order_no }}</span>
            </div>
          </div>
          <div class="info-row highlight-row">
            <div class="info-item-group">
              <span class="info-label">仓库</span>
              <span class="info-value">{{ viewData.warehouse_name }}</span>
            </div>
            <div class="info-item-group">
              <span class="info-label">总金额</span>
              <span class="info-value price">¥{{ formatPrice(viewData.total_amount) }}</span>
            </div>
          </div>
          <div class="info-row">
            <div class="info-item">
              <span class="info-label">采购日期</span>
              <span class="info-value">{{ viewData.order_date }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">入库时间</span>
              <span class="info-value">{{ viewData.stock_in_time ? formatDateTime(viewData.stock_in_time) : '-' }}</span>
            </div>
          </div>
          <div class="info-row">
            <div class="info-item">
              <span class="info-label">创建人</span>
              <span class="info-value">{{ viewData.created_by_name || '-' }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">创建时间</span>
              <span class="info-value">{{ formatDateTime(viewData.created_at) }}</span>
            </div>
          </div>
        </div>
        
        <div class="remark-box" v-if="viewData.remark">
          <div class="remark-header">
            <el-icon class="remark-icon"><Document /></el-icon>
            <span>采购备注</span>
          </div>
          <div class="remark-text">{{ viewData.remark }}</div>
        </div>
        
        <div class="remark-box stock-in-remark" v-if="viewData.stock_in_remark">
          <div class="remark-header">
            <el-icon class="remark-icon"><Finished /></el-icon>
            <span>入库备注</span>
          </div>
          <div class="remark-text">{{ viewData.stock_in_remark }}</div>
        </div>
        
        <div class="items-section">
          <div class="items-header" @click="itemsExpanded = !itemsExpanded">
            <div class="header-left">
              <el-icon class="expand-icon" :class="{ expanded: itemsExpanded }"><ArrowRight /></el-icon>
              <span class="header-title">采购明细</span>
              <span class="header-count">{{ viewData.items?.length || 0 }}项</span>
            </div>
            <span class="expand-hint">{{ itemsExpanded ? '收起' : '展开' }}</span>
          </div>
          <el-collapse-transition>
            <div class="items-body" v-show="itemsExpanded">
              <el-table :data="viewData?.items || []" border size="small" class="detail-table">
                <el-table-column prop="goods_name" label="商品" min-width="140">
                  <template #default="{ row }">
                    <div class="goods-cell">
                      <span class="goods-name">{{ row.goods_name }}</span>
                      <span class="goods-spec">{{ row.goods_spec || '-' }}</span>
                    </div>
                  </template>
                </el-table-column>
                <el-table-column prop="unit" label="单位" width="55" align="center" />
                <el-table-column prop="quantity" label="数量" width="75" align="center">
                  <template #default="{ row }">
                    <span class="quantity-cell">{{ formatQuantity(row.quantity) }}</span>
                  </template>
                </el-table-column>
                <el-table-column prop="price" label="单价" width="85" align="right">
                  <template #default="{ row }">¥{{ formatPrice(row.price) }}</template>
                </el-table-column>
                <el-table-column prop="amount" label="金额" width="95" align="right">
                  <template #default="{ row }">
                    <span class="amount-cell">¥{{ formatPrice(row.amount) }}</span>
                  </template>
                </el-table-column>
              </el-table>
            </div>
          </el-collapse-transition>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, nextTick, onUnmounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Refresh, Plus, Edit, Delete, View, Download, Document, ArrowRight, Finished } from '@element-plus/icons-vue'
import { 
  getPurchaseOrders, createPurchaseOrder, 
  updatePurchaseOrder, deletePurchaseOrder,
  getPurchaseOrder
} from '../../api/purchase'
import { getSuppliers, getWarehouses, getGoods } from '../../api/basic'
import { createStockIn, confirmStockIn } from '../../api/inventory'
import { formatPrice, formatQuantity, formatInputNumber, parseInputNumber, calculateAmount } from '../../utils/format'
import { canAdd, canEdit, canDelete } from '../../utils/permission'

const canAddPurchase = computed(() => canAdd('purchase'))
const canEditPurchase = computed(() => canEdit('purchase'))
const canDeletePurchase = computed(() => canDelete('purchase'))
const canStockIn = computed(() => canAdd('inventory'))

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

const loading = ref(false)
const submitLoading = ref(false)
const dialogVisible = ref(false)
const viewDialogVisible = ref(false)
const isEdit = ref(false)
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
const itemsExpanded = ref(false)

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
  return goods?.unit_name || '-'
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
    const { value: userRemark } = await ElMessageBox.prompt(
      `请确认采购单「${row.order_no}」的入库操作`,
      '确认入库',
      {
        confirmButtonText: '确定入库',
        cancelButtonText: '取消',
        inputType: 'textarea',
        inputPlaceholder: '请输入入库备注（可选）',
        inputValidator: () => true,
        customClass: 'stock-in-dialog'
      }
    )

    const stockInData = {
      purchase_order: row.id,
      warehouse: row.warehouse,
      total_amount: row.total_amount,
      remark: userRemark || ''
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
  if (!form.value.supplier) {
    ElMessage.warning('请选择供应商')
    return
  }
  if (!form.value.warehouse) {
    ElMessage.warning('请选择仓库')
    return
  }
  if (!form.value.order_date) {
    ElMessage.warning('请选择采购日期')
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
  form.value = {
    supplier: '',
    warehouse: '',
    order_date: new Date().toISOString().split('T')[0],
    remark: '',
    items: []
  }
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

.data-table :deep(.el-table__header-wrapper) {
  position: sticky;
  top: 0;
  z-index: 10;
}

.data-table :deep(.el-table__body-wrapper) {
  overflow-y: auto;
}

.data-table :deep(.el-table__row) {
  height: 48px;
}

.data-table :deep(.el-table__cell) {
  padding: 8px 0;
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

.status-badge.small {
  padding: 2px 8px;
  font-size: 12px;
  gap: 4px;
}

.status-badge.small .status-dot {
  width: 5px;
  height: 5px;
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
  --el-dialog-border-radius: 8px;
}

.form-dialog :deep(.el-dialog__header) {
  padding: 0;
  margin: 0;
  position: relative;
}

.form-dialog :deep(.el-dialog__body) {
  padding: 12px 16px;
  max-height: 65vh;
  overflow-y: auto;
}

.form-dialog :deep(.el-dialog__footer) {
  padding: 12px 16px;
  border-top: 1px solid #e8e8e8;
}

.form-dialog .dialog-header {
  display: flex;
  flex-direction: column;
  gap: 2px;
  padding: 14px 16px;
  background: linear-gradient(135deg, #f0f5ff 0%, #e6f4ff 100%);
  border-bottom: 1px solid #bae0ff;
  border-radius: 8px 8px 0 0;
  padding-right: 50px;
}

.form-dialog .dialog-title {
  font-size: 16px;
  font-weight: 600;
  color: #333;
}

.form-dialog .dialog-subtitle {
  font-size: 12px;
  color: #666;
}

.form-container {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.form-section-card {
  border: 1px solid #e8e8e8;
  border-radius: 6px;
  overflow: hidden;
}

.form-section-header {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 12px;
  background: #f5f5f5;
  border-bottom: 1px solid #e8e8e8;
}

.form-section-header .section-icon {
  font-size: 14px;
}

.form-section-header .section-title {
  font-size: 13px;
  font-weight: 600;
  color: #333;
  margin: 0;
  padding: 0;
  border: none;
}

.form-section-header .item-count-badge {
  font-size: 11px;
  color: #999;
  background: #f0f0f0;
  padding: 1px 6px;
  border-radius: 10px;
}

.form-section-body {
  padding: 12px;
}

.form-section-body.no-padding {
  padding: 0;
}

.form-row {
  display: flex;
  gap: 16px;
  margin-bottom: 10px;
}

.form-row:last-child {
  margin-bottom: 0;
}

.form-item {
  flex: 1;
  display: flex;
  flex-direction: row;
  align-items: center;
  gap: 8px;
}

.form-label {
  font-size: 12px;
  color: #666;
  min-width: 60px;
  flex-shrink: 0;
  text-align: right;
}

.form-label.required::before {
  content: '*';
  color: #f5222d;
  margin-right: 2px;
}

.form-table {
  --el-table-header-bg-color: #f5f7fa;
  --el-table-border-color: #ebeef5;
}

.form-table :deep(.el-table__header th) {
  font-weight: 600;
  font-size: 12px;
  color: #606266;
  padding: 8px 0;
  background: linear-gradient(180deg, #f8fafc 0%, #f0f4f8 100%);
}

.form-table :deep(.el-table__body td) {
  padding: 6px 0;
}

.goods-option {
  display: flex;
  align-items: center;
  gap: 8px;
}

.goods-option .goods-name {
  font-size: 13px;
  color: #333;
}

.goods-option .goods-spec {
  font-size: 11px;
  color: #999;
  background: #f4f4f5;
  padding: 1px 4px;
  border-radius: 2px;
}

.input-suffix {
  color: #909399;
  font-size: 12px;
}

.unit-text {
  color: #666;
  font-size: 12px;
}

.amount-cell {
  font-weight: 600;
  color: var(--color-primary);
  font-family: 'Monaco', 'Consolas', monospace;
}

.table-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 12px;
  background: #fafafa;
  border-top: 1px solid #e8e8e8;
}

.total-display {
  display: flex;
  align-items: center;
  gap: 12px;
}

.total-item {
  font-size: 12px;
  color: #666;
}

.total-item strong {
  color: #333;
}

.total-divider {
  color: #ddd;
}

.total-amount-display {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-left: 12px;
  padding-left: 12px;
  border-left: 1px solid #e8e8e8;
}

.total-amount-display .label {
  font-size: 12px;
  color: #666;
}

.total-amount-display .value {
  font-size: 16px;
  font-weight: 700;
  color: var(--color-primary);
  font-family: 'Monaco', 'Consolas', monospace;
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

.info-value.price {
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

.remark-box.stock-in-remark {
  background: #f6ffed;
  border-color: #b7eb8f;
}

.remark-box.stock-in-remark .remark-header {
  color: #52c41a;
}

.remark-box.stock-in-remark .remark-text {
  color: #389e0d;
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

.detail-table :deep(.el-table__body tr:hover > td) {
  background-color: #f5f9ff !important;
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
  color: #409eff;
  font-family: 'Monaco', 'Consolas', monospace;
}

.amount-cell {
  font-weight: 600;
  color: var(--color-primary);
  font-family: 'Monaco', 'Consolas', monospace;
}

:deep(.stock-in-dialog) {
  --el-dialog-border-radius: var(--border-radius-lg);
}

:deep(.stock-in-dialog .el-message-box__content) {
  padding: var(--spacing-md) 0;
}

:deep(.stock-in-dialog .el-textarea__inner) {
  min-height: 80px;
  resize: none;
}

/* 响应式设计 */
@media screen and (max-width: 1400px) {
  .search-input {
    width: 280px;
  }
  
  .data-table :deep(.el-table__row) {
    height: 44px;
  }
}

@media screen and (max-width: 1200px) {
  .search-input {
    width: 240px;
  }
  
  .toolbar-left,
  .toolbar-right {
    gap: var(--spacing-sm);
  }
  
  .action-buttons {
    flex-wrap: wrap;
    justify-content: center;
  }
}

@media screen and (max-width: 992px) {
  .toolbar-card {
    flex-direction: column;
    gap: var(--spacing-sm);
    padding: var(--spacing-sm);
  }
  
  .toolbar-left,
  .toolbar-right {
    width: 100%;
    justify-content: center;
  }
  
  .search-input {
    width: 100%;
  }
  
  .data-table :deep(.el-table__row) {
    height: 40px;
  }
  
  .data-table :deep(.el-table__cell) {
    padding: 6px 0;
    font-size: var(--font-size-sm);
  }
}

@media screen and (max-width: 768px) {
  .purchase-page {
    padding: 4px;
  }
  
  .page-content {
    gap: 4px;
  }
  
  .toolbar-card {
    border-radius: var(--border-radius-md);
  }
  
  .table-card {
    border-radius: var(--border-radius-md);
  }
  
  .action-buttons {
    gap: 2px;
  }
  
  .action-buttons .el-button {
    padding: 4px 8px;
  }
  
  .pagination-wrapper {
    padding: 4px var(--spacing-sm);
  }
  
  .pagination-wrapper :deep(.el-pagination) {
    flex-wrap: wrap;
    justify-content: center;
  }
}
</style>

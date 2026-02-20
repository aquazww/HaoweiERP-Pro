<template>
  <div class="sale-page">
    <div class="page-content">
      <div class="toolbar-card">
        <div class="toolbar-left">
          <div class="search-box">
            <el-icon class="search-icon"><Search /></el-icon>
            <el-input
              v-model="searchKeyword"
              placeholder="搜索销售单号、客户"
              class="search-input"
              clearable
              @keyup.enter="loadOrders"
            />
          </div>
          <el-select v-model="statusFilter" placeholder="状态筛选" clearable style="width: 140px" @change="loadOrders">
            <el-option label="全部" :value="''" />
            <el-option label="待出库" value="pending" />
            <el-option label="部分出库" value="partial" />
            <el-option label="已出库" value="completed" />
            <el-option label="已取消" value="cancelled" />
          </el-select>
        </div>
        <div class="toolbar-right">
          <el-button :icon="Refresh" @click="loadOrders">刷新</el-button>
          <el-button type="primary" :icon="Plus" @click="handleAdd">新增销售单</el-button>
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
          <el-table-column prop="order_no" label="销售单号" width="160">
            <template #default="{ row }">
              <span class="order-no-badge">{{ row.order_no }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="customer_name" label="客户" min-width="160" />
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
                <el-button type="success" link :icon="Upload" size="small" @click="handleStockOut(row)" v-if="row.status !== 'completed' && row.status !== 'cancelled'">出库</el-button>
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

    <!-- 查看弹窗 -->
    <el-dialog
      v-model="viewDialogVisible"
      title="销售单详情"
      width="800px"
      class="view-dialog"
      destroy-on-close
    >
      <el-descriptions :column="2" border class="view-descriptions">
        <el-descriptions-item label="销售单号">{{ viewData.order_no }}</el-descriptions-item>
        <el-descriptions-item label="客户">{{ viewData.customer_name }}</el-descriptions-item>
        <el-descriptions-item label="仓库">{{ viewData.warehouse_name }}</el-descriptions-item>
        <el-descriptions-item label="销售日期">{{ viewData.order_date }}</el-descriptions-item>
        <el-descriptions-item label="总金额">¥{{ formatPrice(viewData.total_amount) }}</el-descriptions-item>
        <el-descriptions-item label="状态">
          <div class="status-badge" :class="viewData.status">
            <span class="status-dot"></span>
            {{ getStatusText(viewData.status) }}
          </div>
        </el-descriptions-item>
        <el-descriptions-item label="备注" :span="2">{{ viewData.remark || '-' }}</el-descriptions-item>
      </el-descriptions>
      
      <div class="view-items-title">销售明细</div>
      <el-table :data="viewData.items" border style="width: 100%;">
        <el-table-column type="index" label="#" width="50" align="center" />
        <el-table-column prop="goods_name" label="商品名称" min-width="180" />
        <el-table-column prop="quantity" label="数量" width="100" align="right">
          <template #default="{ row }">{{ formatQuantity(row.quantity) }}</template>
        </el-table-column>
        <el-table-column label="单价" width="120" align="right">
          <template #default="{ row }">¥{{ formatPrice(row.price) }}</template>
        </el-table-column>
        <el-table-column label="金额" width="120" align="right">
          <template #default="{ row }">¥{{ formatPrice(row.amount) }}</template>
        </el-table-column>
      </el-table>
    </el-dialog>

    <!-- 新增/编辑弹窗 -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? '编辑销售单' : '新增销售单'"
      width="1000px"
      class="form-dialog"
      destroy-on-close
      @close="resetForm"
    >
      <el-form :model="form" :rules="rules" ref="formRef" label-width="100px">
        <div class="form-section">
          <div class="section-title">基本信息</div>
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="客户" prop="customer">
                <el-select v-model="form.customer" placeholder="请选择客户" style="width: 100%" filterable>
                  <el-option 
                    v-for="item in customerList" 
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
          
          <el-form-item label="销售日期" prop="order_date">
            <el-date-picker
              v-model="form.order_date"
              type="date"
              placeholder="选择日期"
              style="width: 100%"
              value-format="YYYY-MM-DD"
            />
          </el-form-item>

          <el-form-item label="备注">
            <el-input v-model="form.remark" type="textarea" :rows="2" placeholder="请输入备注" />
          </el-form-item>
        </div>

        <div class="form-section">
          <div class="section-title">销售明细</div>
          
          <div class="detail-table-wrapper">
            <el-table :data="form.items" border style="width: 100%;" class="detail-table">
              <el-table-column prop="goods" label="商品" min-width="200">
                <template #default="{ row, $index }">
                  <el-select v-model="row.goods" placeholder="选择商品" style="width: 100%" filterable @change="handleGoodsChange(row)">
                    <el-option 
                      v-for="item in goodsList" 
                      :key="item.id" 
                      :label="item.name" 
                      :value="item.id" 
                    />
                  </el-select>
                </template>
              </el-table-column>
              <el-table-column prop="quantity" label="数量" width="150">
                <template #default="{ row }">
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
                        <span class="input-suffix" v-if="row.quantity">{{ getGoodsUnit(row.goods) }}</span>
                      </template>
                    </el-input>
                    <div class="error-tip" v-if="row._quantityError">{{ row._quantityError }}</div>
                  </div>
                </template>
              </el-table-column>
              <el-table-column prop="price" label="单价(元)" width="150">
                <template #default="{ row }">
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
            {{ isEdit ? '保存修改' : '创建销售单' }}
          </el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, nextTick, onUnmounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Refresh, Plus, Edit, Delete, View, Upload } from '@element-plus/icons-vue'
import { 
  getSaleOrders, createSaleOrder, 
  updateSaleOrder, deleteSaleOrder,
  getSaleOrder, confirmSaleOrder
} from '../../api/sale'
import { getCustomers, getWarehouses, getGoods } from '../../api/basic'
import { formatPrice, formatQuantity, formatInputNumber, parseInputNumber, calculateAmount } from '../../utils/format'

const loading = ref(false)
const submitLoading = ref(false)
const dialogVisible = ref(false)
const viewDialogVisible = ref(false)
const isEdit = ref(false)
const formRef = ref(null)
const orderList = ref([])
const customerList = ref([])
const warehouseList = ref([])
const goodsList = ref([])
const searchKeyword = ref('')
const statusFilter = ref('')
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)
const tableHeight = ref(0)

const viewData = ref({
  order_no: '',
  customer_name: '',
  warehouse_name: '',
  order_date: '',
  total_amount: 0,
  status: '',
  remark: '',
  items: []
})

const form = ref({
  customer: '',
  warehouse: '',
  order_date: '',
  remark: '',
  items: []
})

const rules = {
  customer: [{ required: true, message: '请选择客户', trigger: 'change' }],
  warehouse: [{ required: true, message: '请选择仓库', trigger: 'change' }],
  order_date: [{ required: true, message: '请选择日期', trigger: 'change' }]
}

const getStatusText = (status) => {
  const textMap = {
    'pending': '待出库',
    'partial': '部分出库',
    'completed': '已出库',
    'cancelled': '已取消'
  }
  return textMap[status] || status
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

const calculateItemAmount = (row) => {
  return calculateAmount(row.quantity, row.price)
}

const getGoodsUnit = (goodsId) => {
  const goods = goodsList.value.find(g => g.id === goodsId)
  return goods?.unit_name || ''
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
    const res = await getSaleOrders(params)
    orderList.value = res.data.items || res.data.results || []
    total.value = res.data.count || 0
  } catch (error) {
    orderList.value = []
    total.value = 0
    ElMessage.error('加载销售订单失败：' + (error.message || '未知错误'))
  } finally {
    loading.value = false
  }
}

const loadOptions = async () => {
  try {
    const [customersRes, warehousesRes, goodsRes] = await Promise.all([
      getCustomers(),
      getWarehouses(),
      getGoods()
    ])
    customerList.value = customersRes.data.items || customersRes.data.results || []
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
    customer: '',
    warehouse: '',
    order_date: '',
    remark: '',
    items: []
  }
  dialogVisible.value = true
}

const handleView = async (row) => {
  try {
    const res = await getSaleOrder(row.id)
    viewData.value = res.data.data || res.data
    viewDialogVisible.value = true
  } catch (error) {
    ElMessage.error('加载销售单详情失败')
  }
}

const handleEdit = async (row) => {
  try {
    const res = await getSaleOrder(row.id)
    const data = res.data.data || res.data
    isEdit.value = true
    form.value = {
      id: data.id,
      customer: data.customer,
      warehouse: data.warehouse,
      order_date: data.order_date,
      remark: data.remark,
      items: (data.items || []).map(item => ({
        goods: item.goods,
        quantity: item.quantity,
        price: item.price,
        remark: item.remark || '',
        _quantityError: '',
        _priceError: ''
      }))
    }
    dialogVisible.value = true
  } catch (error) {
    ElMessage.error('加载销售单详情失败')
  }
}

const handleStockOut = async (row) => {
  if (row.status === 'completed') {
    ElMessage.warning('该销售单已全部出库')
    return
  }

  try {
    await ElMessageBox.confirm('确定要出库此销售单吗？', '确认出库', {
      confirmButtonText: '确定出库',
      cancelButtonText: '取消',
      type: 'warning'
    })

    await confirmSaleOrder(row.id)
    ElMessage.success('出库成功')
    loadOrders()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('出库失败：' + (error.response?.data?.msg || error.message || '未知错误'))
    }
  }
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm(`确定要删除销售单「${row.order_no}」吗？`, '确认删除', {
      confirmButtonText: '确定删除',
      cancelButtonText: '取消',
      type: 'warning',
      confirmButtonClass: 'el-button--danger'
    })
    await deleteSaleOrder(row.id)
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

const handleGoodsChange = (row) => {
  const goods = goodsList.value.find(g => g.id === row.goods)
  if (goods) {
    row.price = goods.sale_price || 0
  }
}

const handleSubmit = async () => {
  try {
    await formRef.value.validate()
  } catch (error) {
    ElMessage.warning('请检查表单填写是否正确')
    return
  }
  
  const hasError = form.value.items.some(item => item._quantityError || item._priceError)
  if (hasError) {
    ElMessage.warning('请检查明细数据是否正确')
    return
  }
  
  if (form.value.items.length === 0) {
    ElMessage.warning('请添加销售明细')
    return
  }
  
  const goodsIds = form.value.items.map(item => item.goods).filter(id => id)
  const uniqueGoodsIds = [...new Set(goodsIds)]
  if (goodsIds.length !== uniqueGoodsIds.length) {
    ElMessage.warning('销售明细中存在重复商品，请移除重复项或合并数量')
    return
  }
  
  submitLoading.value = true
  
  try {
    const data = {
      customer: form.value.customer,
      warehouse: form.value.warehouse,
      order_date: form.value.order_date,
      remark: form.value.remark,
      items: form.value.items.map(item => ({
        goods: item.goods,
        quantity: item.quantity,
        price: item.price,
        remark: item.remark || ''
      }))
    }
    
    if (isEdit.value) {
      await updateSaleOrder(form.value.id, data)
      ElMessage.success('更新成功')
    } else {
      await createSaleOrder(data)
      ElMessage.success('创建成功')
    }
    
    dialogVisible.value = false
    loadOrders()
  } catch (error) {
    const errorMsg = parseErrorMessage(error)
    ElMessage.error(errorMsg)
  } finally {
    submitLoading.value = false
  }
}

const parseErrorMessage = (error) => {
  const responseData = error.response?.data
  if (!responseData) {
    return error.message || '操作失败，请稍后重试'
  }
  
  if (responseData.msg) {
    return responseData.msg
  }
  
  if (responseData.items) {
    const itemsErrors = responseData.items
    if (Array.isArray(itemsErrors)) {
      for (const err of itemsErrors) {
        if (typeof err === 'string') return err
        if (err.string) return err.string
        if (err.message) return err.message
      }
    }
    if (typeof itemsErrors === 'string') return itemsErrors
    return '销售明细数据有误，请检查后重试'
  }
  
  if (responseData.non_field_errors) {
    const errors = responseData.non_field_errors
    if (Array.isArray(errors) && errors.length > 0) {
      return typeof errors[0] === 'string' ? errors[0] : errors[0]?.string || '数据验证失败'
    }
    return String(errors)
  }
  
  const firstKey = Object.keys(responseData)[0]
  if (firstKey && responseData[firstKey]) {
    const value = responseData[firstKey]
    if (typeof value === 'string') return value
    if (Array.isArray(value) && value.length > 0) {
      const firstItem = value[0]
      if (typeof firstItem === 'string') return firstItem
      if (firstItem.string) return firstItem.string
    }
  }
  
  return '操作失败，请稍后重试'
}

const resetForm = () => {
  if (formRef.value) {
    formRef.value.resetFields()
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
.sale-page {
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

.view-dialog :deep(.el-dialog__body) {
  padding: var(--spacing-lg);
}

.view-descriptions {
  margin-bottom: var(--spacing-lg);
}

.view-items-title {
  font-size: 15px;
  font-weight: 600;
  color: var(--color-text-primary);
  margin-bottom: var(--spacing-md);
  padding-left: var(--spacing-sm);
  border-left: 3px solid var(--color-primary);
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
}

.detail-table-wrapper {
  border-radius: var(--border-radius-md);
  overflow: hidden;
  border: 1px solid var(--color-border);
}

.detail-table {
  --el-table-header-bg-color: var(--color-bg-light);
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

.number-input :deep(.el-input__inner) {
  text-align: right;
}

.number-input.is-error :deep(.el-input__wrapper) {
  border-color: var(--color-danger);
}

.input-prefix {
  color: var(--color-primary);
  font-weight: 600;
}

.input-suffix {
  color: var(--color-text-tertiary);
  font-size: 12px;
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
  align-items: center;
  justify-content: flex-end;
  gap: 2px;
}

.amount-symbol {
  color: var(--color-text-tertiary);
}

.amount-value {
  font-weight: 600;
  font-family: 'Monaco', 'Consolas', monospace;
}

.detail-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: var(--spacing-md);
}

.total-section {
  display: flex;
  align-items: center;
  gap: 24px;
}

.total-info {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
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
  gap: 12px;
}
</style>

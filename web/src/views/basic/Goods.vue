<template>
  <div class="goods-page">
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
          <el-select v-model="statusFilter" placeholder="状态筛选" clearable style="width: 140px" @change="loadGoods">
            <el-option label="全部" :value="''" />
            <el-option label="启用" :value="1" />
            <el-option label="禁用" :value="0" />
          </el-select>
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
          class="data-table"
          stripe
          :height="tableHeight"
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
          <el-table-column label="状态" width="100" align="center">
            <template #default="{ row }">
              <el-switch
                v-model="row.status"
                active-color="#165DFF"
                inactive-color="#9ca3af"
                :active-value="1"
                :inactive-value="0"
                :loading="toggleLoading === row.id"
                @change="handleToggleStatus(row)"
              />
            </template>
          </el-table-column>
          <el-table-column label="操作" width="140" align="center">
            <template #default="{ row }">
              <div class="action-buttons">
                <el-button type="primary" link :icon="Edit" size="small" @click="handleEdit(row)">编辑</el-button>
                <el-button type="danger" link :icon="Delete" size="small" @click="handleDelete(row)">删除</el-button>
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
            @size-change="loadGoods"
            @current-change="loadGoods"
          />
        </div>
      </div>
    </div>

    <!-- 新增/编辑商品对话框 -->
    <el-dialog 
      v-model="dialogVisible" 
      :title="dialogTitle" 
      width="680px"
      :close-on-click-modal="false"
      @close="handleDialogClose"
    >
      <el-form 
        ref="formRef" 
        :model="form" 
        :rules="rules" 
        label-width="100px"
        label-position="right"
        class="goods-form"
      >
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="商品编码" prop="code">
              <el-input 
                v-model="form.code" 
                placeholder="请输入商品编码"
                maxlength="50"
                show-word-limit
                :disabled="isEdit"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="商品名称" prop="name">
              <el-input 
                v-model="form.name" 
                placeholder="请输入商品名称"
                maxlength="100"
                show-word-limit
              />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="商品分类" prop="category">
              <el-select 
                v-model="form.category" 
                placeholder="请选择商品分类"
                style="width: 100%"
                filterable
              >
                <el-option 
                  v-for="item in categoryList" 
                  :key="item.id" 
                  :label="item.name" 
                  :value="item.id"
                />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="计量单位" prop="unit">
              <el-select 
                v-model="form.unit" 
                placeholder="请选择或输入单位"
                style="width: 100%"
                filterable
                allow-create
              >
                <el-option label="个" value="个" />
                <el-option label="件" value="件" />
                <el-option label="台" value="台" />
                <el-option label="套" value="套" />
                <el-option label="箱" value="箱" />
                <el-option label="包" value="包" />
                <el-option label="盒" value="盒" />
                <el-option label="千克" value="千克" />
                <el-option label="米" value="米" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="规格" prop="spec">
              <el-input 
                v-model="form.spec" 
                placeholder="请输入规格（选填）"
                maxlength="100"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="条形码" prop="barcode">
              <el-input 
                v-model="form.barcode" 
                placeholder="请输入条形码（选填）"
                maxlength="50"
              />
            </el-form-item>
          </el-col>
        </el-row>

        <el-divider content-position="left">价格信息</el-divider>

        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="进货价" prop="purchase_price">
              <div class="price-input-wrapper" :class="{ 'has-error': priceErrors.purchase_price }">
                <el-input
                  :model-value="formatInputNumber(form.purchase_price)"
                  @input="(val) => handlePriceInput('purchase_price', val)"
                  @blur="handlePriceBlur('purchase_price')"
                  placeholder="请输入"
                  class="price-input"
                  :class="{ 'is-error': priceErrors.purchase_price }"
                >
                  <template #prefix>
                    <span class="input-prefix">¥</span>
                  </template>
                </el-input>
                <div class="error-tip" v-if="priceErrors.purchase_price">{{ priceErrors.purchase_price }}</div>
              </div>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="销售价" prop="sale_price">
              <div class="price-input-wrapper" :class="{ 'has-error': priceErrors.sale_price }">
                <el-input
                  :model-value="formatInputNumber(form.sale_price)"
                  @input="(val) => handlePriceInput('sale_price', val)"
                  @blur="handlePriceBlur('sale_price')"
                  placeholder="请输入"
                  class="price-input"
                  :class="{ 'is-error': priceErrors.sale_price }"
                >
                  <template #prefix>
                    <span class="input-prefix">¥</span>
                  </template>
                </el-input>
                <div class="error-tip" v-if="priceErrors.sale_price">{{ priceErrors.sale_price }}</div>
              </div>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="零售价" prop="retail_price">
              <div class="price-input-wrapper" :class="{ 'has-error': priceErrors.retail_price }">
                <el-input
                  :model-value="formatInputNumber(form.retail_price)"
                  @input="(val) => handlePriceInput('retail_price', val)"
                  @blur="handlePriceBlur('retail_price')"
                  placeholder="请输入"
                  class="price-input"
                  :class="{ 'is-error': priceErrors.retail_price }"
                >
                  <template #prefix>
                    <span class="input-prefix">¥</span>
                  </template>
                </el-input>
                <div class="error-tip" v-if="priceErrors.retail_price">{{ priceErrors.retail_price }}</div>
              </div>
            </el-form-item>
          </el-col>
        </el-row>

        <el-divider content-position="left">库存设置</el-divider>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="最低库存" prop="min_stock">
              <el-input-number 
                v-model="form.min_stock" 
                :min="0"
                :max="999999999"
                placeholder="请输入最低库存"
                style="width: 100%"
                controls-position="right"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="最高库存" prop="max_stock">
              <el-input-number 
                v-model="form.max_stock" 
                :min="0"
                :max="999999999"
                placeholder="请输入最高库存"
                style="width: 100%"
                controls-position="right"
              />
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="状态" prop="status">
          <el-radio-group v-model="form.status">
            <el-radio :value="1">上架</el-radio>
            <el-radio :value="0">下架</el-radio>
          </el-radio-group>
        </el-form-item>

        <el-form-item label="备注" prop="remark">
          <el-input 
            v-model="form.remark" 
            type="textarea" 
            :rows="3"
            placeholder="请输入备注信息（选填）"
            maxlength="500"
            show-word-limit
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <div class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleSubmit" :loading="submitLoading">
            {{ isEdit ? '保存修改' : '确认新增' }}
          </el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, nextTick, onUnmounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Refresh, Plus, Edit, Delete } from '@element-plus/icons-vue'
import { getGoods, createGoods, deleteGoods, updateGoods } from '../../api/basic'
import { getCategories } from '../../api/basic'
import { formatPrice, formatInputNumber, parseInputNumber } from '../../utils/format'

const loading = ref(false)
const toggleLoading = ref(null)
const goodsList = ref([])
const searchKeyword = ref('')
const statusFilter = ref('')
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)
const tableHeight = ref(0)

const dialogVisible = ref(false)
const dialogTitle = ref('新增商品')
const isEdit = ref(false)
const submitLoading = ref(false)
const formRef = ref(null)
const categoryList = ref([])

const priceErrors = reactive({
  purchase_price: '',
  sale_price: '',
  retail_price: ''
})

const form = reactive({
  id: null,
  code: '',
  name: '',
  category: null,
  unit: '',
  spec: '',
  barcode: '',
  purchase_price: 0,
  sale_price: 0,
  retail_price: 0,
  min_stock: 0,
  max_stock: 0,
  status: 1,
  remark: ''
})

const validateCode = (rule, value, callback) => {
  if (!value || !value.trim()) {
    callback(new Error('请输入商品编码'))
  } else if (value.length > 50) {
    callback(new Error('商品编码不能超过50个字符'))
  } else if (!/^[A-Za-z0-9_-]+$/.test(value)) {
    callback(new Error('商品编码只能包含字母、数字、下划线和横线'))
  } else {
    callback()
  }
}

const validateName = (rule, value, callback) => {
  if (!value || !value.trim()) {
    callback(new Error('请输入商品名称'))
  } else if (value.length > 100) {
    callback(new Error('商品名称不能超过100个字符'))
  } else {
    callback()
  }
}

const validateSalePrice = (rule, value, callback) => {
  if (value < form.purchase_price) {
    callback(new Error('销售价不能低于进货价'))
  } else {
    callback()
  }
}

const validateMaxStock = (rule, value, callback) => {
  if (value < form.min_stock) {
    callback(new Error('最高库存不能低于最低库存'))
  } else {
    callback()
  }
}

const rules = {
  code: [
    { required: true, validator: validateCode, trigger: 'blur' }
  ],
  name: [
    { required: true, validator: validateName, trigger: 'blur' }
  ],
  category: [
    { required: true, message: '请选择商品分类', trigger: 'change' }
  ],
  unit: [
    { required: true, message: '请选择或输入计量单位', trigger: 'change' }
  ],
  sale_price: [
    { validator: validateSalePrice, trigger: 'blur' }
  ],
  max_stock: [
    { validator: validateMaxStock, trigger: 'blur' }
  ]
}

const handlePriceInput = (field, value) => {
  priceErrors[field] = ''
  const num = parseInputNumber(value)
  form[field] = num
}

const handlePriceBlur = (field) => {
  const value = form[field]
  if (value === null || value === undefined || value === '') {
    priceErrors[field] = '请输入价格'
    return
  }
  if (value < 0) {
    priceErrors[field] = '价格不能为负数'
    return
  }
  if (value > 99999999.99) {
    priceErrors[field] = '价格超出范围'
    return
  }
  
  if (field === 'sale_price' && form.purchase_price && value < form.purchase_price) {
    priceErrors[field] = '销售价不能低于进货价'
    return
  }
  
  priceErrors[field] = ''
}

const getGoodsInitials = (name) => {
  if (!name) return ''
  return name.slice(0, 2)
}

const calculateProfit = (row) => {
  const purchase = Number(row.purchase_price) || 0
  const sale = Number(row.sale_price) || 0
  return sale - purchase
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

const loadCategories = async () => {
  try {
    const res = await getCategories({ page_size: 1000, is_active: true })
    categoryList.value = res.data.items || res.data.results || []
  } catch (error) {
    categoryList.value = []
  }
}

const loadGoods = async () => {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      page_size: pageSize.value
    }
    if (searchKeyword.value) {
      params.search = searchKeyword.value
    }
    if (statusFilter.value !== '') {
      params.status = statusFilter.value
    }
    const res = await getGoods(params)
    goodsList.value = res.data.items || res.data.results || []
    total.value = res.data.count || 0
  } catch (error) {
    goodsList.value = []
    total.value = 0
    ElMessage.error('加载数据失败：' + (error.message || '未知错误'))
  } finally {
    loading.value = false
  }
}

const resetForm = () => {
  form.id = null
  form.code = ''
  form.name = ''
  form.category = null
  form.unit = ''
  form.spec = ''
  form.barcode = ''
  form.purchase_price = 0
  form.sale_price = 0
  form.retail_price = 0
  form.min_stock = 0
  form.max_stock = 0
  form.status = 1
  form.remark = ''
  priceErrors.purchase_price = ''
  priceErrors.sale_price = ''
  priceErrors.retail_price = ''
}

const handleAdd = () => {
  resetForm()
  isEdit.value = false
  dialogTitle.value = '新增商品'
  dialogVisible.value = true
}

const handleEdit = (row) => {
  resetForm()
  isEdit.value = true
  dialogTitle.value = '编辑商品'
  
  form.id = row.id
  form.code = row.code
  form.name = row.name
  form.category = row.category
  form.unit = row.unit
  form.spec = row.spec || ''
  form.barcode = row.barcode || ''
  form.purchase_price = Number(row.purchase_price) || 0
  form.sale_price = Number(row.sale_price) || 0
  form.retail_price = Number(row.retail_price) || 0
  form.min_stock = row.min_stock || 0
  form.max_stock = row.max_stock || 0
  form.status = row.status
  form.remark = row.remark || ''
  
  dialogVisible.value = true
}

const handleDialogClose = () => {
  formRef.value?.resetFields()
}

const handleSubmit = async () => {
  if (!formRef.value) return
  
  try {
    await formRef.value.validate()
  } catch (error) {
    ElMessage.warning('请检查表单填写是否正确')
    return
  }
  
  submitLoading.value = true
  
  try {
    const submitData = {
      code: form.code.trim().toUpperCase(),
      name: form.name.trim(),
      category: form.category,
      unit: form.unit,
      spec: form.spec?.trim() || '',
      barcode: form.barcode?.trim() || '',
      purchase_price: form.purchase_price,
      sale_price: form.sale_price,
      retail_price: form.retail_price,
      min_stock: form.min_stock,
      max_stock: form.max_stock,
      status: form.status,
      remark: form.remark?.trim() || ''
    }
    
    if (isEdit.value) {
      await updateGoods(form.id, submitData)
      ElMessage.success('商品修改成功')
    } else {
      await createGoods(submitData)
      ElMessage.success('商品新增成功')
    }
    
    dialogVisible.value = false
    loadGoods()
  } catch (error) {
    const errorMsg = error.response?.data?.msg || error.message || '操作失败'
    
    if (error.response?.data?.data) {
      const errors = error.response.data.data
      const errorMessages = Object.values(errors).flat().join('；')
      ElMessage.error(errorMessages)
    } else {
      ElMessage.error(errorMsg)
    }
  } finally {
    submitLoading.value = false
  }
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

const handleToggleStatus = async (row) => {
  const originalStatus = row.status === 1 ? 0 : 1
  try {
    await ElMessageBox.confirm(`确定要${row.status === 1 ? '启用' : '禁用'}商品「${row.name}」吗？`, '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    toggleLoading.value = row.id
    await updateGoods(row.id, { ...row, status: row.status })
    ElMessage.success('操作成功')
    loadGoods()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('操作失败')
    }
    row.status = originalStatus
  } finally {
    toggleLoading.value = null
  }
}

onMounted(() => {
  loadCategories()
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

.pagination-wrapper :deep(.el-pagination .btn-prev),
.pagination-wrapper :deep(.el-pagination .btn-next) {
  min-width: 32px;
  padding: 0 8px;
}

.pagination-wrapper :deep(.el-pagination .el-pager li) {
  min-width: 32px;
  height: 32px;
  line-height: 32px;
}

.pagination-wrapper :deep(.el-pagination .el-pagination__sizes) {
  margin-right: 8px;
}

.pagination-wrapper :deep(.el-pagination .el-pagination__jump) {
  margin-left: 8px;
}

.goods-form {
  padding: 10px 20px;
}

.goods-form :deep(.el-divider__text) {
  font-weight: 500;
  color: var(--color-text-secondary);
}

.goods-form :deep(.el-form-item__label) {
  font-weight: 500;
}

.price-input-wrapper {
  position: relative;
  width: 100%;
}

.price-input-wrapper.has-error .price-input :deep(.el-input__wrapper) {
  border-color: var(--color-danger);
  box-shadow: 0 0 0 1px var(--color-danger) inset;
}

.price-input :deep(.el-input__wrapper) {
  padding: 0 8px;
}

.price-input :deep(.el-input__inner) {
  text-align: right;
}

.price-input.is-error :deep(.el-input__wrapper) {
  border-color: var(--color-danger);
}

.input-prefix {
  color: var(--color-primary);
  font-weight: 600;
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

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}
</style>

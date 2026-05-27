<template>
  <el-dialog 
    v-model="dialogVisible" 
    :title="dialogTitle" 
    width="1000px"
    :close-on-click-modal="false"
    @close="handleDialogClose"
    class="purchase-order-dialog"
  >
    <el-form 
      ref="formRef" 
      :model="form" 
      :rules="rules" 
      label-width="80px"
      label-position="right"
      class="order-form"
    >
      <div class="form-section">
        <el-row :gutter="16">
          <el-col :span="8">
            <el-form-item label="供应商" prop="supplier">
              <el-select 
                v-model="form.supplier" 
                placeholder="请选择供应商"
                style="width: 100%"
                filterable
                clearable
                size="default"
              >
                <el-option 
                  v-for="item in supplierList" 
                  :key="item.id" 
                  :label="item.name" 
                  :value="item.id"
                />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="仓库" prop="warehouse">
              <el-select 
                v-model="form.warehouse" 
                placeholder="请选择仓库"
                style="width: 100%"
                filterable
                clearable
                size="default"
              >
                <el-option 
                  v-for="item in warehouseList" 
                  :key="item.id" 
                  :label="item.name" 
                  :value="item.id"
                />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="采购日期" prop="order_date">
              <el-date-picker
                v-model="form.order_date"
                type="date"
                placeholder="请选择日期"
                style="width: 100%"
                value-format="YYYY-MM-DD"
                size="default"
              />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="24">
            <el-form-item label="备注">
              <el-input 
                v-model="form.remark" 
                type="textarea"
                :rows="2"
                placeholder="请输入备注信息（选填）"
                resize="none"
              />
            </el-form-item>
          </el-col>
        </el-row>
      </div>

      <div class="form-section items-section">
        <div class="section-header">
          <div class="header-left">
            <span class="section-title">采购明细</span>
            <div class="summary-info">
              <span class="summary-item">
                <span class="summary-label">数量:</span>
                <span class="summary-value">{{ totalQuantity }}</span>
              </span>
              <span class="summary-item">
                <span class="summary-label">金额:</span>
                <span class="summary-value amount">¥{{ totalAmount }}</span>
              </span>
            </div>
          </div>
          <el-button type="primary" :icon="Plus" @click="addItem">添加商品</el-button>
        </div>

        <div class="table-wrapper" v-if="form.items.length > 0">
          <el-table 
            :data="form.items" 
            border 
            style="width: 100%"
            class="items-table"
            size="small"
            :header-cell-style="{ 
              background: '#fafafa', 
              color: '#606266', 
              fontWeight: '600',
              fontSize: '13px',
              padding: '10px 0'
            }"
          >
            <el-table-column label="商品编码" width="140">
              <template #default="{ row, $index }">
                <el-input
                  v-model="row.goods_code"
                  placeholder="输入编码"
                  size="small"
                  clearable
                  @change="handleCodeChange(row, $index)"
                  @keyup.enter="handleCodeEnter(row, $index)"
                />
              </template>
            </el-table-column>
            
            <el-table-column label="商品名称" min-width="180" show-overflow-tooltip>
              <template #default="{ row, $index }">
                <div class="goods-name-cell" @click="openGoodsSelect($index)">
                  <span :class="{ 'placeholder-text': !row.goods_name }">
                    {{ row.goods_name || '点击选择商品' }}
                  </span>
                  <el-icon class="select-icon"><Search /></el-icon>
                </div>
              </template>
            </el-table-column>
            
            <el-table-column label="规格" width="120" show-overflow-tooltip>
              <template #default="{ row }">
                <el-select
                  v-model="row.spec"
                  placeholder="选择规格"
                  size="small"
                  style="width: 100%"
                  clearable
                  :disabled="!row.goods"
                  @change="handleSpecChange(row)"
                >
                  <el-option
                    v-for="spec in getGoodsSpecs(row.goods)"
                    :key="spec"
                    :label="spec"
                    :value="spec"
                  />
                </el-select>
              </template>
            </el-table-column>
            
            <el-table-column label="数量/单位" width="130" align="center">
              <template #default="{ row }">
                <div class="quantity-unit-cell">
                  <el-input-number
                    v-model="row.quantity"
                    :min="1"
                    :precision="0"
                    :step="1"
                    :controls="false"
                    size="small"
                    class="quantity-input"
                    placeholder="数量"
                    @change="handleQuantityChange(row)"
                  />
                  <span class="unit-text-inline">{{ row.unit_name || '-' }}</span>
                </div>
              </template>
            </el-table-column>
            
            <el-table-column label="单价(元)" width="100" align="center">
              <template #default="{ row }">
                <el-input-number
                  v-model="row.price"
                  :min="0"
                  :precision="2"
                  :controls="false"
                  size="small"
                  style="width: 100%"
                  placeholder="单价"
                  @change="handlePriceChange(row)"
                />
              </template>
            </el-table-column>
            
            <el-table-column label="金额(元)" width="100" align="right">
              <template #default="{ row }">
                <span class="amount-text">¥{{ formatAmount(row.amount) }}</span>
              </template>
            </el-table-column>
            
            <el-table-column label="" width="50" align="center">
              <template #default="{ $index }">
                <el-button 
                  type="danger" 
                  link 
                  size="small"
                  :icon="Delete"
                  @click="removeItem($index)"
                  title="删除"
                />
              </template>
            </el-table-column>
          </el-table>
        </div>
        
        <div class="empty-state" v-else>
          <div class="empty-content">
            <el-icon class="empty-icon"><Document /></el-icon>
            <p class="empty-text">暂无采购明细，请点击上方按钮添加商品</p>
          </div>
        </div>
      </div>
    </el-form>

    <template #footer>
      <div class="dialog-footer">
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitLoading">
          {{ isEdit ? '保存修改' : '确认新增' }}
        </el-button>
      </div>
    </template>
    
    <!-- 商品选择弹窗 -->
    <GoodsSelectDialog
      v-model="goodsSelectVisible"
      :goods-list="goodsList"
      :category-list="categoryList"
      :exclude-ids="excludeGoodsIds"
      @select="handleGoodsSelect"
    />
  </el-dialog>
</template>

<script setup>
/**
 * 采购单表单组件
 * 用于新增和编辑采购订单
 */
import { ref, watch, computed } from 'vue'
import { Plus, Delete, Document, Search } from '@element-plus/icons-vue'
import GoodsSelectDialog from './GoodsSelectDialog.vue'

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  },
  dialogTitle: {
    type: String,
    default: '新增采购单'
  },
  isEdit: {
    type: Boolean,
    default: false
  },
  form: {
    type: Object,
    required: true
  },
  rules: {
    type: Object,
    default: () => ({})
  },
  supplierList: {
    type: Array,
    default: () => []
  },
  warehouseList: {
    type: Array,
    default: () => []
  },
  goodsList: {
    type: Array,
    default: () => []
  },
  categoryList: {
    type: Array,
    default: () => []
  },
  totalQuantity: {
    type: [Number, String],
    default: 0
  },
  totalAmount: {
    type: [Number, String],
    default: '0.00'
  },
  submitLoading: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits([
  'update:modelValue',
  'submit',
  'add-item',
  'remove-item',
  'goods-change',
  'code-change',
  'spec-change',
  'quantity-input',
  'price-input',
  'dialog-close'
])

const dialogVisible = ref(props.modelValue)
const formRef = ref(null)
const goodsSelectVisible = ref(false)
const currentEditIndex = ref(null)

watch(() => props.modelValue, (val) => {
  dialogVisible.value = val
})

watch(dialogVisible, (val) => {
  emit('update:modelValue', val)
})

/**
 * 计算已选商品ID列表（用于排除）
 */
const excludeGoodsIds = computed(() => {
  return props.form.items
    .filter(item => item.goods)
    .map(item => item.goods)
})

const addItem = () => {
  emit('add-item')
}

const removeItem = (index) => {
  emit('remove-item', index)
}

/**
 * 打开商品选择弹窗
 */
const openGoodsSelect = (index) => {
  currentEditIndex.value = index
  goodsSelectVisible.value = true
}

/**
 * 处理商品选择
 */
const handleGoodsSelect = (goods) => {
  if (currentEditIndex.value !== null) {
    emit('goods-change', props.form.items[currentEditIndex.value], currentEditIndex.value, goods)
  }
  currentEditIndex.value = null
}

/**
 * 处理商品编码输入变化
 */
const handleCodeChange = (row, index) => {
  emit('code-change', row, index)
}

/**
 * 处理商品编码回车
 */
const handleCodeEnter = (row, index) => {
  emit('code-change', row, index)
}

/**
 * 处理规格变化
 */
const handleSpecChange = (row) => {
  emit('spec-change', row)
}

const handleQuantityChange = (row) => {
  if (row.quantity && row.price) {
    row.amount = (row.quantity * row.price).toFixed(2)
  }
  emit('quantity-input', row, row.quantity)
}

const handlePriceChange = (row) => {
  if (row.quantity && row.price) {
    row.amount = (row.quantity * row.price).toFixed(2)
  }
  emit('price-input', row, row.price)
}

const handleDialogClose = () => {
  emit('dialog-close')
}

const handleSubmit = async () => {
  if (!formRef.value) return
  
  try {
    await formRef.value.validate()
    emit('submit')
  } catch (error) {
    // 验证失败
  }
}

/**
 * 获取商品的规格列表
 */
const getGoodsSpecs = (goodsId) => {
  const goods = props.goodsList.find(g => g.id === goodsId)
  if (!goods || !goods.spec) return []
  // 如果规格字段包含多个规格（用逗号分隔），则拆分
  if (typeof goods.spec === 'string' && goods.spec.includes(',')) {
    return goods.spec.split(',').map(s => s.trim()).filter(s => s)
  }
  return goods.spec ? [goods.spec] : []
}

const formatAmount = (amount) => {
  if (!amount) return '0.00'
  return Number(amount).toFixed(2)
}

defineExpose({
  formRef,
  resetFields: () => formRef.value?.resetFields(),
  validate: () => formRef.value?.validate()
})
</script>

<style scoped>
.purchase-order-dialog :deep(.el-dialog__body) {
  padding: 16px 20px;
  max-height: 60vh;
  overflow-y: auto;
}

.purchase-order-dialog :deep(.el-dialog__header) {
  border-bottom: 1px solid #ebeef5;
  padding: 14px 20px;
  margin: 0;
}

.purchase-order-dialog :deep(.el-dialog__title) {
  font-size: 15px;
  font-weight: 600;
  color: #303133;
}

.purchase-order-dialog :deep(.el-dialog__footer) {
  border-top: 1px solid #ebeef5;
  padding: 12px 20px;
}

.order-form {
  padding: 0;
}

.form-section {
  margin-bottom: 16px;
  background: #fff;
  border: 1px solid #ebeef5;
  border-radius: 4px;
  padding: 14px 16px 4px;
}

.form-section:last-child {
  margin-bottom: 0;
}

.form-section :deep(.el-form-item) {
  margin-bottom: 12px;
}

.items-section {
  padding: 0;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: #fafafa;
  border-bottom: 1px solid #ebeef5;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 20px;
}

.section-title {
  font-size: 14px;
  font-weight: 600;
  color: #303133;
  position: relative;
  padding-left: 10px;
}

.section-title::before {
  content: '';
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 3px;
  height: 14px;
  background: #409eff;
  border-radius: 2px;
}

.summary-info {
  display: flex;
  align-items: center;
  gap: 16px;
}

.summary-item {
  display: flex;
  align-items: center;
  gap: 4px;
}

.summary-label {
  font-size: 13px;
  color: #909399;
}

.summary-value {
  font-size: 15px;
  font-weight: 600;
  color: #409eff;
}

.summary-value.amount {
  color: #f56c6c;
  font-size: 16px;
}

.table-wrapper {
  padding: 0;
}

.items-table {
  border-left: none;
  border-right: none;
  border-bottom: none;
}

.items-table :deep(.el-table__header-wrapper th) {
  background: #fafafa !important;
}

.items-table :deep(.el-input-number) {
  width: 100%;
}

.items-table :deep(.el-input-number .el-input__inner) {
  text-align: center;
  padding: 0 6px;
}

.goods-name-cell {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 4px 8px;
  cursor: pointer;
  border-radius: 4px;
  transition: all 0.2s;
  min-height: 24px;
}

.goods-name-cell:hover {
  background: #f5f7fa;
}

.goods-name-cell .placeholder-text {
  color: #c0c4cc;
}

.goods-name-cell .select-icon {
  color: #c0c4cc;
  font-size: 14px;
  opacity: 0;
  transition: opacity 0.2s;
}

.goods-name-cell:hover .select-icon {
  opacity: 1;
}

.quantity-unit-cell {
  display: flex;
  align-items: center;
  gap: 8px;
}

.quantity-input {
  flex: 1;
}

.quantity-input :deep(.el-input__inner) {
  color: #409eff;
  font-weight: 600;
  font-size: 14px;
}

.unit-text-inline {
  flex-shrink: 0;
  color: #303133;
  font-size: 14px;
  font-weight: 400;
  white-space: nowrap;
}

.amount-text {
  color: #f56c6c;
  font-weight: 600;
  font-size: 13px;
}

.empty-state {
  padding: 50px 20px;
  text-align: center;
  background: #fafafa;
}

.empty-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
}

.empty-icon {
  font-size: 48px;
  color: #c0c4cc;
}

.empty-text {
  color: #909399;
  font-size: 14px;
  margin: 0;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

.dialog-footer .el-button {
  min-width: 80px;
}

@media screen and (max-width: 992px) {
  .purchase-order-dialog :deep(.el-dialog) {
    width: 90% !important;
  }
  
  .form-section :deep(.el-col-8) {
    width: 100%;
    margin-bottom: 0;
  }
  
  .header-left {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
  
  .section-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
  
  .section-header .el-button {
    width: 100%;
  }
  
  .quantity-unit-cell {
    flex-direction: column;
    gap: 4px;
  }
  
  .unit-text-inline {
    width: 100%;
    text-align: center;
  }
}
</style>

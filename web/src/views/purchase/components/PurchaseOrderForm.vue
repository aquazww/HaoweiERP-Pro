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
      label-width="100px"
      class="order-form"
    >
      <el-row :gutter="20">
        <el-col :span="8">
          <el-form-item label="供应商" prop="supplier">
            <el-select 
              v-model="form.supplier" 
              placeholder="请选择供应商"
              style="width: 100%"
              filterable
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
            />
          </el-form-item>
        </el-col>
      </el-row>

      <el-form-item label="备注">
        <el-input 
          v-model="form.remark" 
          type="textarea"
          :rows="2"
          placeholder="请输入备注信息（选填）"
        />
      </el-form-item>

      <el-divider content-position="left">
        <span class="divider-title">采购明细</span>
      </el-divider>

      <div class="items-toolbar">
        <el-button type="primary" :icon="Plus" @click="addItem">添加商品</el-button>
        <div class="items-summary">
          <span>合计数量：<strong>{{ totalQuantity }}</strong></span>
          <span>合计金额：<strong>¥{{ totalAmount }}</strong></span>
        </div>
      </div>

      <el-table 
        :data="form.items" 
        border 
        style="width: 100%"
        max-height="400"
        class="items-table"
      >
        <el-table-column label="商品" min-width="180">
          <template #default="{ row, $index }">
            <el-select 
              v-model="row.goods" 
              placeholder="请选择商品"
              style="width: 100%"
              filterable
              @change="handleGoodsChange(row, $index)"
            >
              <el-option 
                v-for="item in availableGoods" 
                :key="item.id" 
                :label="item.name" 
                :value="item.id"
              />
            </el-select>
          </template>
        </el-table-column>
        <el-table-column label="数量" width="120">
          <template #default="{ row }">
            <el-input
              :model-value="row.quantity"
              @input="(val) => handleQuantityInput(row, val)"
              @blur="handleQuantityBlur(row)"
              placeholder="请输入"
              :class="{ 'is-error': row._quantityError }"
            />
            <div class="error-tip" v-if="row._quantityError">{{ row._quantityError }}</div>
          </template>
        </el-table-column>
        <el-table-column label="单位" width="80" align="center">
          <template #default="{ row }">
            {{ getGoodsUnit(row.goods) }}
          </template>
        </el-table-column>
        <el-table-column label="单价" width="120">
          <template #default="{ row }">
            <el-input
              :model-value="row.price"
              @input="(val) => handlePriceInput(row, val)"
              @blur="handlePriceBlur(row)"
              placeholder="请输入"
              :class="{ 'is-error': row._priceError }"
            >
              <template #prefix>¥</template>
            </el-input>
            <div class="error-tip" v-if="row._priceError">{{ row._priceError }}</div>
          </template>
        </el-table-column>
        <el-table-column label="金额" width="100" align="right">
          <template #default="{ row }">
            ¥{{ row.amount?.toFixed(2) || '0.00' }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="80" align="center" fixed="right">
          <template #default="{ $index }">
            <el-button 
              type="danger" 
              link 
              :icon="Delete"
              @click="removeItem($index)"
            />
          </template>
        </el-table-column>
      </el-table>
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
</template>

<script setup>
import { ref, watch } from 'vue'
import { Plus, Delete } from '@element-plus/icons-vue'

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
  availableGoods: {
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
  'quantity-input',
  'quantity-blur',
  'price-input',
  'price-blur',
  'dialog-close'
])

const dialogVisible = ref(props.modelValue)
const formRef = ref(null)

watch(() => props.modelValue, (val) => {
  dialogVisible.value = val
})

watch(dialogVisible, (val) => {
  emit('update:modelValue', val)
})

const addItem = () => {
  emit('add-item')
}

const removeItem = (index) => {
  emit('remove-item', index)
}

const handleGoodsChange = (row, index) => {
  emit('goods-change', row, index)
}

const handleQuantityInput = (row, value) => {
  emit('quantity-input', row, value)
}

const handleQuantityBlur = (row) => {
  emit('quantity-blur', row)
}

const handlePriceInput = (row, value) => {
  emit('price-input', row, value)
}

const handlePriceBlur = (row) => {
  emit('price-blur', row)
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

const getGoodsUnit = (goodsId) => {
  const goods = props.goodsList.find(g => g.id === goodsId)
  return goods?.unit?.name || '-'
}

defineExpose({
  formRef,
  resetFields: () => formRef.value?.resetFields(),
  validate: () => formRef.value?.validate()
})
</script>

<style scoped>
.purchase-order-dialog :deep(.el-dialog__body) {
  padding: 20px;
}

.order-form .divider-title {
  font-size: 14px;
  font-weight: 500;
  color: #303133;
}

.items-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.items-summary {
  display: flex;
  gap: 20px;
  font-size: 14px;
  color: #606266;
}

.items-summary strong {
  color: #409eff;
  font-size: 15px;
}

.items-table :deep(.el-input__wrapper) {
  padding: 0 8px;
}

.items-table .error-tip {
  font-size: 11px;
  color: #f56c6c;
  margin-top: 2px;
}

.items-table :deep(.is-error .el-input__wrapper) {
  box-shadow: 0 0 0 1px #f56c6c inset;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}
</style>

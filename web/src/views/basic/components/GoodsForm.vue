<template>
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
            <el-tree-select
              v-model="form.category"
              :data="categoryOptions"
              :props="{ value: 'id', label: 'name', children: 'children', disabled: 'disabled' }"
              placeholder="请选择商品分类（仅二级及以下）"
              style="width: 100%"
              filterable
              clearable
              :filter-node-method="filterCategoryNode"
              check-strictly
              :render-after-expand="false"
              node-key="id"
              highlight-current
            >
              <template #default="{ node, data }">
                <span class="category-select-node" :class="{ 'is-disabled': data.disabled }">
                  <el-icon v-if="data.level === 1" class="level-icon"><Warning /></el-icon>
                  {{ data.name }}
                  <el-tag v-if="data.level === 1" size="small" type="warning" effect="plain">不可选</el-tag>
                </span>
              </template>
            </el-tree-select>
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="计量单位" prop="unit">
            <el-select 
              v-model="form.unit" 
              placeholder="请选择计量单位"
              style="width: 100%"
              filterable
              allow-create
            >
              <el-option 
                v-for="item in unitList" 
                :key="item.id" 
                :label="item.name" 
                :value="item.id"
              />
            </el-select>
          </el-form-item>
        </el-col>
      </el-row>

      <el-row :gutter="20">
        <el-col :span="12">
          <el-form-item label="规格">
            <el-input 
              v-model="form.spec" 
              placeholder="请输入规格"
              maxlength="100"
            />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="条形码">
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
</template>

<script setup>
import { ref, watch } from 'vue'
import { Warning } from '@element-plus/icons-vue'
import { formatInputNumber } from '../../../utils/format'

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  },
  dialogTitle: {
    type: String,
    default: '新增商品'
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
  priceErrors: {
    type: Object,
    default: () => ({})
  },
  categoryOptions: {
    type: Array,
    default: () => []
  },
  unitList: {
    type: Array,
    default: () => []
  },
  submitLoading: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:modelValue', 'submit', 'price-input', 'price-blur', 'dialog-close'])

const dialogVisible = ref(props.modelValue)
const formRef = ref(null)

watch(() => props.modelValue, (val) => {
  dialogVisible.value = val
})

watch(dialogVisible, (val) => {
  emit('update:modelValue', val)
})

const handlePriceInput = (field, value) => {
  emit('price-input', field, value)
}

const handlePriceBlur = (field) => {
  emit('price-blur', field)
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

const filterCategoryNode = (value, data) => {
  if (!value) return true
  return data.name.includes(value) || (data.code && data.code.toLowerCase().includes(value.toLowerCase()))
}

defineExpose({
  formRef,
  resetFields: () => formRef.value?.resetFields(),
  validate: () => formRef.value?.validate()
})
</script>

<style scoped>
.goods-form .price-input-wrapper {
  position: relative;
}

.goods-form .price-input-wrapper .error-tip {
  position: absolute;
  bottom: -18px;
  left: 0;
  font-size: 11px;
  color: #f56c6c;
  white-space: nowrap;
}

.goods-form .price-input-wrapper.has-error {
  margin-bottom: 18px;
}

.goods-form .price-input :deep(.el-input__wrapper) {
  padding-left: 8px;
}

.goods-form .input-prefix {
  color: #909399;
  font-weight: 500;
}

.goods-form :deep(.el-divider__text) {
  font-size: 13px;
  color: #606266;
  font-weight: 500;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.category-select-node {
  display: flex;
  align-items: center;
  gap: 6px;
}

.category-select-node.is-disabled {
  color: #909399;
}

.category-select-node .level-icon {
  color: #E6A23C;
  font-size: 14px;
}
</style>

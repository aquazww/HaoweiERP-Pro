<template>
  <el-dialog
    :model-value="modelValue"
    @update:model-value="$emit('update:modelValue', $event)"
    :title="dialogTitle"
    width="900px"
    destroy-on-close
  >
    <el-form
      ref="formRef"
      :model="form"
      :rules="rules"
      label-width="80px"
    >
      <el-row :gutter="20">
        <el-col :span="8">
          <el-form-item label="客户" prop="customer">
            <el-select
              v-model="form.customer"
              placeholder="选择客户"
              filterable
              style="width: 100%"
            >
              <el-option
                v-for="item in customerList"
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
              placeholder="选择仓库"
              style="width: 100%"
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
          <el-form-item label="备注">
            <el-input v-model="form.remark" placeholder="请输入备注" />
          </el-form-item>
        </el-col>
      </el-row>
      
      <el-divider content-position="left">销售明细</el-divider>
      
      <div class="items-header">
        <el-button type="primary" size="small" @click="$emit('add-item')">添加商品</el-button>
      </div>
      
      <el-table :data="form.items" border size="small">
        <el-table-column label="商品" min-width="200">
          <template #default="{ row, $index }">
            <el-select
              v-model="row.goods"
              placeholder="选择商品"
              filterable
              style="width: 100%"
              @change="(val) => $emit('goods-change', val, $index)"
            >
              <el-option
                v-for="item in goodsList"
                :key="item.id"
                :label="`${item.code} - ${item.name}`"
                :value="item.id"
              />
            </el-select>
          </template>
        </el-table-column>
        <el-table-column label="单位" width="80" align="center">
          <template #default="{ row }">{{ row.unit_name || '-' }}</template>
        </el-table-column>
        <el-table-column label="数量" width="120">
          <template #default="{ row, $index }">
            <el-input-number
              v-model="row.quantity"
              :min="1"
              size="small"
              style="width: 100%"
              @input="$emit('quantity-input', $index)"
            />
          </template>
        </el-table-column>
        <el-table-column label="单价" width="120">
          <template #default="{ row, $index }">
            <el-input-number
              v-model="row.price"
              :min="0"
              :precision="2"
              size="small"
              style="width: 100%"
              @input="$emit('price-input', $index)"
            />
          </template>
        </el-table-column>
        <el-table-column label="金额" width="100" align="right">
          <template #default="{ row }">
            ¥{{ (row.quantity * row.price || 0).toFixed(2) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="60" align="center">
          <template #default="{ $index }">
            <el-button type="danger" link size="small" @click="$emit('remove-item', $index)">
              <el-icon><Delete /></el-icon>
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <div class="items-summary">
        <span>合计数量: {{ totalQuantity }}</span>
        <span>合计金额: ¥{{ totalAmount.toFixed(2) }}</span>
      </div>
    </el-form>
    
    <template #footer>
      <el-button @click="$emit('update:modelValue', false)">取消</el-button>
      <el-button type="primary" @click="$emit('submit')" :loading="submitLoading">保存</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref } from 'vue'
import { Delete } from '@element-plus/icons-vue'

defineProps({
  modelValue: { type: Boolean, default: false },
  dialogTitle: { type: String, default: '' },
  isEdit: { type: Boolean, default: false },
  form: { type: Object, default: () => ({}) },
  rules: { type: Object, default: () => ({}) },
  customerList: { type: Array, default: () => [] },
  warehouseList: { type: Array, default: () => [] },
  goodsList: { type: Array, default: () => [] },
  totalQuantity: { type: Number, default: 0 },
  totalAmount: { type: Number, default: 0 },
  submitLoading: { type: Boolean, default: false }
})

defineEmits(['update:modelValue', 'submit', 'add-item', 'remove-item', 'goods-change', 'quantity-input', 'price-input'])

const formRef = ref(null)

defineExpose({ formRef })
</script>

<style scoped>
.items-header {
  margin-bottom: 12px;
}

.items-summary {
  margin-top: 12px;
  display: flex;
  justify-content: flex-end;
  gap: 24px;
  font-size: 14px;
  color: #606266;
}
</style>

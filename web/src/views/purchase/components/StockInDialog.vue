<template>
  <el-dialog 
    v-model="dialogVisible" 
    title="采购入库" 
    width="800px"
    class="stock-in-dialog"
    :close-on-click-modal="false"
  >
    <div class="stock-in-content" v-if="purchaseOrder">
      <div class="order-info">
        <div class="info-item">
          <span class="label">采购单号：</span>
          <span class="value">{{ purchaseOrder.order_no }}</span>
        </div>
        <div class="info-item">
          <span class="label">供应商：</span>
          <span class="value">{{ purchaseOrder.supplier_name }}</span>
        </div>
        <div class="info-item">
          <span class="label">入库仓库：</span>
          <span class="value">{{ purchaseOrder.warehouse_name }}</span>
        </div>
      </div>

      <el-form ref="formRef" :model="form" :rules="rules" label-width="80px" class="stock-in-form">
        <el-form-item label="入库备注" prop="remark">
          <el-input 
            v-model="form.remark" 
            type="textarea" 
            :rows="2"
            placeholder="请输入入库备注（选填）"
          />
        </el-form-item>
      </el-form>

      <div class="items-title">
        <span>入库商品明细</span>
        <span class="tips">请确认入库数量，可修改实际入库数量</span>
      </div>

      <el-table :data="form.items" border class="items-table">
        <el-table-column type="index" label="序号" width="60" align="center" />
        <el-table-column prop="goods_name" label="商品名称" min-width="140">
          <template #default="{ row }">
            <div class="goods-cell">
              <span class="goods-name">{{ row.goods_name }}</span>
              <span class="goods-spec" v-if="row.goods_spec">{{ row.goods_spec }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="unit" label="单位" width="70" align="center">
          <template #default="{ row }">
            {{ row.unit || '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="quantity" label="采购数量" width="100" align="center">
          <template #default="{ row }">
            <span class="purchase-qty">{{ formatQuantity(row.quantity) }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="received_quantity" label="已入库" width="90" align="center">
          <template #default="{ row }">
            <span class="received-qty">{{ formatQuantity(row.received_quantity || 0) }}</span>
          </template>
        </el-table-column>
        <el-table-column label="本次入库" width="130" align="center">
          <template #default="{ row }">
            <el-input-number
              v-model="row.this_quantity"
              :min="0"
              :max="getMaxQuantity(row)"
              :precision="0"
              :step="1"
              :controls="false"
              size="small"
              class="quantity-input"
            />
          </template>
        </el-table-column>
        <el-table-column prop="price" label="单价" width="90" align="right">
          <template #default="{ row }">
            ¥{{ formatPrice(row.price) }}
          </template>
        </el-table-column>
        <el-table-column label="金额" width="100" align="right">
          <template #default="{ row }">
            <span class="amount-text">¥{{ formatPrice(row.this_quantity * row.price) }}</span>
          </template>
        </el-table-column>
      </el-table>

      <div class="summary-bar">
        <div class="summary-item">
          <span class="label">本次入库合计：</span>
          <span class="value">{{ formatQuantity(totalThisQuantity) }} 件</span>
        </div>
        <div class="summary-item highlight">
          <span class="label">入库总金额：</span>
          <span class="value">¥{{ formatPrice(totalThisAmount) }}</span>
        </div>
      </div>
    </div>

    <template #footer>
      <div class="dialog-footer">
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button 
          type="primary" 
          :loading="submitLoading"
          @click="handleSubmit"
        >
          确认入库
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup>
/**
 * 采购入库弹窗组件
 * 处理采购单的入库操作
 */
import { ref, watch, computed, reactive } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { formatPrice, formatQuantity } from '../../../utils/format'
import { createStockIn, confirmStockIn } from '../../../api/inventory'

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  },
  purchaseOrder: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['update:modelValue', 'success'])

const dialogVisible = ref(props.modelValue)
const formRef = ref(null)
const submitLoading = ref(false)

const form = reactive({
  remark: '',
  items: []
})

const rules = {
  remark: [
    { max: 200, message: '备注不能超过200个字符', trigger: 'blur' }
  ]
}

watch(() => props.modelValue, (val) => {
  dialogVisible.value = val
  if (val && props.purchaseOrder) {
    initForm()
  }
})

watch(dialogVisible, (val) => {
  emit('update:modelValue', val)
})

const initForm = () => {
  form.remark = ''
  form.items = (props.purchaseOrder.items || []).map(item => ({
    ...item,
    received_quantity: item.received_quantity || 0,
    this_quantity: Math.max(0, Number(item.quantity) - Number(item.received_quantity || 0))
  }))
}

const getMaxQuantity = (row) => {
  return Math.max(0, Number(row.quantity) - Number(row.received_quantity || 0))
}

const totalThisQuantity = computed(() => {
  return form.items.reduce((sum, item) => {
    return sum + (Number(item.this_quantity) || 0)
  }, 0)
})

const totalThisAmount = computed(() => {
  return form.items.reduce((sum, item) => {
    return sum + (Number(item.this_quantity) || 0) * (Number(item.price) || 0)
  }, 0)
})

const handleSubmit = async () => {
  if (!formRef.value) return
  
  try {
    await formRef.value.validate()
  } catch (error) {
    return
  }

  const hasItems = form.items.some(item => item.this_quantity > 0)
  if (!hasItems) {
    ElMessage.warning('请至少选择一个商品进行入库')
    return
  }

  try {
    await ElMessageBox.confirm(
      '确认执行入库操作？入库后库存将实时更新。',
      '入库确认',
      {
        confirmButtonText: '确认入库',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
  } catch {
    return
  }

  submitLoading.value = true
  try {
    const stockInData = {
      purchase_order: props.purchaseOrder.id,
      warehouse: props.purchaseOrder.warehouse,
      remark: form.remark,
      items: form.items
        .filter(item => item.this_quantity > 0)
        .map(item => ({
          goods: item.goods,
          quantity: item.this_quantity,
          price: item.price
        }))
    }

    const createRes = await createStockIn(stockInData)
    
    if (createRes && createRes.id) {
      await confirmStockIn(createRes.id)
    }

    ElMessage.success('入库成功')
    dialogVisible.value = false
    emit('success')
  } catch (error) {
    ElMessage.error(error.message || '入库失败，请重试')
  } finally {
    submitLoading.value = false
  }
}
</script>

<style scoped>
.stock-in-dialog :deep(.el-dialog__body) {
  padding: 20px;
}

.stock-in-content {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.order-info {
  display: flex;
  gap: 24px;
  padding: 12px 16px;
  background: #f5f7fa;
  border-radius: 8px;
}

.order-info .info-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.order-info .label {
  font-size: 13px;
  color: #909399;
}

.order-info .value {
  font-size: 14px;
  color: #303133;
  font-weight: 500;
}

.stock-in-form {
  margin-bottom: 0;
}

.items-title {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
  border-bottom: 1px solid #ebeef5;
  margin-bottom: 12px;
}

.items-title span:first-child {
  font-size: 14px;
  font-weight: 500;
  color: #303133;
}

.items-title .tips {
  font-size: 12px;
  color: #909399;
}

.items-table .goods-cell {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.items-table .goods-name {
  font-weight: 500;
  color: #303133;
}

.items-table .goods-spec {
  font-size: 12px;
  color: #909399;
}

.items-table .purchase-qty {
  color: #409eff;
  font-weight: 500;
}

.items-table .received-qty {
  color: #67c23a;
  font-weight: 500;
}

.items-table .quantity-input {
  width: 100%;
}

.items-table .amount-text {
  color: #f56c6c;
  font-weight: 500;
}

.summary-bar {
  display: flex;
  justify-content: flex-end;
  gap: 32px;
  padding: 12px 16px;
  background: #fafafa;
  border-radius: 4px;
  margin-top: 12px;
}

.summary-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.summary-item .label {
  font-size: 13px;
  color: #909399;
}

.summary-item .value {
  font-size: 14px;
  font-weight: 500;
  color: #303133;
}

.summary-item.highlight .value {
  color: #f56c6c;
  font-size: 16px;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}
</style>

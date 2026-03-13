<template>
  <el-dialog
    :model-value="modelValue"
    @update:model-value="$emit('update:modelValue', $event)"
    :title="dialogTitle"
    width="500px"
    destroy-on-close
  >
    <el-form
      ref="formRef"
      :model="form"
      :rules="rules"
      label-width="80px"
    >
      <el-form-item label="付款金额" prop="amount">
        <el-input-number
          v-model="form.amount"
          :min="0"
          :precision="2"
          style="width: 100%"
        />
      </el-form-item>
      <el-form-item label="付款方式" prop="payment_method">
        <el-select v-model="form.payment_method" placeholder="选择付款方式" style="width: 100%">
          <el-option label="现金" value="cash" />
          <el-option label="银行转账" value="bank" />
          <el-option label="支票" value="check" />
          <el-option label="其他" value="other" />
        </el-select>
      </el-form-item>
      <el-form-item label="付款日期" prop="payment_date">
        <el-date-picker
          v-model="form.payment_date"
          type="date"
          placeholder="选择日期"
          style="width: 100%"
          value-format="YYYY-MM-DD"
        />
      </el-form-item>
      <el-form-item label="备注">
        <el-input v-model="form.remark" type="textarea" :rows="2" placeholder="请输入备注" />
      </el-form-item>
    </el-form>
    
    <template #footer>
      <el-button @click="$emit('update:modelValue', false)">取消</el-button>
      <el-button type="primary" @click="$emit('submit')" :loading="submitLoading">确认付款</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref } from 'vue'

defineProps({
  modelValue: { type: Boolean, default: false },
  dialogTitle: { type: String, default: '' },
  isEdit: { type: Boolean, default: false },
  form: { type: Object, default: () => ({}) },
  rules: { type: Object, default: () => ({}) },
  submitLoading: { type: Boolean, default: false }
})

defineEmits(['update:modelValue', 'submit'])

const formRef = ref(null)

defineExpose({ formRef })
</script>

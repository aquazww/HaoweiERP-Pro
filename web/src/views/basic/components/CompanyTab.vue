<template>
  <div class="company-tab" v-loading="companyLoading">
    <el-form
      ref="formRef"
      :model="companyForm"
      :rules="companyRules"
      label-width="100px"
      class="company-form"
    >
      <el-row :gutter="24">
        <el-col :span="12">
          <el-form-item label="公司名称" prop="name">
            <el-input v-model="companyForm.name" placeholder="请输入公司名称" />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="联系电话" prop="phone">
            <el-input v-model="companyForm.phone" placeholder="请输入联系电话" />
          </el-form-item>
        </el-col>
      </el-row>
      
      <el-row :gutter="24">
        <el-col :span="12">
          <el-form-item label="传真" prop="fax">
            <el-input v-model="companyForm.fax" placeholder="请输入传真" />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="邮箱" prop="email">
            <el-input v-model="companyForm.email" placeholder="请输入邮箱" />
          </el-form-item>
        </el-col>
      </el-row>
      
      <el-form-item label="公司地址" prop="address">
        <el-input v-model="companyForm.address" placeholder="请输入公司地址" />
      </el-form-item>
      
      <el-row :gutter="24">
        <el-col :span="12">
          <el-form-item label="开户银行" prop="bank_name">
            <el-input v-model="companyForm.bank_name" placeholder="请输入开户银行" />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="银行账号" prop="bank_account">
            <el-input v-model="companyForm.bank_account" placeholder="请输入银行账号" />
          </el-form-item>
        </el-col>
      </el-row>
      
      <el-row :gutter="24">
        <el-col :span="12">
          <el-form-item label="税号" prop="tax_no">
            <el-input v-model="companyForm.tax_no" placeholder="请输入税号" />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="纳税人类型" prop="taxpayer_type">
            <el-select v-model="companyForm.taxpayer_type" placeholder="请选择" style="width: 100%">
              <el-option label="一般纳税人" value="general" />
              <el-option label="小规模纳税人" value="small" />
            </el-select>
          </el-form-item>
        </el-col>
      </el-row>
      
      <el-row :gutter="24">
        <el-col :span="12">
          <el-form-item label="公司Logo">
            <el-upload
              class="logo-uploader"
              :show-file-list="false"
              :before-upload="(file) => $emit('logo-upload', file)"
              accept="image/*"
            >
              <img v-if="companyForm.logo" :src="companyForm.logo" class="logo-preview" />
              <el-icon v-else class="logo-uploader-icon"><Plus /></el-icon>
            </el-upload>
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="公司印章">
            <el-upload
              class="stamp-uploader"
              :show-file-list="false"
              :before-upload="(file) => $emit('stamp-upload', file)"
              accept="image/*"
            >
              <img v-if="companyForm.stamp" :src="companyForm.stamp" class="stamp-preview" />
              <el-icon v-else class="stamp-uploader-icon"><Plus /></el-icon>
            </el-upload>
          </el-form-item>
        </el-col>
      </el-row>
      
      <el-form-item>
        <el-button type="primary" @click="$emit('save')" :loading="companySubmitLoading">保存设置</el-button>
      </el-form-item>
    </el-form>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { Plus } from '@element-plus/icons-vue'

const props = defineProps({
  companyForm: { type: Object, default: () => ({}) },
  companyRules: { type: Object, default: () => ({}) },
  companyLoading: { type: Boolean, default: false },
  companySubmitLoading: { type: Boolean, default: false },
  companyErrorFields: { type: Object, default: () => ({}) }
})

defineEmits(['save', 'clear-error', 'logo-upload', 'stamp-upload'])

const formRef = ref(null)

defineExpose({ formRef })
</script>

<style scoped>
.company-tab {
  height: 100%;
  overflow-y: auto;
}

.company-form {
  max-width: 800px;
  padding: 20px;
}

.logo-uploader,
.stamp-uploader {
  border: 1px dashed #d9d9d9;
  border-radius: 6px;
  cursor: pointer;
  position: relative;
  overflow: hidden;
  width: 100px;
  height: 100px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.logo-uploader:hover,
.stamp-uploader:hover {
  border-color: #409eff;
}

.logo-uploader-icon,
.stamp-uploader-icon {
  font-size: 28px;
  color: #8c939d;
}

.logo-preview,
.stamp-preview {
  width: 100%;
  height: 100%;
  object-fit: contain;
}
</style>

/**
 * 公司信息管理组合式函数
 * 管理公司信息的加载、保存、图片上传等操作
 */
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import { getCompanyInfo, updateCompanyInfo } from '@/api/basic'

export function useCompany() {
  const companyLoading = ref(false)
  const companySubmitLoading = ref(false)
  const companyFormRef = ref(null)
  const companyErrorFields = reactive({})
  
  const companyForm = reactive({
    name: '',
    short_name: '',
    legal_person: '',
    credit_code: '',
    phone: '',
    email: '',
    registered_address: '',
    business_address: '',
    website: '',
    bank_name: '',
    bank_account: '',
    tax_number: '',
    invoice_title: '',
    fax: '',
    remark: '',
    logo_base64: '',
    stamp_base64: ''
  })
  
  const companyRules = {
    name: [{ required: true, message: '请输入公司名称', trigger: 'blur' }]
  }
  
  const clearFieldError = (field) => {
    if (companyErrorFields[field]) {
      delete companyErrorFields[field]
    }
  }
  
  const loadCompanyInfo = async () => {
    companyLoading.value = true
    try {
      const res = await getCompanyInfo()
      const data = res.data || {}
      
      companyForm.name = data.name || ''
      companyForm.short_name = data.short_name || ''
      companyForm.legal_person = data.legal_person || ''
      companyForm.credit_code = data.credit_code || ''
      companyForm.phone = data.phone || ''
      companyForm.email = data.email || ''
      companyForm.registered_address = data.registered_address || ''
      companyForm.business_address = data.business_address || ''
      companyForm.website = data.website || ''
      companyForm.bank_name = data.bank_name || ''
      companyForm.bank_account = data.bank_account || ''
      companyForm.tax_number = data.tax_number || ''
      companyForm.invoice_title = data.invoice_title || ''
      companyForm.fax = data.fax || ''
      companyForm.remark = data.remark || ''
      companyForm.logo_base64 = data.logo_base64 || ''
      companyForm.stamp_base64 = data.stamp_base64 || ''
    } catch (error) {
      ElMessage.error('加载公司信息失败')
    } finally {
      companyLoading.value = false
    }
  }
  
  const handleSaveCompany = async () => {
    if (!companyFormRef.value) return
    
    try {
      await companyFormRef.value.validate()
    } catch (error) {
      return
    }
    
    companySubmitLoading.value = true
    try {
      const data = {
        name: companyForm.name,
        short_name: companyForm.short_name,
        legal_person: companyForm.legal_person,
        credit_code: companyForm.credit_code,
        phone: companyForm.phone,
        email: companyForm.email,
        registered_address: companyForm.registered_address,
        business_address: companyForm.business_address,
        website: companyForm.website,
        bank_name: companyForm.bank_name,
        bank_account: companyForm.bank_account,
        tax_number: companyForm.tax_number,
        invoice_title: companyForm.invoice_title,
        fax: companyForm.fax,
        remark: companyForm.remark,
        logo_base64: companyForm.logo_base64,
        stamp_base64: companyForm.stamp_base64
      }
      
      await updateCompanyInfo(data)
      ElMessage.success('保存成功')
      loadCompanyInfo()
    } catch (error) {
      const errorData = error.response?.data
      if (errorData?.data) {
        Object.keys(errorData.data).forEach(field => {
          companyErrorFields[field] = true
        })
        const messages = Object.values(errorData.data).flat()
        ElMessage.error(messages.join('；'))
      } else if (errorData?.msg) {
        ElMessage.error(errorData.msg)
      } else {
        ElMessage.error('保存失败')
      }
    } finally {
      companySubmitLoading.value = false
    }
  }
  
  const beforeLogoUpload = (file) => {
    const isImage = file.type.startsWith('image/')
    const isLt2M = file.size / 1024 / 1024 < 2
    
    if (!isImage) {
      ElMessage.error('只能上传图片文件')
      return false
    }
    if (!isLt2M) {
      ElMessage.error('图片大小不能超过 2MB')
      return false
    }
    return true
  }
  
  const beforeStampUpload = (file) => {
    return beforeLogoUpload(file)
  }
  
  const handleLogoUpload = async (options) => {
    const { file } = options
    const reader = new FileReader()
    reader.onload = (e) => {
      const base64 = e.target.result.split(',')[1]
      companyForm.logo_base64 = base64
    }
    reader.readAsDataURL(file)
  }
  
  const handleStampUpload = async (options) => {
    const { file } = options
    const reader = new FileReader()
    reader.onload = (e) => {
      const base64 = e.target.result.split(',')[1]
      companyForm.stamp_base64 = base64
    }
    reader.readAsDataURL(file)
  }
  
  return {
    companyLoading,
    companySubmitLoading,
    companyFormRef,
    companyErrorFields,
    companyForm,
    companyRules,
    clearFieldError,
    loadCompanyInfo,
    handleSaveCompany,
    beforeLogoUpload,
    beforeStampUpload,
    handleLogoUpload,
    handleStampUpload
  }
}

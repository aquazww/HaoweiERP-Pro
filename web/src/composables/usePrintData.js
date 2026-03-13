/**
 * 打印数据管理组合式函数
 * 管理送货单数据、公司信息等
 */
import { ref } from 'vue'
import { getCompanyInfo } from '@/api/basic'
import { error } from '@/utils/logger'

export function usePrintData() {
  const companyInfo = ref({
    name: '豪威工贸有限公司',
    short_name: '',
    address: '',
    phone: '',
    email: '',
    website: '',
    logo_base64: '',
    stamp_base64: ''
  })
  
  const deliveryData = ref({
    order_no: '',
    sale_order_no: '',
    customer_name: '',
    customer_contact: '',
    customer_phone: '',
    customer_address: '',
    warehouse_name: '',
    delivery_date: '',
    total_amount: 0,
    remark: '',
    items: []
  })
  
  const initDeliveryData = (stockOutData) => {
    if (!stockOutData) return
    const data = stockOutData
    deliveryData.value = {
      order_no: data.order_no || '',
      sale_order_no: data.sale_order_no || '',
      customer_name: data.customer_name || '',
      customer_contact: data.customer_contact || '',
      customer_phone: data.customer_phone || '',
      customer_address: data.customer_address || '',
      warehouse_name: data.warehouse_name || '',
      delivery_date: data.created_at ? data.created_at.split('T')[0] : new Date().toISOString().split('T')[0],
      total_amount: data.total_amount || 0,
      remark: data.remark || '',
      items: (data.items || []).map(item => ({
        goods_code: item.goods_code || '',
        goods_name: item.goods_name || '',
        goods_spec: item.goods_spec || '',
        unit_name: item.unit_name || '',
        quantity: item.quantity || 0,
        price: item.price || 0,
        amount: item.amount || 0,
        remark: item.remark || ''
      }))
    }
  }
  
  const loadCompanyInfo = async () => {
    try {
      const res = await getCompanyInfo()
      if (res.data) {
        companyInfo.value = {
          name: res.data.name || '豪威工贸有限公司',
          short_name: res.data.short_name || '',
          address: res.data.business_address || res.data.registered_address || '',
          phone: res.data.phone || '',
          email: res.data.email || '',
          website: res.data.website || '',
          logo_base64: res.data.logo_base64 || '',
          stamp_base64: res.data.stamp_base64 || ''
        }
      }
    } catch (err) {
      error('加载公司信息失败:', err)
    }
  }
  
  const getFieldValue = (key, element) => {
    if (element && element.content) {
      let content = element.content
      content = content.replace(/\{(\w+)\}/g, (match, fieldKey) => {
        if (fieldKey.startsWith('company_')) {
          const companyFieldMap = {
            'company_name': companyInfo.value.name,
            'company_address': companyInfo.value.address,
            'company_phone': companyInfo.value.phone,
            'company_email': companyInfo.value.email
          }
          return companyFieldMap[fieldKey] || ''
        }
        const value = deliveryData.value[fieldKey]
        if (fieldKey === 'total_amount') {
          return value ? `¥${Number(value).toFixed(2)}` : '¥0.00'
        }
        return value || ''
      })
      return content
    }
    
    const value = deliveryData.value[key]
    if (key === 'total_amount') {
      return value ? `¥${Number(value).toFixed(2)}` : '¥0.00'
    }
    return value || '-'
  }
  
  const getItemFieldValue = (item, key) => {
    const value = item[key]
    if (['price', 'amount'].includes(key)) {
      return value ? `¥${Number(value).toFixed(2)}` : '¥0.00'
    }
    return value || '-'
  }
  
  const formatAmount = (amount) => {
    return Number(amount || 0).toFixed(2)
  }
  
  const circleNumbers = ['①', '②', '③', '④', '⑤', '⑥', '⑦', '⑧', '⑨', '⑩']
  const copyNames = ['存根', '客户', '回单', '送货', '财务']
  const copyColors = ['白', '红', '黄', '蓝', '绿']
  
  const getCircleNumber = (index) => {
    return circleNumbers[index - 1] || index
  }
  
  const getCopyName = (index) => {
    return copyNames[index - 1] || `第${index}联`
  }
  
  const getCopyColor = (index) => {
    return copyColors[index - 1] || ''
  }
  
  return {
    companyInfo,
    deliveryData,
    initDeliveryData,
    loadCompanyInfo,
    getFieldValue,
    getItemFieldValue,
    formatAmount,
    getCircleNumber,
    getCopyName,
    getCopyColor
  }
}

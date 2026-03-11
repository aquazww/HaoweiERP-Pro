/**
 * 打印模板配置
 * 定义系统中打印功能的字段和格式配置
 */

/**
 * 送货单字段配置
 */
export const DeliveryNoteFields = {
  mainFields: [
    { key: 'order_no', label: '送货单号', visible: true, width: 150 },
    { key: 'sale_order_no', label: '销售单号', visible: true, width: 150 },
    { key: 'customer_name', label: '客户名称', visible: true, width: 150 },
    { key: 'customer_contact', label: '联系人', visible: true, width: 100 },
    { key: 'customer_phone', label: '联系电话', visible: true, width: 120 },
    { key: 'customer_address', label: '送货地址', visible: true, width: 250 },
    { key: 'warehouse_name', label: '发货仓库', visible: true, width: 120 },
    { key: 'delivery_date', label: '送货日期', visible: true, width: 120 },
    { key: 'total_amount', label: '总金额', visible: true, width: 120 },
    { key: 'remark', label: '备注', visible: true, width: 200 }
  ],
  detailFields: [
    { key: 'goods_code', label: '商品编码', visible: true, width: 100 },
    { key: 'goods_name', label: '商品名称', visible: true, width: 150 },
    { key: 'goods_spec', label: '规格型号', visible: true, width: 100 },
    { key: 'unit_name', label: '单位', visible: true, width: 60 },
    { key: 'quantity', label: '送货数量', visible: true, width: 80 },
    { key: 'price', label: '单价', visible: true, width: 80 },
    { key: 'amount', label: '金额', visible: true, width: 100 },
    { key: 'remark', label: '备注', visible: true, width: 120 }
  ]
}

/**
 * 默认打印设置
 */
export const DefaultPrintSettings = {
  paperSize: 'A4',
  orientation: 'portrait',
  margins: { top: 15, right: 10, bottom: 15, left: 10 },
  fontSize: '12px',
  header: '送货单',
  footer: '收货人签字：________________  收货日期：________________',
  showPageNumbers: true,
  showDate: true,
  showPrice: true,
  showAmount: true
}

/**
 * 获取送货单字段配置
 * @returns {Object} 字段配置
 */
export function getDeliveryNoteFields() {
  const savedConfig = localStorage.getItem('deliveryNoteFieldsConfig')
  if (savedConfig) {
    try {
      return JSON.parse(savedConfig)
    } catch (e) {
      console.error('解析保存的字段配置失败:', e)
    }
  }
  return DeliveryNoteFields
}

/**
 * 保存送货单字段配置
 * @param {Object} config - 字段配置
 */
export function saveDeliveryNoteFields(config) {
  try {
    localStorage.setItem('deliveryNoteFieldsConfig', JSON.stringify(config))
    return true
  } catch (e) {
    console.error('保存字段配置失败:', e)
    return false
  }
}

/**
 * 获取打印设置
 * @returns {Object} 打印设置
 */
export function getPrintSettings() {
  const savedSettings = localStorage.getItem('printSettings')
  if (savedSettings) {
    try {
      return { ...DefaultPrintSettings, ...JSON.parse(savedSettings) }
    } catch (e) {
      console.error('解析保存的打印设置失败:', e)
    }
  }
  return DefaultPrintSettings
}

/**
 * 保存打印设置
 * @param {Object} settings - 打印设置
 */
export function savePrintSettings(settings) {
  try {
    localStorage.setItem('printSettings', JSON.stringify(settings))
    return true
  } catch (e) {
    console.error('保存打印设置失败:', e)
    return false
  }
}

/**
 * 重置字段配置为默认值
 */
export function resetDeliveryNoteFields() {
  localStorage.removeItem('deliveryNoteFieldsConfig')
  return DeliveryNoteFields
}

/**
 * 重置打印设置为默认值
 */
export function resetPrintSettings() {
  localStorage.removeItem('printSettings')
  return DefaultPrintSettings
}

/**
 * 价格格式化工具
 * 统一商品价格、采购单价、销售单价等价格字段的显示格式
 */

/**
 * 格式化价格（两位小数）
 * @param {number|string} price - 价格值
 * @returns {string} 格式化后的价格字符串
 */
export const formatPrice = (price) => {
  if (price === undefined || price === null || price === '') return '0.00'
  const num = Number(price)
  if (isNaN(num)) return '0.00'
  return num.toFixed(2)
}

/**
 * 格式化数量（整数）
 * @param {number|string} quantity - 数量值
 * @returns {string} 格式化后的数量字符串
 */
export const formatQuantity = (quantity) => {
  if (quantity === undefined || quantity === null || quantity === '') return '0'
  const num = Number(quantity)
  if (isNaN(num)) return '0'
  return Math.round(num).toString()
}

/**
 * 格式化输入数字
 * @param {number|string} value - 数值
 * @param {boolean} isQuantity - 是否为数量字段
 * @returns {string} 格式化后的字符串
 */
export const formatInputNumber = (value, isQuantity = false) => {
  if (value === null || value === undefined || value === '') return ''
  const num = Number(value)
  if (isNaN(num)) return ''
  if (isQuantity) {
    return Math.round(num).toString()
  }
  return num.toFixed(2)
}

/**
 * 解析输入数字
 * @param {string} value - 输入值
 * @returns {number|null} 解析后的数字
 */
export const parseInputNumber = (value) => {
  if (!value) return null
  const cleaned = String(value).replace(/[^\d.]/g, '')
  if (cleaned === '' || cleaned === '.') return null
  const num = parseFloat(cleaned)
  return isNaN(num) ? null : num
}

/**
 * 格式化金额（带货币符号）
 * @param {number|string} amount - 金额值
 * @returns {string} 格式化后的金额字符串
 */
export const formatAmount = (amount) => {
  return `¥${formatPrice(amount)}`
}

/**
 * 计算金额
 * @param {number} quantity - 数量
 * @param {number} price - 单价
 * @returns {string} 金额字符串
 */
export const calculateAmount = (quantity, price) => {
  const qty = Number(quantity) || 0
  const prc = Number(price) || 0
  return (qty * prc).toFixed(2)
}

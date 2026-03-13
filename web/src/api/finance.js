/**
 * 财务管理 API 接口
 * 包含付款单的增删改查和付款操作接口
 */
import request from './index'

// ==================== 付款单接口 ====================

/**
 * 获取付款单列表
 * @param {Object} params - 查询参数
 * @returns {Promise} 付款单列表
 */
export const getPayments = (params) => {
  return request.get('/finance/payments/', { params })
}

/**
 * 获取付款单详情
 * @param {number} id - 付款单ID
 * @returns {Promise} 付款单详情
 */
export const getPayment = (id) => {
  return request.get(`/finance/payments/${id}/`)
}

/**
 * 创建付款单
 * @param {Object} data - 付款单数据
 * @returns {Promise} 创建结果
 */
export const createPayment = (data) => {
  return request.post('/finance/payments/', data)
}

/**
 * 更新付款单
 * @param {number} id - 付款单ID
 * @param {Object} data - 更新数据
 * @returns {Promise} 更新结果
 */
export const updatePayment = (id, data) => {
  return request.put(`/finance/payments/${id}/`, data)
}

/**
 * 删除付款单
 * @param {number} id - 付款单ID
 * @returns {Promise} 删除结果
 */
export const deletePayment = (id) => {
  return request.delete(`/finance/payments/${id}/`)
}

/**
 * 执行付款操作
 * @param {number} id - 付款单ID
 * @param {Object} data - 付款数据
 * @returns {Promise} 付款结果
 */
export const payPayment = (id, data) => {
  return request.post(`/finance/payments/${id}/pay/`, data)
}

/**
 * 获取关联订单信息
 * @param {string} orderType - 订单类型
 * @param {number} orderId - 订单ID
 * @returns {Promise} 订单信息
 */
export const getPaymentOrderInfo = (orderType, orderId) => {
  return request.get('/finance/payments/order_info/', { params: { order_type: orderType, order_id: orderId } })
}

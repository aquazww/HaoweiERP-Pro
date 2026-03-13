/**
 * 采购管理 API 接口
 * 包含采购订单和采购明细的增删改查接口
 */
import request from './index'

// ==================== 采购订单接口 ====================

/**
 * 获取采购订单列表
 * @param {Object} params - 查询参数
 * @returns {Promise} 订单列表
 */
export const getPurchaseOrders = (params) => {
  return request.get('/purchase/orders/', { params })
}

/**
 * 获取采购订单详情
 * @param {number} id - 订单ID
 * @returns {Promise} 订单详情
 */
export const getPurchaseOrder = (id) => {
  return request.get(`/purchase/orders/${id}/`)
}

/**
 * 根据单号获取采购订单
 * @param {string} orderNo - 订单号
 * @returns {Promise} 订单详情
 */
export const getPurchaseOrderByNo = (orderNo) => {
  return request.get(`/purchase/orders/by-no/${orderNo}/`)
}

/**
 * 创建采购订单
 * @param {Object} data - 订单数据
 * @returns {Promise} 创建结果
 */
export const createPurchaseOrder = (data) => {
  return request.post('/purchase/orders/', data)
}

/**
 * 更新采购订单
 * @param {number} id - 订单ID
 * @param {Object} data - 更新数据
 * @returns {Promise} 更新结果
 */
export const updatePurchaseOrder = (id, data) => {
  return request.put(`/purchase/orders/${id}/`, data)
}

/**
 * 删除采购订单
 * @param {number} id - 订单ID
 * @returns {Promise} 删除结果
 */
export const deletePurchaseOrder = (id) => {
  return request.delete(`/purchase/orders/${id}/`)
}

// ==================== 采购明细接口 ====================

/**
 * 获取采购明细列表
 * @param {Object} params - 查询参数
 * @returns {Promise} 明细列表
 */
export const getPurchaseItems = (params) => {
  return request.get('/purchase/items/', { params })
}

/**
 * 创建采购明细
 * @param {Object} data - 明细数据
 * @returns {Promise} 创建结果
 */
export const createPurchaseItem = (data) => {
  return request.post('/purchase/items/', data)
}

/**
 * 更新采购明细
 * @param {number} id - 明细ID
 * @param {Object} data - 更新数据
 * @returns {Promise} 更新结果
 */
export const updatePurchaseItem = (id, data) => {
  return request.put(`/purchase/items/${id}/`, data)
}

/**
 * 删除采购明细
 * @param {number} id - 明细ID
 * @returns {Promise} 删除结果
 */
export const deletePurchaseItem = (id) => {
  return request.delete(`/purchase/items/${id}/`)
}

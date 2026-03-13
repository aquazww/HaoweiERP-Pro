/**
 * 销售管理 API 接口
 * 包含销售订单和销售明细的增删改查接口
 */
import request from './index'

// ==================== 销售订单接口 ====================

/**
 * 获取销售订单列表
 * @param {Object} params - 查询参数
 * @returns {Promise} 订单列表
 */
export const getSaleOrders = (params) => {
  return request.get('/sale/orders/', { params })
}

/**
 * 获取销售订单详情
 * @param {number} id - 订单ID
 * @returns {Promise} 订单详情
 */
export const getSaleOrder = (id) => {
  return request.get(`/sale/orders/${id}/`)
}

/**
 * 根据单号获取销售订单
 * @param {string} orderNo - 订单号
 * @returns {Promise} 订单详情
 */
export const getSaleOrderByNo = (orderNo) => {
  return request.get(`/sale/orders/by-no/${orderNo}/`)
}

/**
 * 创建销售订单
 * @param {Object} data - 订单数据
 * @returns {Promise} 创建结果
 */
export const createSaleOrder = (data) => {
  return request.post('/sale/orders/', data)
}

/**
 * 更新销售订单
 * @param {number} id - 订单ID
 * @param {Object} data - 更新数据
 * @returns {Promise} 更新结果
 */
export const updateSaleOrder = (id, data) => {
  return request.put(`/sale/orders/${id}/`, data)
}

/**
 * 删除销售订单
 * @param {number} id - 订单ID
 * @returns {Promise} 删除结果
 */
export const deleteSaleOrder = (id) => {
  return request.delete(`/sale/orders/${id}/`)
}

/**
 * 确认销售订单
 * @param {number} id - 订单ID
 * @returns {Promise} 确认结果
 */
export const confirmSaleOrder = (id) => {
  return request.post(`/sale/orders/${id}/confirm/`)
}

// ==================== 销售明细接口 ====================

/**
 * 获取销售明细列表
 * @param {Object} params - 查询参数
 * @returns {Promise} 明细列表
 */
export const getSaleItems = (params) => {
  return request.get('/sale/items/', { params })
}

/**
 * 创建销售明细
 * @param {Object} data - 明细数据
 * @returns {Promise} 创建结果
 */
export const createSaleItem = (data) => {
  return request.post('/sale/items/', data)
}

/**
 * 更新销售明细
 * @param {number} id - 明细ID
 * @param {Object} data - 更新数据
 * @returns {Promise} 更新结果
 */
export const updateSaleItem = (id, data) => {
  return request.put(`/sale/items/${id}/`, data)
}

/**
 * 删除销售明细
 * @param {number} id - 明细ID
 * @returns {Promise} 删除结果
 */
export const deleteSaleItem = (id) => {
  return request.delete(`/sale/items/${id}/`)
}

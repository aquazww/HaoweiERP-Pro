/**
 * 库存管理 API 接口
 * 包含库存查询、入库、出库、调拨、盘点等接口
 */
import request from './index'

// ==================== 库存查询接口 ====================

/**
 * 获取库存列表
 * @param {Object} params - 查询参数
 * @returns {Promise} 库存列表
 */
export const getInventory = (params) => {
  return request.get('/inventory/inventory/', { params })
}

/**
 * 删除库存记录
 * @param {number} id - 库存ID
 * @returns {Promise} 删除结果
 */
export const deleteInventory = (id) => {
  return request.delete(`/inventory/inventory/${id}/`)
}

/**
 * 获取库存汇总信息
 * @returns {Promise} 库存汇总数据
 */
export const getInventorySummary = () => {
  return request.get('/inventory/inventory/summary/')
}

/**
 * 获取库存预警列表
 * @returns {Promise} 预警列表
 */
export const getInventoryWarning = () => {
  return request.get('/inventory/inventory/warning/')
}

/**
 * 获取库存变动日志
 * @param {Object} params - 查询参数
 * @returns {Promise} 日志列表
 */
export const getInventoryLogs = (params) => {
  return request.get('/inventory/logs/', { params })
}

// ==================== 入库接口 ====================

/**
 * 获取入库单列表
 * @param {Object} params - 查询参数
 * @returns {Promise} 入库单列表
 */
export const getStockInList = (params) => {
  return request.get('/inventory/stock-in/', { params })
}

/**
 * 获取入库单详情
 * @param {number} id - 入库单ID
 * @returns {Promise} 入库单详情
 */
export const getStockIn = (id) => {
  return request.get(`/inventory/stock-in/${id}/`)
}

/**
 * 创建入库单
 * @param {Object} data - 入库单数据
 * @returns {Promise} 创建结果
 */
export const createStockIn = (data) => {
  return request.post('/inventory/stock-in/', data)
}

/**
 * 确认入库
 * @param {number} id - 入库单ID
 * @returns {Promise} 确认结果
 */
export const confirmStockIn = (id) => {
  return request.post(`/inventory/stock-in/${id}/confirm/`)
}

// ==================== 出库接口 ====================

/**
 * 获取出库单列表
 * @param {Object} params - 查询参数
 * @returns {Promise} 出库单列表
 */
export const getStockOutList = (params) => {
  return request.get('/inventory/stock-out/', { params })
}

/**
 * 获取出库单详情
 * @param {number} id - 出库单ID
 * @returns {Promise} 出库单详情
 */
export const getStockOut = (id) => {
  return request.get(`/inventory/stock-out/${id}/`)
}

/**
 * 创建出库单
 * @param {Object} data - 出库单数据
 * @returns {Promise} 创建结果
 */
export const createStockOut = (data) => {
  return request.post('/inventory/stock-out/', data)
}

// ==================== 库存调整接口 ====================

/**
 * 获取库存调整列表
 * @param {Object} params - 查询参数
 * @returns {Promise} 调整列表
 */
export const getStockAdjustList = (params) => {
  return request.get('/inventory/adjust/', { params })
}

/**
 * 获取库存调整详情
 * @param {number} id - 调整ID
 * @returns {Promise} 调整详情
 */
export const getStockAdjust = (id) => {
  return request.get(`/inventory/adjust/${id}/`)
}

/**
 * 根据单号获取库存调整
 * @param {string} orderNo - 调整单号
 * @returns {Promise} 调整详情
 */
export const getStockAdjustByNo = (orderNo) => {
  return request.get(`/inventory/adjust/by-no/${orderNo}/`)
}

// ==================== 库存调拨接口 ====================

/**
 * 获取库存调拨列表
 * @param {Object} params - 查询参数
 * @returns {Promise} 调拨列表
 */
export const getStockTransferList = (params) => {
  return request.get('/inventory/transfer/', { params })
}

/**
 * 获取库存调拨详情
 * @param {number} id - 调拨ID
 * @returns {Promise} 调拨详情
 */
export const getStockTransfer = (id) => {
  return request.get(`/inventory/transfer/${id}/`)
}

/**
 * 根据单号获取库存调拨
 * @param {string} orderNo - 调拨单号
 * @returns {Promise} 调拨详情
 */
export const getStockTransferByNo = (orderNo) => {
  return request.get(`/inventory/transfer/by-no/${orderNo}/`)
}

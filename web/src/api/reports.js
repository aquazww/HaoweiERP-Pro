/**
 * 报表统计 API 接口
 * 包含采购、销售、库存、财务报表和仪表盘数据接口
 */
import request from './index'

// ==================== 报表接口 ====================

/**
 * 获取采购报表数据
 * @param {Object} params - 查询参数
 * @returns {Promise} 采购报表数据
 */
export const getPurchaseReport = (params) => {
  return request.get('/reports/purchase/', { params })
}

/**
 * 获取销售报表数据
 * @param {Object} params - 查询参数
 * @returns {Promise} 销售报表数据
 */
export const getSaleReport = (params) => {
  return request.get('/reports/sale/', { params })
}

/**
 * 获取库存报表数据
 * @param {Object} params - 查询参数
 * @returns {Promise} 库存报表数据
 */
export const getInventoryReport = (params) => {
  return request.get('/reports/inventory/', { params })
}

/**
 * 获取财务报表数据
 * @param {Object} params - 查询参数
 * @returns {Promise} 财务报表数据
 */
export const getFinanceReport = (params) => {
  return request.get('/reports/finance/', { params })
}

/**
 * 获取仪表盘数据
 * @returns {Promise} 仪表盘统计数据
 */
export const getDashboardData = () => {
  return request.get('/reports/dashboard/')
}

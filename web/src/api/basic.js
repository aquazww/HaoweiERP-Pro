/**
 * 基础数据 API 接口
 * 包含计量单位、分类、仓库、供应商、客户、商品、公司信息、打印模板等接口
 */
import request from './index'

// ==================== 计量单位接口 ====================

/**
 * 获取计量单位列表
 * @param {Object} params - 查询参数
 * @returns {Promise} 计量单位列表
 */
export const getUnits = (params) => {
  return request.get('/basic/units/', { params })
}

/**
 * 创建计量单位
 * @param {Object} data - 单位数据
 * @returns {Promise} 创建结果
 */
export const createUnit = (data) => {
  return request.post('/basic/units/', data)
}

/**
 * 更新计量单位
 * @param {number} id - 单位ID
 * @param {Object} data - 更新数据
 * @returns {Promise} 更新结果
 */
export const updateUnit = (id, data) => {
  return request.put(`/basic/units/${id}/`, data)
}

/**
 * 部分更新计量单位
 * @param {number} id - 单位ID
 * @param {Object} data - 更新数据
 * @returns {Promise} 更新结果
 */
export const partialUpdateUnit = (id, data) => {
  return request.patch(`/basic/units/${id}/`, data)
}

/**
 * 删除计量单位
 * @param {number} id - 单位ID
 * @returns {Promise} 删除结果
 */
export const deleteUnit = (id) => {
  return request.delete(`/basic/units/${id}/`)
}

// ==================== 商品分类接口 ====================

/**
 * 获取商品分类列表
 * @param {Object} params - 查询参数
 * @returns {Promise} 分类列表
 */
export const getCategories = (params) => {
  return request.get('/basic/categories/', { params })
}

/**
 * 获取商品分类树形结构
 * @returns {Promise} 分类树数据
 */
export const getCategoryTree = () => {
  return request.get('/basic/categories/tree/')
}

/**
 * 获取商品分类详情
 * @param {number} id - 分类ID
 * @returns {Promise} 分类详情
 */
export const getCategoryDetail = (id) => {
  return request.get(`/basic/categories/${id}/`)
}

/**
 * 获取商品分类选项列表
 * @returns {Promise} 分类选项
 */
export const getCategoryOptions = () => {
  return request.get('/basic/categories/options/')
}

/**
 * 创建商品分类
 * @param {Object} data - 分类数据
 * @returns {Promise} 创建结果
 */
export const createCategory = (data) => {
  return request.post('/basic/categories/', data)
}

/**
 * 更新商品分类
 * @param {number} id - 分类ID
 * @param {Object} data - 更新数据
 * @returns {Promise} 更新结果
 */
export const updateCategory = (id, data) => {
  return request.put(`/basic/categories/${id}/`, data)
}

/**
 * 部分更新商品分类
 * @param {number} id - 分类ID
 * @param {Object} data - 更新数据
 * @returns {Promise} 更新结果
 */
export const partialUpdateCategory = (id, data) => {
  return request.patch(`/basic/categories/${id}/`, data)
}

/**
 * 批量更新分类排序
 * @param {Object} data - 排序数据
 * @returns {Promise} 更新结果
 */
export const batchUpdateCategorySort = (data) => {
  return request.post('/basic/categories/batch_update_sort/', data)
}

/**
 * 删除商品分类
 * @param {number} id - 分类ID
 * @returns {Promise} 删除结果
 */
export const deleteCategory = (id) => {
  return request.delete(`/basic/categories/${id}/`)
}

// ==================== 仓库接口 ====================

/**
 * 获取仓库列表
 * @param {Object} params - 查询参数
 * @returns {Promise} 仓库列表
 */
export const getWarehouses = (params) => {
  return request.get('/basic/warehouses/', { params })
}

/**
 * 创建仓库
 * @param {Object} data - 仓库数据
 * @returns {Promise} 创建结果
 */
export const createWarehouse = (data) => {
  return request.post('/basic/warehouses/', data)
}

/**
 * 更新仓库
 * @param {number} id - 仓库ID
 * @param {Object} data - 更新数据
 * @returns {Promise} 更新结果
 */
export const updateWarehouse = (id, data) => {
  return request.put(`/basic/warehouses/${id}/`, data)
}

/**
 * 部分更新仓库
 * @param {number} id - 仓库ID
 * @param {Object} data - 更新数据
 * @returns {Promise} 更新结果
 */
export const partialUpdateWarehouse = (id, data) => {
  return request.patch(`/basic/warehouses/${id}/`, data)
}

/**
 * 删除仓库
 * @param {number} id - 仓库ID
 * @returns {Promise} 删除结果
 */
export const deleteWarehouse = (id) => {
  return request.delete(`/basic/warehouses/${id}/`)
}

// ==================== 供应商接口 ====================

/**
 * 获取供应商列表
 * @param {Object} params - 查询参数
 * @returns {Promise} 供应商列表
 */
export const getSuppliers = (params) => {
  return request.get('/basic/suppliers/', { params })
}

/**
 * 创建供应商
 * @param {Object} data - 供应商数据
 * @returns {Promise} 创建结果
 */
export const createSupplier = (data) => {
  return request.post('/basic/suppliers/', data)
}

/**
 * 更新供应商
 * @param {number} id - 供应商ID
 * @param {Object} data - 更新数据
 * @returns {Promise} 更新结果
 */
export const updateSupplier = (id, data) => {
  return request.put(`/basic/suppliers/${id}/`, data)
}

/**
 * 部分更新供应商
 * @param {number} id - 供应商ID
 * @param {Object} data - 更新数据
 * @returns {Promise} 更新结果
 */
export const partialUpdateSupplier = (id, data) => {
  return request.patch(`/basic/suppliers/${id}/`, data)
}

/**
 * 删除供应商
 * @param {number} id - 供应商ID
 * @returns {Promise} 删除结果
 */
export const deleteSupplier = (id) => {
  return request.delete(`/basic/suppliers/${id}/`)
}

// ==================== 客户接口 ====================

/**
 * 获取客户列表
 * @param {Object} params - 查询参数
 * @returns {Promise} 客户列表
 */
export const getCustomers = (params) => {
  return request.get('/basic/customers/', { params })
}

/**
 * 创建客户
 * @param {Object} data - 客户数据
 * @returns {Promise} 创建结果
 */
export const createCustomer = (data) => {
  return request.post('/basic/customers/', data)
}

/**
 * 更新客户
 * @param {number} id - 客户ID
 * @param {Object} data - 更新数据
 * @returns {Promise} 更新结果
 */
export const updateCustomer = (id, data) => {
  return request.put(`/basic/customers/${id}/`, data)
}

/**
 * 部分更新客户
 * @param {number} id - 客户ID
 * @param {Object} data - 更新数据
 * @returns {Promise} 更新结果
 */
export const partialUpdateCustomer = (id, data) => {
  return request.patch(`/basic/customers/${id}/`, data)
}

/**
 * 删除客户
 * @param {number} id - 客户ID
 * @returns {Promise} 删除结果
 */
export const deleteCustomer = (id) => {
  return request.delete(`/basic/customers/${id}/`)
}

// ==================== 商品接口 ====================

/**
 * 获取商品列表
 * @param {Object} params - 查询参数
 * @returns {Promise} 商品列表
 */
export const getGoods = (params) => {
  return request.get('/basic/goods/', { params })
}

/**
 * 创建商品
 * @param {Object} data - 商品数据
 * @returns {Promise} 创建结果
 */
export const createGoods = (data) => {
  return request.post('/basic/goods/', data)
}

/**
 * 更新商品
 * @param {number} id - 商品ID
 * @param {Object} data - 更新数据
 * @returns {Promise} 更新结果
 */
export const updateGoods = (id, data) => {
  return request.put(`/basic/goods/${id}/`, data)
}

/**
 * 部分更新商品
 * @param {number} id - 商品ID
 * @param {Object} data - 更新数据
 * @returns {Promise} 更新结果
 */
export const partialUpdateGoods = (id, data) => {
  return request.patch(`/basic/goods/${id}/`, data)
}

/**
 * 删除商品
 * @param {number} id - 商品ID
 * @returns {Promise} 删除结果
 */
export const deleteGoods = (id) => {
  return request.delete(`/basic/goods/${id}/`)
}

// ==================== 公司信息接口 ====================

/**
 * 获取公司信息
 * @returns {Promise} 公司信息
 */
export const getCompanyInfo = () => {
  return request.get('/basic/company/')
}

/**
 * 更新公司信息
 * @param {Object} data - 公司数据
 * @returns {Promise} 更新结果
 */
export const updateCompanyInfo = (data) => {
  return request.put('/basic/company/1/', data)
}

/**
 * 上传公司Logo
 * @param {FormData} formData - 表单数据
 * @returns {Promise} 上传结果
 */
export const uploadCompanyLogo = (formData) => {
  return request.put('/basic/company/1/', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
}

// ==================== 打印模板接口 ====================

/**
 * 获取打印模板列表
 * @param {Object} params - 查询参数
 * @returns {Promise} 模板列表
 */
export const getPrintTemplates = (params) => {
  return request.get('/basic/print-templates/', { params })
}

/**
 * 获取打印模板详情
 * @param {number} id - 模板ID
 * @returns {Promise} 模板详情
 */
export const getPrintTemplate = (id) => {
  return request.get(`/basic/print-templates/${id}/`)
}

/**
 * 创建打印模板
 * @param {Object} data - 模板数据
 * @returns {Promise} 创建结果
 */
export const createPrintTemplate = (data) => {
  return request.post('/basic/print-templates/', data)
}

/**
 * 更新打印模板
 * @param {number} id - 模板ID
 * @param {Object} data - 更新数据
 * @returns {Promise} 更新结果
 */
export const updatePrintTemplate = (id, data) => {
  return request.put(`/basic/print-templates/${id}/`, data)
}

/**
 * 删除打印模板
 * @param {number} id - 模板ID
 * @returns {Promise} 删除结果
 */
export const deletePrintTemplate = (id) => {
  return request.delete(`/basic/print-templates/${id}/`)
}

/**
 * 获取默认打印模板
 * @param {string} templateType - 模板类型，默认为 'delivery'
 * @returns {Promise} 默认模板
 */
export const getDefaultPrintTemplate = (templateType = 'delivery') => {
  return request.get('/basic/print-templates/default/', { params: { template_type: templateType } })
}

/**
 * 设置默认打印模板
 * @param {number} id - 模板ID
 * @returns {Promise} 设置结果
 */
export const setDefaultPrintTemplate = (id) => {
  return request.post(`/basic/print-templates/${id}/set_default/`)
}

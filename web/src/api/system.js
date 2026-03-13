/**
 * 系统管理 API 接口
 * 包含用户管理和系统日志接口
 */
import request from './index'

// ==================== 用户管理接口 ====================

/**
 * 获取用户列表
 * @param {Object} params - 查询参数
 * @returns {Promise} 用户列表
 */
export const getUsers = (params) => {
  return request.get('/auth/users/', { params })
}

/**
 * 创建用户
 * @param {Object} data - 用户数据
 * @returns {Promise} 创建结果
 */
export const createUser = (data) => {
  return request.post('/auth/users/', data)
}

/**
 * 更新用户
 * @param {number} id - 用户ID
 * @param {Object} data - 更新数据
 * @returns {Promise} 更新结果
 */
export const updateUser = (id, data) => {
  return request.put(`/auth/users/${id}/`, data)
}

/**
 * 部分更新用户
 * @param {number} id - 用户ID
 * @param {Object} data - 更新数据
 * @returns {Promise} 更新结果
 */
export const partialUpdateUser = (id, data) => {
  return request.patch(`/auth/users/${id}/`, data)
}

/**
 * 删除用户
 * @param {number} id - 用户ID
 * @returns {Promise} 删除结果
 */
export const deleteUser = (id) => {
  return request.delete(`/auth/users/${id}/`)
}

/**
 * 重置用户密码
 * @param {number} id - 用户ID
 * @param {Object} data - 密码数据
 * @returns {Promise} 重置结果
 */
export const resetPassword = (id, data) => {
  return request.post(`/auth/users/${id}/reset_password/`, data)
}

/**
 * 获取权限模块列表
 * @returns {Promise} 权限模块列表
 */
export const getPermissionModules = () => {
  return request.get('/auth/users/permission_modules/')
}

// ==================== 系统日志接口 ====================

/**
 * 获取系统日志列表
 * @param {Object} params - 查询参数
 * @returns {Promise} 日志列表
 */
export const getLogs = (params) => {
  return request.get('/auth/logs/', { params })
}

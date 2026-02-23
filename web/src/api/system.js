import request from './index'

export const getUsers = (params) => {
  return request.get('/auth/users/', { params })
}

export const createUser = (data) => {
  return request.post('/auth/users/', data)
}

export const updateUser = (id, data) => {
  return request.put(`/auth/users/${id}/`, data)
}

export const deleteUser = (id) => {
  return request.delete(`/auth/users/${id}/`)
}

export const resetPassword = (id, data) => {
  return request.post(`/auth/users/${id}/reset_password/`, data)
}

export const getPermissionModules = () => {
  return request.get('/auth/users/permission_modules/')
}

export const getLogs = (params) => {
  return request.get('/auth/logs/', { params })
}

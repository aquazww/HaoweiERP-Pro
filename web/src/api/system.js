import request from './index'

export const getRoles = (params) => {
  return request.get('/system/roles/', { params })
}

export const createRole = (data) => {
  return request.post('/system/roles/', data)
}

export const updateRole = (id, data) => {
  return request.put(`/system/roles/${id}/`, data)
}

export const deleteRole = (id) => {
  return request.delete(`/system/roles/${id}/`)
}

export const getUsers = (params) => {
  return request.get('/system/users/', { params })
}

export const createUser = (data) => {
  return request.post('/system/users/', data)
}

export const updateUser = (id, data) => {
  return request.put(`/system/users/${id}/`, data)
}

export const deleteUser = (id) => {
  return request.delete(`/system/users/${id}/`)
}

export const getLogs = (params) => {
  return request.get('/system/logs/', { params })
}

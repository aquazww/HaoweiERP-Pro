import request from './index'

export const getCategories = (params) => {
  return request.get('/basic/categories/', { params })
}

export const createCategory = (data) => {
  return request.post('/basic/categories/', data)
}

export const updateCategory = (id, data) => {
  return request.put(`/basic/categories/${id}/`, data)
}

export const deleteCategory = (id) => {
  return request.delete(`/basic/categories/${id}/`)
}

export const getWarehouses = (params) => {
  return request.get('/basic/warehouses/', { params })
}

export const getSuppliers = (params) => {
  return request.get('/basic/suppliers/', { params })
}

export const createSupplier = (data) => {
  return request.post('/basic/suppliers/', data)
}

export const updateSupplier = (id, data) => {
  return request.put(`/basic/suppliers/${id}/`, data)
}

export const deleteSupplier = (id) => {
  return request.delete(`/basic/suppliers/${id}/`)
}

export const getCustomers = (params) => {
  return request.get('/basic/customers/', { params })
}

export const createCustomer = (data) => {
  return request.post('/basic/customers/', data)
}

export const updateCustomer = (id, data) => {
  return request.put(`/basic/customers/${id}/`, data)
}

export const deleteCustomer = (id) => {
  return request.delete(`/basic/customers/${id}/`)
}

export const getGoods = (params) => {
  return request.get('/basic/goods/', { params })
}

export const createGoods = (data) => {
  return request.post('/basic/goods/', data)
}

export const updateGoods = (id, data) => {
  return request.put(`/basic/goods/${id}/`, data)
}

export const deleteGoods = (id) => {
  return request.delete(`/basic/goods/${id}/`)
}

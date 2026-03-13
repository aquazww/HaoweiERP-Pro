import request from './index'

export const getUnits = (params) => {
  return request.get('/basic/units/', { params })
}

export const createUnit = (data) => {
  return request.post('/basic/units/', data)
}

export const updateUnit = (id, data) => {
  return request.put(`/basic/units/${id}/`, data)
}

export const deleteUnit = (id) => {
  return request.delete(`/basic/units/${id}/`)
}

export const getCategories = (params) => {
  return request.get('/basic/categories/', { params })
}

export const getCategoryTree = () => {
  return request.get('/basic/categories/tree/')
}

export const getCategoryDetail = (id) => {
  return request.get(`/basic/categories/${id}/`)
}

export const getCategoryOptions = () => {
  return request.get('/basic/categories/options/')
}

export const createCategory = (data) => {
  return request.post('/basic/categories/', data)
}

export const updateCategory = (id, data) => {
  return request.put(`/basic/categories/${id}/`, data)
}

export const batchUpdateCategorySort = (data) => {
  return request.post('/basic/categories/batch_update_sort/', data)
}

export const deleteCategory = (id) => {
  return request.delete(`/basic/categories/${id}/`)
}

export const getWarehouses = (params) => {
  return request.get('/basic/warehouses/', { params })
}

export const createWarehouse = (data) => {
  return request.post('/basic/warehouses/', data)
}

export const updateWarehouse = (id, data) => {
  return request.put(`/basic/warehouses/${id}/`, data)
}

export const deleteWarehouse = (id) => {
  return request.delete(`/basic/warehouses/${id}/`)
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

export const getCompanyInfo = () => {
  return request.get('/basic/company/')
}

export const updateCompanyInfo = (data) => {
  return request.put('/basic/company/1/', data)
}

export const uploadCompanyLogo = (formData) => {
  return request.put('/basic/company/1/', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
}

export const getPrintTemplates = (params) => {
  return request.get('/basic/print-templates/', { params })
}

export const getPrintTemplate = (id) => {
  return request.get(`/basic/print-templates/${id}/`)
}

export const createPrintTemplate = (data) => {
  return request.post('/basic/print-templates/', data)
}

export const updatePrintTemplate = (id, data) => {
  return request.put(`/basic/print-templates/${id}/`, data)
}

export const deletePrintTemplate = (id) => {
  return request.delete(`/basic/print-templates/${id}/`)
}

export const getDefaultPrintTemplate = (templateType = 'delivery') => {
  return request.get('/basic/print-templates/default/', { params: { template_type: templateType } })
}

export const setDefaultPrintTemplate = (id) => {
  return request.post(`/basic/print-templates/${id}/set_default/`)
}

import request from './index'

export const getInventory = (params) => {
  return request.get('/inventory/inventory/', { params })
}

export const deleteInventory = (id) => {
  return request.delete(`/inventory/inventory/${id}/`)
}

export const getInventorySummary = () => {
  return request.get('/inventory/inventory/summary/')
}

export const getInventoryWarning = () => {
  return request.get('/inventory/inventory/warning/')
}

export const getInventoryLogs = (params) => {
  return request.get('/inventory/logs/', { params })
}

export const getStockInList = (params) => {
  return request.get('/inventory/stock-in/', { params })
}

export const getStockIn = (id) => {
  return request.get(`/inventory/stock-in/${id}/`)
}

export const createStockIn = (data) => {
  return request.post('/inventory/stock-in/', data)
}

export const confirmStockIn = (id) => {
  return request.post(`/inventory/stock-in/${id}/confirm/`)
}

export const getStockOutList = (params) => {
  return request.get('/inventory/stock-out/', { params })
}

export const createStockOut = (data) => {
  return request.post('/inventory/stock-out/', data)
}

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

export const getStockOut = (id) => {
  return request.get(`/inventory/stock-out/${id}/`)
}

export const createStockOut = (data) => {
  return request.post('/inventory/stock-out/', data)
}

export const getStockAdjustList = (params) => {
  return request.get('/inventory/adjust/', { params })
}

export const getStockAdjust = (id) => {
  return request.get(`/inventory/adjust/${id}/`)
}

export const getStockAdjustByNo = (orderNo) => {
  return request.get(`/inventory/adjust/by-no/${orderNo}/`)
}

export const getStockTransferList = (params) => {
  return request.get('/inventory/transfer/', { params })
}

export const getStockTransfer = (id) => {
  return request.get(`/inventory/transfer/${id}/`)
}

export const getStockTransferByNo = (orderNo) => {
  return request.get(`/inventory/transfer/by-no/${orderNo}/`)
}

import request from './index'

export const getPurchaseOrders = (params) => {
  return request.get('/purchase/orders/', { params })
}

export const getPurchaseOrder = (id) => {
  return request.get(`/purchase/orders/${id}/`)
}

export const getPurchaseOrderByNo = (orderNo) => {
  return request.get(`/purchase/orders/by-no/${orderNo}/`)
}

export const createPurchaseOrder = (data) => {
  return request.post('/purchase/orders/', data)
}

export const updatePurchaseOrder = (id, data) => {
  return request.put(`/purchase/orders/${id}/`, data)
}

export const deletePurchaseOrder = (id) => {
  return request.delete(`/purchase/orders/${id}/`)
}

export const getPurchaseItems = (params) => {
  return request.get('/purchase/items/', { params })
}

export const createPurchaseItem = (data) => {
  return request.post('/purchase/items/', data)
}

export const updatePurchaseItem = (id, data) => {
  return request.put(`/purchase/items/${id}/`, data)
}

export const deletePurchaseItem = (id) => {
  return request.delete(`/purchase/items/${id}/`)
}

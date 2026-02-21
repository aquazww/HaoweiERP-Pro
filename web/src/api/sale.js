import request from './index'

export const getSaleOrders = (params) => {
  return request.get('/sale/orders/', { params })
}

export const getSaleOrder = (id) => {
  return request.get(`/sale/orders/${id}/`)
}

export const getSaleOrderByNo = (orderNo) => {
  return request.get(`/sale/orders/by-no/${orderNo}/`)
}

export const createSaleOrder = (data) => {
  return request.post('/sale/orders/', data)
}

export const updateSaleOrder = (id, data) => {
  return request.put(`/sale/orders/${id}/`, data)
}

export const deleteSaleOrder = (id) => {
  return request.delete(`/sale/orders/${id}/`)
}

export const confirmSaleOrder = (id) => {
  return request.post(`/sale/orders/${id}/confirm/`)
}

export const getSaleItems = (params) => {
  return request.get('/sale/items/', { params })
}

export const createSaleItem = (data) => {
  return request.post('/sale/items/', data)
}

export const updateSaleItem = (id, data) => {
  return request.put(`/sale/items/${id}/`, data)
}

export const deleteSaleItem = (id) => {
  return request.delete(`/sale/items/${id}/`)
}

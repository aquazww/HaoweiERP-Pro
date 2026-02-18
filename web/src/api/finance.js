import request from './index'

export const getPayments = (params) => {
  return request.get('/finance/payments/', { params })
}

export const getPayment = (id) => {
  return request.get(`/finance/payments/${id}/`)
}

export const createPayment = (data) => {
  return request.post('/finance/payments/', data)
}

export const updatePayment = (id, data) => {
  return request.put(`/finance/payments/${id}/`, data)
}

export const deletePayment = (id) => {
  return request.delete(`/finance/payments/${id}/`)
}

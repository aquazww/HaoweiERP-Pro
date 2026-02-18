import request from './index'

export const getPurchaseReport = (params) => {
  return request.get('/reports/purchase/', { params })
}

export const getSaleReport = (params) => {
  return request.get('/reports/sale/', { params })
}

export const getInventoryReport = (params) => {
  return request.get('/reports/inventory/', { params })
}

export const getFinanceReport = (params) => {
  return request.get('/reports/finance/', { params })
}

export const getDashboardData = () => {
  return request.get('/reports/dashboard/')
}

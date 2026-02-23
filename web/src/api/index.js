import axios from 'axios'

const request = axios.create({
  baseURL: '/api/v1',
  timeout: 10000,
  withCredentials: true
})

let isRefreshing = false
let refreshSubscribers = []

const subscribeTokenRefresh = (cb) => {
  refreshSubscribers.push(cb)
}

const onRefreshed = () => {
  refreshSubscribers.forEach(cb => cb())
  refreshSubscribers = []
}

const onRefreshFailed = () => {
  refreshSubscribers = []
  localStorage.removeItem('permissions')
  localStorage.removeItem('username')
  window.location.href = '/login'
}

const refreshToken = async () => {
  const response = await axios.post('/api/v1/auth/refresh/', {}, {
    withCredentials: true
  })
  return response.data
}

request.interceptors.request.use(
  config => {
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

request.interceptors.response.use(
  response => {
    const res = response.data
    if (res.code === 200) {
      return res
    } else {
      console.error(res.msg || '请求失败')
      return Promise.reject(new Error(res.msg || '请求失败'))
    }
  },
  async error => {
    const originalRequest = error.config
    
    if (error.response?.status === 401 && originalRequest._skipAuthRedirect) {
      return Promise.reject(error)
    }
    
    if (error.response?.status === 401 && !originalRequest._retry) {
      if (isRefreshing) {
        return new Promise(resolve => {
          subscribeTokenRefresh(() => {
            resolve(request(originalRequest))
          })
        })
      }
      
      originalRequest._retry = true
      isRefreshing = true
      
      try {
        await refreshToken()
        onRefreshed()
        isRefreshing = false
        return request(originalRequest)
      } catch (refreshError) {
        isRefreshing = false
        onRefreshFailed()
        return Promise.reject(refreshError)
      }
    }
    
    if (error.response?.status === 401) {
      const msg = error.response?.data?.msg || '登录已过期'
      localStorage.removeItem('permissions')
      localStorage.removeItem('username')
      
      if (msg.includes('权限已变更') || msg.includes('重新登录')) {
        window.location.href = '/login?reason=permission_changed'
      } else {
        window.location.href = '/login'
      }
    }
    
    if (error.response?.status === 403) {
      const msg = error.response?.data?.msg || error.response?.data?.message || '您没有权限执行此操作'
      return Promise.reject(new Error(msg))
    }
    
    if (error.response?.status === 500) {
      return Promise.reject(new Error('服务器内部错误，请稍后重试'))
    }
    
    if (error.response?.status === 404) {
      return Promise.reject(new Error('请求的资源不存在'))
    }
    
    if (error.code === 'ECONNABORTED') {
      return Promise.reject(new Error('请求超时，请检查网络连接'))
    }
    
    if (!error.response) {
      return Promise.reject(new Error('网络连接失败，请检查网络'))
    }
    
    return Promise.reject(error)
  }
)

export default request

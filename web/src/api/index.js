import axios from 'axios'
import tokenManager from '../utils/tokenManager'

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
  tokenManager.refreshToken()
}

const onRefreshFailed = () => {
  refreshSubscribers = []
  tokenManager.handleTokenExpired()
}

const refreshToken = async () => {
  const response = await axios.post('/api/v1/auth/refresh/', {}, {
    withCredentials: true
  })
  return response.data
}

request.interceptors.request.use(
  config => {
    if (tokenManager.isTokenExpired()) {
      tokenManager.handleTokenExpired()
      return Promise.reject(new Error('Token expired'))
    }
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

request.interceptors.response.use(
  response => {
    const res = response.data
    
    if (response.config.url?.includes('/auth/login/') && res.data) {
      const expiresIn = res.data.expires_in || res.data.access_expires_in
      if (expiresIn) {
        const expiryTime = Date.now() + (expiresIn * 1000)
        tokenManager.setTokenExpiry(expiryTime)
      }
    }
    
    if (response.config.url?.includes('/auth/refresh/') && res.data) {
      const expiresIn = res.data.expires_in || res.data.access_expires_in
      if (expiresIn) {
        const expiryTime = Date.now() + (expiresIn * 1000)
        tokenManager.setTokenExpiry(expiryTime)
      }
    }
    
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
      tokenManager.handleTokenExpired()
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

export const initTokenCheck = () => {
  const username = localStorage.getItem('username')
  if (username) {
    tokenManager.startExpiryCheck()
  }
}

export default request

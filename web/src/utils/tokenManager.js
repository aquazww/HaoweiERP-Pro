const TOKEN_EXPIRY_KEY = 'token_expiry'
const TOKEN_WARNING_KEY = 'token_warning_shown'

let expiryCheckInterval = null
let warningTimeout = null

const getElMessage = async () => {
  const { ElMessage } = await import('element-plus')
  return ElMessage
}

export const tokenManager = {
  setTokenExpiry(expiryTime) {
    if (expiryTime) {
      localStorage.setItem(TOKEN_EXPIRY_KEY, expiryTime.toString())
      this.startExpiryCheck()
    }
  },

  getTokenExpiry() {
    const expiry = localStorage.getItem(TOKEN_EXPIRY_KEY)
    return expiry ? parseInt(expiry, 10) : null
  },

  getTimeUntilExpiry() {
    const expiry = this.getTokenExpiry()
    if (!expiry) return null
    return expiry - Date.now()
  },

  isTokenExpired() {
    const timeUntilExpiry = this.getTimeUntilExpiry()
    return timeUntilExpiry !== null && timeUntilExpiry <= 0
  },

  isTokenExpiringSoon(warningThreshold = 5 * 60 * 1000) {
    const timeUntilExpiry = this.getTimeUntilExpiry()
    return timeUntilExpiry !== null && timeUntilExpiry > 0 && timeUntilExpiry <= warningThreshold
  },

  startExpiryCheck() {
    this.stopExpiryCheck()
    
    const checkExpiry = async () => {
      if (this.isTokenExpired()) {
        this.handleTokenExpired()
        return
      }
      
      const warningThreshold = 5 * 60 * 1000
      if (this.isTokenExpiringSoon(warningThreshold)) {
        this.showExpiryWarning()
      }
    }
    
    checkExpiry()
    
    expiryCheckInterval = setInterval(checkExpiry, 30 * 1000)
    
    const timeUntilExpiry = this.getTimeUntilExpiry()
    if (timeUntilExpiry && timeUntilExpiry > 0) {
      const warningTime = timeUntilExpiry - 5 * 60 * 1000
      if (warningTime > 0) {
        warningTimeout = setTimeout(() => {
          this.showExpiryWarning()
        }, warningTime)
      }
    }
  },

  stopExpiryCheck() {
    if (expiryCheckInterval) {
      clearInterval(expiryCheckInterval)
      expiryCheckInterval = null
    }
    if (warningTimeout) {
      clearTimeout(warningTimeout)
      warningTimeout = null
    }
  },

  async showExpiryWarning() {
    const warningShown = sessionStorage.getItem(TOKEN_WARNING_KEY)
    if (warningShown) return
    
    sessionStorage.setItem(TOKEN_WARNING_KEY, 'true')
    
    const timeLeft = Math.max(1, Math.floor((this.getTimeUntilExpiry() || 0) / 60000))
    
    try {
      const ElMessage = await getElMessage()
      ElMessage.warning({
        message: `登录即将过期（剩余约 ${timeLeft} 分钟），请保存当前工作`,
        duration: 0,
        showClose: true,
        type: 'warning'
      })
    } catch (e) {
      console.warn('显示过期警告失败', e)
    }
  },

  async handleTokenExpired() {
    this.stopExpiryCheck()
    this.clearTokenData()
    
    try {
      const ElMessage = await getElMessage()
      ElMessage.error({
        message: '登录已过期，请重新登录',
        duration: 3000
      })
    } catch (e) {
      console.warn('显示过期提示失败', e)
    }
    
    setTimeout(() => {
      window.location.href = '/login?reason=token_expired'
    }, 1500)
  },

  clearTokenData() {
    localStorage.removeItem(TOKEN_EXPIRY_KEY)
    localStorage.removeItem('permissions')
    localStorage.removeItem('username')
    sessionStorage.removeItem(TOKEN_WARNING_KEY)
  },

  refreshToken() {
    this.stopExpiryCheck()
    sessionStorage.removeItem(TOKEN_WARNING_KEY)
  }
}

export default tokenManager

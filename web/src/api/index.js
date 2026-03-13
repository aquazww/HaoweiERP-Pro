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
      const error = new Error(res.msg || '请求失败')
      error.data = res
      return Promise.reject(error)
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
    
    if (error.response?.status === 400) {
      const errorData = error.response?.data
      if (errorData) {
        const messages = []
        if (errorData.msg && typeof errorData.msg === 'string') {
          return Promise.reject(new Error(errorData.msg))
        }
        const fieldNames = {
          // 公司信息
          'website': '公司网站',
          'email': '电子邮箱',
          'phone': '联系电话',
          'fax': '传真号码',
          'credit_code': '统一社会信用代码',
          'tax_number': '纳税人识别号',
          'bank_account': '银行账号',
          'name': '名称',
          'short_name': '公司简称',
          'legal_person': '法定代表人',
          'registered_address': '注册地址',
          'business_address': '经营地址',
          'bank_name': '开户银行',
          'invoice_title': '发票抬头',
          'remark': '备注',
          'logo': '公司Logo',
          'stamp': '公司印章',
          // 计量单位
          'unit': '单位',
          'unit_name': '单位名称',
          // 商品
          'code': '编码',
          'goods': '商品',
          'goods_name': '商品名称',
          'goods_code': '商品编码',
          'goods_spec': '规格型号',
          'category': '分类',
          'purchase_price': '采购价',
          'sale_price': '销售价',
          'min_stock': '最低库存',
          'max_stock': '最高库存',
          'status': '状态',
          'is_active': '是否启用',
          // 仓库
          'warehouse': '仓库',
          'warehouse_name': '仓库名称',
          'address': '地址',
          'contact': '联系人',
          // 供应商/客户
          'supplier': '供应商',
          'supplier_name': '供应商名称',
          'customer': '客户',
          'customer_name': '客户名称',
          'customer_contact': '客户联系人',
          'customer_phone': '客户电话',
          'customer_address': '客户地址',
          // 采购/销售订单
          'order_no': '订单编号',
          'order_date': '订单日期',
          'total_amount': '总金额',
          'quantity': '数量',
          'price': '单价',
          'amount': '金额',
          // 库存
          'stock': '库存',
          'stock_quantity': '库存数量',
          'change_type': '变动类型',
          'change_quantity': '变动数量',
          'before_quantity': '变动前数量',
          'after_quantity': '变动后数量',
          // 财务
          'payment_type': '付款类型',
          'payment_method': '付款方式',
          'payment_amount': '付款金额',
          'payment_date': '付款日期',
          // 用户
          'username': '用户名',
          'password': '密码',
          'password2': '确认密码',
          'real_name': '真实姓名',
          'role': '角色',
          'new_password': '新密码',
          'confirm_password': '确认密码'
        }
        for (const [field, msg] of Object.entries(errorData)) {
          if (field === 'msg' || field === 'code' || field === 'data') continue
          const fieldName = fieldNames[field] || field
          if (Array.isArray(msg)) {
            messages.push(`${fieldName}${msg.join('')}`)
          } else if (typeof msg === 'string') {
            messages.push(`${fieldName}${msg}`)
          }
        }
        if (messages.length > 0) {
          return Promise.reject(new Error(messages.join('；')))
        }
      }
      return Promise.reject(new Error('提交数据格式错误'))
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

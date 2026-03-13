/**
 * 库存日志管理组合式函数
 * 管理库存日志的加载、查询等操作
 */
import { ref, reactive, computed, onMounted, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import { getInventoryLogs } from '@/api/inventory'
import { formatQuantity } from '@/utils/format'

export function useInventoryLog() {
  const loading = ref(false)
  const logList = ref([])
  const searchKeyword = ref('')
  const changeTypeFilter = ref('')
  const currentPage = ref(1)
  const pageSize = ref(20)
  const total = ref(0)
  const tableHeight = ref(0)
  
  const orderDetailVisible = ref(false)
  const orderDetail = ref(null)
  const orderType = ref('')
  const orderDetailTitle = ref('')
  
  const getStatusText = (status) => {
    const statusMap = {
    pending: '待处理',
    partial: '部分完成',
    completed: '已完成',
    cancelled: '已取消'
    }
    return statusMap[status] || status
  }
  
  const getTransactionType = (row) => {
    const typeMap = {
    purchase_in: { text: '采购入库', color: 'success' },
    sale_out: { text: '销售出库', color: 'danger' },
    transfer_in: { text: '调拨入库', color: 'warning' },
    transfer_out: { text: '调拨出库', color: 'warning' },
    adjust: { text: '库存调整', color: 'info' }
    }
    return typeMap[row.transaction_type] || { text: '未知', color: 'info' }
  }
  
  const formatDateTime = (datetime) => {
    if (!datetime) return '-'
    return datetime.replace('T', ' ').substring(0, 19)
  }
  
  const formatChangeQuantity = (row) => {
    const quantity = Math.abs(row.quantity_change)
    const sign = row.change_type === 'inbound' ? '+' : '-'
    return `${sign}${formatQuantity(quantity)}`
  }
  
  const formatQuantity = (quantity) => {
    if (quantity === null || quantity === undefined) return '-'
    return Number(quantity).toFixed(2)
  }
  
  const formatRemark = (remark) => {
    if (!remark) return '-'
    return remark
  }
  
  const handleOrderClick = (event) => {
    const target = event.target
    if (target.classList.contains('order-link')) {
      const orderId = target.dataset.orderId
      const type = target.dataset.orderType
      if (orderId && type) {
        loadOrderDetail(orderId, type)
      }
    }
  }
  
  const loadOrderDetail = async (orderId, type) => {
    try {
      orderType.value = type
      orderDetailTitle.value = type === 'purchase' ? '采购单详情' : 
                    type === 'sale' ? '销售单详情' : 
                    type === 'transfer' ? '调拨单详情' : '库存调整详情'
      
      if (type === 'purchase') {
        const res = await getPurchaseOrder(orderId)
        orderDetail.value = res.data
      } else if (type === 'sale') {
        const res = await getSaleOrder(orderId)
        orderDetail.value = res.data
      } else if (type === 'transfer') {
        const res = await getTransferOrder(orderId)
        orderDetail.value = res.data
      } else {
        orderDetail.value = null
      }
      
      orderDetailVisible.value = true
    } catch (error) {
      ElMessage.error('加载订单详情失败')
    }
  }
  
  const loadLogs = async () => {
    loading.value = true
    try {
      const params = {
        page: currentPage.value,
        page_size: pageSize.value
      }
      if (searchKeyword.value) {
        params.search = searchKeyword.value
      }
      if (changeTypeFilter.value) {
        params.transaction_type = changeTypeFilter.value
      }
      
      const res = await getInventoryLogs(params)
      logList.value = res.data?.items || res.data?.results || []
      total.value = res.data?.count || 0
    } catch (error) {
      logList.value = []
      total.value = 0
      ElMessage.error('加载数据失败')
    } finally {
      loading.value = false
    }
  }
  
  const calculateTableHeight = () => {
    nextTick(() => {
      const toolbarCard = document.querySelector('.toolbar-card')
      const paginationWrapper = document.querySelector('.pagination-wrapper')
      const pageContent = document.querySelector('.page-content')
      
      if (pageContent) {
        let usedHeight = 0
        if (toolbarCard) usedHeight += toolbarCard.offsetHeight + 4
        if (paginationWrapper) usedHeight += paginationWrapper.offsetHeight + 2
        usedHeight += 4
        
        const availableHeight = window.innerHeight - 64 - 16
        tableHeight.value = Math.max(availableHeight - usedHeight, 150)
      }
    })
  }
  
  onMounted(() => {
    loadLogs()
    calculateTableHeight()
    window.addEventListener('resize', calculateTableHeight)
  })
  
  return {
    loading,
    logList,
    searchKeyword,
    changeTypeFilter,
    currentPage,
    pageSize,
    total,
    tableHeight,
    orderDetailVisible,
    orderDetail,
    orderType,
    orderDetailTitle,
    getStatusText,
    getTransactionType,
    formatDateTime,
    formatChangeQuantity,
    formatQuantity,
    formatRemark,
    handleOrderClick,
    loadLogs
  }
}

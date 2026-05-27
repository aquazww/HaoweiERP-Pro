/**
 * 订单管理组合式函数
 * 独立的订单管理逻辑
 */
import { ref, reactive, computed, onMounted, onUnmounted, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'

import { getPurchaseOrders, createPurchaseOrder, updatePurchaseOrder, deletePurchaseOrder, cancelPurchaseOrder } from '@/api/purchase'
import { getSuppliers, getWarehouses, getGoods, getCategories } from '@/api/basic'
import { formatPrice, formatInputNumber, parseInputNumber } from '@/utils/format'
import { canAdd, canEdit, canDelete } from '@/utils/permission'

export function usePurchaseOrders(purchaseFormRef) {
  const loading = ref(false)
  const orderList = ref([])
  const searchKeyword = ref('')
  const statusFilter = ref('')
  const currentPage = ref(1)
  const pageSize = ref(20)
  const total = ref(0)
  const tableHeight = ref(0)
  
  const dialogVisible = ref(false)
  const dialogTitle = ref('新增采购单')
  const isEdit = ref(false)
  const submitLoading = ref(false)
  const viewDialogVisible = ref(false)
  const viewData = ref(null)
  const formRef = ref(null)
  const supplierList = ref([])
  const warehouseList = ref([])
  const goodsList = ref([])
  const categoryList = ref([])
  const selectedGoods = ref([])
  
  const form = reactive({
    supplier: null,
    warehouse: null,
    order_date: '',
    remark: '',
    items: []
  })
  
  const rules = reactive({
    supplier: [
      { required: true, message: '请选择供应商', trigger: 'change' }
    ],
    warehouse: [
      { required: true, message: '请选择仓库', trigger: 'change' }
    ],
    order_date: [
      { required: true, message: '请选择采购日期', trigger: 'change' }
    ],
    items: [
      {
        validator: (rule, value, callback) => {
          if (value.length === 0) {
            callback(new Error('采购明细不能为空'))
          } else {
            callback()
          }
        },
        trigger: 'change'
      }
    ]
  })
  
  const availableGoods = computed(() => {
    const selectedIds = form.items.map(item => item.goods)
    return goodsList.value.filter(g => !selectedIds.includes(g.id))
  })
  
  const totalQuantity = computed(() => {
    return form.items.reduce((sum, item) => {
      const quantity = Number(item.quantity) || 0
      return sum + quantity
    }, 0)
  })
  
  const totalAmount = computed(() => {
    return form.items.reduce((sum, item) => {
      const amount = Number(item.amount) || 0
      return sum + amount
    }, 0).toFixed(2)
  })
  
  const getStatusText = (status) => {
    const statusMap = {
      pending: '待入库',
      partial: '部分入库',
      completed: '已入库',
      cancelled: '已取消'
    }
    return statusMap[status] || '-'
  }
  
  const handleAdd = () => {
    isEdit.value = false
    dialogTitle.value = '新增采购单'
    resetForm()
    dialogVisible.value = true
  }
  
  const handleEdit = (row) => {
    isEdit.value = true
    dialogTitle.value = '编辑采购单'
    resetForm()
    form.id = row.id
    form.supplier = row.supplier
    form.warehouse = row.warehouse
    form.order_date = row.order_date
    form.remark = row.remark || ''
    form.items = row.items ? JSON.parse(JSON.stringify(row.items)) : []
    dialogVisible.value = true
  }
  
  const handleView = (row) => {
    viewData.value = row
    viewDialogVisible.value = true
  }
  
  const handleEditFromView = () => {
    const data = viewData.value
    viewDialogVisible.value = false
    nextTick(() => {
      handleEdit(data)
    })
  }
  
  const handleDeleteFromView = async () => {
    if (!viewData.value) return
    
    const statusText = getStatusText(viewData.value.status)
    
    if (viewData.value.status === 'completed') {
      ElMessage.warning('已入库的采购单不能删除')
      return
    }
    
    if (viewData.value.status === 'partial') {
      ElMessage.warning('部分入库的采购单不能删除，请先处理完入库')
      return
    }
    
    if (viewData.value.status === 'cancelled') {
      ElMessage.warning('已取消的采购单不能删除')
      return
    }
    
    try {
      await ElMessageBox.confirm(
        `确定删除采购单「${viewData.value.order_no}」？此操作不可恢复`,
        '删除确认',
        {
          confirmButtonText: '确定删除',
          cancelButtonText: '取消',
          type: 'warning',
          confirmButtonClass: 'el-button--danger'
        }
      )
      
      await deletePurchaseOrder(viewData.value.id)
      ElMessage.success('删除成功')
      loadOrders()
      viewDialogVisible.value = false
    } catch (error) {
      if (error !== 'cancel') {
        ElMessage.error(error.message || '删除失败')
      }
    }
  }
  
  const handleCancelFromView = async () => {
    if (!viewData.value) return
    
    try {
      await ElMessageBox.confirm(
        `确定取消采购单「${viewData.value.order_no}」？取消后将无法再进行入库操作。`,
        '取消确认',
        {
          confirmButtonText: '确定取消',
          cancelButtonText: '返回',
          type: 'warning'
        }
      )
      
      await cancelPurchaseOrder(viewData.value.id)
      ElMessage.success('取消成功')
      loadOrders()
      viewDialogVisible.value = false
    } catch (error) {
      if (error !== 'cancel') {
        ElMessage.error(error.message || '取消失败')
      }
    }
  }

  const handleRefresh = () => {
    loadOrders()
  }
  
  const loadOrders = async () => {
    loading.value = true
    try {
      const params = {
        page: currentPage.value,
        page_size: pageSize.value
      }
      if (searchKeyword.value) {
        params.search = searchKeyword.value
      }
      if (statusFilter.value) {
        params.status = statusFilter.value
      }
      
      const res = await getPurchaseOrders(params)
      orderList.value = res.data?.items || res.data?.results || []
      total.value = res.data?.count || 0
    } catch (error) {
      orderList.value = []
      total.value = 0
      ElMessage.error('加载数据失败')
    } finally {
      loading.value = false
    }
  }
  
  const loadSuppliers = async () => {
    try {
      const res = await getSuppliers({ page_size: 1000, is_active: true })
      supplierList.value = res.data?.items || res.data?.results || []
    } catch (error) {
      supplierList.value = []
    }
  }
  
  const loadWarehouses = async () => {
    try {
      const res = await getWarehouses({ page_size: 1000, is_active: true })
      warehouseList.value = res.data?.items || res.data?.results || []
    } catch (error) {
      warehouseList.value = []
    }
  }
  
  /**
   * 加载商品列表
   */
  const loadGoods = async () => {
    try {
      const res = await getGoods({ page_size: 1000, status: 1 })
      goodsList.value = res.data?.items || res.data?.results || []
    } catch (error) {
      goodsList.value = []
    }
  }
  
  /**
   * 加载商品分类列表
   */
  const loadCategories = async () => {
    try {
      const res = await getCategories({ page_size: 1000, is_active: true })
      const categories = res.data?.items || res.data?.results || []
      // 只获取二级及以下分类（有商品的分类）
      categoryList.value = categories.filter(c => c.level >= 2)
    } catch (error) {
      categoryList.value = []
    }
  }
  
  const resetForm = () => {
    form.id = null
    form.supplier = null
    form.warehouse = null
    form.order_date = ''
    form.remark = ''
    form.items = []
  }
  
  /**
   * 添加商品项
   */
  const addItem = () => {
    form.items.push({
      goods: null,
      goods_code: '',
      goods_name: '',
      spec: '',
      unit_name: '',
      quantity: 0,
      price: 0,
      amount: 0,
      _quantityError: '',
      _priceError: ''
    })
  }
  
  const removeItem = (index) => {
    form.items.splice(index, 1)
  }
  
  /**
   * 处理商品编码输入
   * 根据编码自动匹配商品
   */
  const handleCodeChange = (row, index) => {
    const code = row.goods_code?.trim().toUpperCase()
    if (!code) {
      // 清空商品信息
      row.goods = null
      row.goods_name = ''
      row.spec = ''
      row.unit_name = ''
      row.price = 0
      return
    }
    
    // 根据编码查找商品
    const goods = goodsList.value.find(g => g.code?.toUpperCase() === code)
    if (goods) {
      // 检查是否已选择
      const existingIndex = form.items.findIndex((item, i) => i !== index && item.goods === goods.id)
      if (existingIndex !== -1) {
        ElMessage.warning(`商品「${goods.name}」已在第${existingIndex + 1}行选择`)
        row.goods_code = ''
        return
      }
      
      // 填充商品信息
      row.goods = goods.id
      row.goods_name = goods.name
      row.spec = goods.spec || ''
      row.unit_name = goods.unit_name || goods.unit?.name || ''
      row.price = goods.purchase_price || 0
      calculateItemAmount(row)
    } else {
      ElMessage.warning(`未找到编码为「${code}」的商品`)
      row.goods = null
      row.goods_name = ''
      row.spec = ''
      row.unit_name = ''
    }
  }
  
  /**
   * 处理商品选择（从弹窗选择）
   */
  const handleGoodsChange = (row, index, goods) => {
    if (!goods) return
    
    // 检查是否已选择
    const existingIndex = form.items.findIndex((item, i) => i !== index && item.goods === goods.id)
    if (existingIndex !== -1) {
      ElMessage.warning(`商品「${goods.name}」已在第${existingIndex + 1}行选择`)
      return
    }
    
    // 填充商品信息
    row.goods = goods.id
    row.goods_code = goods.code || ''
    row.goods_name = goods.name
    row.spec = goods.spec || ''
    row.unit_name = goods.unit_name || goods.unit?.name || ''
    row.price = goods.purchase_price || 0
    row._priceError = ''
    calculateItemAmount(row)
  }
  
  /**
   * 处理规格变化
   */
  const handleSpecChange = (row) => {
    // 规格变化时可以触发其他逻辑
  }
  
  const handleQuantityInput = (row, value) => {
    row._quantityError = ''
    const num = parseInputNumber(value)
    row.quantity = num
    calculateItemAmount(row)
  }
  
  const handleQuantityBlur = (row) => {
    if (!row.quantity || row.quantity <= 0) {
      row._quantityError = '请输入数量'
    }
  }
  
  const handlePriceInput = (row, value) => {
    row._priceError = ''
    const num = parseInputNumber(value)
    row.price = num
    calculateItemAmount(row)
  }
  
  const handlePriceBlur = (row) => {
    if (!row.price || row.price <= 0) {
      row._priceError = '请输入单价'
    }
  }
  
  const calculateItemAmount = (row) => {
    const quantity = Number(row.quantity) || 0
    const price = Number(row.price) || 0
    row.amount = quantity * price
  }
  
  const getGoodsUnit = (goodsId) => {
    const goods = goodsList.value.find(g => g.id === goodsId)
    return goods?.unit?.name || ''
  }
  
  const handleSubmit = async () => {
    if (!purchaseFormRef.value) {
      console.error('purchaseFormRef 未初始化')
      return
    }
    
    const formRefInstance = purchaseFormRef.value.formRef
    if (!formRefInstance) {
      console.error('formRef 未找到')
      return
    }
    
    try {
      await formRefInstance.validate()
    } catch (error) {
      return
    }
    
    const hasError = form.items.some(item => item._quantityError || item._priceError)
    if (hasError) {
      ElMessage.warning('请检查明细数据')
      return
    }
    
    if (form.items.length === 0) {
      ElMessage.warning('请添加采购明细')
      return
    }
    
    const hasInvalidItems = form.items.some(item => !item.goods || !item.quantity || !item.price)
    if (hasInvalidItems) {
      ElMessage.warning('请完善采购明细信息')
      return
    }
    
    submitLoading.value = true
    try {
      const data = {
        supplier: form.supplier,
        warehouse: form.warehouse,
        order_date: form.order_date,
        remark: form.remark,
        items: form.items.map(item => ({
          goods: item.goods,
          goods_code: item.goods_code,
          goods_name: item.goods_name,
          spec: item.spec,
          quantity: Number(item.quantity),
          price: Number(item.price),
          amount: Number(item.amount)
        }))
      }
      
      if (isEdit.value) {
        await updatePurchaseOrder(form.id, data)
        ElMessage.success('修改成功')
      } else {
        await createPurchaseOrder(data)
        ElMessage.success('新增成功')
      }
      
      dialogVisible.value = false
      loadOrders()
    } catch (error) {
      ElMessage.error(isEdit.value ? '修改失败' : '新增失败')
    } finally {
      submitLoading.value = false
    }
  }
  
  const handleDialogClose = () => {
    formRef.value?.resetFields()
    resetForm()
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
    loadSuppliers()
    loadWarehouses()
    loadGoods()
    loadCategories()
    loadOrders()
    calculateTableHeight()
    window.addEventListener('resize', calculateTableHeight)
  })

  onUnmounted(() => {
    window.removeEventListener('resize', calculateTableHeight)
  })
  
  return {
    loading,
    orderList,
    searchKeyword,
    statusFilter,
    currentPage,
    pageSize,
    total,
    tableHeight,
    dialogVisible,
    dialogTitle,
    isEdit,
    submitLoading,
    viewDialogVisible,
    viewData,
    formRef,
    supplierList,
    warehouseList,
    goodsList,
    categoryList,
    form,
    rules,
    availableGoods,
    totalQuantity,
    totalAmount,
    getStatusText,
    handleAdd,
    handleEdit,
    handleView,
    handleEditFromView,
    handleDeleteFromView,
    handleCancelFromView,
    handleRefresh,
    loadOrders,
    loadSuppliers,
    loadWarehouses,
    loadGoods,
    loadCategories,
    calculateTableHeight,
    addItem,
    removeItem,
    handleGoodsChange,
    handleCodeChange,
    handleSpecChange,
    handleQuantityInput,
    handleQuantityBlur,
    handlePriceInput,
    handlePriceBlur,
    calculateItemAmount,
    getGoodsUnit,
    resetForm,
    handleSubmit,
    handleDialogClose
  }
}

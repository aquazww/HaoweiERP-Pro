/**
 * 订单管理组合式函数
 * 独立的订单管理逻辑， */
import { ref, reactive, computed, onMounted, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'

import { getPurchaseOrders, createPurchaseOrder, updatePurchaseOrder, deletePurchaseOrder } from '@/api/purchase'
import { getSuppliers, getWarehouses, getGoods } from '@/api/basic'
import { formatPrice, formatInputNumber, parseInputNumber } from '@/utils/format'
import { canAdd, canEdit, canDelete } from '@/utils/permission'

export function usePurchaseOrders() {
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
    form.supplier = row.supplier
    form.warehouse = row.warehouse
    form.order_date = row.order_date
    form.remark = row.remark || ''
    form.items = row.items ? structuredClone(row.items) : []
    dialogVisible.value = true
  }
  
  const handleView = (row) => {
    viewData.value = row
    viewDialogVisible.value = true
  }
  
  const handleEditFromView = () => {
    viewDialogVisible.value = false
    handleEdit(viewData.value)
  }
  
  const handleDeleteFromView = async () => {
    try {
      await ElMessageBox.confirm(
        `确定删除采购单「${viewData.value.order_no}」？此操作不可恢复`,
        '提示',
        { type: 'warning' }
      )
      await deletePurchaseOrder(viewData.value.id)
      ElMessage.success('删除成功')
      loadOrders()
      viewDialogVisible.value = false
    } catch (error) {
      if (error !== 'cancel') {
        ElMessage.error('删除失败')
      }
    }
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
  
  const loadGoods = async () => {
    try {
      const res = await getGoods({ page_size: 1000, status: 1 })
      goodsList.value = res.data?.items || res.data?.results || []
    } catch (error) {
      goodsList.value = []
    }
  }
  
  const resetForm = () => {
    form.supplier = null
    form.warehouse = null
    form.order_date = ''
    form.remark = ''
    form.items = []
  }
  
  const addItem = () => {
    form.items.push({
      goods: null,
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
  
  const handleGoodsChange = (row, index) => {
    const goods = goodsList.value.find(g => g.id === row.goods)
    if (goods) {
      row.unit = goods.unit?.name || ''
      row.price = goods.purchase_price || 0
      row._priceError = ''
      calculateItemAmount(row)
    }
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
    if (!formRef.value) return
    
    try {
      await formRef.value.validate()
    } catch (error) {
      return
    }
    
    const hasError = form.items.some(item => item._quantityError || item._priceError)
    if (hasError) {
      ElMessage.warning('请检查明细数据')
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
    loadOrders()
    calculateTableHeight()
    window.addEventListener('resize', calculateTableHeight)
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
    selectedGoods,
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
    loadOrders,
    loadSuppliers,
    loadWarehouses,
    loadGoods,
    calculateTableHeight,
    addItem,
    removeItem,
    handleGoodsChange,
    handleQuantityInput,
    handleQuantityBlur,
    handlePriceInput,
    handlePriceBlur,
    calculateItemAmount,
    getGoodsUnit,
    availableGoods,
    resetForm,
    handleSubmit,
    handleDialogClose
  }
}

/**
 * 商品管理组合式函数
 * 管理商品的加载、增删改查、状态切换等操作
 */
import { ref, reactive, onMounted, nextTick, onUnmounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getGoods, createGoods, updateGoods, partialUpdateGoods, deleteGoods, getUnits } from '@/api/basic'
import { formatPrice, formatInputNumber, parseInputNumber } from '@/utils/format'
import { canAdd, canEdit, canDelete } from '@/utils/permission'

export function useGoods(selectedCategoryId, selectedCategoryIncludeChildren) {
  const loading = ref(false)
  const toggleLoading = ref(null)
  const goodsList = ref([])
  const searchKeyword = ref('')
  const statusFilter = ref('')
  const currentPage = ref(1)
  const pageSize = ref(20)
  const total = ref(0)
  const tableHeight = ref(0)
  const unitList = ref([])
  
  const dialogVisible = ref(false)
  const dialogTitle = ref('新增商品')
  const isEdit = ref(false)
  const submitLoading = ref(false)
  const formRef = ref(null)
  
  const canAddGoods = canAdd('basic')
  const canEditGoods = canEdit('basic')
  const canDeleteGoods = canDelete('basic')
  
  const priceErrors = reactive({
    purchase_price: '',
    sale_price: '',
    retail_price: ''
  })
  
  const form = reactive({
    id: null,
    code: '',
    name: '',
    category: null,
    unit: null,
    spec: '',
    barcode: '',
    purchase_price: 0,
    sale_price: 0,
    retail_price: 0,
    min_stock: 0,
    max_stock: 0,
    status: 1,
    remark: ''
  })
  
  const validateCode = (rule, value, callback) => {
    if (!value || !value.trim()) {
      callback(new Error('请输入商品编码'))
    } else if (value.length > 50) {
      callback(new Error('商品编码不能超过50个字符'))
    } else if (!/^[A-Za-z0-9_-]+$/.test(value)) {
      callback(new Error('商品编码只能包含字母、数字、下划线和横线'))
    } else {
      callback()
    }
  }
  
  const validateName = (rule, value, callback) => {
    if (!value || !value.trim()) {
      callback(new Error('请输入商品名称'))
    } else if (value.length > 100) {
      callback(new Error('商品名称不能超过100个字符'))
    } else {
      callback()
    }
  }
  
  const validateMaxStock = (rule, value, callback) => {
    if (value < form.min_stock) {
      callback(new Error('最高库存不能低于最低库存'))
    } else {
      callback()
    }
  }
  
  const rules = {
    code: [{ required: true, validator: validateCode, trigger: 'blur' }],
    name: [{ required: true, validator: validateName, trigger: 'blur' }],
    category: [{ required: true, message: '请选择商品分类', trigger: 'change' }],
    unit: [{ required: true, message: '请选择或输入计量单位', trigger: 'change' }],
    max_stock: [{ validator: validateMaxStock, trigger: 'blur' }]
  }
  
  const handlePriceInput = (field, value) => {
    priceErrors[field] = ''
    const num = parseInputNumber(value)
    form[field] = num
  }
  
  const handlePriceBlur = (field) => {
    const value = form[field]
    if (value === null || value === undefined || value === '') {
      priceErrors[field] = '请输入价格'
      return
    }
    if (value < 0) {
      priceErrors[field] = '价格不能为负数'
      return
    }
    if (value > 99999999.99) {
      priceErrors[field] = '价格超出范围'
      return
    }
    
    if (field === 'sale_price' && form.purchase_price && value < form.purchase_price) {
      priceErrors[field] = '销售价不能低于进货价'
      return
    }
    
    priceErrors[field] = ''
  }
  
  const getGoodsInitials = (name) => {
    if (!name) return ''
    return name.slice(0, 2)
  }
  
  const calculateProfit = (row) => {
    const purchase = Number(row.purchase_price) || 0
    const sale = Number(row.sale_price) || 0
    return sale - purchase
  }
  
  const calculateTableHeight = () => {
    nextTick(() => {
      const toolbarCard = document.querySelector('.goods-card .toolbar-card')
      const paginationWrapper = document.querySelector('.goods-card .pagination-wrapper')
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
  
  const loadUnits = async () => {
    try {
      const res = await getUnits({ page_size: 1000, is_active: true })
      unitList.value = res.data?.items || res.data?.results || []
    } catch (error) {
      unitList.value = []
    }
  }
  
  const loadGoods = async () => {
    loading.value = true
    try {
      const params = {
        page: currentPage.value,
        page_size: pageSize.value
      }
      if (searchKeyword.value) {
        params.search = searchKeyword.value
      }
      if (statusFilter.value !== '') {
        params.status = statusFilter.value
      }
      if (selectedCategoryId && selectedCategoryId.value) {
        if (selectedCategoryIncludeChildren && selectedCategoryIncludeChildren.value) {
          params.category_include_children = selectedCategoryId.value
        } else {
          params.category = selectedCategoryId.value
        }
      }
      const res = await getGoods(params)
      goodsList.value = res.data?.items || res.data?.results || []
      total.value = res.data?.count || 0
    } catch (error) {
      goodsList.value = []
      total.value = 0
      ElMessage.error('加载数据失败：' + (error.message || '未知错误'))
    } finally {
      loading.value = false
    }
  }
  
  const resetForm = () => {
    form.id = null
    form.code = ''
    form.name = ''
    form.category = selectedCategoryId?.value || null
    form.unit = ''
    form.spec = ''
    form.barcode = ''
    form.purchase_price = 0
    form.sale_price = 0
    form.retail_price = 0
    form.min_stock = 0
    form.max_stock = 0
    form.status = 1
    form.remark = ''
    priceErrors.purchase_price = ''
    priceErrors.sale_price = ''
    priceErrors.retail_price = ''
  }
  
  const handleDialogClose = () => {
    formRef.value?.resetFields()
    resetForm()
  }
  
  const handleAdd = () => {
    isEdit.value = false
    dialogTitle.value = '新增商品'
    resetForm()
    if (selectedCategoryId && selectedCategoryId.value) {
      form.category = selectedCategoryId.value
    }
    dialogVisible.value = true
  }
  
  const handleEdit = (row) => {
    isEdit.value = true
    dialogTitle.value = '编辑商品'
    resetForm()
    form.id = row.id
    form.code = row.code
    form.name = row.name
    form.category = row.category
    form.unit = row.unit
    form.spec = row.spec || ''
    form.barcode = row.barcode || ''
    form.purchase_price = row.purchase_price || 0
    form.sale_price = row.sale_price || 0
    form.retail_price = row.retail_price || 0
    form.min_stock = row.min_stock || 0
    form.max_stock = row.max_stock || 0
    form.status = row.status
    form.remark = row.remark || ''
    dialogVisible.value = true
  }
  
  const handleSubmit = async () => {
    if (!formRef.value) return
    
    try {
      await formRef.value.validate()
    } catch (error) {
      return
    }
    
    if (priceErrors.purchase_price || priceErrors.sale_price || priceErrors.retail_price) {
      ElMessage.warning('请检查价格输入')
      return
    }
    
    submitLoading.value = true
    try {
      const data = {
        code: form.code,
        name: form.name,
        category: form.category,
        unit: form.unit,
        spec: form.spec,
        barcode: form.barcode,
        purchase_price: form.purchase_price || 0,
        sale_price: form.sale_price || 0,
        retail_price: form.retail_price || 0,
        min_stock: form.min_stock || 0,
        max_stock: form.max_stock || 0,
        status: form.status,
        remark: form.remark
      }
      
      if (isEdit.value) {
        await updateGoods(form.id, data)
        ElMessage.success('修改成功')
      } else {
        await createGoods(data)
        ElMessage.success('新增成功')
      }
      
      dialogVisible.value = false
      loadGoods()
    } catch (error) {
      ElMessage.error(isEdit.value ? '修改失败' : '新增失败')
    } finally {
      submitLoading.value = false
    }
  }
  
  const handleDelete = async (row) => {
    try {
      await ElMessageBox.confirm(`确定删除商品「${row.name}」？`, '确认删除', { type: 'warning' })
      await deleteGoods(row.id)
      ElMessage.success('删除成功')
      loadGoods()
    } catch (error) {
      if (error !== 'cancel') {
        ElMessage.error('删除失败')
      }
    }
  }
  
  const handleToggleStatus = async (row) => {
    toggleLoading.value = row.id
    try {
      await partialUpdateGoods(row.id, { status: row.status })
      ElMessage.success(row.status === 1 ? '已上架' : '已下架')
    } catch (error) {
      row.status = row.status === 1 ? 0 : 1
      ElMessage.error('操作失败')
    } finally {
      toggleLoading.value = null
    }
  }
  
  onMounted(() => {
    loadUnits()
    loadGoods()
    calculateTableHeight()
    window.addEventListener('resize', calculateTableHeight)
  })
  
  onUnmounted(() => {
    window.removeEventListener('resize', calculateTableHeight)
  })
  
  return {
    loading,
    toggleLoading,
    goodsList,
    searchKeyword,
    statusFilter,
    currentPage,
    pageSize,
    total,
    tableHeight,
    unitList,
    dialogVisible,
    dialogTitle,
    isEdit,
    submitLoading,
    formRef,
    canAddGoods,
    canEditGoods,
    canDeleteGoods,
    priceErrors,
    form,
    rules,
    handlePriceInput,
    handlePriceBlur,
    getGoodsInitials,
    calculateProfit,
    calculateTableHeight,
    loadUnits,
    loadGoods,
    resetForm,
    handleDialogClose,
    handleAdd,
    handleEdit,
    handleSubmit,
    handleDelete,
    handleToggleStatus
  }
}

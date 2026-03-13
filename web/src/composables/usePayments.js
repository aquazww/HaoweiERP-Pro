/**
 * 付款管理组合式函数
 * 管理付款的加载、增删改查、状态管理等操作
 */
import { ref, reactive, computed, onMounted, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getPayments, createPayment, updatePayment, deletePayment } from '@/api/finance'
import { formatPrice } from '@/utils/format'
import { canAdd, canEdit, canDelete } from '@/utils/permission'

export function usePayments() {
  const loading = ref(false)
  const paymentList = ref([])
  const searchKeyword = ref('')
  const query = reactive({
    type: '',
    status: '',
    page: 1,
    pageSize: 20,
    total: 0
  })
  const tableHeight = ref(0)
  
  const dialogVisible = ref(false)
  const dialogTitle = ref('新增付款')
  const isEdit = ref(false)
  const submitLoading = ref(false)
  const viewDialogVisible = ref(false)
  const viewData = ref(null)
  const recordsExpanded = ref(true)
  const formRef = ref(null)
  
  const canAddFinance = computed(() => canAdd('finance'))
  const canEditFinance = computed(() => canEdit('finance'))
  const canDeleteFinance = computed(() => canDelete('finance'))
  
  const form = reactive({
    related_party: null,
    related_party_name: '',
    related_order: null,
    type: 'pay',
    total_amount: 0,
    amount: 0,
    payment_method: 'cash',
    payment_date: '',
    remark: ''
  })
  
  const rules = reactive({
    related_party: [
      { required: true, message: '请选择往来单位', trigger: 'change' }
    ],
    type: [
      { required: true, message: '请选择类型', trigger: 'change' }
    ],
    total_amount: [
      { required: true, message: '请输入总金额', trigger: 'blur' }
    ],
    amount: [
      { required: true, message: '请输入付款金额', trigger: 'blur' }
    ],
    payment_date: [
      { required: true, message: '请选择付款日期', trigger: 'change' }
    ]
  })
  
  const getStatusText = (status) => {
    const statusMap = {
      pending: '待付款',
      partial: '部分付款',
      paid: '已付款'
    }
    return statusMap[status] || status
  }
  
  const formatDateTime = (datetime) => {
    if (!datetime) return '-'
    return datetime.replace('T', ' ').substring(0, 19)
  }
  
  const loadPayments = async () => {
    loading.value = true
    try {
      const params = {
        page: query.page,
        page_size: query.pageSize
      }
      if (searchKeyword.value) {
        params.search = searchKeyword.value
      }
      if (query.type) {
        params.type = query.type
      }
      if (query.status) {
        params.status = query.status
      }
      
      const res = await getPayments(params)
      paymentList.value = res.data?.items || res.data?.results || []
      query.total = res.data?.count || 0
    } catch (error) {
      paymentList.value = []
      query.total = 0
      ElMessage.error('加载数据失败')
    } finally {
      loading.value = false
    }
  }
  
  const handleAdd = () => {
    isEdit.value = false
    dialogTitle.value = '新增付款'
    resetForm()
    dialogVisible.value = true
  }
  
  const handleEdit = (row) => {
    isEdit.value = true
    dialogTitle.value = '编辑付款'
    resetForm()
    form.related_party = row.related_party
    form.related_party_name = row.related_party_name
    form.related_order = row.related_order
    form.type = row.type
    form.total_amount = row.total_amount
    form.amount = row.amount
    form.payment_method = row.payment_method
    form.payment_date = row.payment_date
    form.remark = row.remark || ''
    dialogVisible.value = true
  }
  
  const handleView = (row) => {
    viewData.value = row
    viewDialogVisible.value = true
  }
  
  const handleViewOrder = (row) => {
    console.log('查看关联订单:', row.related_order_no)
  }
  
  const handlePayFromView = () => {
    if (!viewData.value) return
    viewDialogVisible.value = false
    handleEdit(viewData.value)
  }
  
  const handleDeleteFromView = async () => {
    if (!viewData.value) return
    
    try {
      await ElMessageBox.confirm(
        `确定删除付款单「${viewData.value.order_no}」？`,
        '确认删除',
        { type: 'warning' }
      )
      
      await deletePayment(viewData.value.id)
      ElMessage.success('删除成功')
      viewDialogVisible.value = false
      loadPayments()
    } catch (error) {
      if (error !== 'cancel') {
        ElMessage.error('删除失败')
      }
    }
  }
  
  const resetForm = () => {
    form.related_party = null
    form.related_party_name = ''
    form.related_order = null
    form.type = 'pay'
    form.total_amount = 0
    form.amount = 0
    form.payment_method = 'cash'
    form.payment_date = ''
    form.remark = ''
  }
  
  const handleSubmit = async () => {
    if (!formRef.value) return
    
    try {
      await formRef.value.validate()
    } catch (error) {
      return
    }
    
    submitLoading.value = true
    try {
      const data = {
        related_party: form.related_party,
        related_order: form.related_order,
        type: form.type,
        total_amount: form.total_amount,
        amount: form.amount,
        payment_method: form.payment_method,
        payment_date: form.payment_date,
        remark: form.remark
      }
      
      if (isEdit.value) {
        await updatePayment(viewData.value.id, data)
        ElMessage.success('修改成功')
      } else {
        await createPayment(data)
        ElMessage.success('新增成功')
      }
      
      dialogVisible.value = false
      loadPayments()
    } catch (error) {
      ElMessage.error(isEdit.value ? '修改失败' : '新增失败')
    } finally {
      submitLoading.value = false
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
    loadPayments()
    calculateTableHeight()
    window.addEventListener('resize', calculateTableHeight)
  })
  
  return {
    loading,
    paymentList,
    searchKeyword,
    query,
    total: query.total,
    tableHeight,
    dialogVisible,
    dialogTitle,
    isEdit,
    submitLoading,
    viewDialogVisible,
    viewData,
    recordsExpanded,
    formRef,
    canAddFinance,
    canEditFinance,
    canDeleteFinance,
    form,
    rules,
    getStatusText,
    formatDateTime,
    loadPayments,
    handleAdd,
    handleEdit,
    handleView,
    handleViewOrder,
    handlePayFromView,
    handleDeleteFromView,
    resetForm,
    handleSubmit
  }
}

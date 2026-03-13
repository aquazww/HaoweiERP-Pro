/**
 * 仓库管理组合式函数
 * 管理仓库的加载、增删改查、状态切换等操作
 */
import { ref, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getWarehouses, createWarehouse, updateWarehouse, partialUpdateWarehouse, deleteWarehouse } from '@/api/basic'

export function useWarehouses() {
  const warehouseList = ref([])
  const warehouseLoading = ref(false)
  const warehouseSearch = ref('')
  const warehouseDialogVisible = ref(false)
  const warehouseDialogTitle = ref('')
  const warehouseFormRef = ref(null)
  const warehouseSubmitLoading = ref(false)
  const warehouseEditingId = ref(null)
  const warehouseToggleLoading = ref(null)
  const selectedWarehouse = ref(null)
  
  const warehouseForm = ref({
    name: '',
    address: '',
    contact: '',
    phone: '',
    is_active: true
  })
  
  const warehouseRules = {
    name: [{ required: true, message: '请输入仓库名称', trigger: 'blur' }]
  }
  
  const filteredWarehouseList = computed(() => {
    if (!warehouseSearch.value) return warehouseList.value
    const keyword = warehouseSearch.value.toLowerCase()
    return warehouseList.value.filter(item => 
      item.name.toLowerCase().includes(keyword) ||
      (item.address && item.address.toLowerCase().includes(keyword))
    )
  })
  
  const formatDateTime = (datetime) => {
    if (!datetime) return '-'
    return datetime.replace('T', ' ').substring(0, 19)
  }
  
  const parseErrorMessage = (error) => {
    const errorData = error.response?.data
    if (!errorData) return error.message || '网络错误，请稍后重试'
    
    if (errorData.msg && typeof errorData.msg === 'string') {
      return errorData.msg
    }
    
    if (typeof errorData === 'object') {
      const messages = []
      for (const [field, msg] of Object.entries(errorData)) {
        if (field === 'msg' || field === 'code' || field === 'data') continue
        
        let message = ''
        if (Array.isArray(msg)) {
          message = msg.map(item => {
            if (typeof item === 'object' && item.string) {
              return item.string
            }
            return String(item)
          }).join('；')
        } else if (typeof msg === 'object' && msg.string) {
          message = msg.string
        } else if (typeof msg === 'string') {
          message = msg
        }
        
        if (message) {
          messages.push(message)
        }
      }
      
      if (messages.length > 0) {
        return messages.join('；')
      }
    }
    
    return '操作失败，请稍后重试'
  }
  
  const handleWarehouseClick = (item) => {
    if (selectedWarehouse.value?.id === item.id) {
      selectedWarehouse.value = null
    } else {
      selectedWarehouse.value = item
    }
  }
  
  const loadWarehouses = async () => {
    warehouseLoading.value = true
    try {
      const params = { page_size: 1000 }
      if (warehouseSearch.value) params.search = warehouseSearch.value
      const res = await getWarehouses(params)
      warehouseList.value = res.data.items || res.data.results || []
    } catch (error) {
      ElMessage.error('加载仓库失败')
    } finally {
      warehouseLoading.value = false
    }
  }
  
  const handleAddWarehouse = () => {
    warehouseDialogTitle.value = '新增仓库'
    warehouseEditingId.value = null
    warehouseForm.value = {
      name: '',
      address: '',
      contact: '',
      phone: '',
      is_active: true
    }
    warehouseDialogVisible.value = true
  }
  
  const handleEditWarehouse = (row) => {
    warehouseDialogTitle.value = '编辑仓库'
    warehouseEditingId.value = row.id
    warehouseForm.value = {
      name: row.name,
      address: row.address || '',
      contact: row.contact || '',
      phone: row.phone || '',
      is_active: row.is_active
    }
    warehouseDialogVisible.value = true
  }
  
  const handleWarehouseSubmit = async () => {
    if (!warehouseFormRef.value) return
    
    try {
      await warehouseFormRef.value.validate()
    } catch (error) {
      return
    }
    
    warehouseSubmitLoading.value = true
    try {
      const data = {
        name: warehouseForm.value.name,
        address: warehouseForm.value.address,
        contact: warehouseForm.value.contact,
        phone: warehouseForm.value.phone,
        is_active: warehouseForm.value.is_active
      }
      
      if (warehouseEditingId.value) {
        await updateWarehouse(warehouseEditingId.value, data)
        ElMessage.success('修改成功')
      } else {
        await createWarehouse(data)
        ElMessage.success('新增成功')
      }
      
      warehouseDialogVisible.value = false
      loadWarehouses()
    } catch (error) {
      const errorMsg = parseErrorMessage(error)
      ElMessage.error(errorMsg)
    } finally {
      warehouseSubmitLoading.value = false
    }
  }
  
  const handleToggleWarehouseStatus = async (row) => {
    warehouseToggleLoading.value = row.id
    try {
      await partialUpdateWarehouse(row.id, { is_active: row.is_active })
      ElMessage.success(row.is_active ? '已启用' : '已停用')
    } catch (error) {
      row.is_active = !row.is_active
      ElMessage.error('操作失败')
    } finally {
      warehouseToggleLoading.value = null
    }
  }
  
  const handleDeleteWarehouse = async (row) => {
    try {
      await ElMessageBox.confirm(`确定删除仓库「${row.name}」？`, '确认删除', { type: 'warning' })
      await deleteWarehouse(row.id)
      ElMessage.success('删除成功')
      if (selectedWarehouse.value?.id === row.id) {
        selectedWarehouse.value = null
      }
      loadWarehouses()
    } catch (error) {
      if (error !== 'cancel') {
        ElMessage.error('删除失败')
      }
    }
  }
  
  return {
    warehouseList,
    warehouseLoading,
    warehouseSearch,
    warehouseDialogVisible,
    warehouseDialogTitle,
    warehouseFormRef,
    warehouseSubmitLoading,
    warehouseToggleLoading,
    selectedWarehouse,
    warehouseForm,
    warehouseRules,
    filteredWarehouseList,
    formatDateTime,
    handleWarehouseClick,
    loadWarehouses,
    handleAddWarehouse,
    handleEditWarehouse,
    handleWarehouseSubmit,
    handleToggleWarehouseStatus,
    handleDeleteWarehouse
  }
}

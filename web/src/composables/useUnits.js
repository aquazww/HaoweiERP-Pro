/**
 * 计量单位管理组合式函数
 * 管理计量单位的加载、增删改查、状态切换等操作
 */
import { ref, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getUnits, createUnit, updateUnit, partialUpdateUnit, deleteUnit } from '@/api/basic'

export function useUnits() {
  const unitList = ref([])
  const unitLoading = ref(false)
  const unitSearch = ref('')
  const unitDialogVisible = ref(false)
  const unitDialogTitle = ref('')
  const unitFormRef = ref(null)
  const unitSubmitLoading = ref(false)
  const unitEditingId = ref(null)
  const unitToggleLoading = ref(null)
  const selectedUnit = ref(null)
  
  const unitForm = ref({
    name: '',
    is_active: true
  })
  
  const unitRules = {
    name: [{ required: true, message: '请输入单位名称', trigger: 'blur' }]
  }
  
  const filteredUnitList = computed(() => {
    if (!unitSearch.value) return unitList.value
    const keyword = unitSearch.value.toLowerCase()
    return unitList.value.filter(item => 
      item.name.toLowerCase().includes(keyword)
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
  
  const handleUnitClick = (item) => {
    if (selectedUnit.value?.id === item.id) {
      selectedUnit.value = null
    } else {
      selectedUnit.value = item
    }
  }
  
  const loadUnits = async () => {
    unitLoading.value = true
    try {
      const params = { page_size: 1000 }
      if (unitSearch.value) params.search = unitSearch.value
      const res = await getUnits(params)
      unitList.value = res.data.items || res.data.results || []
    } catch (error) {
      ElMessage.error('加载计量单位失败')
    } finally {
      unitLoading.value = false
    }
  }
  
  const handleAddUnit = () => {
    unitDialogTitle.value = '新增计量单位'
    unitEditingId.value = null
    unitForm.value = { name: '', is_active: true }
    unitDialogVisible.value = true
  }
  
  const handleEditUnit = (row) => {
    unitDialogTitle.value = '编辑计量单位'
    unitEditingId.value = row.id
    unitForm.value = {
      name: row.name,
      is_active: row.is_active
    }
    unitDialogVisible.value = true
  }
  
  const handleUnitSubmit = async () => {
    if (!unitFormRef.value) return
    
    try {
      await unitFormRef.value.validate()
    } catch (error) {
      return
    }
    
    unitSubmitLoading.value = true
    try {
      const data = {
        name: unitForm.value.name,
        is_active: unitForm.value.is_active
      }
      
      if (unitEditingId.value) {
        await updateUnit(unitEditingId.value, data)
        ElMessage.success('修改成功')
      } else {
        await createUnit(data)
        ElMessage.success('新增成功')
      }
      
      unitDialogVisible.value = false
      loadUnits()
    } catch (error) {
      const errorMsg = parseErrorMessage(error)
      ElMessage.error(errorMsg)
    } finally {
      unitSubmitLoading.value = false
    }
  }
  
  const handleToggleUnitStatus = async (row) => {
    unitToggleLoading.value = row.id
    try {
      await partialUpdateUnit(row.id, { is_active: row.is_active })
      ElMessage.success(row.is_active ? '已启用' : '已停用')
    } catch (error) {
      row.is_active = !row.is_active
      ElMessage.error('操作失败')
    } finally {
      unitToggleLoading.value = null
    }
  }
  
  const handleDeleteUnit = async (row) => {
    try {
      await ElMessageBox.confirm(`确定删除单位「${row.name}」？`, '确认删除', { type: 'warning' })
      await deleteUnit(row.id)
      ElMessage.success('删除成功')
      if (selectedUnit.value?.id === row.id) {
        selectedUnit.value = null
      }
      loadUnits()
    } catch (error) {
      if (error !== 'cancel') {
        ElMessage.error('删除失败')
      }
    }
  }
  
  return {
    unitList,
    unitLoading,
    unitSearch,
    unitDialogVisible,
    unitDialogTitle,
    unitFormRef,
    unitSubmitLoading,
    unitToggleLoading,
    selectedUnit,
    unitForm,
    unitRules,
    filteredUnitList,
    formatDateTime,
    handleUnitClick,
    loadUnits,
    handleAddUnit,
    handleEditUnit,
    handleUnitSubmit,
    handleToggleUnitStatus,
    handleDeleteUnit
  }
}

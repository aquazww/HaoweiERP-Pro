/**
 * 打印元素管理组合式函数
 * 管理打印元素的拖拽、放置、选择、调整大小等操作
 */
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { error } from '@/utils/logger'

export function usePrintElements(printSettings, canvasWidthPx, canvasHeightPx, MM_TO_PX) {
  const selectedElementId = ref(null)
  const placedElements = ref([])
  
  const mainFieldDefinitions = [
    { key: 'order_no', label: '送货单号' },
    { key: 'sale_order_no', label: '销售单号' },
    { key: 'customer_name', label: '客户名称' },
    { key: 'customer_contact', label: '联系人' },
    { key: 'customer_phone', label: '联系电话' },
    { key: 'customer_address', label: '送货地址' },
    { key: 'warehouse_name', label: '发货仓库' },
    { key: 'delivery_date', label: '送货日期' },
    { key: 'total_amount', label: '总金额' },
    { key: 'remark', label: '备注' }
  ]
  
  const detailFieldDefinitions = [
    { key: 'goods_code', label: '商品编码' },
    { key: 'goods_name', label: '商品名称' },
    { key: 'goods_spec', label: '规格型号' },
    { key: 'unit_name', label: '单位' },
    { key: 'quantity', label: '数量' },
    { key: 'price', label: '单价' },
    { key: 'amount', label: '金额' }
  ]
  
  const companyFieldDefinitions = [
    { key: 'company_name', label: '公司名称' },
    { key: 'company_address', label: '公司地址' },
    { key: 'company_phone', label: '公司电话' },
    { key: 'company_email', label: '公司邮箱' }
  ]
  
  const selectedElement = computed(() => {
    return placedElements.value.find(el => el.id === selectedElementId.value)
  })
  
  const availableMainFields = computed(() => {
    const placedKeys = placedElements.value
      .filter(el => el.type === 'field' && el.fieldType === 'main')
      .map(el => el.key)
    return mainFieldDefinitions.filter(f => !placedKeys.includes(f.key))
  })
  
  const availableDetailFields = computed(() => {
    return detailFieldDefinitions
  })
  
  const tableColumns = computed(() => {
    return detailFieldDefinitions.filter(f => {
      if (f.key === 'price' && !printSettings.showPrice) return false
      if (f.key === 'amount' && !printSettings.showAmount) return false
      return true
    })
  })
  
  const generateId = () => `el_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
  
  const onPaletteDragStart = (event, field, fieldType) => {
    event.dataTransfer.setData('type', 'field')
    event.dataTransfer.setData('fieldType', fieldType)
    event.dataTransfer.setData('fieldKey', field.key)
    event.dataTransfer.setData('fieldLabel', field.label)
    event.dataTransfer.effectAllowed = 'copy'
  }
  
  const onPresetDragStart = (event, presetType) => {
    event.dataTransfer.setData('type', 'preset')
    event.dataTransfer.setData('presetType', presetType)
    event.dataTransfer.effectAllowed = 'copy'
  }
  
  const onCanvasDragOver = (event) => {
    event.preventDefault()
    event.dataTransfer.dropEffect = 'copy'
  }
  
  const onCanvasDrop = (event, zoom, designCanvas) => {
    event.preventDefault()
    
    const type = event.dataTransfer.getData('type')
    const rect = designCanvas.value.getBoundingClientRect()
    const scale = zoom / 100
    const x = (event.clientX - rect.left) / scale
    const y = (event.clientY - rect.top) / scale
    
    if (type === 'field') {
      const fieldType = event.dataTransfer.getData('fieldType')
      const fieldKey = event.dataTransfer.getData('fieldKey')
      const fieldLabel = event.dataTransfer.getData('fieldLabel')
      
      placedElements.value.push({
        id: generateId(),
        type: 'field',
        fieldType,
        key: fieldKey,
        label: fieldLabel,
        content: '',
        x: Math.round(x),
        y: Math.round(y),
        width: 180,
        height: 22,
        fontSize: '12px',
        fontWeight: 'normal',
        fontFamily: '',
        textAlign: 'left',
        showBorder: false
      })
    } else if (type === 'preset') {
      const presetType = event.dataTransfer.getData('presetType')
      
      const presetConfig = {
        title: { width: 300, height: 50, fontSize: '28px', fontWeight: 'bold', textAlign: 'center' },
        qrCode: { width: 120, height: 140, fontSize: '12px', fontWeight: 'normal', textAlign: 'center' },
        companyName: { width: 250, height: 28, fontSize: '16px', fontWeight: 'bold', textAlign: 'center' },
        companyLogo: { width: 80, height: 80, fontSize: '12px', fontWeight: 'normal', textAlign: 'center' },
        companyAddress: { width: 280, height: 24, fontSize: '11px', fontWeight: 'normal', textAlign: 'left' },
        companyPhone: { width: 150, height: 24, fontSize: '11px', fontWeight: 'normal', textAlign: 'left' },
        companyEmail: { width: 200, height: 24, fontSize: '11px', fontWeight: 'normal', textAlign: 'left' },
        companyStamp: { width: 80, height: 80, fontSize: '12px', fontWeight: 'normal', textAlign: 'center' },
        signature: { width: canvasWidthPx.value - 80, height: 35, fontSize: '12px', fontWeight: 'normal', textAlign: 'left' },
        table: { width: canvasWidthPx.value - 80, height: 180, fontSize: '11px', fontWeight: 'normal', textAlign: 'left' },
        copyLabels: { width: 30, height: 200, fontSize: '14px', fontWeight: 'bold', textAlign: 'center' }
      }
      
      const presetLabels = {
        title: '标题',
        qrCode: '二维码单号',
        companyName: '公司名称',
        companyLogo: '公司Logo',
        companyAddress: '公司地址',
        companyPhone: '公司电话',
        companyEmail: '公司邮箱',
        companyStamp: '公司印章',
        signature: '签收区',
        table: '明细表格',
        copyLabels: '联单名称'
      }
      
      const config = presetConfig[presetType] || {}
      
      placedElements.value.push({
        id: generateId(),
        type: 'preset',
        presetType,
        label: presetLabels[presetType] || '预设元素',
        x: Math.round(x),
        y: Math.round(y),
        width: config.width || 150,
        height: config.height || 30,
        fontSize: config.fontSize || '12px',
        fontWeight: config.fontWeight || 'normal',
        fontFamily: '',
        textAlign: config.textAlign || 'left',
        showBorder: false
      })
    }
    
    saveLayout()
  }
  
  const onCanvasClick = () => {
    selectedElementId.value = null
  }
  
  const selectElement = (element) => {
    selectedElementId.value = element.id
  }
  
  const deleteElement = (element) => {
    const index = placedElements.value.findIndex(el => el.id === element.id)
    if (index > -1) {
      placedElements.value.splice(index, 1)
      selectedElementId.value = null
      saveLayout()
    }
  }
  
  const updateElement = () => {
    const index = placedElements.value.findIndex(el => el.id === selectedElementId.value)
    if (index > -1) {
      const element = placedElements.value[index]
      placedElements.value[index] = { ...element }
    }
    saveLayout()
  }
  
  const saveLayout = () => {
    localStorage.setItem('deliveryPrintLayout', JSON.stringify(placedElements.value))
  }
  
  const loadLayout = () => {
    const saved = localStorage.getItem('deliveryPrintLayout')
    if (saved) {
      try {
        const elements = JSON.parse(saved)
        placedElements.value = elements.map(el => ({
          ...el,
          fontFamily: el.fontFamily || ''
        }))
      } catch (e) {
        error('加载布局失败:', e)
        return false
      }
    }
    return true
  }
  
  const adjustElementsForPaper = () => {
    placedElements.value.forEach(el => {
      if (el.x + el.width > canvasWidthPx.value) {
        el.x = canvasWidthPx.value - el.width - 20
      }
      if (el.y + el.height > canvasHeightPx.value) {
        el.y = canvasHeightPx.value - el.height - 20
      }
      if (el.x < 0) el.x = 20
      if (el.y < 0) el.y = 20
    })
    saveLayout()
  }
  
  const alignElement = (alignment) => {
    if (!selectedElement.value) return
    
    const el = selectedElement.value
    const marginPx = Math.round(printSettings.marginLeft * MM_TO_PX)
    
    switch (alignment) {
      case 'left':
        el.x = marginPx
        break
      case 'centerH':
        el.x = Math.round((canvasWidthPx.value - el.width) / 2)
        break
      case 'right':
        el.x = canvasWidthPx.value - el.width - marginPx
        break
      case 'top':
        el.y = Math.round(printSettings.marginTop * MM_TO_PX)
        break
      case 'centerV':
        el.y = Math.round((canvasHeightPx.value - el.height) / 2)
        break
      case 'bottom':
        el.y = canvasHeightPx.value - el.height - Math.round(printSettings.marginBottom * MM_TO_PX)
        break
    }
    
    saveLayout()
  }
  
  const getElementStyle = (element) => {
    const style = {
      left: `${element.x}px`,
      top: `${element.y}px`,
      width: `${element.width}px`,
      fontSize: element.fontSize,
      fontWeight: element.fontWeight,
      fontFamily: element.fontFamily || '',
      textAlign: element.textAlign,
      border: element.showBorder ? '1px solid #333' : 'none',
      boxSizing: 'border-box'
    }
    
    if (element.type === 'preset' && element.presetType === 'table') {
      style.height = 'auto'
      style.minHeight = `${element.height}px`
    } else {
      style.height = 'auto'
      style.minHeight = `${element.height}px`
    }
    
    return style
  }
  
  return {
    selectedElementId,
    placedElements,
    mainFieldDefinitions,
    detailFieldDefinitions,
    companyFieldDefinitions,
    selectedElement,
    availableMainFields,
    availableDetailFields,
    tableColumns,
    generateId,
    onPaletteDragStart,
    onPresetDragStart,
    onCanvasDragOver,
    onCanvasDrop,
    onCanvasClick,
    selectElement,
    deleteElement,
    updateElement,
    saveLayout,
    loadLayout,
    adjustElementsForPaper,
    alignElement,
    getElementStyle
  }
}

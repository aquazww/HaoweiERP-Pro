/**
 * 打印设置组合式函数
 * 管理打印相关的所有设置项
 */
import { ref, reactive, computed, watch, onMounted } from 'vue'
import { ElMessage } from 'element-plus'

export function usePrintSettings() {
  const showGrid = ref(true)
  const zoom = ref(100)
  
  const printSettings = reactive({
    paperSize: 'A4Half',
    paperDivision: 'full',
    copyCount: 3,
    orientation: 'portrait',
    scale: 100,
    marginTop: 10,
    marginBottom: 10,
    marginLeft: 10,
    marginRight: 10,
    showPrice: true,
    showAmount: true,
    showPageNumbers: true,
    showDate: true,
    tableFixedRows: 10,
    tableOverflowMode: 'scroll',
    dotMatrixMode: true,
    printQuality: 'normal',
    paperFeed: 'auto',
    showCopyTitle: true,
    copyNames: ['存根联', '客户联', '记账联', '送货联', '财务联']
  })
  
  const paperSizes = {
    A4: { width: 210, height: 297, label: 'A4标准' },
    A4Half: { width: 210, height: 148.5, label: 'A4二等分' },
    A4Third: { width: 210, height: 99, label: 'A4三等分' },
    A4Quarter: { width: 210, height: 74.25, label: 'A4四等分' },
    A5: { width: 148, height: 210, label: 'A5标准' },
    A5Half: { width: 148, height: 105, label: 'A5二等分' },
    Thermal80: { width: 80, height: 210, label: '热敏纸80mm' },
    Thermal110: { width: 110, height: 210, label: '热敏纸110mm' },
    Custom: { width: 210, height: 140, label: '自定义' }
  }
  
  const copyOptions = [
    { value: 2, label: '2联单（存根+客户）' },
    { value: 3, label: '3联单（存根+客户+记账）' },
    { value: 4, label: '4联单（存根+客户+记账+送货）' },
    { value: 5, label: '5联单（存根+客户+记账+送货+财务）' }
  ]
  
  const MM_TO_PX = 3.7795275591
  
  const canvasWidth = computed(() => {
    const size = paperSizes[printSettings.paperSize]
    return printSettings.orientation === 'landscape' ? size.height : size.width
  })
  
  const canvasHeight = computed(() => {
    const size = paperSizes[printSettings.paperSize]
    return printSettings.orientation === 'landscape' ? size.width : size.height
  })
  
  const canvasWidthPx = computed(() => Math.round(canvasWidth.value * MM_TO_PX))
  const canvasHeightPx = computed(() => Math.round(canvasHeight.value * MM_TO_PX))
  
  const canvasStyle = computed(() => ({
    width: `${canvasWidthPx.value}px`,
    height: `${canvasHeightPx.value}px`,
    transform: `scale(${zoom.value / 100})`,
    transformOrigin: 'top center'
  }))
  
  const zoomIn = () => {
    zoom.value = Math.min(200, zoom.value + 10)
  }
  
  const zoomOut = () => {
    zoom.value = Math.max(30, zoom.value - 10)
  }
  
  const resetZoom = () => {
    zoom.value = 100
  }
  
  const toggleGrid = () => {
    showGrid.value = !showGrid.value
  }
  
  const handlePaperChange = () => {
    handleSettingsChange()
  }
  
  const handleSettingsChange = () => {
    localStorage.setItem('advancedPrintSettings', JSON.stringify(printSettings))
  }
  
  const loadSettings = () => {
    const savedSettings = localStorage.getItem('advancedPrintSettings')
    if (savedSettings) {
      try {
        Object.assign(printSettings, JSON.parse(savedSettings))
      } catch (e) {
        console.error('加载打印设置失败:', e)
      }
    }
  }
  
  onMounted(() => {
    loadSettings()
  })
  
  return {
    showGrid,
    zoom,
    printSettings,
    paperSizes,
    copyOptions,
    MM_TO_PX,
    canvasWidth,
    canvasHeight,
    canvasWidthPx,
    canvasHeightPx,
    canvasStyle,
    zoomIn,
    zoomOut,
    resetZoom,
    toggleGrid,
    handlePaperChange,
    handleSettingsChange,
    loadSettings
  }
}

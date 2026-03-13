<template>
  <el-dialog
    title="送货单打印设计器"
    v-model="dialogVisible"
    width="98%"
    :before-close="handleClose"
    top="1vh"
    destroy-on-close
    class="advanced-print-dialog"
  >
    <div class="advanced-print-container">
      <!-- 左侧工具栏 -->
      <PrintToolbar
        :available-main-fields="availableMainFields"
        :available-detail-fields="availableDetailFields"
        @palette-drag-start="onPaletteDragStart"
        @preset-drag-start="onPresetDragStart"
      />

      <!-- 中间设计区域 -->
      <div class="design-panel">
        <div class="design-canvas-wrapper" ref="canvasWrapper">
          <div
            class="design-canvas"
            ref="designCanvas"
            :style="canvasStyle"
            @dragover.prevent="onCanvasDragOver"
            @drop="onCanvasDrop"
            @click="onCanvasClick"
          >
            <div v-if="showGrid" class="grid-overlay"></div>
            
            <div
              v-for="element in placedElements"
              :key="element.id"
              class="placed-element"
              :class="{ 
                selected: selectedElementId === element.id,
                'is-field': element.type === 'field',
                'is-preset': element.type === 'preset'
              }"
              :style="getElementStyle(element)"
              @mousedown="onElementMouseDown($event, element)"
              @click.stop="selectElement(element)"
            >
              <template v-if="element.type === 'field'">
                <span class="element-label">{{ element.label }}：</span>
                <span class="element-value">{{ getFieldValue(element.key, element) }}</span>
              </template>
              <template v-else-if="element.type === 'preset'">
                <div v-if="element.presetType === 'title'" class="preset-title">送 货 单</div>
                <div v-else-if="element.presetType === 'qrCode'" class="preset-qrcode">
                  <QrcodeVue :value="deliveryData.order_no || 'QR'" :size="Math.min(element.width, element.height) * 0.7" level="M" />
                </div>
                <div v-else-if="element.presetType === 'companyName'" class="preset-company-name">
                  {{ companyInfo.name || '公司名称' }}
                </div>
                <div v-else-if="element.presetType === 'table'" class="preset-table">
                  <table>
                    <thead>
                      <tr>
                        <th>序号</th>
                        <th v-for="col in tableColumns" :key="col.key">{{ col.label }}</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr v-for="(row, idx) in getTableDisplayRows(element)" :key="idx">
                        <td>{{ row.isEmpty ? '' : row.index }}</td>
                        <td v-for="col in tableColumns" :key="col.key">
                          {{ row.isEmpty ? '' : getItemFieldValue(row.data, col.key) }}
                        </td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </template>
              
              <div v-if="selectedElementId === element.id" class="resize-handles">
                <div class="resize-handle nw" @mousedown.stop="startResize($event, element, 'nw')"></div>
                <div class="resize-handle ne" @mousedown.stop="startResize($event, element, 'ne')"></div>
                <div class="resize-handle sw" @mousedown.stop="startResize($event, element, 'sw')"></div>
                <div class="resize-handle se" @mousedown.stop="startResize($event, element, 'se')"></div>
              </div>
              
              <el-button
                v-if="selectedElementId === element.id"
                class="delete-btn"
                type="danger"
                size="small"
                circle
                :icon="Close"
                @click.stop="deleteElement(element)"
              />
            </div>
          </div>
        </div>
      </div>

      <!-- 右侧属性面板 -->
      <PrintPropertiesPanel
        :selected-element="selectedElement"
        :print-settings="printSettings"
        :paper-sizes="paperSizes"
        :copy-options="copyOptions"
        :canvas-width="canvasWidth"
        :canvas-height="canvasHeight"
        :canvas-width-px="canvasWidthPx"
        :canvas-height-px="canvasHeightPx"
        :zoom="zoom"
        :show-grid="showGrid"
        :templates="templates"
        :main-field-definitions="mainFieldDefinitions"
        :company-field-definitions="companyFieldDefinitions"
        :has-table-overflow="hasTableOverflow"
        :items-count="deliveryData.items.length"
        @update-element="updateElement"
        @align-element="alignElement"
        @zoom-in="zoomIn"
        @zoom-out="zoomOut"
        @reset-zoom="resetZoom"
        @auto-arrange="autoArrangeLayout"
        @paper-change="handlePaperChange"
        @settings-change="handleSettingsChange"
        @save-template="saveAsTemplate"
        @load-template="handleLoadTemplate"
        @delete-template="deleteTemplate"
        @insert-field="insertField"
      />
    </div>

    <template #footer>
      <div class="dialog-footer">
        <el-button @click="resetLayout" :icon="RefreshRight">重置布局</el-button>
        <el-button @click="handleClose">取消</el-button>
        <el-button type="warning" @click="exportPDF" :loading="exporting" :icon="Download">导出PDF</el-button>
        <el-button type="primary" @click="handlePrint" :loading="printing" :icon="Printer">打印</el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Close, Printer, RefreshRight, Download } from '@element-plus/icons-vue'
import QrcodeVue from 'qrcode.vue'

import PrintToolbar from './PrintToolbar.vue'
import PrintPropertiesPanel from './PrintPropertiesPanel.vue'
import { exportToPDF } from './printUtils'

import {
  usePrintSettings,
  usePrintElements,
  useElementDrag,
  usePrintTemplates,
  usePrintData,
  usePrintGenerator
} from '../../composables'

const props = defineProps({
  modelValue: { type: Boolean, default: false },
  stockOutData: { type: Object, default: null }
})

const emit = defineEmits(['update:modelValue'])

const dialogVisible = ref(props.modelValue)
const designCanvas = ref(null)
const canvasWrapper = ref(null)
const printing = ref(false)
const exporting = ref(false)

const {
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
  handlePaperChange,
  handleSettingsChange
} = usePrintSettings()

const {
  selectedElementId,
  placedElements,
  mainFieldDefinitions,
  detailFieldDefinitions,
  companyFieldDefinitions,
  selectedElement,
  availableMainFields,
  availableDetailFields,
  tableColumns,
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
  alignElement,
  getElementStyle
} = usePrintElements(printSettings, canvasWidthPx, canvasHeightPx, MM_TO_PX)

const { onElementMouseDown, startResize } = useElementDrag(zoom, saveLayout)

const {
  templates,
  saveAsTemplate,
  loadTemplate,
  deleteTemplate
} = usePrintTemplates(placedElements, printSettings, canvasWidth, canvasHeight)

const {
  companyInfo,
  deliveryData,
  initDeliveryData,
  loadCompanyInfo,
  getFieldValue,
  getItemFieldValue,
  getCircleNumber,
  getCopyName,
  getCopyColor
} = usePrintData()

const hasTableOverflow = ref(false)

const getTableDisplayRows = (element) => {
  const fixedRows = printSettings.tableFixedRows
  const items = deliveryData.value.items
  const rows = []
  
  for (let i = 0; i < fixedRows; i++) {
    if (i < items.length) {
      rows.push({ index: i + 1, data: items[i], isEmpty: false })
    } else {
      rows.push({ index: i + 1, data: {}, isEmpty: true })
    }
  }
  
  hasTableOverflow.value = items.length > fixedRows
  return rows
}

const { generatePrintHTML } = usePrintGenerator(
  placedElements,
  printSettings,
  canvasWidth,
  canvasHeight,
  companyInfo,
  deliveryData,
  tableColumns,
  MM_TO_PX,
  hasTableOverflow,
  getCircleNumber,
  getCopyName,
  getCopyColor,
  getItemFieldValue
)

const initDefaultLayout = () => {
  const marginPx = Math.round(10 * MM_TO_PX)
  
  placedElements.value = [
    {
      id: `el_${Date.now()}_1`,
      type: 'preset',
      presetType: 'title',
      label: '标题',
      x: Math.round((canvasWidthPx.value - 300) / 2),
      y: marginPx,
      width: 300,
      height: 50,
      fontSize: '28px',
      fontWeight: 'bold',
      textAlign: 'center',
      showBorder: false
    },
    {
      id: `el_${Date.now()}_table`,
      type: 'preset',
      presetType: 'table',
      label: '明细表格',
      x: marginPx,
      y: marginPx + 150,
      width: canvasWidthPx.value - marginPx * 2,
      height: 180,
      fontSize: '11px',
      fontWeight: 'normal',
      textAlign: 'left',
      showBorder: false
    }
  ]
  
  saveLayout()
}

const autoArrangeLayout = async () => {
  try {
    await ElMessageBox.confirm('自动排版将重新排列所有元素，当前布局将被覆盖。是否继续？', '提示', {
      type: 'warning',
      confirmButtonText: '确定',
      cancelButtonText: '取消'
    })
    initDefaultLayout()
    ElMessage.success('自动排版完成')
  } catch {
    // 用户取消操作，无需处理
  }
}

const resetLayout = async () => {
  try {
    await ElMessageBox.confirm('确定要重置为默认布局吗？当前布局将被清除。', '提示', {
      type: 'warning'
    })
    placedElements.value = []
    initDefaultLayout()
    ElMessage.success('布局已重置')
  } catch {
    // 用户取消操作，无需处理
  }
}

const handleLoadTemplate = async (template) => {
  const success = await loadTemplate(template)
  if (success) {
    selectedElementId.value = null
  }
}

const insertField = (field) => {
  if (!selectedElement.value) return
  selectedElement.value.content = `{${field.key}}`
  updateElement()
}

const handlePrint = async () => {
  if (printing.value) return
  printing.value = true
  
  try {
    const html = await generatePrintHTML()
    const printWindow = window.open('', '_blank')
    
    if (!printWindow) {
      ElMessage.error('无法打开打印窗口')
      return
    }
    
    printWindow.document.write(html)
    printWindow.document.close()
    printWindow.focus()
    
    await new Promise(resolve => setTimeout(resolve, 300))
    printWindow.print()
    printWindow.onafterprint = () => printWindow.close()
  } catch (error) {
    ElMessage.error('打印失败')
  } finally {
    printing.value = false
  }
}

const exportPDF = async () => {
  if (exporting.value) return
  exporting.value = true
  
  try {
    const html = await generatePrintHTML()
    await exportToPDF(html, `送货单-${deliveryData.value.order_no}`)
    ElMessage.success('PDF导出成功')
  } catch (error) {
    ElMessage.error('导出PDF失败')
  } finally {
    exporting.value = false
  }
}

const handleClose = () => {
  dialogVisible.value = false
}

watch(() => props.modelValue, (val) => {
  dialogVisible.value = val
  if (val) {
    if (!loadLayout()) {
      initDefaultLayout()
    }
    loadTemplates()
    loadCompanyInfo()
    initDeliveryData(props.stockOutData)
    selectedElementId.value = null
  }
})

watch(dialogVisible, (val) => {
  emit('update:modelValue', val)
})
</script>

<style scoped>
.advanced-print-dialog :deep(.el-dialog__body) {
  padding: 10px;
  height: calc(90vh - 120px);
  overflow: hidden;
}

.advanced-print-container {
  display: flex;
  height: 100%;
  gap: 10px;
}

.design-panel {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.design-canvas-wrapper {
  flex: 1;
  overflow: auto;
  background: #e0e0e0;
  border-radius: 8px;
  padding: 20px;
  display: flex;
  justify-content: center;
  align-items: flex-start;
}

.design-canvas {
  position: relative;
  background: #fff;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
  transition: transform 0.15s ease-out;
}

.grid-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-image: 
    linear-gradient(rgba(0, 0, 0, 0.06) 1px, transparent 1px),
    linear-gradient(90deg, rgba(0, 0, 0, 0.06) 1px, transparent 1px);
  background-size: 20px 20px;
  pointer-events: none;
  z-index: 1;
}

.placed-element {
  position: absolute;
  cursor: move;
  user-select: none;
  display: flex;
  align-items: center;
  padding: 2px 4px;
  transition: box-shadow 0.15s;
  z-index: 10;
  box-sizing: border-box;
}

.placed-element:hover {
  box-shadow: 0 0 0 1px #409eff;
}

.placed-element.selected {
  box-shadow: 0 0 0 2px #409eff, 0 2px 8px rgba(64, 158, 255, 0.3);
  z-index: 20;
}

.element-label {
  font-weight: bold;
  white-space: nowrap;
  color: #303133;
}

.element-value {
  white-space: nowrap;
  color: #606266;
}

.preset-title {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  border-bottom: 2px solid #000;
}

.preset-company-name {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #333;
  font-weight: bold;
}

.preset-table table {
  width: 100%;
  border-collapse: collapse;
  table-layout: fixed;
}

.preset-table th,
.preset-table td {
  border: 1px solid #000;
  padding: 3px 5px;
  text-align: center;
}

.resize-handles {
  position: absolute;
  top: -4px;
  left: -4px;
  right: -4px;
  bottom: -4px;
  pointer-events: none;
}

.resize-handle {
  position: absolute;
  width: 10px;
  height: 10px;
  background: #409eff;
  border: 2px solid #fff;
  border-radius: 2px;
  pointer-events: auto;
}

.resize-handle.nw { top: 0; left: 0; cursor: nw-resize; }
.resize-handle.ne { top: 0; right: 0; cursor: ne-resize; }
.resize-handle.sw { bottom: 0; left: 0; cursor: sw-resize; }
.resize-handle.se { bottom: 0; right: 0; cursor: se-resize; }

.delete-btn {
  position: absolute;
  top: -12px;
  right: -12px;
  width: 22px;
  height: 22px;
  padding: 0;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}
</style>

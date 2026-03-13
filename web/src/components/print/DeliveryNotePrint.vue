<template>
  <el-dialog
    title="送货单打印"
    v-model="dialogVisible"
    width="95%"
    :before-close="handleClose"
    top="3vh"
    destroy-on-close
  >
    <div class="delivery-print-container">
      <!-- 配置面板 -->
      <div class="config-panel">
        <el-tabs v-model="activeTab" type="border-card">
          <!-- 字段配置 -->
          <el-tab-pane label="字段配置" name="fields">
            <div class="field-config">
              <div class="field-section">
                <h4>主单字段</h4>
                <div class="field-list">
                  <div
                    v-for="(field, index) in mainFields"
                    :key="field.key"
                    class="field-item"
                    draggable="true"
                    @dragstart="onDragStart($event, index, 'main')"
                    @dragover.prevent
                    @drop="onDrop($event, index, 'main')"
                  >
                    <el-checkbox v-model="field.visible" @change="handleFieldChange">
                      {{ field.label }}
                    </el-checkbox>
                    <el-icon class="drag-handle"><Rank /></el-icon>
                  </div>
                </div>
              </div>
              <div class="field-section">
                <h4>明细字段</h4>
                <div class="field-list">
                  <div
                    v-for="(field, index) in detailFields"
                    :key="field.key"
                    class="field-item"
                    draggable="true"
                    @dragstart="onDragStart($event, index, 'detail')"
                    @dragover.prevent
                    @drop="onDrop($event, index, 'detail')"
                  >
                    <el-checkbox v-model="field.visible" @change="handleFieldChange">
                      {{ field.label }}
                    </el-checkbox>
                    <el-icon class="drag-handle"><Rank /></el-icon>
                  </div>
                </div>
              </div>
              <div class="config-actions">
                <el-button type="default" size="small" @click="resetSettings">
                  恢复默认
                </el-button>
              </div>
            </div>
          </el-tab-pane>

          <!-- 打印设置 -->
          <el-tab-pane label="打印设置" name="settings">
            <div class="print-settings">
              <el-form :model="printSettings" label-width="80px" size="small">
                <el-row :gutter="12">
                  <el-col :span="12">
                    <el-form-item label="纸张大小">
                      <el-select v-model="printSettings.paperSize" @change="handleSettingsChange">
                        <el-option label="A4" value="A4" />
                        <el-option label="A5" value="A5" />
                      </el-select>
                    </el-form-item>
                  </el-col>
                  <el-col :span="12">
                    <el-form-item label="字体大小">
                      <el-select v-model="printSettings.fontSize" @change="handleSettingsChange">
                        <el-option label="小 (10px)" value="10px" />
                        <el-option label="中 (12px)" value="12px" />
                        <el-option label="大 (14px)" value="14px" />
                      </el-select>
                    </el-form-item>
                  </el-col>
                </el-row>
                <el-row :gutter="12">
                  <el-col :span="12">
                    <el-form-item label="显示单价">
                      <el-switch v-model="printSettings.showPrice" @change="handleSettingsChange" />
                    </el-form-item>
                  </el-col>
                  <el-col :span="12">
                    <el-form-item label="显示金额">
                      <el-switch v-model="printSettings.showAmount" @change="handleSettingsChange" />
                    </el-form-item>
                  </el-col>
                </el-row>
                <el-row :gutter="12">
                  <el-col :span="12">
                    <el-form-item label="显示页码">
                      <el-switch v-model="printSettings.showPageNumbers" @change="handleSettingsChange" />
                    </el-form-item>
                  </el-col>
                  <el-col :span="12">
                    <el-form-item label="显示日期">
                      <el-switch v-model="printSettings.showDate" @change="handleSettingsChange" />
                    </el-form-item>
                  </el-col>
                </el-row>
                <el-form-item label="页眉">
                  <el-input v-model="printSettings.header" placeholder="输入页眉内容" @change="handleSettingsChange" size="small" />
                </el-form-item>
                <el-form-item label="页脚">
                  <el-input v-model="printSettings.footer" placeholder="输入页脚内容" @change="handleSettingsChange" size="small" />
                </el-form-item>
              </el-form>
            </div>
          </el-tab-pane>
        </el-tabs>
      </div>

      <!-- 打印预览 -->
      <div class="preview-panel">
        <div class="preview-header">
          <span class="preview-title">打印预览</span>
          <div class="preview-actions">
            <el-button type="default" size="default" @click="handleClose">取消</el-button>
            <el-button type="warning" size="default" @click="exportPDF" :loading="exporting">导出PDF</el-button>
            <el-button type="primary" size="default" @click="handlePrint" :loading="printing">打印</el-button>
          </div>
        </div>
        <div class="preview-content" ref="previewContent">
          <div class="print-page" :style="pageStyle">
            <!-- 送货单头部 -->
            <div class="delivery-header">
              <h1>送 货 单</h1>
              <div class="company-info">豪威工贸有限公司</div>
            </div>

            <!-- 订单基本信息 -->
            <div class="order-info">
              <div v-for="(row, rowIndex) in mainInfoRows" :key="rowIndex" class="info-row">
                <div v-for="field in row" :key="field.key" class="info-item" :class="{ 'full-width': field.fullWidth }">
                  <span class="label">{{ field.label }}：</span>
                  <span class="value">{{ getFieldValue(field.key) }}</span>
                </div>
              </div>
            </div>

            <!-- 商品明细表格 -->
            <div class="goods-table">
              <table>
                <thead>
                  <tr>
                    <th style="width: 40px">序号</th>
                    <th v-for="field in visibleDetailFields" :key="field.key" :style="{ width: field.width + 'px' }">
                      {{ field.label }}
                    </th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(item, index) in deliveryData.items" :key="index">
                    <td class="center">{{ index + 1 }}</td>
                    <td v-for="field in visibleDetailFields" :key="field.key" :class="getFieldAlign(field.key)">
                      {{ getItemFieldValue(item, field.key) }}
                    </td>
                  </tr>
                </tbody>
                <tfoot v-if="printSettings.showAmount">
                  <tr>
                    <td :colspan="footerColspan" class="right bold">合计金额：</td>
                    <td class="right bold">¥{{ formatAmount(deliveryData.total_amount) }}</td>
                  </tr>
                </tfoot>
              </table>
            </div>

            <!-- 签收区域 -->
            <div class="signature-area">
              <div class="signature-item">
                <span class="label">送货人：</span>
                <span class="line">________________</span>
              </div>
              <div class="signature-item">
                <span class="label">收货人：</span>
                <span class="line">________________</span>
              </div>
              <div class="signature-item">
                <span class="label">收货日期：</span>
                <span class="line">____年____月____日</span>
              </div>
            </div>

            <!-- 页脚 -->
            <div class="page-footer">
              <span v-if="printSettings.showDate">打印日期：{{ currentDate }}</span>
              <span v-if="printSettings.showPageNumbers">第 1 页</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </el-dialog>
</template>

<script setup>
import { ref, reactive, computed, watch, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Rank } from '@element-plus/icons-vue'
import { exportToPDF } from './printUtils'
import {
  getDeliveryNoteFields,
  saveDeliveryNoteFields,
  getPrintSettings,
  savePrintSettings,
  resetDeliveryNoteFields,
  resetPrintSettings
} from './printTemplates'

const props = defineProps({
  modelValue: { type: Boolean, default: false },
  stockOutData: { type: Object, default: null }
})

const emit = defineEmits(['update:modelValue'])

const dialogVisible = ref(props.modelValue)
const activeTab = ref('fields')
const previewContent = ref(null)
const printing = ref(false)
const exporting = ref(false)

const mainFields = ref([])
const detailFields = ref([])

const printSettings = reactive({
  paperSize: 'A4',
  fontSize: '12px',
  showPrice: true,
  showAmount: true,
  showPageNumbers: true,
  showDate: true,
  header: '送货单',
  footer: ''
})

const deliveryData = ref({
  order_no: '',
  sale_order_no: '',
  customer_name: '',
  customer_contact: '',
  customer_phone: '',
  customer_address: '',
  warehouse_name: '',
  delivery_date: '',
  total_amount: 0,
  remark: '',
  items: []
})

const currentDate = computed(() => new Date().toLocaleDateString('zh-CN'))

const pageStyle = computed(() => {
  const paperSizes = {
    A4: { width: '210mm', minHeight: '297mm' },
    A5: { width: '148mm', minHeight: '210mm' }
  }
  const size = paperSizes[printSettings.paperSize] || paperSizes.A4
  return {
    width: size.width,
    minHeight: size.minHeight,
    padding: '15mm',
    background: '#fff',
    fontSize: printSettings.fontSize,
    position: 'relative'
  }
})

const visibleMainFields = computed(() => mainFields.value.filter(f => f.visible))
const visibleDetailFields = computed(() => detailFields.value.filter(f => f.visible))

const mainInfoRows = computed(() => {
  const fields = visibleMainFields.value
  const rows = []
  for (let i = 0; i < fields.length; i += 3) {
    const row = fields.slice(i, i + 3)
    if (row.length === 1) row[0].fullWidth = true
    rows.push(row)
  }
  return rows
})

const footerColspan = computed(() => {
  let count = 1
  count += visibleDetailFields.value.filter(f => !['price', 'amount'].includes(f.key)).length
  if (printSettings.showPrice) count++
  return count
})

const draggedIndex = ref(-1)
const draggedType = ref('')

const formatAmount = (amount) => {
  if (!amount) return '0.00'
  return Number(amount).toFixed(2)
}

const getFieldValue = (key) => {
  const value = deliveryData.value[key]
  return value !== null && value !== undefined && value !== '' ? value : '-'
}

const getItemFieldValue = (item, key) => {
  const value = item[key]
  if (['price', 'amount'].includes(key)) {
    return formatAmount(value)
  }
  return value !== null && value !== undefined && value !== '' ? value : '-'
}

const getFieldAlign = (key) => {
  if (['quantity', 'price', 'amount'].includes(key)) return 'right'
  if (['unit_name', 'unit'].includes(key)) return 'center'
  return 'left'
}

watch(() => props.modelValue, (val) => {
  dialogVisible.value = val
  if (val) {
    loadConfig()
    initDeliveryData()
  }
})

watch(dialogVisible, (val) => {
  emit('update:modelValue', val)
})

const loadConfig = () => {
  const fieldsConfig = getDeliveryNoteFields()
  mainFields.value = JSON.parse(JSON.stringify(fieldsConfig.mainFields))
  detailFields.value = JSON.parse(JSON.stringify(fieldsConfig.detailFields))
  
  const settings = getPrintSettings()
  Object.assign(printSettings, settings)
}

const initDeliveryData = () => {
  if (!props.stockOutData) return
  const data = props.stockOutData
  deliveryData.value = {
    order_no: data.order_no || '',
    sale_order_no: data.sale_order_no || '',
    customer_name: data.sale_order?.customer_name || data.customer_name || '',
    customer_contact: data.sale_order?.customer_contact || data.customer_contact || '',
    customer_phone: data.sale_order?.customer_phone || data.customer_phone || '',
    customer_address: data.sale_order?.customer_address || data.customer_address || '',
    warehouse_name: data.warehouse_name || '',
    delivery_date: data.created_at ? data.created_at.split('T')[0] : new Date().toISOString().split('T')[0],
    total_amount: data.total_amount || 0,
    remark: data.remark || '',
    items: (data.items || []).map(item => ({
      goods_code: item.goods_code || '',
      goods_name: item.goods_name || '',
      goods_spec: item.goods_spec || '',
      unit_name: item.unit_name || item.unit || '',
      quantity: item.quantity || 0,
      price: item.price || 0,
      amount: item.amount || 0,
      remark: item.remark || ''
    }))
  }
}

const onDragStart = (event, index, type) => {
  draggedIndex.value = index
  draggedType.value = type
  event.dataTransfer.effectAllowed = 'move'
}

const onDrop = (event, index, type) => {
  event.preventDefault()
  if (draggedType.value !== type || draggedIndex.value === index) return
  
  const fields = type === 'main' ? mainFields.value : detailFields.value
  const draggedField = fields.splice(draggedIndex.value, 1)[0]
  fields.splice(index, 0, draggedField)
  
  handleFieldChange()
  draggedIndex.value = -1
}

const handleFieldChange = () => {
  saveDeliveryNoteFields({
    mainFields: mainFields.value,
    detailFields: detailFields.value
  })
}

const handleSettingsChange = () => {
  savePrintSettings(printSettings)
}

const resetSettings = () => {
  const defaultFields = resetDeliveryNoteFields()
  mainFields.value = JSON.parse(JSON.stringify(defaultFields.mainFields))
  detailFields.value = JSON.parse(JSON.stringify(defaultFields.detailFields))
  
  const defaultSettings = resetPrintSettings()
  Object.assign(printSettings, defaultSettings)
  
  ElMessage.success('已恢复默认设置')
}

const handlePrint = async () => {
  if (printing.value) return
  printing.value = true
  
  try {
    const content = previewContent.value.innerHTML
    const printWindow = window.open('', '_blank')
    
    if (!printWindow) {
      ElMessage.error('无法打开打印窗口，请检查浏览器的弹出窗口阻止设置')
      return
    }
    
    printWindow.document.write(generatePrintHTML(content))
    printWindow.document.close()
    printWindow.focus()
    
    await new Promise(resolve => setTimeout(resolve, 100))
    printWindow.print()
    printWindow.onafterprint = () => printWindow.close()
  } catch (error) {
    console.error('打印失败:', error)
    ElMessage.error('打印失败，请重试')
  } finally {
    printing.value = false
  }
}

const exportPDF = async () => {
  if (exporting.value) return
  exporting.value = true
  
  try {
    const content = previewContent.value.innerHTML
    const html = generatePrintHTML(content)
    exportToPDF(html, `送货单-${deliveryData.value.order_no}`)
  } catch (error) {
    console.error('导出PDF失败:', error)
    ElMessage.error('导出PDF失败，请重试')
  } finally {
    exporting.value = false
  }
}

const generatePrintHTML = (content) => {
  return `
    <html>
    <head>
      <title>送货单 - ${deliveryData.value.order_no}</title>
      <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
          font-family: 'Microsoft YaHei', Arial, sans-serif;
          font-size: ${printSettings.fontSize};
          line-height: 1.6;
        }
        .print-page {
          width: 210mm;
          min-height: 297mm;
          padding: 15mm;
          margin: 0 auto;
          background: #fff;
        }
        .delivery-header {
          text-align: center;
          margin-bottom: 20px;
          padding-bottom: 10px;
          border-bottom: 2px solid #000;
        }
        .delivery-header h1 {
          font-size: 24px;
          font-weight: bold;
          margin-bottom: 5px;
        }
        .company-info { font-size: 14px; color: #666; }
        .order-info { margin-bottom: 15px; }
        .info-row {
          display: flex;
          margin-bottom: 8px;
        }
        .info-item {
          flex: 1;
          display: flex;
        }
        .info-item.full-width { flex: 3; }
        .info-item .label {
          font-weight: bold;
          min-width: 70px;
        }
        .info-item .value { flex: 1; }
        .goods-table { margin-bottom: 20px; }
        .goods-table table {
          width: 100%;
          border-collapse: collapse;
        }
        .goods-table th,
        .goods-table td {
          border: 1px solid #000;
          padding: 6px 8px;
          font-size: ${printSettings.fontSize};
        }
        .goods-table th {
          background-color: #f5f5f5;
          font-weight: bold;
          text-align: center;
        }
        .goods-table .center { text-align: center; }
        .goods-table .right { text-align: right; }
        .goods-table .left { text-align: left; }
        .goods-table .bold { font-weight: bold; }
        .signature-area {
          display: flex;
          justify-content: space-between;
          margin-top: 40px;
          padding-top: 20px;
        }
        .signature-item {
          display: flex;
          align-items: center;
        }
        .signature-item .label {
          font-weight: bold;
          margin-right: 10px;
        }
        .signature-item .line {
          display: inline-block;
          width: 150px;
        }
        .page-footer {
          position: absolute;
          bottom: 10mm;
          left: 15mm;
          right: 15mm;
          display: flex;
          justify-content: space-between;
          font-size: 11px;
          color: #999;
        }
        @media print {
          body { margin: 0; padding: 0; }
          .print-page { margin: 0; padding: 15mm; }
        }
      </style>
    </head>
    <body>${content}</body>
    </html>
  `
}

const handleClose = () => {
  dialogVisible.value = false
}

onUnmounted(() => {
  draggedIndex.value = -1
  draggedType.value = ''
})
</script>

<style scoped>
.delivery-print-container {
  display: flex;
  gap: 12px;
  height: 80vh;
}

.config-panel {
  width: 360px;
  flex-shrink: 0;
  overflow: hidden;
}

.config-panel :deep(.el-tabs__content) {
  padding: 12px;
  max-height: calc(80vh - 90px);
  overflow-y: auto;
}

.field-config {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.field-section h4 {
  margin: 0 0 8px 0;
  font-size: 14px;
  color: #303133;
  font-weight: 600;
}

.field-list {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.field-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 6px 10px;
  background: #f5f7fa;
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  cursor: move;
  transition: all 0.2s;
}

.field-item:hover {
  background: #ecf5ff;
  border-color: #409eff;
}

.drag-handle {
  color: #909399;
  cursor: move;
  font-size: 14px;
}

.config-actions {
  display: flex;
  justify-content: flex-start;
  padding-top: 8px;
  border-top: 1px solid #e4e7ed;
}

.print-settings {
  padding: 0;
}

.preview-panel {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.preview-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 14px;
  background: #f5f7fa;
  border-radius: 4px 4px 0 0;
  border: 1px solid #e4e7ed;
  border-bottom: none;
}

.preview-title {
  font-size: 15px;
  font-weight: 600;
  color: #303133;
}

.preview-actions {
  display: flex;
  gap: 8px;
}

.preview-content {
  flex: 1;
  overflow: auto;
  background: #f0f2f5;
  padding: 16px;
  border: 1px solid #e4e7ed;
  border-radius: 0 0 4px 4px;
  display: flex;
  justify-content: center;
}

.print-page {
  background: #fff;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.delivery-header {
  text-align: center;
  margin-bottom: 20px;
  padding-bottom: 10px;
  border-bottom: 2px solid #000;
}

.delivery-header h1 {
  font-size: 24px;
  font-weight: bold;
  margin-bottom: 5px;
}

.company-info {
  font-size: 14px;
  color: #666;
}

.order-info {
  margin-bottom: 15px;
}

.info-row {
  display: flex;
  margin-bottom: 8px;
}

.info-item {
  flex: 1;
  display: flex;
}

.info-item.full-width {
  flex: 3;
}

.info-item .label {
  font-weight: bold;
  min-width: 70px;
}

.info-item .value {
  flex: 1;
}

.goods-table {
  margin-bottom: 20px;
}

.goods-table table {
  width: 100%;
  border-collapse: collapse;
}

.goods-table th,
.goods-table td {
  border: 1px solid #000;
  padding: 6px 8px;
}

.goods-table th {
  background-color: #f5f5f5;
  font-weight: bold;
  text-align: center;
}

.goods-table .center {
  text-align: center;
}

.goods-table .right {
  text-align: right;
}

.goods-table .left {
  text-align: left;
}

.goods-table .bold {
  font-weight: bold;
}

.signature-area {
  display: flex;
  justify-content: space-between;
  margin-top: 40px;
  padding-top: 20px;
}

.signature-item {
  display: flex;
  align-items: center;
}

.signature-item .label {
  font-weight: bold;
  margin-right: 10px;
}

.signature-item .line {
  display: inline-block;
  width: 150px;
}

.page-footer {
  position: absolute;
  bottom: 10mm;
  left: 15mm;
  right: 15mm;
  display: flex;
  justify-content: space-between;
  font-size: 11px;
  color: #999;
}

@media screen and (max-width: 1200px) {
  .delivery-print-container {
    flex-direction: column;
    height: auto;
  }
  
  .config-panel {
    width: 100%;
  }
  
  .preview-panel {
    min-height: 500px;
  }
}
</style>

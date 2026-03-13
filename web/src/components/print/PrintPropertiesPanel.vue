<template>
  <div class="properties-panel">
    <el-tabs v-model="activeTab">
      <el-tab-pane label="属性" name="properties">
        <div v-if="selectedElement" class="properties-content">
          <el-form label-width="80px" size="small">
            <el-form-item label="元素类型">
              <el-tag>{{ selectedElement.type === 'field' ? '字段' : '预设元素' }}</el-tag>
            </el-form-item>
            <el-form-item label="名称">
              <el-input v-model="selectedElement.label" @change="updateElement" placeholder="自定义名称" />
            </el-form-item>
            <el-form-item label="内容" v-if="selectedElement.type === 'field'">
              <div class="content-input-wrapper">
                <el-input
                  v-model="selectedElement.content"
                  @input="handleContentInput"
                  @change="updateElement"
                  placeholder="输入@插入字段"
                  type="textarea"
                  :rows="2"
                />
                <el-popover
                  placement="bottom"
                  :width="200"
                  trigger="manual"
                  v-model:visible="showFieldPicker"
                >
                  <template #reference>
                    <div></div>
                  </template>
                  <div class="field-picker-list">
                    <div class="field-picker-title">主信息字段</div>
                    <div
                      v-for="field in mainFieldDefinitions"
                      :key="field.key"
                      class="field-picker-item"
                      @click="insertField(field)"
                    >
                      {{ field.label }}
                    </div>
                    <div class="field-picker-title">公司信息字段</div>
                    <div
                      v-for="field in companyFieldDefinitions"
                      :key="field.key"
                      class="field-picker-item"
                      @click="insertField(field)"
                    >
                      {{ field.label }}
                    </div>
                  </div>
                </el-popover>
              </div>
            </el-form-item>
            
            <el-divider>位置与对齐</el-divider>
            <el-row :gutter="12">
              <el-col :span="12">
                <el-form-item label="X" label-width="20px">
                  <el-input-number v-model="selectedElement.x" :min="-500" :max="canvasWidthPx + 500" @change="updateElement" size="small" style="width: 100%;" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="Y" label-width="20px">
                  <el-input-number v-model="selectedElement.y" :min="-500" :max="canvasHeightPx + 500" @change="updateElement" size="small" style="width: 100%;" />
                </el-form-item>
              </el-col>
            </el-row>
            <el-row :gutter="12">
              <el-col :span="12">
                <el-form-item label="宽" label-width="20px">
                  <el-input-number v-model="selectedElement.width" :min="30" :max="canvasWidthPx" @change="updateElement" size="small" style="width: 100%;" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="高" label-width="20px">
                  <el-input-number v-model="selectedElement.height" :min="15" :max="500" @change="updateElement" size="small" style="width: 100%;" />
                </el-form-item>
              </el-col>
            </el-row>
            <div class="align-buttons-row">
              <el-button-group>
                <el-button size="small" @click="alignElement('left')" title="左对齐">
                  <el-icon><Back /></el-icon>
                </el-button>
                <el-button size="small" @click="alignElement('centerH')" title="水平居中">
                  <el-icon><Switch /></el-icon>
                </el-button>
                <el-button size="small" @click="alignElement('right')" title="右对齐">
                  <el-icon><Right /></el-icon>
                </el-button>
              </el-button-group>
              <el-button-group style="margin-left: 8px;">
                <el-button size="small" @click="alignElement('top')" title="顶部对齐">
                  <el-icon><Top /></el-icon>
                </el-button>
                <el-button size="small" @click="alignElement('centerV')" title="垂直居中">
                  <el-icon><Minus /></el-icon>
                </el-button>
                <el-button size="small" @click="alignElement('bottom')" title="底部对齐">
                  <el-icon><Bottom /></el-icon>
                </el-button>
              </el-button-group>
            </div>
            
            <el-divider>样式设置</el-divider>
            <el-form-item label="字体">
              <el-select v-model="selectedElement.fontFamily" @change="updateElement" placeholder="选择字体">
                <el-option label="默认" value="" />
                <el-option label="宋体" value="SimSun, serif" />
                <el-option label="黑体" value="SimHei, sans-serif" />
                <el-option label="微软雅黑" value="Microsoft YaHei, sans-serif" />
                <el-option label="楷体" value="KaiTi, serif" />
                <el-option label="仿宋" value="FangSong, serif" />
                <el-option label="Arial" value="Arial, sans-serif" />
                <el-option label="Times New Roman" value="Times New Roman, serif" />
              </el-select>
            </el-form-item>
            <el-form-item label="字体大小">
              <el-select v-model="selectedElement.fontSize" @change="updateElement">
                <el-option label="10px" value="10px" />
                <el-option label="12px" value="12px" />
                <el-option label="14px" value="14px" />
                <el-option label="16px" value="16px" />
                <el-option label="18px" value="18px" />
                <el-option label="20px" value="20px" />
                <el-option label="24px" value="24px" />
                <el-option label="28px" value="28px" />
                <el-option label="32px" value="32px" />
              </el-select>
            </el-form-item>
            <el-form-item label="字体粗细">
              <el-select v-model="selectedElement.fontWeight" @change="updateElement">
                <el-option label="正常" value="normal" />
                <el-option label="粗体" value="bold" />
              </el-select>
            </el-form-item>
            <el-form-item label="对齐方式">
              <el-select v-model="selectedElement.textAlign" @change="updateElement">
                <el-option label="左对齐" value="left" />
                <el-option label="居中" value="center" />
                <el-option label="右对齐" value="right" />
              </el-select>
            </el-form-item>
            <el-form-item label="边框">
              <el-switch v-model="selectedElement.showBorder" @change="updateElement" />
            </el-form-item>
          </el-form>
        </div>
        <div v-else class="no-selection">
          <el-empty description="请选择一个元素进行编辑" :image-size="80" />
          <div class="quick-tips">
            <p><strong>操作提示：</strong></p>
            <ul>
              <li>从左侧拖拽字段到画布</li>
              <li>点击元素可选中编辑</li>
              <li>拖拽元素可移动位置</li>
              <li>拖拽四角可调整大小</li>
            </ul>
          </div>
        </div>
      </el-tab-pane>
      
      <el-tab-pane label="设置" name="settings">
        <div class="settings-content">
          <el-form label-width="100px" size="small">
            <el-divider>打印控制</el-divider>
            <el-form-item label="显示比例">
              <el-button-group>
                <el-button :icon="ZoomOut" @click="zoomOut" />
                <el-button style="width: 70px;">{{ zoom }}%</el-button>
                <el-button :icon="ZoomIn" @click="zoomIn" />
              </el-button-group>
              <el-button :icon="RefreshRight" @click="resetZoom" style="margin-left: 8px;">重置</el-button>
            </el-form-item>
            <el-form-item label="显示网格">
              <el-switch :model-value="showGrid" @update:model-value="emit('toggle-grid')" />
            </el-form-item>
            <el-form-item label="自动排版">
              <el-button type="success" @click="autoArrangeLayout" :icon="Grid">
                自动排版
              </el-button>
            </el-form-item>
            
            <el-divider>纸张格式</el-divider>
            <el-form-item label="纸张类型">
              <el-select v-model="printSettings.paperSize" @change="handlePaperChange" style="width: 100%">
                <el-option v-for="(config, key) in paperSizes" :key="key" :label="config.label" :value="key" />
              </el-select>
            </el-form-item>
            <el-form-item label="纸张尺寸">
              <el-tag size="large">{{ canvasWidth }}×{{ canvasHeight }}mm</el-tag>
            </el-form-item>
            <el-form-item label="打印方向">
              <el-radio-group v-model="printSettings.orientation" @change="handleSettingsChange">
                <el-radio-button label="portrait">纵向</el-radio-button>
                <el-radio-button label="landscape">横向</el-radio-button>
              </el-radio-group>
            </el-form-item>
            <el-form-item label="缩放比例">
              <el-input-number v-model="printSettings.scale" :min="50" :max="150" :step="10" />
              <span class="unit">%</span>
            </el-form-item>
            
            <el-divider>多联单设置</el-divider>
            <el-form-item label="联单数量">
              <el-select v-model="printSettings.copyCount" @change="handleSettingsChange" style="width: 100%">
                <el-option v-for="opt in copyOptions" :key="opt.value" :label="opt.label" :value="opt.value" />
              </el-select>
            </el-form-item>
            <el-form-item label="联单预览">
              <div class="copy-preview">
                <el-tag v-for="i in printSettings.copyCount" :key="i" size="small" style="margin: 2px;">
                  {{ printSettings.copyNames[i-1] }}
                </el-tag>
              </div>
            </el-form-item>
            <el-form-item label="联单标题">
              <el-switch v-model="printSettings.showCopyTitle" @change="handleSettingsChange" />
              <span class="unit">每联显示联单名称</span>
            </el-form-item>
            
            <el-divider>针式打印机</el-divider>
            <el-form-item label="打印模式">
              <el-switch v-model="printSettings.dotMatrixMode" @change="handleSettingsChange" />
              <span class="unit">针式打印机优化</span>
            </el-form-item>
            <el-form-item label="打印质量" v-if="printSettings.dotMatrixMode">
              <el-select v-model="printSettings.printQuality" @change="handleSettingsChange" style="width: 100%">
                <el-option label="草稿（快速）" value="draft" />
                <el-option label="标准" value="normal" />
                <el-option label="高质量" value="high" />
              </el-select>
            </el-form-item>
            <el-form-item label="走纸控制" v-if="printSettings.dotMatrixMode">
              <el-select v-model="printSettings.paperFeed" @change="handleSettingsChange" style="width: 100%">
                <el-option label="连续走纸" value="continuous" />
                <el-option label="单页走纸" value="single" />
                <el-option label="自动检测" value="auto" />
              </el-select>
            </el-form-item>
            
            <el-divider>页边距</el-divider>
            <el-form-item label="上边距">
              <el-input-number v-model="printSettings.marginTop" :min="0" :max="50" @change="handleSettingsChange" />
              <span class="unit">mm</span>
            </el-form-item>
            <el-form-item label="下边距">
              <el-input-number v-model="printSettings.marginBottom" :min="0" :max="50" @change="handleSettingsChange" />
              <span class="unit">mm</span>
            </el-form-item>
            <el-form-item label="左边距">
              <el-input-number v-model="printSettings.marginLeft" :min="0" :max="50" @change="handleSettingsChange" />
              <span class="unit">mm</span>
            </el-form-item>
            <el-form-item label="右边距">
              <el-input-number v-model="printSettings.marginRight" :min="0" :max="50" @change="handleSettingsChange" />
              <span class="unit">mm</span>
            </el-form-item>
            
            <el-divider>打印选项</el-divider>
            <el-form-item label="显示单价">
              <el-switch v-model="printSettings.showPrice" @change="handleSettingsChange" />
            </el-form-item>
            <el-form-item label="显示金额">
              <el-switch v-model="printSettings.showAmount" @change="handleSettingsChange" />
            </el-form-item>
            <el-form-item label="显示页码">
              <el-switch v-model="printSettings.showPageNumbers" @change="handleSettingsChange" />
            </el-form-item>
            <el-form-item label="显示日期">
              <el-switch v-model="printSettings.showDate" @change="handleSettingsChange" />
            </el-form-item>
            <el-divider>表格设置</el-divider>
            <el-form-item label="固定行数">
              <el-input-number v-model="printSettings.tableFixedRows" :min="3" :max="30" @change="handleSettingsChange" />
              <span class="unit">行</span>
            </el-form-item>
            <el-form-item label="溢出处理">
              <el-select v-model="printSettings.tableOverflowMode" @change="handleSettingsChange">
                <el-option label="滚动显示" value="scroll" />
                <el-option label="截断显示" value="truncate" />
                <el-option label="分页打印" value="paginate" />
              </el-select>
            </el-form-item>
            <el-form-item label="当前数据">
              <el-tag :type="hasTableOverflow ? 'warning' : 'success'">
                {{ itemsCount }} / {{ printSettings.tableFixedRows }} 行
              </el-tag>
              <span v-if="hasTableOverflow" style="margin-left: 8px; color: #e6a23c; font-size: 12px;">
                超出 {{ itemsCount - printSettings.tableFixedRows }} 行
              </span>
            </el-form-item>
          </el-form>
        </div>
      </el-tab-pane>
      
      <el-tab-pane label="模板" name="templates">
        <div class="templates-content">
          <el-button type="primary" class="save-template-btn" @click="saveAsTemplate">
            保存为模板
          </el-button>
          <div class="template-list">
            <div
              v-for="tpl in templates"
              :key="tpl.id"
              class="template-item"
              @click="loadTemplate(tpl)"
            >
              <div class="template-preview">
                <el-icon><Document /></el-icon>
              </div>
              <div class="template-info">
                <span class="template-name">{{ tpl.name }}</span>
                <span class="template-date">{{ tpl.created_at ? tpl.created_at.split('T')[0] : '' }}</span>
              </div>
              <el-button
                type="danger"
                size="small"
                circle
                :icon="Delete"
                @click.stop="deleteTemplate(tpl)"
              />
            </div>
            <el-empty v-if="templates.length === 0" description="暂无保存的模板" :image-size="60" />
          </div>
        </div>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import {
  Document, Grid, ZoomIn, ZoomOut, RefreshRight, Delete,
  Back, Right, Top, Bottom, Switch, Minus
} from '@element-plus/icons-vue'

const activeTab = ref('properties')
const showFieldPicker = ref(false)

const props = defineProps({
  selectedElement: {
    type: Object,
    default: null
  },
  printSettings: {
    type: Object,
    required: true
  },
  paperSizes: {
    type: Object,
    required: true
  },
  copyOptions: {
    type: Array,
    required: true
  },
  canvasWidth: {
    type: Number,
    required: true
  },
  canvasHeight: {
    type: Number,
    required: true
  },
  canvasWidthPx: {
    type: Number,
    required: true
  },
  canvasHeightPx: {
    type: Number,
    required: true
  },
  zoom: {
    type: Number,
    required: true
  },
  showGrid: {
    type: Boolean,
    required: true
  },
  templates: {
    type: Array,
    default: () => []
  },
  mainFieldDefinitions: {
    type: Array,
    default: () => []
  },
  companyFieldDefinitions: {
    type: Array,
    default: () => []
  },
  hasTableOverflow: {
    type: Boolean,
    default: false
  },
  itemsCount: {
    type: Number,
    default: 0
  }
})

const emit = defineEmits([
  'update-element',
  'align-element',
  'zoom-in',
  'zoom-out',
  'reset-zoom',
  'toggle-grid',
  'auto-arrange',
  'paper-change',
  'settings-change',
  'save-template',
  'load-template',
  'delete-template',
  'insert-field'
])

const updateElement = () => {
  emit('update-element')
}

const alignElement = (alignment) => {
  emit('align-element', alignment)
}

const zoomIn = () => {
  emit('zoom-in')
}

const zoomOut = () => {
  emit('zoom-out')
}

const resetZoom = () => {
  emit('reset-zoom')
}

const autoArrangeLayout = () => {
  emit('auto-arrange')
}

const handlePaperChange = () => {
  emit('paper-change')
}

const handleSettingsChange = () => {
  emit('settings-change')
}

const saveAsTemplate = () => {
  emit('save-template')
}

const loadTemplate = (template) => {
  emit('load-template', template)
}

const deleteTemplate = (template) => {
  emit('delete-template', template)
}

const handleContentInput = (value) => {
  if (value && value.endsWith('@')) {
    showFieldPicker.value = true
  } else {
    showFieldPicker.value = false
  }
}

const insertField = (field) => {
  emit('insert-field', field)
  showFieldPicker.value = false
}
</script>

<style scoped>
.properties-panel {
  width: 280px;
  flex-shrink: 0;
  background: #fff;
  border-radius: 8px;
  overflow: hidden;
}

.properties-panel :deep(.el-tabs__header) {
  margin: 0;
  padding: 0 12px;
  background: #f5f7fa;
}

.properties-panel :deep(.el-tabs__content) {
  padding: 12px;
  height: calc(100% - 40px);
  overflow-y: auto;
}

.settings-content {
  padding: 8px;
}

.settings-content .el-divider {
  margin: 16px 0 12px 0;
}

.settings-content .el-form-item {
  margin-bottom: 14px;
}

.properties-content {
  padding: 8px;
}

.properties-content .el-divider {
  margin: 16px 0 12px 0;
}

.properties-content .el-form-item {
  margin-bottom: 14px;
}

.templates-content {
  padding: 8px;
}

.no-selection {
  padding: 15px;
}

.quick-tips {
  margin-top: 15px;
  padding: 12px;
  background: #f5f7fa;
  border-radius: 6px;
  font-size: 12px;
  color: #606266;
}

.quick-tips p {
  margin: 0 0 8px 0;
  color: #303133;
}

.quick-tips ul {
  margin: 0;
  padding-left: 18px;
}

.quick-tips li {
  margin-bottom: 4px;
}

.unit {
  margin-left: 5px;
  font-size: 12px;
  color: #909399;
}

.align-buttons-row {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 8px;
  padding: 8px 0;
  margin-bottom: 12px;
}

.content-input-wrapper {
  display: flex;
  gap: 8px;
  align-items: flex-start;
}

.field-picker-list {
  max-height: 300px;
  overflow-y: auto;
}

.field-picker-title {
  font-size: 12px;
  font-weight: bold;
  color: #909399;
  padding: 8px 12px 4px;
  border-bottom: 1px solid #ebeef5;
}

.field-picker-item {
  padding: 8px 12px;
  cursor: pointer;
  font-size: 13px;
  color: #606266;
  transition: all 0.2s;
}

.field-picker-item:hover {
  background: #f0f7ff;
  color: #165DFF;
}

.save-template-btn {
  width: 100%;
  margin-bottom: 10px;
}

.template-list {
  display: flex;
  flex-direction: column;
  gap: 6px;
  max-height: 300px;
  overflow-y: auto;
}

.template-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px;
  background: #f5f7fa;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
}

.template-item:hover {
  background: #ecf5ff;
}

.template-preview {
  width: 36px;
  height: 36px;
  background: #fff;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #409eff;
  font-size: 18px;
}

.template-info {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.template-name {
  font-size: 13px;
  font-weight: 500;
  color: #303133;
}

.template-date {
  font-size: 11px;
  color: #909399;
}

@media screen and (max-width: 1400px) {
  .properties-panel {
    width: 260px;
  }
}
</style>

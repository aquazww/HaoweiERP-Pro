<template>
  <div class="toolbar-panel">
    <div class="toolbar-section">
      <h4>字段库</h4>
      <div class="field-palette">
        <div
          v-for="field in availableMainFields"
          :key="field.key"
          class="palette-item"
          draggable="true"
          @dragstart="onPaletteDragStart($event, field, 'main')"
        >
          <el-icon><Document /></el-icon>
          <span>{{ field.label }}</span>
        </div>
      </div>
    </div>
    
    <div class="toolbar-section">
      <h4>明细字段</h4>
      <div class="field-palette">
        <div
          v-for="field in availableDetailFields"
          :key="field.key"
          class="palette-item detail"
          draggable="true"
          @dragstart="onPaletteDragStart($event, field, 'detail')"
        >
          <el-icon><List /></el-icon>
          <span>{{ field.label }}</span>
        </div>
      </div>
    </div>

    <div class="toolbar-section">
      <h4>预设元素</h4>
      <div class="field-palette">
        <div
          class="palette-item preset"
          draggable="true"
          @dragstart="onPresetDragStart($event, 'title')"
        >
          <el-icon><EditPen /></el-icon>
          <span>标题</span>
        </div>
        <div
          class="palette-item preset qr-code-item"
          draggable="true"
          @dragstart="onPresetDragStart($event, 'qrCode')"
        >
          <el-icon><Grid /></el-icon>
          <span>二维码单号</span>
        </div>
        <div
          class="palette-item preset company-name-item"
          draggable="true"
          @dragstart="onPresetDragStart($event, 'companyName')"
        >
          <el-icon><OfficeBuilding /></el-icon>
          <span>公司名称</span>
        </div>
        <div
          class="palette-item preset company-logo-item"
          draggable="true"
          @dragstart="onPresetDragStart($event, 'companyLogo')"
        >
          <el-icon><Picture /></el-icon>
          <span>公司Logo</span>
        </div>
        <div
          class="palette-item preset company-address-item"
          draggable="true"
          @dragstart="onPresetDragStart($event, 'companyAddress')"
        >
          <el-icon><Location /></el-icon>
          <span>公司地址</span>
        </div>
        <div
          class="palette-item preset company-phone-item"
          draggable="true"
          @dragstart="onPresetDragStart($event, 'companyPhone')"
        >
          <el-icon><Phone /></el-icon>
          <span>公司电话</span>
        </div>
        <div
          class="palette-item preset company-email-item"
          draggable="true"
          @dragstart="onPresetDragStart($event, 'companyEmail')"
        >
          <el-icon><Message /></el-icon>
          <span>公司邮箱</span>
        </div>
        <div
          class="palette-item preset company-stamp-item"
          draggable="true"
          @dragstart="onPresetDragStart($event, 'companyStamp')"
        >
          <el-icon><Stamp /></el-icon>
          <span>公司印章</span>
        </div>
        <div
          class="palette-item preset"
          draggable="true"
          @dragstart="onPresetDragStart($event, 'signature')"
        >
          <el-icon><Edit /></el-icon>
          <span>签收区</span>
        </div>
        <div
          class="palette-item preset"
          draggable="true"
          @dragstart="onPresetDragStart($event, 'table')"
        >
          <el-icon><Grid /></el-icon>
          <span>明细表格</span>
        </div>
        <div
          class="palette-item preset copy-labels"
          draggable="true"
          @dragstart="onPresetDragStart($event, 'copyLabels')"
        >
          <el-icon><Tickets /></el-icon>
          <span>联单名称</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import {
  Document, List, EditPen, OfficeBuilding, Edit, Grid,
  Tickets, Picture, Location, Phone, Message, Stamp
} from '@element-plus/icons-vue'

defineProps({
  availableMainFields: {
    type: Array,
    default: () => []
  },
  availableDetailFields: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['palette-drag-start', 'preset-drag-start'])

const onPaletteDragStart = (event, field, fieldType) => {
  emit('palette-drag-start', event, field, fieldType)
}

const onPresetDragStart = (event, presetType) => {
  emit('preset-drag-start', event, presetType)
}
</script>

<style scoped>
.toolbar-panel {
  width: 180px;
  flex-shrink: 0;
  background: #f5f7fa;
  border-radius: 8px;
  padding: 10px;
  overflow-y: auto;
}

.toolbar-section {
  margin-bottom: 12px;
}

.toolbar-section h4 {
  margin: 0 0 8px 0;
  font-size: 13px;
  color: #303133;
  padding-bottom: 6px;
  border-bottom: 1px solid #dcdfe6;
}

.field-palette {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.palette-item {
  display: flex;
  align-items: center;
  gap: 5px;
  padding: 6px 8px;
  background: #fff;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  cursor: grab;
  font-size: 12px;
  transition: all 0.2s;
}

.palette-item:hover {
  border-color: #409eff;
  background: #ecf5ff;
  transform: translateX(2px);
}

.palette-item.detail {
  background: #f0f9eb;
  border-color: #c2e7b0;
}

.palette-item.detail:hover {
  background: #e1f3d8;
}

.palette-item.preset {
  background: #fdf6ec;
  border-color: #f5dab1;
}

.palette-item.preset:hover {
  background: #faecd8;
}

@media screen and (max-width: 1400px) {
  .toolbar-panel {
    width: 160px;
  }
}
</style>

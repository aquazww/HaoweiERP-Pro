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
            <!-- 网格背景 -->
            <div v-if="showGrid" class="grid-overlay"></div>
            
            <!-- 安全区域指示 -->
            <div class="safe-area-indicator" v-if="showGrid">
              <div class="safe-area-label">安全打印区域</div>
            </div>
            
            <!-- 已放置的元素 -->
            <div
              v-for="(element, index) in placedElements"
              :key="element.id"
              class="placed-element"
              :class="{ 
                selected: selectedElementId === element.id,
                'is-field': element.type === 'field',
                'is-preset': element.type === 'preset',
                'is-table': element.type === 'preset' && element.presetType === 'table'
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
                <div v-if="element.presetType === 'title'" class="preset-title">
                  送 货 单
                </div>
                <div v-else-if="element.presetType === 'qrCode'" class="preset-qrcode">
                  <div class="qrcode-wrapper">
                    <QrcodeVue :value="deliveryData.order_no || 'QR'" :size="Math.min(element.width, element.height) * 0.7" level="M" />
                  </div>
                  <div class="qrcode-label" :style="{ fontSize: element.fontSize }">{{ deliveryData.order_no || '单号' }}</div>
                </div>
                <div v-else-if="element.presetType === 'companyName'" class="preset-company-name">
                  {{ companyInfo.name || '公司名称' }}
                </div>
                <div v-else-if="element.presetType === 'companyLogo'" class="preset-logo">
                  <img v-if="companyInfo.logo_base64" :src="'data:image/png;base64,' + companyInfo.logo_base64" alt="公司Logo" 
                    :style="{ width: Math.min(element.width, element.height) * 0.9 + 'px', height: Math.min(element.width, element.height) * 0.9 + 'px', objectFit: 'contain' }" />
                  <span v-else class="placeholder-text">公司Logo</span>
                </div>
                <div v-else-if="element.presetType === 'companyAddress'" class="preset-company-field">
                  <span class="field-label">地址：</span>
                  <span class="field-value">{{ companyInfo.address || '公司地址' }}</span>
                </div>
                <div v-else-if="element.presetType === 'companyPhone'" class="preset-company-field">
                  <span class="field-label">电话：</span>
                  <span class="field-value">{{ companyInfo.phone || '公司电话' }}</span>
                </div>
                <div v-else-if="element.presetType === 'companyEmail'" class="preset-company-field">
                  <span class="field-label">邮箱：</span>
                  <span class="field-value">{{ companyInfo.email || '公司邮箱' }}</span>
                </div>
                <div v-else-if="element.presetType === 'companyStamp'" class="preset-stamp">
                  <img v-if="companyInfo.stamp_base64" :src="'data:image/png;base64,' + companyInfo.stamp_base64" alt="公司印章" 
                    :style="{ width: Math.min(element.width, element.height) * 0.9 + 'px', height: Math.min(element.width, element.height) * 0.9 + 'px', objectFit: 'contain' }" />
                  <span v-else class="placeholder-text">公司印章</span>
                </div>
                <div v-else-if="element.presetType === 'signature'" class="preset-signature">
                  <span>送货人：__________</span>
                  <span>收货人：__________</span>
                  <span>日期：____年____月____日</span>
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
                      <tr v-for="(row, idx) in getTableDisplayRows(element)" :key="idx" :class="{ 'empty-row': row.isEmpty }">
                        <td>{{ row.isEmpty ? '' : row.index }}</td>
                        <td v-for="col in tableColumns" :key="col.key">
                          {{ row.isEmpty ? '' : getItemFieldValue(row.data, col.key) }}
                        </td>
                      </tr>
                    </tbody>
                    <tfoot v-if="printSettings.showAmount && !hasTableOverflow">
                      <tr>
                        <td :colspan="tableColumns.length + 1" class="total-row">
                          合计金额：¥{{ formatAmount(deliveryData.total_amount) }}
                        </td>
                      </tr>
                    </tfoot>
                  </table>
                  <div v-if="hasTableOverflow" class="table-overflow-indicator">
                    <el-icon><Warning /></el-icon>
                    <span>数据超出固定行数，{{ printSettings.tableOverflowMode === 'scroll' ? '打印时将滚动显示' : '仅显示前' + printSettings.tableFixedRows + '条' }}</span>
                  </div>
                </div>
                <div v-else-if="element.presetType === 'copyLabels'" class="preset-copy-labels">
                  <div class="copy-label-item" v-for="i in printSettings.copyCount" :key="i">
                    <span class="label-number">{{ getCircleNumber(i) }}</span>
                    <span class="label-name">{{ getCopyName(i) }}</span>
                    <span class="label-bracket-color">({{ getCopyColor(i) }})</span>
                  </div>
                </div>
              </template>
              
              <!-- 调整大小手柄 -->
              <div v-if="selectedElementId === element.id" class="resize-handles">
                <div class="resize-handle nw" @mousedown.stop="startResize($event, element, 'nw')"></div>
                <div class="resize-handle ne" @mousedown.stop="startResize($event, element, 'ne')"></div>
                <div class="resize-handle sw" @mousedown.stop="startResize($event, element, 'sw')"></div>
                <div class="resize-handle se" @mousedown.stop="startResize($event, element, 'se')"></div>
              </div>
              
              <!-- 删除按钮 -->
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
                  <el-switch v-model="showGrid" />
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
                    {{ deliveryData.items.length }} / {{ printSettings.tableFixedRows }} 行
                  </el-tag>
                  <span v-if="hasTableOverflow" style="margin-left: 8px; color: #e6a23c; font-size: 12px;">
                    超出 {{ deliveryData.items.length - printSettings.tableFixedRows }} 行
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
    </div>

    <template #footer>
      <div class="dialog-footer">
        <el-button @click="resetLayout" :icon="RefreshRight">重置布局</el-button>
        <el-button @click="handleClose">取消</el-button>
        <el-button type="warning" @click="exportPDF" :loading="exporting" :icon="Download">导出PDF</el-button>
        <el-button type="primary" @click="handlePrint" :loading="printing" :icon="Printer">
          打印
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, reactive, computed, watch, onMounted, onUnmounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Document, List, EditPen, OfficeBuilding, Edit, Grid,
  ZoomIn, ZoomOut, RefreshRight, Close, Printer, Delete,
  Back, Right, Top, Bottom, Switch, Minus, Download, Tickets,
  Picture, Location, Phone, Message, Stamp
} from '@element-plus/icons-vue'
import { exportToPDF } from './printUtils'
import { getCompanyInfo, getPrintTemplates, createPrintTemplate, updatePrintTemplate, deletePrintTemplate, getDefaultPrintTemplate, setDefaultPrintTemplate } from '../../api/basic'
import QrcodeVue from 'qrcode.vue'
import QRCodeLib from 'qrcode'

const props = defineProps({
  modelValue: { type: Boolean, default: false },
  stockOutData: { type: Object, default: null }
})

const emit = defineEmits(['update:modelValue'])

const dialogVisible = ref(props.modelValue)
const activeTab = ref('properties')
const designCanvas = ref(null)
const canvasWrapper = ref(null)
const printing = ref(false)
const exporting = ref(false)
const showGrid = ref(true)
const selectedElementId = ref(null)
const zoom = ref(100)

const companyInfo = ref({
  name: '豪威工贸有限公司',
  short_name: '',
  address: '',
  phone: '',
  logo_base64: '',
  stamp_base64: ''
})

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

const showFieldPicker = ref(false)

const placedElements = ref([])
const templates = ref([])

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

const getFieldValue = (key, element) => {
  if (element && element.content) {
    let content = element.content
    content = content.replace(/\{(\w+)\}/g, (match, fieldKey) => {
      if (fieldKey.startsWith('company_')) {
        const companyFieldMap = {
          'company_name': companyInfo.value.name,
          'company_address': companyInfo.value.address,
          'company_phone': companyInfo.value.phone,
          'company_email': companyInfo.value.email
        }
        return companyFieldMap[fieldKey] || ''
      }
      const value = deliveryData.value[fieldKey]
      if (fieldKey === 'total_amount') {
        return value ? `¥${Number(value).toFixed(2)}` : '¥0.00'
      }
      return value || ''
    })
    return content
  }
  
  const value = deliveryData.value[key]
  if (key === 'total_amount') {
    return value ? `¥${Number(value).toFixed(2)}` : '¥0.00'
  }
  return value || '-'
}

const getItemFieldValue = (item, key) => {
  const value = item[key]
  if (['price', 'amount'].includes(key)) {
    return value ? `¥${Number(value).toFixed(2)}` : '¥0.00'
  }
  return value || '-'
}

const formatAmount = (amount) => {
  return Number(amount || 0).toFixed(2)
}

const circleNumbers = ['①', '②', '③', '④', '⑤', '⑥', '⑦', '⑧', '⑨', '⑩']
const copyNames = ['存根', '客户', '回单', '送货', '财务']
const copyColors = ['白', '红', '黄', '蓝', '绿']

const getCircleNumber = (index) => {
  return circleNumbers[index - 1] || index
}

const getCopyName = (index) => {
  return copyNames[index - 1] || `第${index}联`
}

const getCopyColor = (index) => {
  return copyColors[index - 1] || ''
}

const hasTableOverflow = computed(() => {
  return deliveryData.value.items.length > printSettings.tableFixedRows
})

const getTableDisplayRows = (element) => {
  const fixedRows = printSettings.tableFixedRows
  const items = deliveryData.value.items
  const rows = []
  
  for (let i = 0; i < fixedRows; i++) {
    if (i < items.length) {
      rows.push({
        index: i + 1,
        data: items[i],
        isEmpty: false
      })
    } else {
      rows.push({
        index: i + 1,
        data: {},
        isEmpty: true
      })
    }
  }
  
  return rows
}

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

const onCanvasDrop = (event) => {
  event.preventDefault()
  
  const type = event.dataTransfer.getData('type')
  const rect = designCanvas.value.getBoundingClientRect()
  const scale = zoom.value / 100
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

let isDragging = false
let dragElement = null
let dragStartX = 0
let dragStartY = 0
let elementStartX = 0
let elementStartY = 0

const onElementMouseDown = (event, element) => {
  if (event.target.classList.contains('resize-handle')) return
  
  isDragging = true
  dragElement = element
  dragStartX = event.clientX
  dragStartY = event.clientY
  elementStartX = element.x
  elementStartY = element.y
  selectedElementId.value = element.id
  
  document.addEventListener('mousemove', onMouseMove)
  document.addEventListener('mouseup', onMouseUp)
  event.preventDefault()
}

const onMouseMove = (event) => {
  if (!isDragging || !dragElement) return
  
  const scale = zoom.value / 100
  const deltaX = (event.clientX - dragStartX) / scale
  const deltaY = (event.clientY - dragStartY) / scale
  
  dragElement.x = Math.round(elementStartX + deltaX)
  dragElement.y = Math.round(elementStartY + deltaY)
}

const onMouseUp = () => {
  if (isDragging) {
    saveLayout()
  }
  isDragging = false
  dragElement = null
  document.removeEventListener('mousemove', onMouseMove)
  document.removeEventListener('mouseup', onMouseUp)
}

let isResizing = false
let resizeElement = null
let resizeHandle = ''
let resizeStartX = 0
let resizeStartY = 0
let resizeStartWidth = 0
let resizeStartHeight = 0
let resizeStartElX = 0
let resizeStartElY = 0

const startResize = (event, element, handle) => {
  isResizing = true
  resizeElement = element
  resizeHandle = handle
  resizeStartX = event.clientX
  resizeStartY = event.clientY
  resizeStartWidth = element.width
  resizeStartHeight = element.height
  resizeStartElX = element.x
  resizeStartElY = element.y
  
  document.addEventListener('mousemove', onResizeMove)
  document.addEventListener('mouseup', onResizeUp)
  event.preventDefault()
}

const onResizeMove = (event) => {
  if (!isResizing || !resizeElement) return
  
  const scale = zoom.value / 100
  const deltaX = (event.clientX - resizeStartX) / scale
  const deltaY = (event.clientY - resizeStartY) / scale
  
  if (resizeHandle.includes('e')) {
    resizeElement.width = Math.max(30, Math.round(resizeStartWidth + deltaX))
  }
  if (resizeHandle.includes('w')) {
    const newWidth = resizeStartWidth - deltaX
    if (newWidth >= 30) {
      resizeElement.width = Math.round(newWidth)
      resizeElement.x = Math.round(resizeStartElX + deltaX)
    }
  }
  if (resizeHandle.includes('s')) {
    resizeElement.height = Math.max(15, Math.round(resizeStartHeight + deltaY))
  }
  if (resizeHandle.includes('n')) {
    const newHeight = resizeStartHeight - deltaY
    if (newHeight >= 15) {
      resizeElement.height = Math.round(newHeight)
      resizeElement.y = Math.round(resizeStartElY + deltaY)
    }
  }
}

const onResizeUp = () => {
  if (isResizing) {
    saveLayout()
  }
  isResizing = false
  resizeElement = null
  document.removeEventListener('mousemove', onResizeMove)
  document.removeEventListener('mouseup', onResizeUp)
}

const updateElement = () => {
  const index = placedElements.value.findIndex(el => el.id === selectedElementId.value)
  if (index > -1) {
    const element = placedElements.value[index]
    placedElements.value[index] = { ...element }
  }
  saveLayout()
}

const handleContentInput = (value) => {
  if (value && value.endsWith('@')) {
    showFieldPicker.value = true
  } else {
    showFieldPicker.value = false
  }
}

const insertField = (field) => {
  if (!selectedElement.value) return
  
  let content = selectedElement.value.content || ''
  const atIndex = content.lastIndexOf('@')
  if (atIndex !== -1) {
    content = content.substring(0, atIndex) + `{${field.key}}`
  } else {
    content += `{${field.key}}`
  }
  
  selectedElement.value.content = content
  selectedElement.value.key = field.key
  showFieldPicker.value = false
  updateElement()
}

const centerElement = (direction) => {
  if (!selectedElement.value) return
  
  const el = selectedElement.value
  
  if (direction === 'horizontal' || direction === 'both') {
    el.x = Math.round((canvasWidthPx.value - el.width) / 2)
  }
  if (direction === 'vertical' || direction === 'both') {
    el.y = Math.round((canvasHeightPx.value - el.height) / 2)
  }
  
  saveLayout()
  ElMessage.success('已居中对齐')
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

const autoArrangeLayout = () => {
  ElMessageBox.confirm('自动排版将重新排列所有元素，当前布局将被覆盖。是否继续？', '提示', {
    type: 'warning',
    confirmButtonText: '确定',
    cancelButtonText: '取消'
  }).then(() => {
    initDefaultLayout()
    ElMessage.success('自动排版完成')
  }).catch(() => {})
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
  adjustElementsForPaper()
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

const handleSettingsChange = () => {
  localStorage.setItem('advancedPrintSettings', JSON.stringify(printSettings))
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
      console.error('加载布局失败:', e)
      initDefaultLayout()
    }
  } else {
    initDefaultLayout()
  }
}

const initDefaultLayout = () => {
  const marginPx = Math.round(10 * MM_TO_PX)
  let currentY = marginPx
  
  placedElements.value = [
    {
      id: generateId(),
      type: 'preset',
      presetType: 'title',
      label: '标题',
      x: Math.round((canvasWidthPx.value - 300) / 2),
      y: currentY,
      width: 300,
      height: 50,
      fontSize: '28px',
      fontWeight: 'bold',
      textAlign: 'center',
      showBorder: false
    }
  ]
  currentY += 60
  
  placedElements.value.push({
    id: generateId(),
    type: 'preset',
    presetType: 'company',
    label: '公司名称',
    x: Math.round((canvasWidthPx.value - 250) / 2),
    y: currentY,
    width: 250,
    height: 28,
    fontSize: '14px',
    fontWeight: 'normal',
    textAlign: 'center',
    showBorder: false
  })
  currentY += 40
  
  const mainFieldsToPlace = ['order_no', 'sale_order_no', 'customer_name', 'customer_contact', 
                              'customer_phone', 'customer_address', 'warehouse_name', 'delivery_date']
  const colWidth = Math.round((canvasWidthPx.value - marginPx * 2) / 2)
  
  mainFieldsToPlace.forEach((key, index) => {
    const field = mainFieldDefinitions.find(f => f.key === key)
    if (field) {
      const col = index % 2
      const row = Math.floor(index / 2)
      placedElements.value.push({
        id: generateId(),
        type: 'field',
        fieldType: 'main',
        key: field.key,
        label: field.label,
        content: '',
        x: marginPx + col * colWidth,
        y: currentY + row * 26,
        width: colWidth - 10,
        height: 22,
        fontSize: '12px',
        fontWeight: 'normal',
        textAlign: 'left',
        showBorder: false
      })
    }
  })
  currentY += Math.ceil(mainFieldsToPlace.length / 2) * 26 + 15
  
  placedElements.value.push({
    id: generateId(),
    type: 'preset',
    presetType: 'table',
    label: '明细表格',
    x: marginPx,
    y: currentY,
    width: canvasWidthPx.value - marginPx * 2,
    height: 180,
    fontSize: '11px',
    fontWeight: 'normal',
    textAlign: 'left',
    showBorder: false
  })
  currentY += 195
  
  placedElements.value.push({
    id: generateId(),
    type: 'preset',
    presetType: 'signature',
    label: '签收区',
    x: marginPx,
    y: currentY,
    width: canvasWidthPx.value - marginPx * 2,
    height: 35,
    fontSize: '12px',
    fontWeight: 'normal',
    textAlign: 'left',
    showBorder: false
  })
  
  saveLayout()
}

const resetLayout = () => {
  ElMessageBox.confirm('确定要重置为默认布局吗？当前布局将被清除。', '提示', {
    type: 'warning'
  }).then(() => {
    placedElements.value = []
    initDefaultLayout()
    ElMessage.success('布局已重置')
  }).catch(() => {})
}

const saveAsTemplate = async () => {
  try {
    const { value } = await ElMessageBox.prompt('请输入模板名称', '保存模板', {
      confirmButtonText: '保存',
      cancelButtonText: '取消',
      inputPattern: /\S+/,
      inputErrorMessage: '模板名称不能为空'
    })
    
    const templateData = {
      name: value,
      template_type: 'delivery',
      elements: JSON.parse(JSON.stringify(placedElements.value)),
      settings: JSON.parse(JSON.stringify(printSettings)),
      paper_width: Math.round(canvasWidth.value),
      paper_height: Math.round(canvasHeight.value),
      orientation: printSettings.orientation
    }
    
    console.log('保存模板数据:', templateData)
    const res = await createPrintTemplate(templateData)
    console.log('保存模板响应:', res)
    
    const newTemplate = res.data || res
    templates.value.unshift(newTemplate)
    ElMessage.success('模板保存成功')
  } catch (e) {
    if (e !== 'cancel') {
      console.error('保存模板失败:', e)
      const errorMsg = e.message || e.msg || '保存模板失败，请稍后重试'
      ElMessage.error(errorMsg)
    }
  }
}

const loadTemplate = async (template) => {
  try {
    await ElMessageBox.confirm('确定要加载此模板吗？当前布局将被替换。', '提示', {
      type: 'warning'
    })
    
    placedElements.value = JSON.parse(JSON.stringify(template.elements))
    if (template.settings?.paperSize) printSettings.paperSize = template.settings.paperSize
    if (template.orientation) printSettings.orientation = template.orientation
    Object.assign(printSettings, template.settings || {})
    selectedElementId.value = null
    ElMessage.success('模板加载成功')
  } catch (e) {
    // 用户取消
  }
}

const deleteTemplate = async (template) => {
  try {
    await ElMessageBox.confirm('确定要删除此模板吗？', '提示', {
      type: 'warning'
    })
    
    await deletePrintTemplate(template.id)
    const index = templates.value.findIndex(t => t.id === template.id)
    if (index > -1) {
      templates.value.splice(index, 1)
    }
    ElMessage.success('模板已删除')
  } catch (e) {
    if (e !== 'cancel') {
      console.error('删除模板失败:', e)
      ElMessage.error('删除模板失败')
    }
  }
}

const loadTemplates = async () => {
  try {
    const res = await getPrintTemplates({ template_type: 'delivery' })
    console.log('模板API返回:', res)
    const data = res.data
    templates.value = data?.items || data?.results || data || []
    console.log('模板列表:', templates.value)
  } catch (e) {
    console.error('加载模板失败:', e)
    templates.value = []
  }
}

const initDeliveryData = () => {
  if (!props.stockOutData) return
  const data = props.stockOutData
  deliveryData.value = {
    order_no: data.order_no || '',
    sale_order_no: data.sale_order_no || '',
    customer_name: data.customer_name || '',
    customer_contact: data.customer_contact || '',
    customer_phone: data.customer_phone || '',
    customer_address: data.customer_address || '',
    warehouse_name: data.warehouse_name || '',
    delivery_date: data.created_at ? data.created_at.split('T')[0] : new Date().toISOString().split('T')[0],
    total_amount: data.total_amount || 0,
    remark: data.remark || '',
    items: (data.items || []).map(item => ({
      goods_code: item.goods_code || '',
      goods_name: item.goods_name || '',
      goods_spec: item.goods_spec || '',
      unit_name: item.unit_name || '',
      quantity: item.quantity || 0,
      price: item.price || 0,
      amount: item.amount || 0,
      remark: item.remark || ''
    }))
  }
}

const loadCompanyInfo = async () => {
  try {
    const res = await getCompanyInfo()
    if (res.data) {
      companyInfo.value = {
        name: res.data.name || '豪威工贸有限公司',
        short_name: res.data.short_name || '',
        address: res.data.business_address || res.data.registered_address || '',
        phone: res.data.phone || '',
        email: res.data.email || '',
        website: res.data.website || '',
        logo_base64: res.data.logo_base64 || '',
        stamp_base64: res.data.stamp_base64 || ''
      }
    }
  } catch (error) {
    console.error('加载公司信息失败:', error)
  }
}

const generateQRCodeDataUrl = async (text, size) => {
  try {
    const dataUrl = await QRCodeLib.toDataURL(text, {
      width: size,
      margin: 1,
      color: {
        dark: '#000000',
        light: '#ffffff'
      }
    })
    return dataUrl
  } catch (e) {
    console.error('二维码生成错误:', e)
    return ''
  }
}

const generatePrintHTML = async () => {
  const elements = await Promise.all(placedElements.value.map(async (el) => {
    const xMm = (el.x / MM_TO_PX).toFixed(2)
    const yMm = (el.y / MM_TO_PX).toFixed(2)
    const widthMm = (el.width / MM_TO_PX).toFixed(2)
    const heightMm = (el.height / MM_TO_PX).toFixed(2)
    
    if (el.type === 'field') {
      let displayValue = ''
      if (el.content) {
        displayValue = el.content.replace(/\{(\w+)\}/g, (match, fieldKey) => {
          if (fieldKey.startsWith('company_')) {
            const companyFieldMap = {
              'company_name': companyInfo.value.name,
              'company_address': companyInfo.value.address,
              'company_phone': companyInfo.value.phone,
              'company_email': companyInfo.value.email
            }
            return companyFieldMap[fieldKey] || ''
          }
          const value = deliveryData.value[fieldKey]
          if (fieldKey === 'total_amount') {
            return value ? `¥${Number(value).toFixed(2)}` : '¥0.00'
          }
          return value || ''
        })
      } else {
        const value = deliveryData.value[el.key]
        if (el.key === 'total_amount') {
          displayValue = value ? `¥${Number(value).toFixed(2)}` : '¥0.00'
        } else {
          displayValue = value || '-'
        }
      }
      
      return `
        <div style="
          position: absolute;
          left: ${xMm}mm;
          top: ${yMm}mm;
          width: ${widthMm}mm;
          font-size: ${el.fontSize};
          font-weight: ${el.fontWeight};
          font-family: ${el.fontFamily || ''};
          text-align: ${el.textAlign};
          border: ${el.showBorder ? '1px solid #333' : 'none'};
          box-sizing: border-box;
          white-space: nowrap;
        ">
          <span style="font-weight: bold;">${el.label}：</span>
          <span>${displayValue}</span>
        </div>
      `
    } else if (el.type === 'preset') {
      if (el.presetType === 'title') {
        return `
          <div style="
            position: absolute;
            left: ${xMm}mm;
            top: ${yMm}mm;
            width: ${widthMm}mm;
            font-size: ${el.fontSize};
            font-weight: ${el.fontWeight};
            text-align: ${el.textAlign};
            border-bottom: 2px solid #000;
            display: flex;
            align-items: center;
            justify-content: center;
            box-sizing: border-box;
          ">送 货 单</div>
        `
      } else if (el.presetType === 'qrCode') {
        const orderNo = deliveryData.value.order_no || 'QR'
        const qrSize = Math.min(el.width, el.height) * 0.7
        const qrDataUrl = await generateQRCodeDataUrl(orderNo, Math.round(qrSize))
        return `
          <div style="
            position: absolute;
            left: ${xMm}mm;
            top: ${yMm}mm;
            width: ${widthMm}mm;
            height: ${heightMm}mm;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            box-sizing: border-box;
            padding: 2mm;
          ">
            <img src="${qrDataUrl}" style="width: ${(qrSize / MM_TO_PX).toFixed(2)}mm; height: ${(qrSize / MM_TO_PX).toFixed(2)}mm; object-fit: contain;" />
            <div style="font-size: ${el.fontSize}; color: #333; margin-top: 1mm; text-align: center; word-break: break-all;">${orderNo}</div>
          </div>
        `
      } else if (el.presetType === 'companyName') {
        return `
          <div style="
            position: absolute;
            left: ${xMm}mm;
            top: ${yMm}mm;
            width: ${widthMm}mm;
            font-size: ${el.fontSize};
            font-weight: ${el.fontWeight};
            text-align: ${el.textAlign};
            color: #333;
            display: flex;
            align-items: center;
            justify-content: center;
            box-sizing: border-box;
          ">${companyInfo.value.name || '公司名称'}</div>
        `
      } else if (el.presetType === 'companyLogo') {
        if (companyInfo.value.logo_base64) {
          const logoSize = Math.min(el.width, el.height) * 0.9
          return `
            <div style="
              position: absolute;
              left: ${xMm}mm;
              top: ${yMm}mm;
              width: ${widthMm}mm;
              height: ${heightMm}mm;
              display: flex;
              align-items: center;
              justify-content: center;
              box-sizing: border-box;
            ">
              <img src="data:image/png;base64,${companyInfo.value.logo_base64}" style="width: ${(logoSize / MM_TO_PX).toFixed(2)}mm; height: ${(logoSize / MM_TO_PX).toFixed(2)}mm; object-fit: contain;" />
            </div>
          `
        } else {
          return ''
        }
      } else if (el.presetType === 'companyAddress') {
        return `
          <div style="
            position: absolute;
            left: ${xMm}mm;
            top: ${yMm}mm;
            width: ${widthMm}mm;
            font-size: ${el.fontSize};
            text-align: ${el.textAlign};
            color: #333;
            display: flex;
            align-items: center;
            box-sizing: border-box;
          "><span style="color: #666;">地址：</span>${companyInfo.value.address || ''}</div>
        `
      } else if (el.presetType === 'companyPhone') {
        return `
          <div style="
            position: absolute;
            left: ${xMm}mm;
            top: ${yMm}mm;
            width: ${widthMm}mm;
            font-size: ${el.fontSize};
            text-align: ${el.textAlign};
            color: #333;
            display: flex;
            align-items: center;
            box-sizing: border-box;
          "><span style="color: #666;">电话：</span>${companyInfo.value.phone || ''}</div>
        `
      } else if (el.presetType === 'companyEmail') {
        return `
          <div style="
            position: absolute;
            left: ${xMm}mm;
            top: ${yMm}mm;
            width: ${widthMm}mm;
            font-size: ${el.fontSize};
            text-align: ${el.textAlign};
            color: #333;
            display: flex;
            align-items: center;
            box-sizing: border-box;
          "><span style="color: #666;">邮箱：</span>${companyInfo.value.email || ''}</div>
        `
      } else if (el.presetType === 'companyStamp') {
        if (companyInfo.value.stamp_base64) {
          const stampSize = Math.min(el.width, el.height) * 0.9
          return `
            <div style="
              position: absolute;
              left: ${xMm}mm;
              top: ${yMm}mm;
              width: ${widthMm}mm;
              height: ${heightMm}mm;
              display: flex;
              align-items: center;
              justify-content: center;
              box-sizing: border-box;
            ">
              <img src="data:image/png;base64,${companyInfo.value.stamp_base64}" style="width: ${(stampSize / MM_TO_PX).toFixed(2)}mm; height: ${(stampSize / MM_TO_PX).toFixed(2)}mm; object-fit: contain;" />
            </div>
          `
        } else {
          return ''
        }
      } else if (el.presetType === 'signature') {
        return `
          <div style="
            position: absolute;
            left: ${xMm}mm;
            top: ${yMm}mm;
            width: ${widthMm}mm;
            font-size: ${el.fontSize};
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding-top: 15px;
            box-sizing: border-box;
          ">
            <span>送货人：__________</span>
            <span>收货人：__________</span>
            <span>日期：____年____月____日</span>
          </div>
        `
      } else if (el.presetType === 'table') {
        const headerHtml = tableColumns.value.map(col => 
          `<th style="border: 1px solid #000; padding: 4px 6px; background: #f5f5f5; font-size: ${el.fontSize};">${col.label}</th>`
        ).join('')
        
        const fixedRows = printSettings.tableFixedRows
        const items = deliveryData.value.items
        const overflowMode = printSettings.tableOverflowMode
        
        let displayItems = []
        for (let i = 0; i < fixedRows; i++) {
          if (i < items.length) {
            displayItems.push({ index: i + 1, data: items[i], isEmpty: false })
          } else {
            displayItems.push({ index: i + 1, data: {}, isEmpty: true })
          }
        }
        
        const rowsHtml = displayItems.map(row => {
          const cellsHtml = tableColumns.value.map(col => 
            `<td style="border: 1px solid #000; padding: 4px 6px; font-size: ${el.fontSize};">${row.isEmpty ? '&nbsp;' : getItemFieldValue(row.data, col.key)}</td>`
          ).join('')
          return `<tr><td style="border: 1px solid #000; padding: 4px 6px; text-align: center; font-size: ${el.fontSize};">${row.isEmpty ? '&nbsp;' : row.index}</td>${cellsHtml}</tr>`
        }).join('')
        
        const overflowHtml = hasTableOverflow.value ? `
          <tr>
            <td colspan="${tableColumns.value.length + 1}" style="border: 1px solid #000; padding: 4px 6px; text-align: center; font-size: 10px; color: #999; background: #fff8e6;">
              ${overflowMode === 'scroll' ? `共 ${items.length} 条记录，滚动查看更多` : `共 ${items.length} 条记录，仅显示前 ${fixedRows} 条`}
            </td>
          </tr>
        ` : ''
        
        return `
          <div style="
            position: absolute;
            left: ${xMm}mm;
            top: ${yMm}mm;
            width: ${widthMm}mm;
            font-size: ${el.fontSize};
            box-sizing: border-box;
          ">
            <table style="width: 100%; border-collapse: collapse; table-layout: fixed;">
              <thead>
                <tr>
                  <th style="width: 30px; border: 1px solid #000; padding: 4px 6px; background: #f5f5f5; font-size: ${el.fontSize};">序号</th>
                  ${headerHtml}
                </tr>
              </thead>
              <tbody>
                ${rowsHtml}
                ${overflowHtml}
              </tbody>
              ${printSettings.showAmount && !hasTableOverflow.value ? `
              <tfoot>
                <tr>
                  <td colspan="${tableColumns.value.length + 1}" style="border: 1px solid #000; padding: 4px 6px; text-align: right; font-weight: bold; font-size: ${el.fontSize};">
                    合计金额：¥${Number(deliveryData.value.total_amount || 0).toFixed(2)}
                  </td>
                </tr>
              </tfoot>
              ` : ''}
            </table>
          </div>
        `
      } else if (el.presetType === 'copyLabels') {
        const labelsHtml = Array.from({ length: printSettings.copyCount }, (_, i) => {
          const idx = i + 1
          const number = getCircleNumber(idx)
          const name = getCopyName(idx)
          const color = getCopyColor(idx)
          return `
            <div style="display: flex; flex-direction: column; align-items: center; gap: 2px; padding: 2px 0;">
              <span style="font-size: 16px; font-weight: bold;">${number}</span>
              <span style="font-size: 14px; font-weight: bold; writing-mode: vertical-rl; text-orientation: upright; letter-spacing: 3px;">${name}</span>
              <span style="font-size: 12px; color: #666; white-space: nowrap;">(${color})</span>
            </div>
          `
        }).join('')
        
        return `
          <div style="
            position: absolute;
            left: ${xMm}mm;
            top: ${yMm}mm;
            width: ${widthMm}mm;
            font-size: ${el.fontSize};
            font-weight: ${el.fontWeight};
            display: flex;
            flex-direction: column;
            gap: 12px;
            padding: 4px;
            box-sizing: border-box;
          ">
            ${labelsHtml}
          </div>
        `
      }
    }
    return ''
  }))

  const elementsHtml = elements.filter(Boolean).join('')

  const dotMatrixStyles = printSettings.dotMatrixMode ? `
    .print-page {
      page-break-after: always;
      page-break-inside: avoid;
    }
  ` : ''

  return `
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="UTF-8">
      <title>送货单 - ${deliveryData.value.order_no}</title>
      <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
          font-family: 'Microsoft YaHei', 'SimHei', Arial, sans-serif;
          font-size: 12px;
          line-height: 1.4;
          -webkit-print-color-adjust: exact;
          print-color-adjust: exact;
        }
        .print-page {
          position: relative;
          width: ${canvasWidth.value}mm;
          min-height: ${canvasHeight.value}mm;
          background: #fff;
          overflow: hidden;
          margin-bottom: 0;
        }
        .page-footer {
          position: absolute;
          bottom: 3mm;
          left: ${printSettings.marginLeft}mm;
          right: ${printSettings.marginRight}mm;
          display: flex;
          justify-content: space-between;
          font-size: 10px;
          color: #999;
        }
        ${dotMatrixStyles}
        @media print {
          body { margin: 0; padding: 0; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
          .print-page { margin: 0; }
          @page {
            size: ${canvasWidth.value}mm ${canvasHeight.value}mm;
            margin: 0;
          }
        }
      </style>
    </head>
    <body>
      <div class="print-page">
        ${elementsHtml}
        <div class="page-footer">
          ${printSettings.showDate ? `<span>打印日期：${new Date().toLocaleDateString('zh-CN')}</span>` : ''}
          <span>共 ${printSettings.copyCount} 联单</span>
        </div>
      </div>
    </body>
    </html>
  `
}

const handlePrint = async () => {
  if (printing.value) return
  printing.value = true
  
  try {
    const html = await generatePrintHTML()
    const printWindow = window.open('', '_blank')
    
    if (!printWindow) {
      ElMessage.error('无法打开打印窗口，请检查浏览器的弹出窗口阻止设置')
      return
    }
    
    printWindow.document.write(html)
    printWindow.document.close()
    printWindow.focus()
    
    await new Promise(resolve => setTimeout(resolve, 300))
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
    const html = await generatePrintHTML()
    await exportToPDF(html, `送货单-${deliveryData.value.order_no}`)
    ElMessage.success('PDF导出成功')
  } catch (error) {
    console.error('导出PDF失败:', error)
    ElMessage.error('导出PDF失败，请重试')
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
    loadLayout()
    loadTemplates()
    loadCompanyInfo()
    initDeliveryData()
    selectedElementId.value = null
  }
})

watch(dialogVisible, (val) => {
  emit('update:modelValue', val)
})

onMounted(() => {
  const savedSettings = localStorage.getItem('advancedPrintSettings')
  if (savedSettings) {
    try {
      Object.assign(printSettings, JSON.parse(savedSettings))
    } catch (e) {
      console.error('加载打印设置失败:', e)
    }
  }
})

onUnmounted(() => {
  document.removeEventListener('mousemove', onMouseMove)
  document.removeEventListener('mouseup', onMouseUp)
  document.removeEventListener('mousemove', onResizeMove)
  document.removeEventListener('mouseup', onResizeUp)
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

.design-panel {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.design-toolbar {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 8px 12px;
  background: #fff;
  border-radius: 8px;
  margin-bottom: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  flex-wrap: wrap;
  gap: 8px;
}

.toolbar-center {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
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

.safe-area-indicator {
  position: absolute;
  top: 10mm;
  left: 10mm;
  right: 10mm;
  bottom: 10mm;
  border: 1px dashed #409eff;
  pointer-events: none;
  z-index: 0;
  opacity: 0.5;
}

.safe-area-label {
  position: absolute;
  top: -20px;
  left: 0;
  font-size: 10px;
  color: #409eff;
  background: #fff;
  padding: 0 5px;
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

.placed-element.is-table {
  align-items: flex-start;
  height: auto !important;
}

.placed-element:hover {
  box-shadow: 0 0 0 1px #409eff;
}

.placed-element.selected {
  box-shadow: 0 0 0 2px #409eff, 0 2px 8px rgba(64, 158, 255, 0.3);
  z-index: 20;
}

.placed-element.is-field {
  background: rgba(64, 158, 255, 0.03);
}

.placed-element.is-preset {
  background: rgba(230, 162, 60, 0.03);
}

.element-label {
  font-weight: bold;
  white-space: nowrap;
  color: #303133;
  flex-shrink: 0;
}

.element-value {
  white-space: nowrap;
  color: #606266;
  flex: 1;
  min-width: 0;
}

.preset-title {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  border-bottom: 2px solid #000;
  box-sizing: border-box;
}

.preset-qrcode {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  box-sizing: border-box;
  padding: 4px;
}

.preset-qrcode .qrcode-wrapper {
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.preset-qrcode .qrcode-label {
  color: #333;
  margin-top: 4px;
  text-align: center;
  word-break: break-all;
  line-height: 1.2;
}

.preset-company-name {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #333;
  font-weight: bold;
  box-sizing: border-box;
}

.preset-logo {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  box-sizing: border-box;
}

.preset-logo .company-logo-img {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
}

.preset-stamp {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  box-sizing: border-box;
}

.preset-stamp .company-stamp-img {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
}

.placeholder-text {
  font-size: 12px;
  color: #999;
  text-align: center;
}

.preset-company-field {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  box-sizing: border-box;
}

.preset-company-field .field-label {
  color: #666;
  font-size: 11px;
}

.preset-company-field .field-value {
  color: #333;
  font-size: 11px;
}

.preset-signature {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-top: 8px;
  box-sizing: border-box;
}

.preset-table {
  width: 100%;
  box-sizing: border-box;
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

.preset-table th {
  background: #f5f5f5;
}

.preset-table .empty-row {
  height: 24px;
}

.preset-table .empty-row td {
  color: #ccc;
}

.table-overflow-indicator {
  background: rgba(230, 162, 60, 0.9);
  color: #fff;
  padding: 4px 8px;
  font-size: 11px;
  display: flex;
  align-items: center;
  gap: 4px;
  margin-top: 4px;
}

.total-row {
  font-weight: bold;
  text-align: right;
}

.preset-copy-labels {
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding: 4px;
  box-sizing: border-box;
  width: 100%;
}

.preset-copy-labels .copy-label-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
  padding: 2px 0;
  min-width: 20px;
}

.preset-copy-labels .copy-label-item span {
  display: block;
  line-height: 1.1;
  text-align: center;
}

.preset-copy-labels .label-number {
  font-size: 16px;
  font-weight: bold;
  margin-bottom: 2px;
}

.preset-copy-labels .label-name {
  font-size: 14px;
  font-weight: bold;
  writing-mode: vertical-rl;
  text-orientation: upright;
  letter-spacing: 3px;
}

.preset-copy-labels .label-bracket-color {
  font-size: 12px;
  color: #666;
  white-space: nowrap;
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
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.2);
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

.field-picker-btn {
  flex-shrink: 0;
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

.align-buttons {
  display: flex;
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

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

@media screen and (max-width: 1400px) {
  .toolbar-panel {
    width: 160px;
  }
  
  .properties-panel {
    width: 260px;
  }
}

@media screen and (max-width: 1200px) {
  .advanced-print-container {
    flex-direction: column;
  }
  
  .toolbar-panel {
    width: 100%;
    display: flex;
    gap: 12px;
    overflow-x: auto;
    padding: 8px;
  }
  
  .toolbar-section {
    min-width: 140px;
    margin-bottom: 0;
  }
  
  .properties-panel {
    width: 100%;
    max-height: 180px;
  }
}
</style>

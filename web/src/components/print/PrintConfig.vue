<template>
  <div class="print-config">
    <h3>打印配置</h3>
    
    <!-- 字段选择和排序 -->
    <div class="field-config">
      <h4>字段配置</h4>
      <div class="field-list" ref="fieldList">
        <div 
          v-for="(field, index) in fields" 
          :key="field.key"
          class="field-item"
          draggable="true"
          @dragstart="onDragStart($event, index)"
          @dragover.prevent
          @drop="onDrop($event, index)"
        >
          <el-checkbox v-model="field.visible">{{ field.label }}</el-checkbox>
          <div class="drag-handle">
            <i class="el-icon-rank"></i>
          </div>
        </div>
      </div>
    </div>

    <!-- 打印设置 -->
    <div class="print-settings">
      <h4>打印设置</h4>
      <el-form :model="printSettings" label-width="100px">
        <el-form-item label="纸张大小">
          <el-select v-model="printSettings.paperSize">
            <el-option label="A4" value="A4"></el-option>
            <el-option label="A3" value="A3"></el-option>
            <el-option label="A5" value="A5"></el-option>
            <el-option label="B4" value="B4"></el-option>
            <el-option label="B5" value="B5"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="纸张方向">
          <el-radio-group v-model="printSettings.orientation">
            <el-radio label="portrait">纵向</el-radio>
            <el-radio label="landscape">横向</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="页边距 (mm)">
          <el-row :gutter="10">
            <el-col :span="6">
              <el-input-number v-model="printSettings.margins.top" :min="0" :max="100" size="small"></el-input-number>
              <span class="margin-label">上</span>
            </el-col>
            <el-col :span="6">
              <el-input-number v-model="printSettings.margins.right" :min="0" :max="100" size="small"></el-input-number>
              <span class="margin-label">右</span>
            </el-col>
            <el-col :span="6">
              <el-input-number v-model="printSettings.margins.bottom" :min="0" :max="100" size="small"></el-input-number>
              <span class="margin-label">下</span>
            </el-col>
            <el-col :span="6">
              <el-input-number v-model="printSettings.margins.left" :min="0" :max="100" size="small"></el-input-number>
              <span class="margin-label">左</span>
            </el-col>
          </el-row>
        </el-form-item>
        <el-form-item label="打印标题">
          <el-input v-model="printSettings.title"></el-input>
        </el-form-item>
        <el-form-item label="字体大小">
          <el-select v-model="printSettings.fontSize">
            <el-option label="小" value="10px"></el-option>
            <el-option label="中" value="12px"></el-option>
            <el-option label="大" value="14px"></el-option>
            <el-option label="特大" value="16px"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="页眉内容">
          <el-input v-model="printSettings.header" placeholder="输入页眉内容"></el-input>
        </el-form-item>
        <el-form-item label="页脚内容">
          <el-input v-model="printSettings.footer" placeholder="输入页脚内容"></el-input>
        </el-form-item>
        <el-form-item label="显示页码">
          <el-checkbox v-model="printSettings.showPageNumbers"></el-checkbox>
        </el-form-item>
        <el-form-item label="显示日期">
          <el-checkbox v-model="printSettings.showDate"></el-checkbox>
        </el-form-item>

      </el-form>
    </div>

    <!-- 模板管理 -->
    <div class="template-management">
      <h4>模板管理</h4>
      <el-row :gutter="10">
        <el-col :span="12">
          <el-input v-model="templateName" placeholder="模板名称"></el-input>
        </el-col>
        <el-col :span="4">
          <el-button type="primary" @click="saveTemplate">保存模板</el-button>
        </el-col>
        <el-col :span="8">
          <el-select v-model="selectedTemplate" placeholder="选择模板">
            <el-option 
              v-for="(config, name) in templates" 
              :key="name" 
              :label="name" 
              :value="name"
            ></el-option>
          </el-select>
          <el-button @click="loadTemplate" :disabled="!selectedTemplate">加载模板</el-button>
          <el-button type="danger" @click="deleteTemplate" :disabled="!selectedTemplate">删除模板</el-button>
        </el-col>
      </el-row>
    </div>

    <!-- 操作按钮 -->
    <div class="actions">
      <el-button @click="$emit('cancel')">取消</el-button>
      <el-button type="primary" @click="confirm">确认</el-button>
    </div>
  </div>
</template>

<script>
import { savePrintTemplate, getPrintTemplate, getAllPrintTemplates, deletePrintTemplate } from './printUtils';

export default {
  name: 'PrintConfig',
  props: {
    fields: {
      type: Array,
      required: true
    },
    printSettings: {
      type: Object,
      default: () => ({
        paperSize: 'A4',
        orientation: 'portrait',
        margins: {
          top: 10,
          right: 10,
          bottom: 10,
          left: 10
        },
        title: '打印预览',
        fontSize: '12px',
        header: '',
        footer: '',
        showPageNumbers: true,
        showDate: true
      })
    }
  },
  data() {
    return {
      templateName: '',
      selectedTemplate: '',
      templates: {},
      draggedIndex: -1
    };
  },
  mounted() {
    this.templates = getAllPrintTemplates();
  },
  methods: {
    onDragStart(event, index) {
      this.draggedIndex = index;
      event.dataTransfer.effectAllowed = 'move';
    },
    onDrop(event, index) {
      event.preventDefault();
      if (this.draggedIndex !== -1 && this.draggedIndex !== index) {
        const draggedField = this.fields.splice(this.draggedIndex, 1)[0];
        this.fields.splice(index, 0, draggedField);
      }
      this.draggedIndex = -1;
    },
    saveTemplate() {
      if (!this.templateName) {
        this.$message.error('请输入模板名称');
        return;
      }
      const config = {
        fields: [...this.fields],
        printSettings: { ...this.printSettings }
      };
      savePrintTemplate(this.templateName, config);
      this.templates = getAllPrintTemplates();
      this.$message.success('模板保存成功');
    },
    loadTemplate() {
      if (!this.selectedTemplate) {
        return;
      }
      const config = getPrintTemplate(this.selectedTemplate);
      if (config) {
        this.fields.splice(0, this.fields.length, ...config.fields);
        this.printSettings = { ...config.printSettings };
        this.$message.success('模板加载成功');
      }
    },
    deleteTemplate() {
      if (!this.selectedTemplate) {
        return;
      }
      this.$confirm('确定要删除这个模板吗？', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        deletePrintTemplate(this.selectedTemplate);
        this.templates = getAllPrintTemplates();
        this.selectedTemplate = '';
        this.$message.success('模板删除成功');
      });
    },
    confirm() {
      this.$emit('confirm', {
        fields: [...this.fields],
        printSettings: { ...this.printSettings }
      });
    }
  }
};
</script>

<style scoped>
.print-config {
  padding: 20px;
  background: #f5f7fa;
  border-radius: 4px;
}

.field-config {
  margin-bottom: 20px;
}

.field-list {
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  padding: 10px;
  background: #fff;
  min-height: 200px;
}

.field-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 12px;
  margin-bottom: 8px;
  background: #f9f9f9;
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  cursor: move;
}

.field-item:hover {
  background: #ecf5ff;
}

.drag-handle {
  color: #909399;
  cursor: move;
}

.print-settings {
  margin-bottom: 20px;
}

.template-management {
  margin-bottom: 20px;
}

.margin-label {
  margin-left: 5px;
  font-size: 12px;
  color: #909399;
}

.actions {
  display: flex;
  justify-content: flex-end;
  margin-top: 20px;
}

.actions button {
  margin-left: 10px;
}
</style>

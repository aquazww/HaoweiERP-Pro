<template>
  <div class="print-preview">
    <div class="preview-header">
      <h3>{{ printSettings.title }}</h3>
      <div class="preview-actions">
        <el-button @click="$emit('close')">关闭</el-button>
        <el-button type="warning" @click="exportPDF">导出PDF</el-button>
        <el-button type="primary" @click="print">打印</el-button>
      </div>
    </div>
    <div class="preview-content" ref="previewContent">
      <div class="print-content" :style="printStyle">
        <slot></slot>
      </div>
    </div>
  </div>
</template>

<script>
import { exportToPDF } from './printUtils';

export default {
  name: 'PrintPreview',
  props: {
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
        header: '',
        footer: '',
        showPageNumbers: true,
        showDate: true
      })
    }
  },
  computed: {
    printStyle() {
      const paperSizes = {
        A4: { width: '210mm', height: '297mm' },
        A3: { width: '297mm', height: '420mm' },
        A5: { width: '148mm', height: '210mm' },
        B4: { width: '250mm', height: '353mm' },
        B5: { width: '176mm', height: '250mm' }
      };
      
      const size = paperSizes[this.printSettings.paperSize] || paperSizes.A4;
      const orientation = this.printSettings.orientation;
      
      return {
        width: orientation === 'portrait' ? size.width : size.height,
        height: orientation === 'portrait' ? size.height : size.width,
        margin: `${this.printSettings.margins.top}mm ${this.printSettings.margins.right}mm ${this.printSettings.margins.bottom}mm ${this.printSettings.margins.left}mm`,
        padding: '20px',
        background: '#fff',
        boxShadow: '0 0 10px rgba(0, 0, 0, 0.1)',
        position: 'relative',
        overflow: 'hidden',
        fontSize: this.printSettings.fontSize || '12px'
      };
    }
  },
  methods: {
    print() {
      try {
        const content = this.$refs.previewContent.innerHTML;
        const currentDate = new Date().toLocaleString();
        const printWindow = window.open('', '_blank');
        
        if (!printWindow) {
          this.$message.error('无法打开打印窗口，请检查浏览器的弹出窗口阻止设置');
          return;
        }
        
        printWindow.document.write(`
          <html>
          <head>
            <title>${this.printSettings.title}</title>
            <style>
              body {
                font-family: Arial, sans-serif;
                font-size: ${this.printSettings.fontSize || '12px'};
                line-height: 1.5;
                margin: 0;
                padding: 0;
              }
              .print-content {
                width: 100%;
                min-height: 80vh;
                page-break-inside: avoid;
              }
              table {
                width: 100%;
                border-collapse: collapse;
                margin-bottom: 20px;
              }
              th, td {
                border: 1px solid #000;
                padding: 8px;
                text-align: left;
              }
              th {
                background-color: #f2f2f2;
                font-weight: bold;
              }
              .page-break {
                page-break-after: always;
              }
              .header {
                text-align: center;
                margin-bottom: 20px;
                padding-bottom: 10px;
                border-bottom: 1px solid #ccc;
              }
              .footer {
                text-align: center;
                margin-top: 20px;
                padding-top: 10px;
                border-top: 1px solid #ccc;
                font-size: 10px;
                color: #666;
              }
              .footer-left {
                float: left;
              }
              .footer-right {
                float: right;
              }
              .clearfix::after {
                content: "";
                display: table;
                clear: both;
              }
            </style>
          </head>
          <body>
            ${this.printSettings.header ? `<div class="header">${this.printSettings.header}</div>` : ''}
            ${content}
            <div class="footer clearfix">
              ${this.printSettings.footer ? `<div class="footer-left">${this.printSettings.footer}</div>` : ''}
              <div class="footer-right">
                ${this.printSettings.showDate ? `日期: ${currentDate} ` : ''}
                ${this.printSettings.showPageNumbers ? '<span class="page-number">第 1 页，共 <span class="page-count"></span> 页</span>' : ''}
              </div>
            </div>
          </body>
          </html>
        `);
        
        printWindow.document.close();
        printWindow.focus();
        
        // 延迟执行打印，确保内容已加载
        setTimeout(() => {
          printWindow.print();
          // 打印对话框关闭后再关闭窗口
          printWindow.onafterprint = function() {
            printWindow.close();
          };
        }, 100);
      } catch (error) {
        console.error('打印失败:', error);
        this.$message.error('打印失败，请重试');
      }
    },
    exportPDF() {
      try {
        const content = this.$refs.previewContent.innerHTML;
        const currentDate = new Date().toLocaleString();
        const fullContent = `
          ${this.printSettings.header ? `<div class="header">${this.printSettings.header}</div>` : ''}
          ${content}
          <div class="footer clearfix">
            ${this.printSettings.footer ? `<div class="footer-left">${this.printSettings.footer}</div>` : ''}
            <div class="footer-right">
              ${this.printSettings.showDate ? `日期: ${currentDate} ` : ''}
              ${this.printSettings.showPageNumbers ? '<span class="page-number">第 1 页，共 <span class="page-count"></span> 页</span>' : ''}
            </div>
          </div>
        `;
        exportToPDF(fullContent, this.printSettings.title);
      } catch (error) {
        console.error('导出PDF失败:', error);
        this.$message.error('导出PDF失败，请重试');
      }
    }
  }
};
</script>

<style scoped>
.print-preview {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.preview-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 20px;
  background: #f5f7fa;
  border-bottom: 1px solid #e4e7ed;
}

.preview-actions {
  display: flex;
  gap: 10px;
}

.preview-content {
  flex: 1;
  padding: 20px;
  overflow: auto;
  background: #f0f2f5;
  display: flex;
  justify-content: center;
  align-items: flex-start;
}

.print-content {
  background: #fff;
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
  overflow: auto;
}
</style>

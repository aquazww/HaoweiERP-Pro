/**
 * 打印工具函数
 */

/**
 * 打开打印预览
 * @param {string} content - 打印内容
 * @param {string} title - 打印标题
 */
export function openPrintPreview(content, title = '打印预览') {
  try {
    const printWindow = window.open('', '_blank');
    
    if (!printWindow) {
      alert('无法打开打印预览窗口，请检查浏览器的弹出窗口阻止设置');
      return;
    }
    
    printWindow.document.write(`
      <html>
      <head>
        <title>${title}</title>
        <style>
          @media print {
            body {
              font-family: Arial, sans-serif;
              font-size: 12px;
              line-height: 1.5;
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
          }
        </style>
      </head>
      <body>
        ${content}
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
    console.error('打开打印预览失败:', error);
    alert('打开打印预览失败，请重试');
  }
}

/**
 * 导出为PDF
 * @param {string} content - 打印内容
 * @param {string} title - 打印标题
 */
export function exportToPDF(content, title = '导出PDF') {
  try {
    // 创建一个新窗口
    const pdfWindow = window.open('', '_blank');
    
    if (!pdfWindow) {
      alert('无法打开导出窗口，请检查浏览器的弹出窗口阻止设置');
      return;
    }
    
    pdfWindow.document.write(`
      <html>
      <head>
        <title>${title}</title>
        <style>
          body {
            font-family: Arial, sans-serif;
            font-size: 12px;
            line-height: 1.5;
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
        ${content}
      </body>
      </html>
    `);
    
    pdfWindow.document.close();
    pdfWindow.focus();
    
    // 延迟执行打印，确保内容已加载
    setTimeout(() => {
      pdfWindow.print();
      // 打印对话框关闭后再关闭窗口
      pdfWindow.onafterprint = function() {
        pdfWindow.close();
      };
    }, 100);
  } catch (error) {
    console.error('导出PDF失败:', error);
    alert('导出PDF失败，请重试');
  }
}

/**
 * 生成打印内容
 * @param {Array} fields - 字段配置
 * @param {Array} data - 数据
 * @returns {string} 打印内容
 */
export function generatePrintContent(fields, data) {
  if (!data || data.length === 0) {
    return '<p>暂无数据</p>';
  }

  let content = '<table>';
  
  // 生成表头
  content += '<thead><tr>';
  fields.forEach(field => {
    if (field.visible) {
      content += `<th>${field.label}</th>`;
    }
  });
  content += '</tr></thead>';

  // 生成表格内容
  content += '<tbody>';
  data.forEach(item => {
    content += '<tr>';
    fields.forEach(field => {
      if (field.visible) {
        const value = item[field.key] || '';
        content += `<td>${value}</td>`;
      }
    });
    content += '</tr>';
  });
  content += '</tbody>';
  content += '</table>';

  return content;
}

/**
 * 保存打印模板
 * @param {string} name - 模板名称
 * @param {Object} config - 打印配置
 */
export function savePrintTemplate(name, config) {
  const templates = JSON.parse(localStorage.getItem('printTemplates') || '{}');
  templates[name] = config;
  localStorage.setItem('printTemplates', JSON.stringify(templates));
}

/**
 * 获取打印模板
 * @param {string} name - 模板名称
 * @returns {Object|null} 打印配置
 */
export function getPrintTemplate(name) {
  const templates = JSON.parse(localStorage.getItem('printTemplates') || '{}');
  return templates[name] || null;
}

/**
 * 获取所有打印模板
 * @returns {Object} 所有打印模板
 */
export function getAllPrintTemplates() {
  return JSON.parse(localStorage.getItem('printTemplates') || '{}');
}

/**
 * 删除打印模板
 * @param {string} name - 模板名称
 */
export function deletePrintTemplate(name) {
  const templates = JSON.parse(localStorage.getItem('printTemplates') || '{}');
  delete templates[name];
  localStorage.setItem('printTemplates', JSON.stringify(templates));
}

/**
 * 下载打印模板
 * @param {string} name - 模板名称
 * @param {Object} config - 打印配置
 */
export function downloadPrintTemplate(name, config) {
  const dataStr = JSON.stringify(config, null, 2);
  const dataBlob = new Blob([dataStr], { type: 'application/json' });
  const url = URL.createObjectURL(dataBlob);
  const link = document.createElement('a');
  link.href = url;
  link.download = `${name}.json`;
  link.click();
  URL.revokeObjectURL(url);
}

/**
 * 上传打印模板
 * @param {File} file - 模板文件
 * @returns {Promise<Object>} 打印配置
 */
export function uploadPrintTemplate(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = e => {
      try {
        const config = JSON.parse(e.target.result);
        resolve(config);
      } catch (error) {
        reject(new Error('模板文件格式错误'));
      }
    };
    reader.onerror = reject;
    reader.readAsText(file);
  });
}

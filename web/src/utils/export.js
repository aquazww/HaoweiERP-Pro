import * as XLSX from 'xlsx'
import { saveAs } from 'file-saver'

/**
 * 导出数据为 Excel 文件
 * @param {Array} data - 数据数组
 * @param {Array} columns - 列配置 [{ key: '字段名', title: '标题' }]
 * @param {string} filename - 文件名（不含扩展名）
 */
export function exportToExcel(data, columns, filename) {
  // 转换数据
  const exportData = data.map(item => {
    const row = {}
    columns.forEach(col => {
      row[col.title] = item[col.key] !== undefined ? item[col.key] : ''
    })
    return row
  })

  // 创建工作簿和工作表
  const worksheet = XLSX.utils.json_to_sheet(exportData)
  const workbook = XLSX.utils.book_new()
  XLSX.utils.book_append_sheet(workbook, worksheet, 'Sheet1')

  // 导出文件
  const excelBuffer = XLSX.write(workbook, { bookType: 'xlsx', type: 'array' })
  const blob = new Blob([excelBuffer], { type: 'application/octet-stream' })
  saveAs(blob, `${filename}.xlsx`)
}

/**
 * 格式化日期
 */
export function formatDate(date) {
  if (!date) return ''
  const d = new Date(date)
  const year = d.getFullYear()
  const month = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

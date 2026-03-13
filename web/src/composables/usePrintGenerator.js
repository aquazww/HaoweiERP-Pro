/**
 * 打印HTML生成组合式函数
 * 生成打印所需的HTML内容
 */
import QRCodeLib from 'qrcode'

export function usePrintGenerator(
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
) {
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
  
  return {
    generatePrintHTML
  }
}

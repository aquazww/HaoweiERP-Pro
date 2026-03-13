/**
 * 元素拖拽组合式函数
 * 管理元素的拖拽移动和调整大小功能
 */
import { ref, onUnmounted } from 'vue'

export function useElementDrag(zoom, saveLayout) {
  let isDragging = false
  let dragElement = null
  let dragStartX = 0
  let dragStartY = 0
  let elementStartX = 0
  let elementStartY = 0
  
  let isResizing = false
  let resizeElement = null
  let resizeHandle = ''
  let resizeStartX = 0
  let resizeStartY = 0
  let resizeStartWidth = 0
  let resizeStartHeight = 0
  let resizeStartElX = 0
  let resizeStartElY = 0
  
  const onElementMouseDown = (event, element, selectedElementId) => {
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
  
  const startResize = (event, element, handle, selectedElementId) => {
    isResizing = true
    resizeElement = element
    resizeHandle = handle
    resizeStartX = event.clientX
    resizeStartY = event.clientY
    resizeStartWidth = element.width
    resizeStartHeight = element.height
    resizeStartElX = element.x
    resizeStartElY = element.y
    selectedElementId.value = element.id
    
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
  
  const cleanup = () => {
    document.removeEventListener('mousemove', onMouseMove)
    document.removeEventListener('mouseup', onMouseUp)
    document.removeEventListener('mousemove', onResizeMove)
    document.removeEventListener('mouseup', onResizeUp)
  }
  
  onUnmounted(() => {
    cleanup()
  })
  
  return {
    onElementMouseDown,
    startResize,
    cleanup
  }
}

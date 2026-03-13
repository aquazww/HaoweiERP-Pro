/**
 * 打印模板管理组合式函数
 * 管理打印模板的加载、保存、删除等操作
 */
import { ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getPrintTemplates, createPrintTemplate, deletePrintTemplate } from '@/api/basic'
import { log, error } from '@/utils/logger'

export function usePrintTemplates(placedElements, printSettings, canvasWidth, canvasHeight) {
  const templates = ref([])
  
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
        elements: structuredClone(placedElements.value),
        settings: structuredClone(printSettings),
        paper_width: Math.round(canvasWidth.value),
        paper_height: Math.round(canvasHeight.value),
        orientation: printSettings.orientation
      }
      
      log('保存模板数据:', templateData)
      const res = await createPrintTemplate(templateData)
      log('保存模板响应:', res)
      
      const newTemplate = res.data || res
      templates.value.unshift(newTemplate)
      ElMessage.success('模板保存成功')
    } catch (e) {
      if (e !== 'cancel') {
        error('保存模板失败:', e)
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
      
      placedElements.value = structuredClone(template.elements)
      if (template.settings?.paperSize) printSettings.paperSize = template.settings.paperSize
      if (template.orientation) printSettings.orientation = template.orientation
      Object.assign(printSettings, template.settings || {})
      ElMessage.success('模板加载成功')
      return true
    } catch (e) {
      return false
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
        error('删除模板失败:', e)
        ElMessage.error('删除模板失败')
      }
    }
  }
  
  const loadTemplates = async () => {
    try {
      const res = await getPrintTemplates({ template_type: 'delivery' })
      log('模板API返回:', res)
      const data = res.data
      templates.value = data?.items || data?.results || data || []
      log('模板列表:', templates.value)
    } catch (e) {
      error('加载模板失败:', e)
      templates.value = []
    }
  }
  
  return {
    templates,
    saveAsTemplate,
    loadTemplate,
    deleteTemplate,
    loadTemplates
  }
}

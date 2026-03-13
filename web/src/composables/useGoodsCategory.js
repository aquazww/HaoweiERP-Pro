/**
 * 商品分类管理组合式函数
 * 管理商品分类的加载、树形结构构建、增删改查等操作
 */
import { ref, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getCategories, createCategory, updateCategory, partialUpdateCategory, deleteCategory } from '@/api/basic'

export function useGoodsCategory() {
  const categoryTreeData = ref([])
  const categoryLoading = ref(false)
  const categoryToggleLoading = ref(null)
  const selectedCategoryId = ref(null)
  const selectedCategoryIncludeChildren = ref(false)
  const expandedCategories = ref([])
  
  const categoryDialogVisible = ref(false)
  const categorySearch = ref('')
  const categoryFormDialogVisible = ref(false)
  const categoryFormTitle = ref('新增分类')
  const categoryFormLoading = ref(false)
  const categoryFormRef = ref(null)
  const categoryTreeRef = ref(null)
  
  const categoryForm = ref({
    id: null,
    name: '',
    code: '',
    parent: null,
    sort: 0,
    is_active: true,
    remark: ''
  })
  
  const categoryRules = {
    name: [{ required: true, message: '请输入分类名称', trigger: 'blur' }],
    code: [{ required: true, message: '请输入分类编码', trigger: 'blur' }]
  }
  
  const filteredCategoryList = computed(() => {
    if (!categorySearch.value) return categoryTreeData.value
    const search = categorySearch.value.toLowerCase()
    const filterTree = (nodes) => {
      return nodes.reduce((acc, node) => {
        if (node.name.toLowerCase().includes(search) || (node.code && node.code.toLowerCase().includes(search))) {
          acc.push(node)
        } else if (node.children && node.children.length > 0) {
          const filteredChildren = filterTree(node.children)
          if (filteredChildren.length > 0) {
            acc.push({ ...node, children: filteredChildren })
          }
        }
        return acc
      }, [])
    }
    return filterTree(categoryTreeData.value)
  })
  
  const categoryParentOptions = computed(() => {
    const markDisabled = (nodes, excludeId) => {
      nodes.forEach(node => {
        if (node.id === excludeId) {
          node.disabled = true
        }
        if (node.children && node.children.length > 0) {
          markDisabled(node.children, excludeId)
        }
      })
    }
    
    const cloneTree = (nodes) => {
      return nodes.map(node => {
        const cloned = { ...node }
        if (node.children && node.children.length > 0) {
          cloned.children = cloneTree(node.children)
        }
        return cloned
      })
    }
    
    const treeData = cloneTree(categoryTreeData.value)
    markDisabled(treeData, categoryForm.value.id)
    
    return treeData
  })
  
  const goodsCategoryOptions = computed(() => {
    const cloneTree = (nodes) => {
      return nodes.map(node => {
        const cloned = { ...node }
        if (node.level === 1) {
          cloned.disabled = true
        }
        if (node.children && node.children.length > 0) {
          cloned.children = cloneTree(node.children)
        }
        return cloned
      })
    }
    
    return cloneTree(categoryTreeData.value)
  })
  
  const buildCategoryTree = (categories) => {
    const map = {}
    const roots = []
    
    const uniqueCategories = []
    const seenIds = new Set()
    
    categories.forEach(cat => {
      if (!seenIds.has(cat.id)) {
        seenIds.add(cat.id)
        uniqueCategories.push(cat)
        map[cat.id] = { ...cat, children: [] }
      }
    })
    
    uniqueCategories.forEach(cat => {
      const parentId = cat.parent?.id || cat.parent_id || cat.parent
      if (parentId && map[parentId]) {
        const parent = map[parentId]
        const exists = parent.children.some(child => child.id === cat.id)
        if (!exists) {
          parent.children.push(map[cat.id])
        }
      } else if (!parentId) {
        roots.push(map[cat.id])
      }
    })
    
    const removeEmptyChildren = (nodes) => {
      nodes.forEach(node => {
        if (node.children && node.children.length === 0) {
          delete node.children
        } else if (node.children) {
          removeEmptyChildren(node.children)
        }
      })
    }
    
    removeEmptyChildren(roots)
    
    return roots
  }
  
  const loadCategories = async () => {
    try {
      const res = await getCategories({ page_size: 1000, is_active: true })
      const categories = res.data?.items || res.data?.results || []
      categoryTreeData.value = buildCategoryTree(categories)
    } catch (error) {
      categoryTreeData.value = []
    }
  }
  
  const handleCategoryItemClick = (category, onSelect) => {
    const hasChildren = category.children && category.children.length > 0
    
    if (hasChildren) {
      const index = expandedCategories.value.indexOf(category.id)
      if (index > -1) {
        expandedCategories.value.splice(index, 1)
      } else {
        expandedCategories.value.push(category.id)
      }
    }
    
    handleSelectCategory(category.id, category.level === 1, onSelect)
  }
  
  const handleSelectCategory = (categoryId, includeChildren = false, onSelect) => {
    selectedCategoryId.value = categoryId
    selectedCategoryIncludeChildren.value = includeChildren
    if (onSelect) {
      onSelect(categoryId, includeChildren)
    }
  }
  
  const getCategoryTotalGoods = (category) => {
    let total = category.goods_count || 0
    if (category.children && category.children.length > 0) {
      category.children.forEach(child => {
        total += child.goods_count || 0
      })
    }
    return total
  }
  
  const handleManageCategory = () => {
    categoryDialogVisible.value = true
  }
  
  const handleAddCategoryItem = () => {
    categoryFormTitle.value = '新增分类'
    resetCategoryForm()
    categoryFormDialogVisible.value = true
  }
  
  const handleEditCategoryItem = (row) => {
    categoryFormTitle.value = '编辑分类'
    categoryForm.value = {
      id: row.id,
      name: row.name,
      code: row.code || '',
      parent: row.parent || null,
      sort: row.sort_order || 0,
      is_active: row.is_active !== false,
      remark: row.remark || ''
    }
    categoryFormDialogVisible.value = true
  }
  
  const resetCategoryForm = () => {
    categoryForm.value = {
      id: null,
      name: '',
      code: '',
      parent: null,
      sort: 0,
      is_active: true,
      remark: ''
    }
    categoryFormRef.value?.resetFields()
  }
  
  const handleSubmitCategory = async () => {
    if (!categoryFormRef.value) return
    
    try {
      await categoryFormRef.value.validate()
    } catch (error) {
      return
    }
    
    categoryFormLoading.value = true
    try {
      const data = {
        name: categoryForm.value.name,
        code: categoryForm.value.code,
        parent: categoryForm.value.parent || null,
        sort_order: categoryForm.value.sort,
        is_active: categoryForm.value.is_active,
        remark: categoryForm.value.remark
      }
      
      if (categoryForm.value.id) {
        await updateCategory(categoryForm.value.id, data)
        ElMessage.success('修改成功')
      } else {
        await createCategory(data)
        ElMessage.success('新增成功')
      }
      
      categoryFormDialogVisible.value = false
      loadCategories()
    } catch (error) {
      const errorData = error.response?.data
      if (errorData?.data) {
        const errors = []
        for (const [field, msg] of Object.entries(errorData.data)) {
          errors.push(msg)
        }
        ElMessage.error(errors.join('；'))
      } else if (errorData?.msg) {
        ElMessage.error(errorData.msg)
      } else {
        ElMessage.error(categoryForm.value.id ? '修改失败' : '新增失败')
      }
    } finally {
      categoryFormLoading.value = false
    }
  }
  
  const handleDeleteCategoryItem = async (row) => {
    try {
      await ElMessageBox.confirm(`确定删除分类「${row.name}」？`, '确认删除', { type: 'warning' })
      await deleteCategory(row.id)
      ElMessage.success('删除成功')
      loadCategories()
    } catch (error) {
      if (error !== 'cancel') {
        ElMessage.error('删除失败：' + (error.response?.data?.msg || error.message || '未知错误'))
      }
    }
  }
  
  const handleToggleCategoryStatus = async (row) => {
    categoryToggleLoading.value = row.id
    try {
      await partialUpdateCategory(row.id, { is_active: row.is_active })
      ElMessage.success(row.is_active ? '已启用' : '已停用')
    } catch (error) {
      row.is_active = !row.is_active
      ElMessage.error('操作失败：' + (error.response?.data?.msg || error.message || '未知错误'))
    } finally {
      categoryToggleLoading.value = null
    }
  }
  
  const allowDrop = (draggingNode, dropNode, type) => {
    if (type === 'inner') {
      const isChild = checkIsChild(draggingNode.data, dropNode.data)
      return !isChild
    }
    return true
  }
  
  const checkIsChild = (parentNode, childNode) => {
    if (!parentNode || !parentNode.children) return false
    if (parentNode.id === childNode.id) return true
    
    for (const child of parentNode.children) {
      if (checkIsChild(child, childNode)) return true
    }
    return false
  }
  
  const handleNodeDrop = async (draggingNode, dropNode, dropType) => {
    const draggedData = draggingNode.data
    const droppedData = dropNode.data
    
    try {
      let newParent = null
      let newSortOrder = 0
      
      if (dropType === 'inner') {
        newParent = droppedData.id
        newSortOrder = droppedData.children ? droppedData.children.length : 0
      } else if (dropType === 'before') {
        newParent = droppedData.parent || null
        const siblings = getSiblingNodes(droppedData)
        const dropIndex = siblings.findIndex(item => item.id === droppedData.id)
        newSortOrder = dropIndex
      } else if (dropType === 'after') {
        newParent = droppedData.parent || null
        const siblings = getSiblingNodes(droppedData)
        const dropIndex = siblings.findIndex(item => item.id === droppedData.id)
        newSortOrder = dropIndex + 1
      }
      
      await updateCategory(draggedData.id, {
        parent: newParent,
        sort_order: newSortOrder
      })
      
      ElMessage.success('排序已更新')
      loadCategories()
    } catch (error) {
      ElMessage.error('排序更新失败：' + (error.response?.data?.msg || error.message || '未知错误'))
      loadCategories()
    }
  }
  
  const getSiblingNodes = (node) => {
    const parentId = node.parent || node.parent_id
    if (!parentId) {
      return categoryTreeData.value
    }
    
    const findParent = (nodes) => {
      for (const n of nodes) {
        if (n.id === parentId) return n.children || []
        if (n.children) {
          const result = findParent(n.children)
          if (result) return result
        }
      }
      return []
    }
    
    return findParent(categoryTreeData.value)
  }
  
  return {
    categoryTreeData,
    categoryLoading,
    categoryToggleLoading,
    selectedCategoryId,
    selectedCategoryIncludeChildren,
    expandedCategories,
    categoryDialogVisible,
    categorySearch,
    categoryFormDialogVisible,
    categoryFormTitle,
    categoryFormLoading,
    categoryFormRef,
    categoryTreeRef,
    categoryForm,
    categoryRules,
    filteredCategoryList,
    categoryParentOptions,
    goodsCategoryOptions,
    buildCategoryTree,
    loadCategories,
    handleCategoryItemClick,
    handleSelectCategory,
    getCategoryTotalGoods,
    handleManageCategory,
    handleAddCategoryItem,
    handleEditCategoryItem,
    resetCategoryForm,
    handleSubmitCategory,
    handleDeleteCategoryItem,
    handleToggleCategoryStatus,
    allowDrop,
    handleNodeDrop
  }
}

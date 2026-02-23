<template>
  <div class="params-page">
    <div class="page-content">
      <div class="table-card">
        <el-tabs v-model="activeTab" class="params-tabs">
          <el-tab-pane label="计量单位" name="units">
            <div class="unit-wrapper">
              <div class="unit-list-panel">
                <div class="panel-toolbar">
                  <el-input v-model="unitSearch" placeholder="搜索单位名称" clearable :prefix-icon="Search" style="width: 180px" @keyup.enter="loadUnits" />
                  <div class="toolbar-right">
                    <el-button type="primary" :icon="Plus" size="small" @click="handleAddUnit">新增单位</el-button>
                  </div>
                </div>
                <div class="unit-grid-container" v-loading="unitLoading">
                  <div class="unit-grid">
                    <div 
                      v-for="item in filteredUnitList" 
                      :key="item.id" 
                      class="unit-card"
                      :class="{ 'selected': selectedUnit?.id === item.id, 'inactive': !item.is_active }"
                      @click="handleUnitClick(item)"
                    >
                      <span class="unit-name">{{ item.name }}</span>
                      <span class="unit-symbol" v-if="item.symbol">{{ item.symbol }}</span>
                      <div class="unit-actions" v-if="selectedUnit?.id === item.id" @click.stop>
                        <el-switch
                          v-model="item.is_active"
                          size="small"
                          :loading="unitToggleLoading === item.id"
                          @change="handleToggleUnitStatus(item)"
                        />
                        <el-button type="warning" size="small" @click="handleEditUnit(item)">
                          <el-icon><Edit /></el-icon>编辑
                        </el-button>
                        <el-button type="danger" size="small" @click="handleDeleteUnit(item)">
                          <el-icon><Delete /></el-icon>删除
                        </el-button>
                      </div>
                    </div>
                  </div>
                  <el-empty v-if="!unitLoading && filteredUnitList.length === 0" description="暂无单位数据" :image-size="80" />
                </div>
              </div>
              <div class="unit-detail-panel" v-if="selectedUnit">
                <div class="panel-title">单位详情</div>
                <div class="detail-list">
                  <div class="detail-row">
                    <span class="detail-label">单位名称</span>
                    <span class="detail-value name">{{ selectedUnit.name }}</span>
                  </div>
                  <div class="detail-row" v-if="selectedUnit.symbol">
                    <span class="detail-label">单位符号</span>
                    <span class="detail-value symbol">{{ selectedUnit.symbol }}</span>
                  </div>
                  <div class="detail-row" v-if="selectedUnit.base_unit_name">
                    <span class="detail-label">基准单位</span>
                    <span class="detail-value base">{{ selectedUnit.base_unit_name }}</span>
                  </div>
                  <div class="detail-row" v-if="selectedUnit.conversion_display && selectedUnit.conversion_display !== '-'">
                    <span class="detail-label">换算关系</span>
                    <span class="detail-value conversion">{{ selectedUnit.conversion_display }}</span>
                  </div>
                  <div class="detail-row">
                    <span class="detail-label">关联数量</span>
                    <span class="detail-value count">{{ selectedUnit.goods_count || 0 }} 个商品</span>
                  </div>
                  <div class="detail-row">
                    <span class="detail-label">状态</span>
                    <div class="detail-value status">
                      <el-tag :type="selectedUnit.is_active ? 'success' : 'info'" size="small">
                        {{ selectedUnit.is_active ? '启用' : '停用' }}
                      </el-tag>
                    </div>
                  </div>
                  <div class="detail-row">
                    <span class="detail-label">创建人</span>
                    <span class="detail-value creator">{{ selectedUnit.created_by_name || '-' }}</span>
                  </div>
                  <div class="detail-row">
                    <span class="detail-label">创建时间</span>
                    <span class="detail-value time">{{ formatDateTime(selectedUnit.created_at) }}</span>
                  </div>
                  <div class="detail-row">
                    <span class="detail-label">更新时间</span>
                    <span class="detail-value time">{{ formatDateTime(selectedUnit.updated_at) }}</span>
                  </div>
                </div>
              </div>
            </div>
          </el-tab-pane>

          <el-tab-pane label="仓库信息" name="warehouses">
            <div class="tab-header">
              <div class="search-box">
                <el-input v-model="warehouseSearch" placeholder="搜索仓库名称" clearable @keyup.enter="loadWarehouses" style="width: 200px" />
              </div>
              <el-button type="primary" :icon="Plus" @click="handleAddWarehouse">新增仓库</el-button>
            </div>
            <el-table :data="warehouseList" v-loading="warehouseLoading" style="width: 100%;" class="data-table" stripe>
              <el-table-column prop="name" label="仓库名称" min-width="150" />
              <el-table-column prop="address" label="仓库地址" min-width="200" />
              <el-table-column prop="contact" label="联系人" width="120" />
              <el-table-column prop="phone" label="联系电话" width="140" />
              <el-table-column label="状态" width="100" align="center">
                <template #default="{ row }">
                  <el-switch
                    v-model="row.is_active"
                    active-color="#165DFF"
                    inactive-color="#9ca3af"
                    :loading="warehouseToggleLoading === row.id"
                    @change="handleToggleWarehouseStatus(row)"
                  />
                </template>
              </el-table-column>
              <el-table-column label="操作" width="150" fixed="right">
                <template #default="{ row }">
                  <el-button type="primary" link size="small" @click="handleEditWarehouse(row)">编辑</el-button>
                  <el-button type="danger" link size="small" @click="handleDeleteWarehouse(row)">删除</el-button>
                </template>
              </el-table-column>
            </el-table>
          </el-tab-pane>

          <el-tab-pane label="商品分类" name="categories">
            <div class="category-wrapper">
              <div class="category-tree-panel">
                <div class="panel-toolbar">
                  <el-input v-model="categorySearch" placeholder="搜索分类" clearable :prefix-icon="Search" style="width: 180px" @input="filterCategoryTree" />
                  <div class="toolbar-right">
                    <el-button 
                      :type="sortMode ? 'primary' : 'default'" 
                      :class="{ 'sort-active': sortMode }"
                      size="small"
                      @click="toggleSortMode"
                    >
                      {{ sortMode ? '完成排序' : '排序调整' }}
                    </el-button>
                    <el-button type="primary" :icon="Plus" size="small" @click="handleAddCategory(null)">新增一级分类</el-button>
                  </div>
                </div>
                <div class="tree-container" v-loading="categoryLoading">
                  <el-tree
                    ref="categoryTreeRef"
                    :data="categoryTreeData"
                    :props="{ children: 'children', label: 'name' }"
                    node-key="id"
                    :default-expanded-keys="expandedKeys"
                    highlight-current
                    :expand-on-click-node="false"
                    :filter-node-method="filterCategoryNode"
                    :draggable="sortMode"
                    :allow-drop="allowDrop"
                    :allow-drag="allowDrag"
                    @node-drop="handleNodeDrop"
                  >
                    <template #default="{ node, data }">
                      <div 
                        class="category-node" 
                        :class="{ 
                          'dragging': draggingNodeId === data.id, 
                          'sort-mode': sortMode, 
                          [`level-${data.level}`]: true,
                          'selected': selectedCategory?.id === data.id,
                          'has-children': data.children && data.children.length > 0,
                          'show-actions': shouldShowActions(data),
                          'is-parent': selectedCategory?.id === data.id,
                          'is-child': shouldShowActions(data) && selectedCategory?.id !== data.id
                        }"
                        @click.stop="handleCategoryNodeClick(data, node)"
                      >
                        <div class="node-info">
                          <el-icon 
                            v-if="data.children && data.children.length > 0" 
                            class="expand-icon"
                            :class="{ 'expanded': node.expanded }"
                          >
                            <ArrowRight />
                          </el-icon>
                          <span v-else class="expand-placeholder"></span>
                          <el-icon class="drag-handle" :class="{ 'active': sortMode }"><DCaret /></el-icon>
                          <span class="node-name">{{ data.name }}</span>
                          <span class="node-code" v-if="data.code">{{ data.code }}</span>
                        </div>
                        <div class="node-actions" :class="{ 'parent-actions': selectedCategory?.id === data.id, 'child-actions': shouldShowActions(data) && selectedCategory?.id !== data.id }" v-if="shouldShowActions(data)">
                          <el-switch
                            v-model="data.is_active"
                            size="small"
                            :loading="categoryToggleLoading === data.id"
                            @change="handleToggleCategoryStatus(data)"
                            @click.stop
                          />
                          <el-button v-if="data.level < 5" type="primary" size="small" @click.stop="handleAddCategory(data)">
                            <el-icon><Plus /></el-icon>增加
                          </el-button>
                          <el-button type="warning" size="small" @click.stop="handleEditCategory(data)">
                            <el-icon><Edit /></el-icon>编辑
                          </el-button>
                          <el-button type="danger" size="small" @click.stop="handleDeleteCategory(data)">
                            <el-icon><Delete /></el-icon>删除
                          </el-button>
                        </div>
                      </div>
                    </template>
                  </el-tree>
                  <el-empty v-if="!categoryLoading && categoryList.length === 0" description="暂无分类数据" :image-size="80" />
                </div>
              </div>
              <div class="category-detail-panel" v-if="selectedCategory">
                <div class="panel-title">分类详情</div>
                <div class="detail-list">
                  <div class="detail-row">
                    <span class="detail-label">分类名称</span>
                    <span class="detail-value name">{{ selectedCategory.name }}</span>
                  </div>
                  <div class="detail-row">
                    <span class="detail-label">分类编码</span>
                    <span class="detail-value code">{{ selectedCategory.code || '-' }}</span>
                  </div>
                  <div class="detail-row">
                    <span class="detail-label">分类层级</span>
                    <span class="detail-value level">{{ getCategoryLevelText(selectedCategory.level) }}</span>
                  </div>
                  <div class="detail-row">
                    <span class="detail-label">状态</span>
                    <div class="detail-value status">
                      <el-tag :type="selectedCategory.is_active ? 'success' : 'info'" size="small">
                        {{ selectedCategory.is_active ? '启用' : '停用' }}
                      </el-tag>
                    </div>
                  </div>
                  <div class="detail-row">
                    <span class="detail-label">子分类数</span>
                    <span class="detail-value count">{{ selectedCategory.children_count || 0 }} 个</span>
                  </div>
                  <div class="detail-row">
                    <span class="detail-label">商品数量</span>
                    <span class="detail-value goods-count">{{ selectedCategory.goods_count || 0 }} 个</span>
                  </div>
                  <div class="detail-row">
                    <span class="detail-label">创建人</span>
                    <span class="detail-value creator">{{ selectedCategory.created_by_name || '-' }}</span>
                  </div>
                  <div class="detail-row">
                    <span class="detail-label">创建时间</span>
                    <span class="detail-value time">{{ formatDateTime(selectedCategory.created_at) }}</span>
                  </div>
                  <div class="detail-row remark-row" v-if="selectedCategory.remark">
                    <span class="detail-label">备注</span>
                    <span class="detail-value remark">{{ selectedCategory.remark }}</span>
                  </div>
                </div>
              </div>
            </div>
          </el-tab-pane>
        </el-tabs>
      </div>
    </div>

    <!-- 计量单位弹窗 -->
    <el-dialog v-model="unitDialogVisible" :title="unitDialogTitle" width="400px" class="form-dialog" destroy-on-close>
      <el-form :model="unitForm" :rules="unitRules" ref="unitFormRef" label-width="100px">
        <el-form-item label="单位名称" prop="name">
          <el-input v-model="unitForm.name" placeholder="请输入单位名称" maxlength="50" />
        </el-form-item>
        <el-form-item label="状态">
          <el-switch v-model="unitForm.is_active" active-text="启用" inactive-text="禁用" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="unitDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleUnitSubmit" :loading="unitSubmitLoading">确定</el-button>
      </template>
    </el-dialog>

    <!-- 仓库弹窗 -->
    <el-dialog v-model="warehouseDialogVisible" :title="warehouseDialogTitle" width="500px" class="form-dialog" destroy-on-close>
      <el-form :model="warehouseForm" :rules="warehouseRules" ref="warehouseFormRef" label-width="100px">
        <el-form-item label="仓库名称" prop="name">
          <el-input v-model="warehouseForm.name" placeholder="请输入仓库名称" maxlength="100" />
        </el-form-item>
        <el-form-item label="仓库地址">
          <el-input v-model="warehouseForm.address" placeholder="请输入仓库地址" maxlength="200" />
        </el-form-item>
        <el-form-item label="联系人">
          <el-input v-model="warehouseForm.contact" placeholder="请输入联系人" maxlength="50" />
        </el-form-item>
        <el-form-item label="联系电话">
          <el-input v-model="warehouseForm.phone" placeholder="请输入联系电话" maxlength="20" />
        </el-form-item>
        <el-form-item label="状态">
          <el-switch v-model="warehouseForm.is_active" active-text="启用" inactive-text="禁用" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="warehouseDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleWarehouseSubmit" :loading="warehouseSubmitLoading">确定</el-button>
      </template>
    </el-dialog>

    <!-- 商品分类弹窗 -->
    <el-dialog v-model="categoryDialogVisible" :title="categoryDialogTitle" width="450px" class="form-dialog" destroy-on-close>
      <el-form :model="categoryForm" :rules="categoryRules" ref="categoryFormRef" label-width="80px">
        <el-form-item label="父分类" v-if="parentCategory">
          <el-input :model-value="parentCategory.name" disabled />
        </el-form-item>
        <el-form-item label="分类名称" prop="name">
          <el-input v-model="categoryForm.name" placeholder="请输入分类名称" maxlength="100" />
        </el-form-item>
        <el-form-item label="分类编码">
          <el-input v-model="categoryForm.code" placeholder="请输入分类编码（可选）" maxlength="50" />
        </el-form-item>
        <el-form-item label="状态">
          <el-switch v-model="categoryForm.is_active" active-text="启用" inactive-text="禁用" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="categoryForm.remark" type="textarea" :rows="2" placeholder="请输入备注（可选）" maxlength="200" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="categoryDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleCategorySubmit" :loading="categorySubmitLoading">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Edit, Delete, Search, DCaret, ArrowRight } from '@element-plus/icons-vue'
import { getUnits, createUnit, updateUnit, deleteUnit, getWarehouses, createWarehouse, updateWarehouse, deleteWarehouse, getCategories, getCategoryTree, getCategoryDetail, createCategory, updateCategory, deleteCategory, batchUpdateCategorySort } from '../../api/basic'
import request from '../../api/index'

const parseErrorMessage = (error) => {
  const errorData = error.response?.data
  if (!errorData) return error.message || '网络错误，请稍后重试'
  
  if (errorData.msg && typeof errorData.msg === 'string') {
    return errorData.msg
  }
  
  if (typeof errorData === 'object') {
    const messages = []
    for (const [field, msg] of Object.entries(errorData)) {
      if (field === 'msg' || field === 'code' || field === 'data') continue
      
      let message = ''
      if (Array.isArray(msg)) {
        message = msg.map(item => {
          if (typeof item === 'object' && item.string) {
            return item.string
          }
          return String(item)
        }).join('；')
      } else if (typeof msg === 'object' && msg.string) {
        message = msg.string
      } else if (typeof msg === 'string') {
        message = msg
      }
      
      if (message) {
        messages.push(message)
      }
    }
    
    if (messages.length > 0) {
      return messages.join('；')
    }
  }
  
  return '操作失败，请稍后重试'
}

const activeTab = ref('units')

const formatDateTime = (datetime) => {
  if (!datetime) return '-'
  return datetime.replace('T', ' ').substring(0, 19)
}

// 计量单位
const unitList = ref([])
const unitLoading = ref(false)
const unitSearch = ref('')
const unitDialogVisible = ref(false)
const unitDialogTitle = ref('')
const unitFormRef = ref(null)
const unitSubmitLoading = ref(false)
const unitEditingId = ref(null)
const unitToggleLoading = ref(null)
const unitForm = ref({ name: '', is_active: true })
const unitRules = { name: [{ required: true, message: '请输入单位名称', trigger: 'blur' }] }
const selectedUnit = ref(null)

const filteredUnitList = computed(() => {
  if (!unitSearch.value) return unitList.value
  const keyword = unitSearch.value.toLowerCase()
  return unitList.value.filter(item => 
    item.name.toLowerCase().includes(keyword)
  )
})

const handleUnitClick = (item) => {
  if (selectedUnit.value?.id === item.id) {
    selectedUnit.value = null
  } else {
    selectedUnit.value = item
  }
}

const loadUnits = async () => {
  unitLoading.value = true
  try {
    const params = { page_size: 1000 }
    if (unitSearch.value) params.search = unitSearch.value
    const res = await getUnits(params)
    unitList.value = res.data.items || res.data.results || []
  } catch (error) {
    ElMessage.error('加载计量单位失败')
  } finally {
    unitLoading.value = false
  }
}

const handleAddUnit = () => {
  unitDialogTitle.value = '新增计量单位'
  unitEditingId.value = null
  unitForm.value = { name: '', is_active: true }
  unitDialogVisible.value = true
}

const handleEditUnit = (row) => {
  unitDialogTitle.value = '编辑计量单位'
  unitEditingId.value = row.id
  unitForm.value = { name: row.name, is_active: row.is_active }
  unitDialogVisible.value = true
}

const handleDeleteUnit = async (row) => {
  try {
    await ElMessageBox.confirm(`确定删除计量单位「${row.name}」？`, '确认删除', { type: 'warning' })
    await deleteUnit(row.id)
    ElMessage.success('删除成功')
    loadUnits()
  } catch (error) {
    if (error === 'cancel') return
    const errorData = error.response?.data
    if (errorData?.data?.goods_list) {
      const goodsList = errorData.data.goods_list
      const suggestion = errorData.data.suggestion || ''
      ElMessageBox.alert(
        `<div style="line-height: 1.8;">
          <p style="margin-bottom: 12px; color: #303133;"><strong>${errorData.msg}</strong></p>
          <p style="margin-bottom: 8px; color: #606266;">关联商品：</p>
          <ul style="margin: 0 0 12px 20px; padding: 0; color: #909399;">
            ${goodsList.map(g => `<li>${g}</li>`).join('')}
          </ul>
          <p style="color: #E6A23C; font-size: 13px;">${suggestion}</p>
        </div>`,
        '删除失败',
        {
          dangerouslyUseHTMLString: true,
          confirmButtonText: '我知道了',
          type: 'warning'
        }
      )
    } else if (errorData?.msg) {
      ElMessage.error(errorData.msg)
    } else {
      ElMessage.error('删除失败：' + (error.message || '网络错误，请稍后重试'))
    }
  }
}

/**
 * 切换计量单位状态
 */
const handleToggleUnitStatus = async (row) => {
  const originalStatus = !row.is_active
  try {
    await ElMessageBox.confirm(
      `确定要${row.is_active ? '启用' : '禁用'}计量单位「${row.name}」吗？`,
      '提示',
      { confirmButtonText: '确定', cancelButtonText: '取消', type: 'warning' }
    )
    
    unitToggleLoading.value = row.id
    await updateUnit(row.id, { name: row.name, is_active: row.is_active })
    ElMessage.success('操作成功')
    loadUnits()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('操作失败：' + (error.response?.data?.msg || error.message || '未知错误'))
    }
    row.is_active = originalStatus
  } finally {
    unitToggleLoading.value = null
  }
}

const handleUnitSubmit = async () => {
  try { await unitFormRef.value.validate() } catch { return }
  unitSubmitLoading.value = true
  try {
    if (unitEditingId.value) {
      await updateUnit(unitEditingId.value, unitForm.value)
      ElMessage.success('更新成功')
    } else {
      await createUnit(unitForm.value)
      ElMessage.success('创建成功')
    }
    unitDialogVisible.value = false
    loadUnits()
  } catch (error) {
    ElMessage.error(parseErrorMessage(error))
  } finally {
    unitSubmitLoading.value = false
  }
}

// 仓库信息
const warehouseList = ref([])
const warehouseLoading = ref(false)
const warehouseSearch = ref('')
const warehouseDialogVisible = ref(false)
const warehouseDialogTitle = ref('')
const warehouseFormRef = ref(null)
const warehouseSubmitLoading = ref(false)
const warehouseEditingId = ref(null)
const warehouseToggleLoading = ref(null)
const warehouseForm = ref({ name: '', address: '', contact: '', phone: '', is_active: true })
const warehouseRules = { name: [{ required: true, message: '请输入仓库名称', trigger: 'blur' }] }

const loadWarehouses = async () => {
  warehouseLoading.value = true
  try {
    const params = { page_size: 1000 }
    if (warehouseSearch.value) params.search = warehouseSearch.value
    const res = await getWarehouses(params)
    warehouseList.value = res.data.items || res.data.results || []
  } catch (error) {
    ElMessage.error('加载仓库信息失败')
  } finally {
    warehouseLoading.value = false
  }
}

const handleAddWarehouse = () => {
  warehouseDialogTitle.value = '新增仓库'
  warehouseEditingId.value = null
  warehouseForm.value = { name: '', address: '', contact: '', phone: '', is_active: true }
  warehouseDialogVisible.value = true
}

const handleEditWarehouse = (row) => {
  warehouseDialogTitle.value = '编辑仓库'
  warehouseEditingId.value = row.id
  warehouseForm.value = { name: row.name, address: row.address || '', contact: row.contact || '', phone: row.phone || '', is_active: row.is_active }
  warehouseDialogVisible.value = true
}

const handleDeleteWarehouse = async (row) => {
  try {
    await ElMessageBox.confirm(`确定删除仓库「${row.name}」？`, '确认删除', { type: 'warning' })
    await deleteWarehouse(row.id)
    ElMessage.success('删除成功')
    loadWarehouses()
  } catch (error) {
    if (error === 'cancel') return
    const errorData = error.response?.data
    if (errorData?.data?.goods_list) {
      const goodsList = errorData.data.goods_list
      const suggestion = errorData.data.suggestion || ''
      ElMessageBox.alert(
        `<div style="line-height: 1.8;">
          <p style="margin-bottom: 12px; color: #303133;"><strong>${errorData.msg}</strong></p>
          <p style="margin-bottom: 8px; color: #606266;">库存记录：</p>
          <ul style="margin: 0 0 12px 20px; padding: 0; color: #909399;">
            ${goodsList.map(g => `<li>${g}</li>`).join('')}
          </ul>
          <p style="color: #E6A23C; font-size: 13px;">${suggestion}</p>
        </div>`,
        '删除失败',
        {
          dangerouslyUseHTMLString: true,
          confirmButtonText: '我知道了',
          type: 'warning'
        }
      )
    } else if (errorData?.msg) {
      ElMessage.error(errorData.msg)
    } else {
      ElMessage.error('删除失败：' + (error.message || '网络错误，请稍后重试'))
    }
  }
}

/**
 * 切换仓库状态
 */
const handleToggleWarehouseStatus = async (row) => {
  const originalStatus = !row.is_active
  try {
    await ElMessageBox.confirm(
      `确定要${row.is_active ? '启用' : '禁用'}仓库「${row.name}」吗？`,
      '提示',
      { confirmButtonText: '确定', cancelButtonText: '取消', type: 'warning' }
    )
    
    warehouseToggleLoading.value = row.id
    await updateWarehouse(row.id, { name: row.name, address: row.address, contact: row.contact, phone: row.phone, is_active: row.is_active })
    ElMessage.success('操作成功')
    loadWarehouses()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('操作失败：' + (error.response?.data?.msg || error.message || '未知错误'))
    }
    row.is_active = originalStatus
  } finally {
    warehouseToggleLoading.value = null
  }
}

const handleWarehouseSubmit = async () => {
  try { await warehouseFormRef.value.validate() } catch { return }
  warehouseSubmitLoading.value = true
  try {
    if (warehouseEditingId.value) {
      await updateWarehouse(warehouseEditingId.value, warehouseForm.value)
      ElMessage.success('更新成功')
    } else {
      await createWarehouse(warehouseForm.value)
      ElMessage.success('创建成功')
    }
    warehouseDialogVisible.value = false
    loadWarehouses()
  } catch (error) {
    ElMessage.error(parseErrorMessage(error))
  } finally {
    warehouseSubmitLoading.value = false
  }
}

// 商品分类
const categoryList = ref([])
const categoryLoading = ref(false)
const categorySearch = ref('')
const categoryDialogVisible = ref(false)
const categoryDialogTitle = ref('')
const categoryFormRef = ref(null)
const categorySubmitLoading = ref(false)
const categoryEditingId = ref(null)
const categoryToggleLoading = ref(null)
const categoryForm = ref({ name: '', code: '', parent: null, sort_order: 0, is_active: true, remark: '' })
const categoryRules = { name: [{ required: true, message: '请输入分类名称', trigger: 'blur' }] }
const categoryTreeRef = ref(null)
const selectedCategory = ref(null)
const parentCategory = ref(null)
const draggingNodeId = ref(null)
const hasSortChanges = ref(false)
const originalSortData = ref([])
const sortMode = ref(false)
const expandedKeys = ref([])

const categoryTreeData = computed(() => {
  const buildTree = (items, parentId = null) => {
    return items
      .filter(item => item.parent === parentId)
      .map(item => ({
        ...item,
        children: buildTree(items, item.id)
      }))
  }
  return buildTree(categoryList.value)
})

const getCategoryLevelText = (level) => {
  const levelMap = { 1: '一级分类', 2: '二级分类', 3: '三级分类', 4: '四级分类', 5: '五级分类' }
  return levelMap[level] || `${level}级分类`
}

const toggleSortMode = async () => {
  if (!sortMode.value) {
    sortMode.value = true
    return
  }
  
  if (hasSortChanges.value) {
    try {
      await ElMessageBox.confirm(
        '排序已修改，是否保存？',
        '保存确认',
        {
          confirmButtonText: '保存',
          cancelButtonText: '不保存',
          distinguishCancelAndClose: true,
          type: 'warning'
        }
      )
      await saveSortChanges()
    } catch (action) {
      if (action === 'cancel') {
        cancelSortChanges()
      }
    }
  } else {
    sortMode.value = false
  }
}

const loadCategories = async () => {
  categoryLoading.value = true
  try {
    const res = await getCategories({ page_size: 1000 })
    categoryList.value = res.data.items || res.data.results || []
    originalSortData.value = JSON.parse(JSON.stringify(categoryList.value.map(item => ({
      id: item.id,
      parent: item.parent,
      sort_order: item.sort_order
    }))))
    hasSortChanges.value = false
  } catch (error) {
    ElMessage.error('加载商品分类失败')
  } finally {
    categoryLoading.value = false
  }
}

const allowDrag = (draggingNode) => {
  if (!sortMode.value) return false
  draggingNodeId.value = draggingNode.data.id
  return true
}

const allowDrop = (draggingNode, dropNode, type) => {
  if (type === 'inner') {
    return false
  }
  const draggingParent = draggingNode.data.parent
  const dropParent = dropNode.data.parent
  if (draggingParent !== dropParent) {
    return false
  }
  return true
}

const handleNodeDrop = (draggingNode, dropNode, dropType, ev) => {
  draggingNodeId.value = null
  hasSortChanges.value = true
  const updateTreeData = (nodes, parentId = null) => {
    nodes.forEach((node, index) => {
      const item = categoryList.value.find(c => c.id === node.id)
      if (item) {
        item.parent = parentId
        item.sort_order = index
        item.level = parentId ? (categoryList.value.find(c => c.id === parentId)?.level || 0) + 1 : 1
      }
      if (node.children && node.children.length > 0) {
        updateTreeData(node.children, node.id)
      }
    })
  }
  updateTreeData(categoryTreeData.value)
}

const saveSortChanges = async () => {
  const sortList = categoryList.value.map(item => ({
    id: item.id,
    parent: item.parent,
    sort_order: item.sort_order
  }))
  
  try {
    await batchUpdateCategorySort({ sort_list: sortList })
    hasSortChanges.value = false
    sortMode.value = false
    originalSortData.value = JSON.parse(JSON.stringify(sortList))
    loadCategories()
    ElMessage.success('排序保存成功')
  } catch (error) {
    ElMessage.error('保存排序失败：' + (error.response?.data?.msg || error.message))
    throw error
  }
}

const cancelSortChanges = () => {
  categoryList.value.forEach(item => {
    const original = originalSortData.value.find(o => o.id === item.id)
    if (original) {
      item.parent = original.parent
      item.sort_order = original.sort_order
    }
  })
  hasSortChanges.value = false
  sortMode.value = false
}

const handleToggleCategoryStatus = async (row) => {
  const originalStatus = !row.is_active
  
  if (!row.is_active) {
    const childrenCount = countAllChildren(row)
    if (childrenCount > 0) {
      try {
        await ElMessageBox.confirm(
          `禁用该分类将同时禁用其下的 ${childrenCount} 个子分类，是否继续？`,
          '确认禁用',
          {
            confirmButtonText: '确定禁用',
            cancelButtonText: '取消',
            type: 'warning'
          }
        )
      } catch {
        row.is_active = originalStatus
        return
      }
    }
  }
  
  categoryToggleLoading.value = row.id
  try {
    const res = await request.post(`/basic/categories/${row.id}/update_status/`, {
      is_active: row.is_active,
      cascade: true
    })
    
    ElMessage.success(res.msg || (row.is_active ? '已启用' : '已停用'))
    
    if (selectedCategory.value?.id === row.id) {
      selectedCategory.value.is_active = row.is_active
    }
    
    if (!row.is_active && res.data?.affected_ids?.length > 1) {
      updateChildrenStatus(row, false)
    }
    
    await loadCategories()
  } catch (error) {
    row.is_active = originalStatus
    ElMessage.error('操作失败：' + (error.response?.data?.msg || error.message))
  } finally {
    categoryToggleLoading.value = null
  }
}

const countAllChildren = (category) => {
  let count = 0
  if (category.children && category.children.length > 0) {
    count += category.children.length
    category.children.forEach(child => {
      count += countAllChildren(child)
    })
  }
  return count
}

const updateChildrenStatus = (category, status) => {
  if (category.children && category.children.length > 0) {
    category.children.forEach(child => {
      child.is_active = status
      updateChildrenStatus(child, status)
    })
  }
}

const shouldShowActions = (data) => {
  if (!selectedCategory.value) return false
  
  if (selectedCategory.value.id === data.id) {
    return true
  }
  
  return isDescendantOf(data.id, selectedCategory.value.id, categoryTreeData.value)
}

const isDescendantOf = (nodeId, parentId, treeData) => {
  for (const node of treeData) {
    if (node.id === parentId) {
      return findNodeById(nodeId, node.children || [])
    }
    const found = isDescendantOf(nodeId, parentId, node.children || [])
    if (found) return true
  }
  return false
}

const findNodeById = (nodeId, nodes) => {
  for (const node of nodes) {
    if (node.id === nodeId) return true
    if (findNodeById(nodeId, node.children || [])) return true
  }
  return false
}

const filterCategoryTree = () => {
  categoryTreeRef.value?.filter(categorySearch.value)
}

const filterCategoryNode = (value, data) => {
  if (!value) return true
  return data.name.includes(value) || (data.code && data.code.includes(value.toUpperCase()))
}

const handleCategoryNodeClick = async (data, node) => {
  if (selectedCategory.value?.id === data.id) {
    if (data.children && data.children.length > 0) {
      node.expanded = !node.expanded
    }
    return
  }
  
  selectedCategory.value = data
  
  if (data.children && data.children.length > 0) {
    node.expanded = true
  }
  
  try {
    const res = await getCategoryDetail(data.id)
    if (selectedCategory.value?.id === data.id) {
      selectedCategory.value = res.data
    }
  } catch (error) {
    console.error('加载分类详情失败', error)
  }
}

const handleAddCategory = (parent) => {
  parentCategory.value = parent
  categoryDialogTitle.value = parent ? `新增子分类 - ${parent.name}` : '新增一级分类'
  categoryEditingId.value = null
  categoryForm.value = { name: '', code: '', parent: parent?.id || null, sort_order: 0, is_active: true, remark: '' }
  categoryDialogVisible.value = true
}

const handleEditCategory = async (row) => {
  parentCategory.value = row.parent ? { id: row.parent, name: row.parent_name } : null
  categoryDialogTitle.value = '编辑商品分类'
  categoryEditingId.value = row.id
  try {
    const res = await getCategoryDetail(row.id)
    categoryForm.value = { 
      name: res.data.name, 
      code: res.data.code || '', 
      parent: res.data.parent, 
      sort_order: res.data.sort_order || 0, 
      is_active: res.data.is_active,
      remark: res.data.remark || ''
    }
    categoryDialogVisible.value = true
  } catch (error) {
    ElMessage.error('加载分类信息失败')
  }
}

const handleDeleteCategory = async (row) => {
  try {
    await ElMessageBox.confirm(`确定删除商品分类「${row.name}」？`, '确认删除', { type: 'warning' })
    await deleteCategory(row.id)
    ElMessage.success('删除成功')
    if (selectedCategory.value?.id === row.id) {
      selectedCategory.value = null
    }
    loadCategories()
  } catch (error) {
    if (error === 'cancel') return
    const errorData = error.response?.data
    if (errorData?.msg) {
      ElMessage.error(errorData.msg)
    } else {
      ElMessage.error('删除失败：' + (error.message || '网络错误，请稍后重试'))
    }
  }
}

const handleCategorySubmit = async () => {
  try { await categoryFormRef.value.validate() } catch { return }
  categorySubmitLoading.value = true
  try {
    const submitData = {
      name: categoryForm.value.name.trim(),
      code: categoryForm.value.code?.trim().toUpperCase() || '',
      parent: categoryForm.value.parent || null,
      sort_order: categoryForm.value.sort_order,
      is_active: categoryForm.value.is_active,
      remark: categoryForm.value.remark?.trim() || ''
    }
    if (categoryEditingId.value) {
      await updateCategory(categoryEditingId.value, submitData)
      ElMessage.success('更新成功')
    } else {
      await createCategory(submitData)
      ElMessage.success('创建成功')
    }
    categoryDialogVisible.value = false
    loadCategories()
  } catch (error) {
    const msg = error.response?.data?.msg || error.message || '操作失败'
    ElMessage.error(msg)
  } finally {
    categorySubmitLoading.value = false
  }
}

onMounted(() => {
  loadUnits()
  loadWarehouses()
  loadCategories()
})
</script>

<style scoped>
.params-page {
  height: 100%;
  width: 100%;
  display: flex;
  flex-direction: column;
  padding: 8px;
  overflow: hidden;
}

.page-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  width: 100%;
}

.table-card {
  flex: 1;
  display: flex;
  flex-direction: column;
  background-color: var(--color-white);
  border-radius: var(--border-radius-lg);
  border: 1px solid var(--color-border-light);
  box-shadow: var(--shadow-sm);
  overflow: hidden;
  min-height: 0;
}

.params-tabs {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.params-tabs :deep(.el-tabs__header) {
  margin: 0;
  padding: 0 var(--spacing-lg);
  background-color: var(--color-bg-light);
}

.params-tabs :deep(.el-tabs__content) {
  flex: 1;
  overflow: auto;
  padding: var(--spacing-lg);
}

.tab-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-md);
}

.search-box {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
}

.data-table {
  --el-table-header-bg-color: var(--color-bg-light);
}

.form-dialog :deep(.el-dialog__header) {
  border-bottom: 1px solid var(--color-border-light);
  padding: var(--spacing-lg) var(--spacing-xl);
}

.form-dialog :deep(.el-dialog__body) {
  padding: var(--spacing-xl);
}

.form-dialog :deep(.el-dialog__footer) {
  border-top: 1px solid var(--color-border-light);
  padding: var(--spacing-lg) var(--spacing-xl);
}

.text-muted {
  color: var(--color-text-placeholder, #9ca3af);
  font-style: italic;
}

.category-wrapper {
  display: flex;
  gap: 16px;
  height: 100%;
}

.unit-wrapper {
  display: flex;
  gap: 16px;
  height: 100%;
}

.unit-list-panel {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  background: #fff;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04);
  min-width: 0;
}

.unit-detail-panel {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: #fff;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04);
  min-width: 0;
}

.unit-detail-panel .panel-title {
  padding: 14px 16px;
  font-size: 14px;
  font-weight: 600;
  color: #303133;
  border-bottom: 1px solid #e4e7ed;
  background: linear-gradient(135deg, #f0f5ff 0%, #e6f4ff 100%);
  display: flex;
  align-items: center;
  gap: 8px;
}

.unit-detail-panel .panel-title::before {
  content: '';
  width: 3px;
  height: 14px;
  background: #165DFF;
  border-radius: 2px;
}

.unit-grid-container {
  flex: 1;
  overflow: auto;
  padding: 12px;
}

.unit-grid {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.unit-card {
  background: #fff;
  border: 1px solid #e4e7ed;
  border-radius: 6px;
  padding: 0 12px;
  height: 36px;
  line-height: 36px;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  flex-direction: row;
  justify-content: space-between;
  align-items: center;
  gap: 10px;
  white-space: nowrap;
  color: var(--sidebar-text-secondary, #909399);
  font-size: 14px;
  position: relative;
}

.unit-card:hover {
  background-color: var(--color-primary-light, #e6f4ff);
  border-color: #165DFF;
  color: var(--sidebar-text-primary, #303133);
}

.unit-card.selected {
  background-color: var(--color-primary-light, #e6f4ff);
  border-color: var(--color-primary, #165DFF);
  color: var(--color-primary, #165DFF);
  font-weight: 600;
}

.unit-card.selected::before {
  content: '';
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 3px;
  height: 16px;
  background-color: var(--color-primary, #165DFF);
  border-radius: 0 2px 2px 0;
}

.unit-card.inactive {
  opacity: 0.6;
}

.unit-card.inactive .unit-name {
  color: #909399;
}

.unit-name {
  font-size: 14px;
  font-weight: 500;
  color: #303133;
  flex-shrink: 0;
  overflow: hidden;
  text-overflow: ellipsis;
}

.unit-symbol {
  font-size: 12px;
  color: #909399;
  background: #f4f4f5;
  padding: 2px 6px;
  border-radius: 3px;
  font-family: 'Monaco', 'Consolas', monospace;
  margin-left: 8px;
}

.unit-card.selected .unit-name {
  color: #165DFF;
  font-weight: 600;
}

.unit-actions {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-shrink: 0;
}

.unit-actions .el-switch {
  margin-right: 4px;
}

.unit-actions .el-button {
  padding: 5px 10px;
  font-size: 12px;
  white-space: nowrap;
}

.category-tree-panel {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: #fff;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04);
}

.panel-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 14px;
  border-bottom: 1px solid #e4e7ed;
  background: linear-gradient(135deg, #fafbfc 0%, #f5f7fa 100%);
}

.toolbar-right {
  display: flex;
  align-items: center;
  gap: 8px;
}

.toolbar-right .el-button {
  font-weight: 500;
}

.sort-active {
  background: linear-gradient(135deg, #165DFF 0%, #4080ff 100%);
  border-color: #165DFF;
  box-shadow: 0 2px 8px rgba(22, 93, 255, 0.3);
}

.sort-active:hover {
  background: linear-gradient(135deg, #4080ff 0%, #165DFF 100%);
}

.tree-container {
  flex: 1;
  overflow: auto;
  padding: 12px;
}

.tree-container :deep(.el-tree-node__expand-icon) {
  display: none;
}

.tree-container :deep(.el-tree-node__content) {
  height: auto;
  padding: 4px 0;
}

.tree-container :deep(.el-tree-node.is-current > .el-tree-node__content) {
  background: transparent;
}

.expand-icon {
  width: 18px;
  height: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 700;
  color: #909399;
  transition: transform 0.2s;
  cursor: pointer;
}

.expand-icon.expanded {
  transform: rotate(90deg);
}

.expand-placeholder {
  width: 18px;
  height: 18px;
}

.category-node {
  flex: 1;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 6px 10px;
  margin: 2px 0;
  border: 1px solid transparent;
  border-radius: 6px;
  transition: all 0.2s;
  cursor: pointer;
  box-sizing: border-box;
  overflow: hidden;
}

.category-node:hover {
  border-color: #165DFF;
  background: #f5f9ff;
}

.category-node.selected {
  border-color: #165DFF;
  background: #e6f4ff;
}

.category-node.level-1 {
  background: #fafbfc;
  border: 1px solid #e4e7ed;
}

.category-node.level-1:hover {
  border-color: #165DFF;
  background: #f0f5ff;
}

.category-node.level-1.selected {
  border-color: #165DFF;
  background: #e6f4ff;
}

.category-node.level-2 {
  background: #fff;
}

.category-node.level-3,
.category-node.level-4,
.category-node.level-5 {
  background: #fff;
}

.category-node.sort-mode {
  background: #fafafa;
}

.category-node.dragging {
  background: #e6f4ff !important;
  border-color: #165DFF !important;
  box-shadow: 0 4px 12px rgba(22, 93, 255, 0.25);
  transform: scale(1.01);
  z-index: 100;
}

.tree-container :deep(.el-tree-node.is-drop-inner > .el-tree-node__content) {
  background: #f0f5ff;
  border: 2px dashed #165DFF;
}

.tree-container :deep(.el-tree__drop-indicator) {
  height: 2px;
  background: #165DFF;
  margin-left: 24px;
}

.tree-container :deep(.el-tree-node__content) {
  position: relative;
}

.tree-container :deep(.el-tree-node.is-dragging > .el-tree-node__content) {
  opacity: 0.5;
}

.node-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.drag-handle {
  cursor: default;
  color: #dcdfe6;
  font-size: 14px;
  transition: all 0.15s ease;
  padding: 4px;
  border-radius: 4px;
  flex-shrink: 0;
}

.drag-handle.active {
  cursor: grab;
  color: #909399;
}

.drag-handle.active:hover {
  color: #165DFF;
  background: rgba(22, 93, 255, 0.1);
}

.drag-handle.active:active {
  cursor: grabbing;
  background: rgba(22, 93, 255, 0.15);
}

.node-name {
  font-size: 13px;
  color: #303133;
}

.category-node.level-1 .node-name {
  font-size: 14px;
  font-weight: 600;
  color: #1a1a1a;
}

.category-node.level-2 .node-name {
  font-size: 13px;
  font-weight: 500;
  color: #303133;
}

.category-node.level-3 .node-name,
.category-node.level-4 .node-name,
.category-node.level-5 .node-name {
  font-size: 13px;
  font-weight: 400;
  color: #606266;
}

.node-code {
  font-size: 11px;
  color: #909399;
  background: #f4f4f5;
  padding: 1px 6px;
  border-radius: 3px;
  font-family: 'Monaco', 'Consolas', monospace;
}

.node-actions {
  display: flex;
  align-items: center;
  gap: 6px;
  flex-shrink: 0;
}

.category-node.show-actions .node-actions {
  opacity: 1 !important;
  visibility: visible !important;
}

/* 父级按钮样式 - 更大、更醒目 */
.node-actions.parent-actions {
  gap: 8px;
  padding: 4px 8px;
  background: linear-gradient(135deg, #f0f5ff 0%, #e6f4ff 100%);
  border-radius: 6px;
  border: 1px solid #bae0ff;
}

.node-actions.parent-actions .el-switch {
  transform: scale(1.1);
}

.node-actions.parent-actions .el-button {
  padding: 6px 12px;
  font-size: 13px;
  font-weight: 500;
  border-radius: 4px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.node-actions.parent-actions .el-button--primary {
  background: linear-gradient(135deg, #165DFF 0%, #4080ff 100%);
  border-color: #165DFF;
}

.node-actions.parent-actions .el-button--primary:hover {
  background: linear-gradient(135deg, #0d47a1 0%, #165DFF 100%);
}

.node-actions.parent-actions .el-button--warning {
  background: linear-gradient(135deg, #ff9800 0%, #ffb74d 100%);
  border-color: #ff9800;
}

.node-actions.parent-actions .el-button--warning:hover {
  background: linear-gradient(135deg, #f57c00 0%, #ff9800 100%);
}

.node-actions.parent-actions .el-button--danger {
  background: linear-gradient(135deg, #f44336 0%, #ef5350 100%);
  border-color: #f44336;
}

.node-actions.parent-actions .el-button--danger:hover {
  background: linear-gradient(135deg, #d32f2f 0%, #f44336 100%);
}

/* 子级按钮样式 - 更小、更柔和 */
.node-actions.child-actions {
  gap: 4px;
}

.node-actions.child-actions .el-switch {
  transform: scale(0.9);
}

.node-actions.child-actions .el-button {
  padding: 3px 6px;
  font-size: 11px;
  font-weight: 400;
  border-radius: 3px;
  opacity: 0.85;
}

.node-actions.child-actions .el-button--primary {
  background-color: #165DFF;
  border-color: #165DFF;
  color: #FFFFFF;
}

.node-actions.child-actions .el-button--primary:hover {
  background-color: #4080ff;
  border-color: #4080ff;
  color: #FFFFFF;
}

.node-actions.child-actions .el-button--warning {
  background-color: #fff7e6;
  border-color: #ffd591;
  color: #d46b08;
}

.node-actions.child-actions .el-button--warning:hover {
  background-color: #ffe7ba;
  border-color: #ffc069;
  color: #ad4e00;
}

.node-actions.child-actions .el-button--danger {
  background-color: #fff1f0;
  border-color: #ffa39e;
  color: #cf1322;
}

.node-actions.child-actions .el-button--danger:hover {
  background-color: #ffccc7;
  border-color: #ff7875;
  color: #a8071a;
}

.node-actions .el-button {
  padding: 4px 8px;
  font-size: 12px;
  box-sizing: border-box;
  overflow: hidden;
  transition: all 0.2s ease;
}

.node-actions .el-button .el-icon {
  margin-right: 2px;
}

.node-actions .el-switch {
  margin-right: 4px;
}

.category-detail-panel {
  width: 260px;
  background: #fff;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04);
}

.category-detail-panel .panel-title {
  padding: 14px 16px;
  font-size: 14px;
  font-weight: 600;
  color: #303133;
  border-bottom: 1px solid #e4e7ed;
  background: linear-gradient(135deg, #f0f5ff 0%, #e6f4ff 100%);
  display: flex;
  align-items: center;
  gap: 8px;
}

.category-detail-panel .panel-title::before {
  content: '';
  width: 3px;
  height: 14px;
  background: #165DFF;
  border-radius: 2px;
}

.detail-list {
  padding: 12px 16px;
}

.detail-row {
  display: flex;
  align-items: flex-start;
  padding: 8px 0;
  border-bottom: 1px solid #f5f7fa;
}

.detail-row:last-child {
  border-bottom: none;
}

.detail-row.remark-row {
  flex-direction: column;
  gap: 6px;
}

.detail-row.remark-row .detail-value {
  width: 100%;
  background: #fafafa;
  padding: 8px 10px;
  border-radius: 4px;
  font-size: 12px;
  line-height: 1.6;
}

.detail-label {
  width: 60px;
  font-size: 12px;
  color: #909399;
  flex-shrink: 0;
  text-align: right;
  padding-right: 10px;
}

.detail-value {
  flex: 1;
  font-size: 13px;
  color: #303133;
  font-weight: 500;
  min-width: 0;
}

.detail-value.name {
  font-weight: 600;
  color: #165DFF;
}

.detail-value.code {
  font-family: 'Monaco', 'Consolas', monospace;
  font-size: 12px;
  background: #f4f4f5;
  padding: 2px 6px;
  border-radius: 3px;
}

.detail-value.level {
  color: #165DFF;
}

.detail-value.count {
  font-weight: 600;
  color: #ff9800;
}

.detail-value.goods-count {
  font-weight: 600;
  color: #165DFF;
}

.detail-value.status {
  display: flex;
  justify-content: center;
}

.detail-value.creator {
  color: #606266;
}

.detail-value.time {
  font-size: 12px;
  color: #909399;
  font-weight: 400;
}

.detail-value.path {
  color: #606266;
  word-break: break-all;
  font-weight: 400;
  font-size: 12px;
  line-height: 1.5;
}
</style>

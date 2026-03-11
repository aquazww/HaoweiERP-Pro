<template>
  <div class="common-page params-page">
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
            <div class="warehouse-wrapper">
              <div class="warehouse-list-panel">
                <div class="panel-toolbar">
                  <el-input v-model="warehouseSearch" placeholder="搜索仓库名称" clearable :prefix-icon="Search" style="width: 180px" @keyup.enter="loadWarehouses" />
                  <div class="toolbar-right">
                    <el-button type="primary" :icon="Plus" size="small" @click="handleAddWarehouse">新增仓库</el-button>
                  </div>
                </div>
                <div class="warehouse-grid-container" v-loading="warehouseLoading">
                  <div class="warehouse-grid">
                    <div 
                      v-for="item in filteredWarehouseList" 
                      :key="item.id" 
                      class="warehouse-card"
                      :class="{ 'selected': selectedWarehouse?.id === item.id, 'inactive': !item.is_active }"
                      @click="handleWarehouseClick(item)"
                    >
                      <span class="warehouse-name">{{ item.name }}</span>
                      <span class="warehouse-address" v-if="item.address">{{ item.address }}</span>
                      <div class="warehouse-actions" v-if="selectedWarehouse?.id === item.id" @click.stop>
                        <el-switch
                          v-model="item.is_active"
                          size="small"
                          :loading="warehouseToggleLoading === item.id"
                          @change="handleToggleWarehouseStatus(item)"
                        />
                        <el-button type="warning" size="small" @click="handleEditWarehouse(item)">
                          <el-icon><Edit /></el-icon>编辑
                        </el-button>
                        <el-button type="danger" size="small" @click="handleDeleteWarehouse(item)">
                          <el-icon><Delete /></el-icon>删除
                        </el-button>
                      </div>
                    </div>
                  </div>
                  <el-empty v-if="!warehouseLoading && filteredWarehouseList.length === 0" description="暂无仓库数据" :image-size="80" />
                </div>
              </div>
              <div class="warehouse-detail-panel" v-if="selectedWarehouse">
                <div class="panel-title">仓库详情</div>
                <div class="detail-list">
                  <div class="detail-row">
                    <span class="detail-label">仓库名称</span>
                    <span class="detail-value name">{{ selectedWarehouse.name }}</span>
                  </div>
                  <div class="detail-row" v-if="selectedWarehouse.address">
                    <span class="detail-label">仓库地址</span>
                    <span class="detail-value address">{{ selectedWarehouse.address }}</span>
                  </div>
                  <div class="detail-row" v-if="selectedWarehouse.contact">
                    <span class="detail-label">联系人</span>
                    <span class="detail-value contact">{{ selectedWarehouse.contact }}</span>
                  </div>
                  <div class="detail-row" v-if="selectedWarehouse.phone">
                    <span class="detail-label">联系电话</span>
                    <span class="detail-value phone">{{ selectedWarehouse.phone }}</span>
                  </div>
                  <div class="detail-row">
                    <span class="detail-label">状态</span>
                    <div class="detail-value status">
                      <el-tag :type="selectedWarehouse.is_active ? 'success' : 'info'" size="small">
                        {{ selectedWarehouse.is_active ? '启用' : '停用' }}
                      </el-tag>
                    </div>
                  </div>
                  <div class="detail-row">
                    <span class="detail-label">创建人</span>
                    <span class="detail-value creator">{{ selectedWarehouse.created_by_name || '-' }}</span>
                  </div>
                  <div class="detail-row">
                    <span class="detail-label">创建时间</span>
                    <span class="detail-value time">{{ formatDateTime(selectedWarehouse.created_at) }}</span>
                  </div>
                  <div class="detail-row">
                    <span class="detail-label">更新时间</span>
                    <span class="detail-value time">{{ formatDateTime(selectedWarehouse.updated_at) }}</span>
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
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Edit, Delete, Search } from '@element-plus/icons-vue'
import { getUnits, createUnit, updateUnit, deleteUnit, getWarehouses, createWarehouse, updateWarehouse, deleteWarehouse } from '../../api/basic'

const activeTab = ref('units')

const formatDateTime = (datetime) => {
  if (!datetime) return '-'
  return datetime.replace('T', ' ').substring(0, 19)
}

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
const selectedWarehouse = ref(null)

const filteredWarehouseList = computed(() => {
  if (!warehouseSearch.value) return warehouseList.value
  const keyword = warehouseSearch.value.toLowerCase()
  return warehouseList.value.filter(item => 
    item.name.toLowerCase().includes(keyword) ||
    (item.address && item.address.toLowerCase().includes(keyword))
  )
})

const handleWarehouseClick = (item) => {
  if (selectedWarehouse.value?.id === item.id) {
    selectedWarehouse.value = null
  } else {
    selectedWarehouse.value = item
  }
}

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
    if (errorData?.msg) {
      ElMessage.error(errorData.msg)
    } else {
      ElMessage.error('删除失败：' + (error.message || '网络错误，请稍后重试'))
    }
  }
}

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

onMounted(() => {
  loadUnits()
  loadWarehouses()
})
</script>

<style scoped>
.params-page .params-tabs {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.params-page .params-tabs :deep(.el-tabs__header) {
  margin: 0;
  padding: 0 var(--spacing-lg);
  background-color: var(--color-bg-light);
}

.params-page .params-tabs :deep(.el-tabs__content) {
  flex: 1;
  overflow: auto;
  padding: var(--spacing-lg);
}

.params-page .tab-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-md);
}

.params-page .search-box {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
}

.params-page .unit-wrapper {
  display: flex;
  gap: 16px;
  height: 100%;
}

.params-page .unit-list-panel {
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

.params-page .unit-detail-panel {
  width: 280px;
  display: flex;
  flex-direction: column;
  background: #fff;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04);
}

.params-page .unit-detail-panel .panel-title {
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

.params-page .unit-detail-panel .panel-title::before {
  content: '';
  width: 3px;
  height: 14px;
  background: #165DFF;
  border-radius: 2px;
}

.params-page .unit-grid-container {
  flex: 1;
  overflow: auto;
  padding: 12px;
}

.params-page .unit-grid {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.params-page .unit-card {
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

.params-page .unit-card:hover {
  background-color: var(--color-primary-light, #e6f4ff);
  border-color: #165DFF;
  color: var(--sidebar-text-primary, #303133);
}

.params-page .unit-card.selected {
  background-color: var(--color-primary-light, #e6f4ff);
  border-color: var(--color-primary, #165DFF);
  color: var(--color-primary, #165DFF);
  font-weight: 600;
}

.params-page .unit-card.selected::before {
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

.params-page .unit-card.inactive {
  opacity: 0.6;
}

.params-page .unit-card.inactive .unit-name {
  color: #909399;
}

.params-page .unit-name {
  font-size: 14px;
  font-weight: 500;
  color: #303133;
  flex-shrink: 0;
  overflow: hidden;
  text-overflow: ellipsis;
}

.params-page .unit-symbol {
  font-size: 12px;
  color: #909399;
  background: #f4f4f5;
  padding: 2px 6px;
  border-radius: 3px;
  font-family: 'Monaco', 'Consolas', monospace;
  margin-left: 8px;
}

.params-page .unit-card.selected .unit-name {
  color: #165DFF;
  font-weight: 600;
}

.params-page .unit-actions {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-shrink: 0;
}

.params-page .unit-actions .el-switch {
  margin-right: 4px;
}

.params-page .unit-actions .el-button {
  padding: 5px 10px;
  font-size: 12px;
  white-space: nowrap;
}

.params-page .panel-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 14px;
  border-bottom: 1px solid #e4e7ed;
  background: linear-gradient(135deg, #fafbfc 0%, #f5f7fa 100%);
}

.params-page .toolbar-right {
  display: flex;
  align-items: center;
  gap: 8px;
}

.params-page .detail-list {
  padding: 12px 16px;
}

.params-page .detail-row {
  display: flex;
  align-items: flex-start;
  padding: 8px 0;
  border-bottom: 1px solid #f5f7fa;
}

.params-page .detail-row:last-child {
  border-bottom: none;
}

.params-page .detail-label {
  width: 60px;
  font-size: 12px;
  color: #909399;
  flex-shrink: 0;
  text-align: right;
  padding-right: 10px;
}

.params-page .detail-value {
  flex: 1;
  font-size: 13px;
  color: #303133;
  font-weight: 500;
  min-width: 0;
}

.params-page .detail-value.name {
  font-weight: 600;
  color: #165DFF;
}

.params-page .detail-value.status {
  display: flex;
  justify-content: center;
}

.params-page .detail-value.creator {
  color: #606266;
}

.params-page .detail-value.time {
  font-size: 12px;
  color: #909399;
  font-weight: 400;
}

/* 仓库卡片布局样式 */
.params-page .warehouse-wrapper {
  display: flex;
  gap: 16px;
  height: 100%;
}

.params-page .warehouse-list-panel {
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

.params-page .warehouse-detail-panel {
  width: 320px;
  display: flex;
  flex-direction: column;
  background: #fff;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04);
}

.params-page .warehouse-detail-panel .panel-title {
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

.params-page .warehouse-detail-panel .panel-title::before {
  content: '';
  width: 3px;
  height: 14px;
  background: #165DFF;
  border-radius: 2px;
}

.params-page .warehouse-grid-container {
  flex: 1;
  overflow: auto;
  padding: 12px;
}

.params-page .warehouse-grid {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.params-page .warehouse-card {
  background: #fff;
  border: 1px solid #e4e7ed;
  border-radius: 6px;
  padding: 10px 12px;
  min-height: 44px;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: 4px;
  position: relative;
  color: var(--sidebar-text-secondary, #909399);
}

.params-page .warehouse-card:hover {
  background-color: var(--color-primary-light, #e6f4ff);
  border-color: #165DFF;
  color: var(--sidebar-text-primary, #303133);
}

.params-page .warehouse-card.selected {
  background-color: var(--color-primary-light, #e6f4ff);
  border-color: var(--color-primary, #165DFF);
}

.params-page .warehouse-card.selected::before {
  content: '';
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 3px;
  height: 20px;
  background-color: var(--color-primary, #165DFF);
  border-radius: 0 2px 2px 0;
}

.params-page .warehouse-card.inactive {
  opacity: 0.6;
}

.params-page .warehouse-card.inactive .warehouse-name {
  color: #909399;
}

.params-page .warehouse-name {
  font-size: 14px;
  font-weight: 500;
  color: #303133;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.params-page .warehouse-address {
  font-size: 12px;
  color: #909399;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.params-page .warehouse-card.selected .warehouse-name {
  color: #165DFF;
  font-weight: 600;
}

.params-page .warehouse-actions {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-shrink: 0;
  margin-top: 8px;
  padding-top: 8px;
  border-top: 1px solid #f0f0f0;
}

.params-page .warehouse-actions .el-switch {
  margin-right: 4px;
}

.params-page .warehouse-actions .el-button {
  padding: 5px 10px;
  font-size: 12px;
  white-space: nowrap;
}

.params-page .detail-value.address {
  word-break: break-all;
  line-height: 1.5;
}

.params-page .detail-value.contact,
.params-page .detail-value.phone {
  color: #606266;
}

/* 响应式布局 */
@media screen and (max-width: 1200px) {
  .params-page .warehouse-detail-panel {
    width: 280px;
  }
}

@media screen and (max-width: 992px) {
  .params-page .warehouse-wrapper {
    flex-direction: column;
  }
  
  .params-page .warehouse-list-panel {
    min-height: 300px;
  }
  
  .params-page .warehouse-detail-panel {
    width: 100%;
  }
}
</style>

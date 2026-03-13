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

          <el-tab-pane label="公司信息" name="company">
            <div class="company-wrapper">
              <div class="company-form-panel">
                <div class="panel-toolbar">
                  <span class="panel-title-text">公司基本信息</span>
                  <div class="toolbar-right">
                    <el-button type="primary" size="small" @click="handleSaveCompany" :loading="companySubmitLoading">保存设置</el-button>
                  </div>
                </div>
                <div class="company-form-container" v-loading="companyLoading">
                  <el-form :model="companyForm" :rules="companyRules" ref="companyFormRef" label-width="90px" size="small">
                    <!-- 基本信息卡片 -->
                    <div class="info-card">
                      <div class="card-header">
                        <div class="card-icon basic-icon"></div>
                        <span class="card-title">基本信息</span>
                      </div>
                      <div class="card-body">
                        <el-row :gutter="20">
                          <el-col :span="8">
                            <el-form-item label="公司名称" prop="name">
                              <el-input v-model="companyForm.name" placeholder="请输入公司名称" maxlength="200" :class="{'error-input': companyErrorFields.name}" @input="clearFieldError('name')" />
                            </el-form-item>
                          </el-col>
                          <el-col :span="8">
                            <el-form-item label="公司简称">
                              <el-input v-model="companyForm.short_name" placeholder="请输入公司简称" maxlength="100" :class="{'error-input': companyErrorFields.short_name}" @input="clearFieldError('short_name')" />
                            </el-form-item>
                          </el-col>
                          <el-col :span="8">
                            <el-form-item label="法定代表人">
                              <el-input v-model="companyForm.legal_person" placeholder="请输入法定代表人" maxlength="50" :class="{'error-input': companyErrorFields.legal_person}" @input="clearFieldError('legal_person')" />
                            </el-form-item>
                          </el-col>
                        </el-row>
                        <el-row :gutter="20">
                          <el-col :span="8">
                            <el-form-item label="信用代码">
                              <el-input v-model="companyForm.credit_code" placeholder="请输入统一社会信用代码" maxlength="50" :class="{'error-input': companyErrorFields.credit_code}" @input="clearFieldError('credit_code')" />
                            </el-form-item>
                          </el-col>
                          <el-col :span="8">
                            <el-form-item label="联系电话">
                              <el-input v-model="companyForm.phone" placeholder="请输入联系电话" maxlength="50" :class="{'error-input': companyErrorFields.phone}" @input="clearFieldError('phone')" />
                            </el-form-item>
                          </el-col>
                          <el-col :span="8">
                            <el-form-item label="电子邮箱">
                              <el-input v-model="companyForm.email" placeholder="请输入电子邮箱" maxlength="100" :class="{'error-input': companyErrorFields.email}" @input="clearFieldError('email')" />
                            </el-form-item>
                          </el-col>
                        </el-row>
                      </div>
                    </div>
                    
                    <!-- 联系信息卡片 -->
                    <div class="info-card">
                      <div class="card-header">
                        <div class="card-icon contact-icon"></div>
                        <span class="card-title">联系信息</span>
                      </div>
                      <div class="card-body">
                        <el-row :gutter="20">
                          <el-col :span="8">
                            <el-form-item label="注册地址">
                              <el-input v-model="companyForm.registered_address" placeholder="请输入注册地址" maxlength="300" :class="{'error-input': companyErrorFields.registered_address}" @input="clearFieldError('registered_address')" />
                            </el-form-item>
                          </el-col>
                          <el-col :span="8">
                            <el-form-item label="经营地址">
                              <el-input v-model="companyForm.business_address" placeholder="请输入经营地址" maxlength="300" :class="{'error-input': companyErrorFields.business_address}" @input="clearFieldError('business_address')" />
                            </el-form-item>
                          </el-col>
                          <el-col :span="8">
                            <el-form-item label="公司网站">
                              <el-input v-model="companyForm.website" placeholder="请输入公司网站" maxlength="200" :class="{'error-input': companyErrorFields.website}" @input="clearFieldError('website')" />
                            </el-form-item>
                          </el-col>
                        </el-row>
                      </div>
                    </div>
                    
                    <!-- 财务信息卡片 -->
                    <div class="info-card">
                      <div class="card-header">
                        <div class="card-icon finance-icon"></div>
                        <span class="card-title">财务信息</span>
                      </div>
                      <div class="card-body">
                        <el-row :gutter="20">
                          <el-col :span="8">
                            <el-form-item label="开户银行">
                              <el-input v-model="companyForm.bank_name" placeholder="请输入开户银行" maxlength="100" :class="{'error-input': companyErrorFields.bank_name}" @input="clearFieldError('bank_name')" />
                            </el-form-item>
                          </el-col>
                          <el-col :span="8">
                            <el-form-item label="银行账号">
                              <el-input v-model="companyForm.bank_account" placeholder="请输入银行账号" maxlength="50" :class="{'error-input': companyErrorFields.bank_account}" @input="clearFieldError('bank_account')" />
                            </el-form-item>
                          </el-col>
                          <el-col :span="8">
                            <el-form-item label="纳税人识别号">
                              <el-input v-model="companyForm.tax_number" placeholder="请输入纳税人识别号" maxlength="50" :class="{'error-input': companyErrorFields.tax_number}" @input="clearFieldError('tax_number')" />
                            </el-form-item>
                          </el-col>
                        </el-row>
                        <el-row :gutter="20">
                          <el-col :span="8">
                            <el-form-item label="发票抬头">
                              <el-input v-model="companyForm.invoice_title" placeholder="请输入发票抬头" maxlength="200" :class="{'error-input': companyErrorFields.invoice_title}" @input="clearFieldError('invoice_title')" />
                            </el-form-item>
                          </el-col>
                          <el-col :span="8">
                            <el-form-item label="传真号码">
                              <el-input v-model="companyForm.fax" placeholder="请输入传真号码" maxlength="50" :class="{'error-input': companyErrorFields.fax}" @input="clearFieldError('fax')" />
                            </el-form-item>
                          </el-col>
                          <el-col :span="8">
                            <el-form-item label="备注">
                              <el-input v-model="companyForm.remark" placeholder="请输入备注信息" maxlength="500" :class="{'error-input': companyErrorFields.remark}" @input="clearFieldError('remark')" />
                            </el-form-item>
                          </el-col>
                        </el-row>
                      </div>
                    </div>
                    
                    <!-- 品牌形象卡片 -->
                    <div class="info-card">
                      <div class="card-header">
                        <div class="card-icon brand-icon"></div>
                        <span class="card-title">品牌形象</span>
                      </div>
                      <div class="card-body">
                        <el-row :gutter="20">
                          <el-col :span="12">
                            <el-form-item label="公司Logo">
                              <el-upload
                                class="image-uploader"
                                :show-file-list="false"
                                :before-upload="beforeLogoUpload"
                                :http-request="handleLogoUpload"
                                accept="image/*"
                              >
                                <img v-if="companyForm.logo_base64" :src="'data:image/png;base64,' + companyForm.logo_base64" class="preview-image" />
                                <div v-else class="upload-placeholder">
                                  <el-icon class="upload-icon"><Plus /></el-icon>
                                  <span class="upload-text">上传Logo</span>
                                </div>
                              </el-upload>
                            </el-form-item>
                          </el-col>
                          <el-col :span="12">
                            <el-form-item label="公司印章">
                              <el-upload
                                class="image-uploader"
                                :show-file-list="false"
                                :before-upload="beforeStampUpload"
                                :http-request="handleStampUpload"
                                accept="image/*"
                              >
                                <img v-if="companyForm.stamp_base64" :src="'data:image/png;base64,' + companyForm.stamp_base64" class="preview-image" />
                                <div v-else class="upload-placeholder">
                                  <el-icon class="upload-icon"><Plus /></el-icon>
                                  <span class="upload-text">上传印章</span>
                                </div>
                              </el-upload>
                            </el-form-item>
                          </el-col>
                        </el-row>
                      </div>
                    </div>
                  </el-form>
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
import { getUnits, createUnit, updateUnit, deleteUnit, getWarehouses, createWarehouse, updateWarehouse, deleteWarehouse, getCompanyInfo, updateCompanyInfo } from '../../api/basic'

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
  loadCompanyInfo()
})

// 公司信息
const companyLoading = ref(false)
const companySubmitLoading = ref(false)
const companyFormRef = ref(null)
const companyForm = ref({
  name: '',
  short_name: '',
  credit_code: '',
  legal_person: '',
  registered_address: '',
  business_address: '',
  phone: '',
  fax: '',
  email: '',
  website: '',
  bank_name: '',
  bank_account: '',
  tax_number: '',
  invoice_title: '',
  logo_base64: '',
  stamp_base64: '',
  remark: ''
})
const companyRules = {
  name: [{ required: true, message: '请输入公司名称', trigger: 'blur' }]
}

const loadCompanyInfo = async () => {
  companyLoading.value = true
  try {
    const res = await getCompanyInfo()
    if (res.data) {
      Object.keys(companyForm.value).forEach(key => {
        if (res.data[key] !== undefined) {
          companyForm.value[key] = res.data[key]
        }
      })
    }
  } catch (error) {
    ElMessage.error('加载公司信息失败')
  } finally {
    companyLoading.value = false
  }
}

const handleSaveCompany = async () => {
  try { await companyFormRef.value.validate() } catch { return }
  companySubmitLoading.value = true
  clearCompanyErrors()
  try {
    const submitData = { ...companyForm.value }
    if (submitData.website && !submitData.website.match(/^https?:\/\//)) {
      submitData.website = 'https://' + submitData.website
    }
    await updateCompanyInfo(submitData)
    ElMessage.success('保存成功')
    loadCompanyInfo()
  } catch (error) {
    const errorMsg = parseErrorMessage(error)
    ElMessage.error(errorMsg)
    highlightErrorFields(error)
  } finally {
    companySubmitLoading.value = false
  }
}

const companyErrorFields = ref({})

const clearCompanyErrors = () => {
  companyErrorFields.value = {}
}

const highlightErrorFields = (error) => {
  const errorData = error.response?.data || error.data
  if (!errorData) return
  
  if (errorData.data && errorData.data.fields && Array.isArray(errorData.data.fields)) {
    errorData.data.fields.forEach(field => {
      companyErrorFields.value[field] = true
    })
    return
  }
  
  const fieldMap = {
    'website': 'website',
    'email': 'email',
    'phone': 'phone',
    'fax': 'fax',
    'credit_code': 'credit_code',
    'tax_number': 'tax_number',
    'bank_account': 'bank_account',
    'name': 'name',
    'short_name': 'short_name',
    'legal_person': 'legal_person',
    'registered_address': 'registered_address',
    'business_address': 'business_address',
    'bank_name': 'bank_name',
    'invoice_title': 'invoice_title',
    'remark': 'remark'
  }
  
  for (const [field] of Object.entries(errorData)) {
    if (fieldMap[field]) {
      companyErrorFields.value[field] = true
    }
  }
}

const clearFieldError = (field) => {
  if (companyErrorFields.value[field]) {
    delete companyErrorFields.value[field]
  }
}

const beforeLogoUpload = (file) => {
  const isImage = file.type.startsWith('image/')
  const isLt2M = file.size / 1024 / 1024 < 2
  
  if (!isImage) {
    ElMessage.error('只能上传图片文件')
    return false
  }
  if (!isLt2M) {
    ElMessage.error('图片大小不能超过 2MB')
    return false
  }
  return true
}

const beforeStampUpload = (file) => {
  return beforeLogoUpload(file)
}

const handleLogoUpload = async (options) => {
  const formData = new FormData()
  Object.keys(companyForm.value).forEach(key => {
    if (companyForm.value[key] && !['logo_base64', 'stamp_base64'].includes(key)) {
      formData.append(key, companyForm.value[key])
    }
  })
  formData.append('logo_file', options.file)
  
  try {
    const res = await updateCompanyInfo(formData)
    companyForm.value.logo_base64 = res.data.logo_base64
    ElMessage.success('Logo上传成功')
  } catch (error) {
    ElMessage.error('Logo上传失败')
  }
}

const handleStampUpload = async (options) => {
  const formData = new FormData()
  Object.keys(companyForm.value).forEach(key => {
    if (companyForm.value[key] && !['logo_base64', 'stamp_base64'].includes(key)) {
      formData.append(key, companyForm.value[key])
    }
  })
  formData.append('stamp_file', options.file)
  
  try {
    const res = await updateCompanyInfo(formData)
    companyForm.value.stamp_base64 = res.data.stamp_base64
    ElMessage.success('印章上传成功')
  } catch (error) {
    ElMessage.error('印章上传失败')
  }
}
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

/* 公司信息样式 */
.params-page .company-wrapper {
  display: flex;
  gap: 16px;
  height: 100%;
}

.params-page .company-form-panel {
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

.params-page .company-form-container {
  flex: 1;
  overflow: auto;
  padding: 16px 20px;
  background: #fafbfc;
}

.params-page .panel-title-text {
  font-size: 14px;
  font-weight: 600;
  color: #303133;
}

/* 卡片样式 */
.params-page .info-card {
  background: #ffffff;
  border-radius: 8px;
  margin-bottom: 12px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.05);
  border: 1px solid #ebeef5;
  overflow: hidden;
}

.params-page .info-card:last-child {
  margin-bottom: 0;
}

.params-page .card-header {
  display: flex;
  align-items: center;
  padding: 10px 16px;
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
  border-bottom: 1px solid #ebeef5;
}

.params-page .card-icon {
  width: 24px;
  height: 24px;
  border-radius: 6px;
  margin-right: 10px;
}

.params-page .basic-icon {
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
}

.params-page .contact-icon {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
}

.params-page .finance-icon {
  background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
}

.params-page .brand-icon {
  background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%);
}

.params-page .card-title {
  font-size: 13px;
  font-weight: 600;
  color: #1f2937;
}

.params-page .card-body {
  padding: 14px 16px;
}

/* 上传区域样式 */
.params-page .image-uploader {
  border: 1px dashed #d1d5db;
  border-radius: 8px;
  cursor: pointer;
  overflow: hidden;
  transition: all 0.3s ease;
  background: #fafafa;
}

.params-page .image-uploader:hover {
  border-color: #165DFF;
  background: #f0f7ff;
}

.params-page .preview-image {
  width: 80px;
  height: 80px;
  object-fit: contain;
  display: block;
  padding: 4px;
}

.params-page .upload-placeholder {
  width: 80px;
  height: 80px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #9ca3af;
  background: transparent;
}

.params-page .upload-icon {
  font-size: 24px;
  margin-bottom: 4px;
  color: #d1d5db;
}

.params-page .upload-text {
  font-size: 12px;
  color: #9ca3af;
}

.params-page .image-uploader:hover .upload-icon,
.params-page .image-uploader:hover .upload-text {
  color: #165DFF;
}

/* 表单项样式优化 */
.params-page .company-form-container :deep(.el-form-item) {
  margin-bottom: 12px;
}

.params-page .company-form-container :deep(.el-form-item__label) {
  font-weight: 500;
  color: #4b5563;
  font-size: 13px;
}

.params-page .company-form-container :deep(.el-input__wrapper) {
  border-radius: 6px;
}

.params-page .company-form-container :deep(.error-input .el-input__wrapper) {
  border: 2px solid #ff4d4f !important;
  box-shadow: 0 0 0 3px rgba(255, 77, 79, 0.15), 0 2px 8px rgba(255, 77, 79, 0.2) !important;
  background-color: #fff2f0 !important;
  animation: errorShake 0.3s ease-in-out;
}

.params-page .company-form-container :deep(.error-input .el-input__wrapper:hover) {
  border: 2px solid #ff4d4f !important;
  box-shadow: 0 0 0 3px rgba(255, 77, 79, 0.2), 0 2px 8px rgba(255, 77, 79, 0.3) !important;
}

.params-page .company-form-container :deep(.error-input .el-input__wrapper:focus-within) {
  border: 2px solid #ff4d4f !important;
  box-shadow: 0 0 0 3px rgba(255, 77, 79, 0.25), 0 2px 12px rgba(255, 77, 79, 0.35) !important;
}

.params-page .company-form-container :deep(.error-input .el-input__inner) {
  color: #cf1322;
}

.params-page .company-form-container :deep(.error-input .el-input__inner::placeholder) {
  color: #ffa39e;
}

@keyframes errorShake {
  0%, 100% { transform: translateX(0); }
  20% { transform: translateX(-4px); }
  40% { transform: translateX(4px); }
  60% { transform: translateX(-4px); }
  80% { transform: translateX(4px); }
}

/* 响应式布局 */
@media screen and (max-width: 1200px) {
  .params-page .company-form-container {
    padding: 12px 16px;
  }
  
  .params-page .card-body {
    padding: 12px;
  }
}

@media screen and (max-width: 992px) {
  .params-page .company-wrapper {
    flex-direction: column;
  }
  
  .params-page .company-form-panel {
    min-height: 400px;
  }
}
</style>

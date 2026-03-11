<template>
  <div class="goods-page">
    <div class="page-content">
      <div class="dual-card-container">
        <!-- 左侧分类树卡片 -->
        <div class="category-card">
          <div class="category-header">
            <span class="category-title">商品分类</span>
            <div class="category-actions">
              <el-button type="primary" link :icon="Plus" size="small" @click="handleAddCategory" v-if="canAddGoods">添加</el-button>
              <el-button type="primary" link :icon="Setting" size="small" @click="handleManageCategory" v-if="canEditGoods">管理</el-button>
            </div>
          </div>
          <div class="category-tree-wrapper">
            <!-- 分类树 -->
            <div class="category-tree">
              <div 
                v-for="(category, index) in categoryTreeData" 
                :key="category.id"
                class="category-node level-1"
                :class="{ 
                  active: selectedCategoryId === category.id,
                  expanded: expandedCategories.includes(category.id),
                  'has-children': category.children && category.children.length > 0,
                  'last-child': index === categoryTreeData.length - 1
                }"
              >
                <!-- 一级分类 -->
                <div 
                  class="category-item"
                  @click="handleCategoryItemClick(category)"
                >
                  <div class="tree-line"></div>
                  <div class="item-content">
                    <el-icon 
                      class="expand-icon" 
                      :class="{ expanded: expandedCategories.includes(category.id) }"
                      v-if="category.children && category.children.length > 0"
                    >
                      <ArrowRight />
                    </el-icon>
                    <span class="expand-placeholder" v-else></span>
                    <el-icon class="category-icon folder"><Folder /></el-icon>
                    <span class="category-name">{{ category.name }}</span>
                  </div>
                  <span class="category-count" v-if="getCategoryTotalGoods(category) > 0">{{ getCategoryTotalGoods(category) }}</span>
                </div>
                
                <!-- 二级分类列表 -->
                <el-collapse-transition>
                  <div 
                    class="children-container" 
                    v-show="expandedCategories.includes(category.id) && category.children && category.children.length > 0"
                  >
                    <div 
                      v-for="(sub, subIndex) in category.children" 
                      :key="sub.id"
                      class="category-node level-2"
                      :class="{ 
                        active: selectedCategoryId === sub.id,
                        'last-child': subIndex === category.children.length - 1
                      }"
                    >
                      <div 
                        class="category-item"
                        @click.stop="handleSelectCategory(sub.id)"
                      >
                        <div class="tree-line"></div>
                        <div class="item-content">
                          <span class="line-connector"></span>
                          <el-icon class="category-icon leaf"><Document /></el-icon>
                          <span class="category-name">{{ sub.name }}</span>
                        </div>
                        <span class="category-count" v-if="sub.goods_count > 0">{{ sub.goods_count }}</span>
                      </div>
                    </div>
                  </div>
                </el-collapse-transition>
              </div>
            </div>
          </div>
        </div>
        
        <!-- 右侧商品列表卡片 -->
        <div class="goods-card">
          <div class="toolbar-card">
            <div class="toolbar-left">
              <div class="search-box">
                <el-icon class="search-icon"><Search /></el-icon>
                <el-input
                  v-model="searchKeyword"
                  placeholder="搜索商品编码、名称"
                  class="search-input"
                  clearable
                  @keyup.enter="loadGoods"
                />
              </div>
              <el-select v-model="statusFilter" placeholder="状态筛选" clearable style="width: 140px" @change="loadGoods">
                <el-option label="全部" :value="''" />
                <el-option label="启用" :value="1" />
                <el-option label="禁用" :value="0" />
              </el-select>
            </div>
            <div class="toolbar-right">
              <el-button :icon="Refresh" @click="loadGoods">刷新</el-button>
              <el-button type="primary" :icon="Plus" @click="handleAdd" v-if="canAddGoods">新增商品</el-button>
            </div>
          </div>

          <div class="table-card">
            <el-table 
              :data="goodsList" 
              style="width: 100%" 
              v-loading="loading"
              class="data-table"
              stripe
              :height="tableHeight"
              :header-cell-style="{ background: 'var(--color-bg-light)' }"
            >
              <el-table-column prop="code" label="商品编码" width="140">
                <template #default="{ row }">
                  <span class="code-badge">{{ row.code }}</span>
                </template>
              </el-table-column>
              <el-table-column prop="name" label="商品名称" min-width="200">
                <template #default="{ row }">
                  <div class="name-cell">
                    <div class="goods-initials">{{ getGoodsInitials(row.name) }}</div>
                    <div class="goods-info">
                      <div class="goods-name">{{ row.name }}</div>
                      <div class="goods-category" v-if="row.category_name">{{ row.category_name }}</div>
                    </div>
                  </div>
                </template>
              </el-table-column>
              <el-table-column prop="spec" label="规格" min-width="120" align="center">
                <template #default="{ row }">
                  <span class="spec-text">{{ row.spec || '-' }}</span>
                </template>
              </el-table-column>
              <el-table-column prop="unit_name" label="单位" width="80" align="center" />
              <el-table-column prop="purchase_price" label="进货价" width="120" align="right">
                <template #default="{ row }">
                  <span class="price-text purchase">¥{{ formatPrice(row.purchase_price) }}</span>
                </template>
              </el-table-column>
              <el-table-column prop="sale_price" label="销售价" width="120" align="right">
                <template #default="{ row }">
                  <span class="price-text sale">¥{{ formatPrice(row.sale_price) }}</span>
                </template>
              </el-table-column>
              <el-table-column label="利润" width="120" align="right">
                <template #default="{ row }">
                  <span class="price-text profit">¥{{ formatPrice(calculateProfit(row)) }}</span>
                </template>
              </el-table-column>
              <el-table-column label="状态" width="100" align="center">
                <template #default="{ row }">
                  <el-switch
                    v-model="row.status"
                    active-color="#165DFF"
                    inactive-color="#9ca3af"
                    :active-value="1"
                    :inactive-value="0"
                    :loading="toggleLoading === row.id"
                    @change="handleToggleStatus(row)"
                  />
                </template>
              </el-table-column>
              <el-table-column label="操作" width="140" align="center">
                <template #default="{ row }">
                  <div class="action-buttons">
                    <el-button type="primary" link :icon="Edit" size="small" @click="handleEdit(row)" v-if="canEditGoods">编辑</el-button>
                    <el-button type="danger" link :icon="Delete" size="small" @click="handleDelete(row)" v-if="canDeleteGoods">删除</el-button>
                  </div>
                </template>
              </el-table-column>
            </el-table>
            <div class="pagination-wrapper">
              <el-pagination
                v-model:current-page="currentPage"
                v-model:page-size="pageSize"
                :page-sizes="[10, 20, 50, 100]"
                :total="total"
                layout="total, sizes, prev, pager, next, jumper"
                @size-change="loadGoods"
                @current-change="loadGoods"
              />
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 新增/编辑商品对话框 -->
    <el-dialog 
      v-model="dialogVisible" 
      :title="dialogTitle" 
      width="680px"
      :close-on-click-modal="false"
      @close="handleDialogClose"
    >
      <el-form 
        ref="formRef" 
        :model="form" 
        :rules="rules" 
        label-width="100px"
        label-position="right"
        class="goods-form"
      >
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="商品编码" prop="code">
              <el-input 
                v-model="form.code" 
                placeholder="请输入商品编码"
                maxlength="50"
                show-word-limit
                :disabled="isEdit"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="商品名称" prop="name">
              <el-input 
                v-model="form.name" 
                placeholder="请输入商品名称"
                maxlength="100"
                show-word-limit
              />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="商品分类" prop="category">
              <el-tree-select
                v-model="form.category"
                :data="goodsCategoryOptions"
                :props="{ value: 'id', label: 'name', children: 'children', disabled: 'disabled' }"
                placeholder="请选择商品分类（仅二级及以下）"
                style="width: 100%"
                filterable
                clearable
                :filter-node-method="filterCategoryNode"
                check-strictly
                :render-after-expand="false"
                node-key="id"
                highlight-current
              >
                <template #default="{ node, data }">
                  <span class="category-select-node" :class="{ 'is-disabled': data.disabled }">
                    <el-icon v-if="data.level === 1" class="level-icon"><Warning /></el-icon>
                    {{ data.name }}
                    <el-tag v-if="data.level === 1" size="small" type="warning" effect="plain">不可选</el-tag>
                  </span>
                </template>
              </el-tree-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="计量单位" prop="unit">
              <el-select 
                v-model="form.unit" 
                placeholder="请选择计量单位"
                style="width: 100%"
                filterable
              >
                <el-option 
                  v-for="item in unitList" 
                  :key="item.id" 
                  :label="item.name" 
                  :value="item.id"
                />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="规格">
              <el-input 
                v-model="form.spec" 
                placeholder="请输入规格"
                maxlength="100"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="条形码">
              <el-input 
                v-model="form.barcode" 
                placeholder="请输入条形码（选填）"
                maxlength="50"
              />
            </el-form-item>
          </el-col>
        </el-row>

        <el-divider content-position="left">价格信息</el-divider>

        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="进货价" prop="purchase_price">
              <div class="price-input-wrapper" :class="{ 'has-error': priceErrors.purchase_price }">
                <el-input
                  :model-value="formatInputNumber(form.purchase_price)"
                  @input="(val) => handlePriceInput('purchase_price', val)"
                  @blur="handlePriceBlur('purchase_price')"
                  placeholder="请输入"
                  class="price-input"
                  :class="{ 'is-error': priceErrors.purchase_price }"
                >
                  <template #prefix>
                    <span class="input-prefix">¥</span>
                  </template>
                </el-input>
                <div class="error-tip" v-if="priceErrors.purchase_price">{{ priceErrors.purchase_price }}</div>
              </div>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="销售价" prop="sale_price">
              <div class="price-input-wrapper" :class="{ 'has-error': priceErrors.sale_price }">
                <el-input
                  :model-value="formatInputNumber(form.sale_price)"
                  @input="(val) => handlePriceInput('sale_price', val)"
                  @blur="handlePriceBlur('sale_price')"
                  placeholder="请输入"
                  class="price-input"
                  :class="{ 'is-error': priceErrors.sale_price }"
                >
                  <template #prefix>
                    <span class="input-prefix">¥</span>
                  </template>
                </el-input>
                <div class="error-tip" v-if="priceErrors.sale_price">{{ priceErrors.sale_price }}</div>
              </div>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="零售价" prop="retail_price">
              <div class="price-input-wrapper" :class="{ 'has-error': priceErrors.retail_price }">
                <el-input
                  :model-value="formatInputNumber(form.retail_price)"
                  @input="(val) => handlePriceInput('retail_price', val)"
                  @blur="handlePriceBlur('retail_price')"
                  placeholder="请输入"
                  class="price-input"
                  :class="{ 'is-error': priceErrors.retail_price }"
                >
                  <template #prefix>
                    <span class="input-prefix">¥</span>
                  </template>
                </el-input>
                <div class="error-tip" v-if="priceErrors.retail_price">{{ priceErrors.retail_price }}</div>
              </div>
            </el-form-item>
          </el-col>
        </el-row>

        <el-divider content-position="left">库存设置</el-divider>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="最低库存" prop="min_stock">
              <el-input-number 
                v-model="form.min_stock" 
                :min="0"
                :max="999999999"
                placeholder="请输入最低库存"
                style="width: 100%"
                controls-position="right"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="最高库存" prop="max_stock">
              <el-input-number 
                v-model="form.max_stock" 
                :min="0"
                :max="999999999"
                placeholder="请输入最高库存"
                style="width: 100%"
                controls-position="right"
              />
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="状态" prop="status">
          <el-radio-group v-model="form.status">
            <el-radio :value="1">上架</el-radio>
            <el-radio :value="0">下架</el-radio>
          </el-radio-group>
        </el-form-item>

        <el-form-item label="备注" prop="remark">
          <el-input 
            v-model="form.remark" 
            type="textarea" 
            :rows="3"
            placeholder="请输入备注信息（选填）"
            maxlength="500"
            show-word-limit
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <div class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleSubmit" :loading="submitLoading">
            {{ isEdit ? '保存修改' : '确认新增' }}
          </el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 分类管理弹窗 -->
    <el-dialog
      v-model="categoryDialogVisible"
      title="商品分类管理"
      width="700px"
      :close-on-click-modal="false"
      class="category-manage-dialog"
    >
      <div class="category-manage-header">
        <div class="header-left">
          <el-input 
            v-model="categorySearch" 
            placeholder="搜索分类名称或编码" 
            clearable 
            style="width: 220px"
            :prefix-icon="Search"
          />
          <el-tooltip content="拖拽分类名称左侧的图标可调整顺序" placement="bottom">
            <el-tag type="info" size="small" effect="plain">
              <el-icon><Rank /></el-icon>
              拖拽排序
            </el-tag>
          </el-tooltip>
        </div>
        <el-button type="primary" :icon="Plus" @click="handleAddCategoryItem">新增分类</el-button>
      </div>
      
      <div class="category-table-wrapper" v-loading="categoryLoading">
        <el-tree
          ref="categoryTreeRef"
          :data="filteredCategoryList"
          :props="{ children: 'children', label: 'name' }"
          node-key="id"
          default-expand-all
          draggable
          :allow-drop="allowDrop"
          :expand-on-click-node="false"
          @node-drop="handleNodeDrop"
          class="category-drag-tree"
        >
          <template #default="{ node, data }">
            <div class="category-tree-node-content">
              <div class="node-left">
                <el-icon class="drag-handle"><Rank /></el-icon>
                <el-icon class="folder-icon" v-if="data.children && data.children.length > 0"><Folder /></el-icon>
                <el-icon class="leaf-icon" v-else><Document /></el-icon>
                <span class="name-text">{{ node.label }}</span>
                <el-tag v-if="data.code" size="small" class="code-tag">{{ data.code }}</el-tag>
              </div>
              <div class="node-right">
                <span class="goods-count" :class="{ 'has-goods': data.goods_count > 0 }">{{ data.goods_count || 0 }}</span>
                <el-switch
                  v-model="data.is_active"
                  size="small"
                  :loading="categoryToggleLoading === data.id"
                  @change="handleToggleCategoryStatus(data)"
                  @click.stop
                />
                <el-button type="primary" link size="small" @click.stop="handleEditCategoryItem(data)" v-if="canEditGoods">
                  <el-icon><Edit /></el-icon>
                </el-button>
                <el-button type="danger" link size="small" @click.stop="handleDeleteCategoryItem(data)" v-if="canDeleteGoods && (!data.goods_count || data.goods_count === 0)">
                  <el-icon><Delete /></el-icon>
                </el-button>
              </div>
            </div>
          </template>
        </el-tree>
        <el-empty v-if="!categoryLoading && filteredCategoryList.length === 0" description="暂无分类数据" :image-size="60" />
      </div>
    </el-dialog>

    <!-- 新增/编辑分类弹窗 -->
    <el-dialog
      v-model="categoryFormDialogVisible"
      :title="categoryFormTitle"
      width="480px"
      :close-on-click-modal="false"
      class="category-form-dialog"
      @close="resetCategoryForm"
    >
      <el-form 
        ref="categoryFormRef" 
        :model="categoryForm" 
        :rules="categoryRules" 
        label-position="top"
        class="category-form"
      >
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="分类名称" prop="name">
              <el-input v-model="categoryForm.name" placeholder="请输入分类名称" maxlength="50" show-word-limit />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="分类编码" prop="code">
              <el-input v-model="categoryForm.code" placeholder="请输入分类编码" maxlength="30" show-word-limit />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-form-item label="上级分类">
          <el-tree-select
            v-model="categoryForm.parent"
            :data="categoryParentOptions"
            :props="{ value: 'id', label: 'name', children: 'children', disabled: 'disabled' }"
            placeholder="请选择上级分类（可选，默认为顶级分类）"
            style="width: 100%"
            clearable
            filterable
            :filter-method="filterCategoryTree"
            check-strictly
            :render-after-expand="false"
            node-key="id"
            :expand-on-click-node="false"
            :default-expand-all="true"
            :highlight-current="true"
            class="parent-category-select"
          >
            <template #default="{ node, data }">
              <div class="category-tree-node" :class="{ 'is-disabled': data.disabled }">
                <div class="node-content">
                  <el-icon class="node-icon" :class="{ 'is-folder': data.children && data.children.length > 0, 'is-leaf': !data.children || data.children.length === 0 }">
                    <Folder v-if="data.children && data.children.length > 0" />
                    <Document v-else />
                  </el-icon>
                  <span class="node-label">{{ data.name }}</span>
                  <el-tag v-if="data.code && data.id !== 0" size="small" class="node-code">{{ data.code }}</el-tag>
                </div>
                <el-icon v-if="data.id === categoryForm.parent" class="check-icon"><Check /></el-icon>
              </div>
            </template>
          </el-tree-select>
        </el-form-item>
        
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="排序号">
              <el-input-number v-model="categoryForm.sort" :min="0" :max="9999" style="width: 100%" placeholder="数值越小越靠前" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="状态">
              <el-radio-group v-model="categoryForm.is_active" class="status-radio">
                <el-radio :value="true">启用</el-radio>
                <el-radio :value="false">停用</el-radio>
              </el-radio-group>
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-form-item label="备注">
          <el-input v-model="categoryForm.remark" type="textarea" :rows="2" placeholder="请输入备注信息（可选）" maxlength="200" show-word-limit />
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="categoryFormDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleSubmitCategory" :loading="categoryFormLoading">确定保存</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, nextTick, onUnmounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Refresh, Plus, Edit, Delete, Folder, Document, ArrowRight, Grid, Setting, Check, Rank, Warning } from '@element-plus/icons-vue'
import { getGoods, createGoods, deleteGoods, updateGoods, getCategories, getUnits, createCategory, updateCategory, deleteCategory, batchUpdateCategorySort } from '../../api/basic'
import { formatPrice, formatInputNumber, parseInputNumber } from '../../utils/format'
import { canAdd, canEdit, canDelete } from '../../utils/permission'

const loading = ref(false)
const toggleLoading = ref(null)
const goodsList = ref([])
const searchKeyword = ref('')
const statusFilter = ref('')
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)
const tableHeight = ref(0)
const selectedCategoryId = ref(null)
const selectedCategoryIncludeChildren = ref(false)
const expandedCategories = ref([])
const totalGoodsCount = ref(0)

const categoryDialogVisible = ref(false)
const categorySearch = ref('')
const categoryLoading = ref(false)
const categoryToggleLoading = ref(null)
const categoryFormDialogVisible = ref(false)
const categoryFormTitle = ref('新增分类')
const categoryFormLoading = ref(false)
const categoryFormRef = ref(null)
const categoryTreeRef = ref(null)
const categoryForm = reactive({
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
  // 递归标记需要禁用的节点（当前分类及其子孙节点）
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
  
  // 深拷贝树形数据，避免修改原数据
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
  markDisabled(treeData, categoryForm.id)
  
  // 只返回树形数据，顶级分类选项通过 treeData 的根节点自然体现
  return treeData
})

const goodsCategoryOptions = computed(() => {
  // 深拷贝树形数据，避免修改原数据
  const cloneTree = (nodes) => {
    return nodes.map(node => {
      const cloned = { ...node }
      // 一级分类标记为禁用
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

const filterCategoryTree = (value, data) => {
  if (!value) return true
  const keyword = value.toLowerCase()
  return data.name?.toLowerCase().includes(keyword) || 
         data.code?.toLowerCase().includes(keyword)
}

const canAddGoods = computed(() => canAdd('basic'))
const canEditGoods = computed(() => canEdit('basic'))
const canDeleteGoods = computed(() => canDelete('basic'))

const dialogVisible = ref(false)
const dialogTitle = ref('新增商品')
const isEdit = ref(false)
const submitLoading = ref(false)
const formRef = ref(null)
const categoryList = ref([])
const categoryTreeData = ref([])
const unitList = ref([])

const priceErrors = reactive({
  purchase_price: '',
  sale_price: '',
  retail_price: ''
})

const form = reactive({
  id: null,
  code: '',
  name: '',
  category: null,
  unit: null,
  spec: '',
  barcode: '',
  purchase_price: 0,
  sale_price: 0,
  retail_price: 0,
  min_stock: 0,
  max_stock: 0,
  status: 1,
  remark: ''
})

const validateCode = (rule, value, callback) => {
  if (!value || !value.trim()) {
    callback(new Error('请输入商品编码'))
  } else if (value.length > 50) {
    callback(new Error('商品编码不能超过50个字符'))
  } else if (!/^[A-Za-z0-9_-]+$/.test(value)) {
    callback(new Error('商品编码只能包含字母、数字、下划线和横线'))
  } else {
    callback()
  }
}

const validateName = (rule, value, callback) => {
  if (!value || !value.trim()) {
    callback(new Error('请输入商品名称'))
  } else if (value.length > 100) {
    callback(new Error('商品名称不能超过100个字符'))
  } else {
    callback()
  }
}

const validateMaxStock = (rule, value, callback) => {
  if (value < form.min_stock) {
    callback(new Error('最高库存不能低于最低库存'))
  } else {
    callback()
  }
}

const rules = {
  code: [
    { required: true, validator: validateCode, trigger: 'blur' }
  ],
  name: [
    { required: true, validator: validateName, trigger: 'blur' }
  ],
  category: [
    { required: true, message: '请选择商品分类', trigger: 'change' }
  ],
  unit: [
    { required: true, message: '请选择或输入计量单位', trigger: 'change' }
  ],
  max_stock: [
    { validator: validateMaxStock, trigger: 'blur' }
  ]
}

const handlePriceInput = (field, value) => {
  priceErrors[field] = ''
  const num = parseInputNumber(value)
  form[field] = num
}

const handlePriceBlur = (field) => {
  const value = form[field]
  if (value === null || value === undefined || value === '') {
    priceErrors[field] = '请输入价格'
    return
  }
  if (value < 0) {
    priceErrors[field] = '价格不能为负数'
    return
  }
  if (value > 99999999.99) {
    priceErrors[field] = '价格超出范围'
    return
  }
  
  if (field === 'sale_price' && form.purchase_price && value < form.purchase_price) {
    priceErrors[field] = '销售价不能低于进货价'
    return
  }
  
  priceErrors[field] = ''
}

const getGoodsInitials = (name) => {
  if (!name) return ''
  return name.slice(0, 2)
}

const calculateProfit = (row) => {
  const purchase = Number(row.purchase_price) || 0
  const sale = Number(row.sale_price) || 0
  return sale - purchase
}

const calculateTableHeight = () => {
  nextTick(() => {
    const toolbarCard = document.querySelector('.goods-card .toolbar-card')
    const paginationWrapper = document.querySelector('.goods-card .pagination-wrapper')
    const pageContent = document.querySelector('.page-content')
    
    if (pageContent) {
      let usedHeight = 0
      if (toolbarCard) usedHeight += toolbarCard.offsetHeight + 4
      if (paginationWrapper) usedHeight += paginationWrapper.offsetHeight + 2
      usedHeight += 4
      
      const availableHeight = window.innerHeight - 64 - 16
      tableHeight.value = Math.max(availableHeight - usedHeight, 150)
    }
  })
}

const filterCategoryNode = (value, data) => {
  if (!value) return true
  return data.name.includes(value) || (data.code && data.code.toLowerCase().includes(value.toLowerCase()))
}

const handleCategoryItemClick = (category) => {
  const hasChildren = category.children && category.children.length > 0
  
  if (hasChildren) {
    const index = expandedCategories.value.indexOf(category.id)
    if (index > -1) {
      expandedCategories.value.splice(index, 1)
    } else {
      expandedCategories.value.push(category.id)
    }
  }
  
  // 点击一级分类时，显示该分类下所有子分类的商品
  handleSelectCategory(category.id, category.level === 1)
}

const handleSelectCategory = (categoryId, includeChildren = false) => {
  selectedCategoryId.value = categoryId
  selectedCategoryIncludeChildren.value = includeChildren
  currentPage.value = 1
  loadGoods()
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

const handleCategoryClick = (data) => {
  selectedCategoryId.value = data.id
  currentPage.value = 1
  loadGoods()
}

const handleAddCategory = () => {
  handleAddCategoryItem()
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
  categoryForm.id = row.id
  categoryForm.name = row.name
  categoryForm.code = row.code || ''
  categoryForm.parent = row.parent || null
  categoryForm.sort = row.sort_order || 0
  categoryForm.is_active = row.is_active !== false
  categoryForm.remark = row.remark || ''
  categoryFormDialogVisible.value = true
}

const resetCategoryForm = () => {
  categoryForm.id = null
  categoryForm.name = ''
  categoryForm.code = ''
  categoryForm.parent = null
  categoryForm.sort = 0
  categoryForm.is_active = true
  categoryForm.remark = ''
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
      name: categoryForm.name,
      code: categoryForm.code,
      parent: categoryForm.parent || null,
      sort_order: categoryForm.sort,
      is_active: categoryForm.is_active,
      remark: categoryForm.remark
    }
    
    if (categoryForm.id) {
      await updateCategory(categoryForm.id, data)
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
      ElMessage.error(categoryForm.id ? '修改失败' : '新增失败')
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

const allowDrop = (draggingNode, dropNode, type) => {
  // 不能拖拽到自己的子节点中
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

const handleNodeDrop = async (draggingNode, dropNode, dropType, event) => {
  const draggedData = draggingNode.data
  const droppedData = dropNode.data
  
  try {
    // 计算新的父级和排序
    let newParent = null
    let newSortOrder = 0
    
    if (dropType === 'inner') {
      // 拖拽到节点内部，成为子节点
      newParent = droppedData.id
      newSortOrder = droppedData.children ? droppedData.children.length : 0
    } else if (dropType === 'before') {
      // 拖拽到节点前面
      newParent = droppedData.parent || null
      const siblings = getSiblingNodes(droppedData)
      const dropIndex = siblings.findIndex(item => item.id === droppedData.id)
      newSortOrder = dropIndex
    } else if (dropType === 'after') {
      // 拖拽到节点后面
      newParent = droppedData.parent || null
      const siblings = getSiblingNodes(droppedData)
      const dropIndex = siblings.findIndex(item => item.id === droppedData.id)
      newSortOrder = dropIndex + 1
    }
    
    // 更新拖拽节点的排序
    await updateCategory(draggedData.id, {
      parent: newParent,
      sort_order: newSortOrder
    })
    
    ElMessage.success('排序已更新')
    // 重新加载分类树
    loadCategories()
  } catch (error) {
    ElMessage.error('排序更新失败：' + (error.response?.data?.msg || error.message || '未知错误'))
    // 恢复原顺序
    loadCategories()
  }
}

const getSiblingNodes = (node) => {
  // 从树形结构中获取同级节点
  const parentId = node.parent || node.parent_id
  if (!parentId) {
    // 顶级节点的兄弟节点就是根节点
    return categoryTreeData.value
  }
  
  // 查找父节点的 children
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

const handleToggleCategoryStatus = async (row) => {
  categoryToggleLoading.value = row.id
  try {
    await updateCategory(row.id, { is_active: row.is_active })
    ElMessage.success(row.is_active ? '已启用' : '已停用')
  } catch (error) {
    row.is_active = !row.is_active
    ElMessage.error('操作失败：' + (error.response?.data?.msg || error.message || '未知错误'))
  } finally {
    categoryToggleLoading.value = null
  }
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

const buildCategoryTree = (categories) => {
  const map = {}
  const roots = []
  
  // 第一次遍历：创建所有节点，使用 Map 去重
  const uniqueCategories = []
  const seenIds = new Set()
  
  categories.forEach(cat => {
    if (!seenIds.has(cat.id)) {
      seenIds.add(cat.id)
      uniqueCategories.push(cat)
      map[cat.id] = { ...cat, children: [] }
    }
  })
  
  // 第二次遍历：建立父子关系
  uniqueCategories.forEach(cat => {
    // 检查 parent 或 parent_id
    const parentId = cat.parent?.id || cat.parent_id || cat.parent
    if (parentId && map[parentId]) {
      // 检查是否已存在，避免重复添加
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

const loadUnits = async () => {
  try {
    const res = await getUnits({ page_size: 1000, is_active: true })
    unitList.value = res.data?.items || res.data?.results || []
  } catch (error) {
    unitList.value = []
  }
}

const loadGoods = async () => {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      page_size: pageSize.value
    }
    if (searchKeyword.value) {
      params.search = searchKeyword.value
    }
    if (statusFilter.value !== '') {
      params.status = statusFilter.value
    }
    if (selectedCategoryId.value) {
      if (selectedCategoryIncludeChildren.value) {
        // 一级分类：查询该分类及其所有子分类的商品
        params.category_include_children = selectedCategoryId.value
      } else {
        // 二级分类：只查询该分类的商品
        params.category = selectedCategoryId.value
      }
    }
    const res = await getGoods(params)
    goodsList.value = res.data?.items || res.data?.results || []
    total.value = res.data?.count || 0
    totalGoodsCount.value = total.value
  } catch (error) {
    goodsList.value = []
    total.value = 0
    ElMessage.error('加载数据失败：' + (error.message || '未知错误'))
  } finally {
    loading.value = false
  }
}

const resetForm = () => {
  form.id = null
  form.code = ''
  form.name = ''
  form.category = selectedCategoryId.value || null
  form.unit = ''
  form.spec = ''
  form.barcode = ''
  form.purchase_price = 0
  form.sale_price = 0
  form.retail_price = 0
  form.min_stock = 0
  form.max_stock = 0
  form.status = 1
  form.remark = ''
  priceErrors.purchase_price = ''
  priceErrors.sale_price = ''
  priceErrors.retail_price = ''
}

const handleDialogClose = () => {
  formRef.value?.resetFields()
  resetForm()
}

const handleAdd = () => {
  isEdit.value = false
  dialogTitle.value = '新增商品'
  resetForm()
  if (selectedCategoryId.value && selectedCategoryId.value !== 0) {
    form.category = selectedCategoryId.value
  }
  dialogVisible.value = true
}

const handleEdit = (row) => {
  isEdit.value = true
  dialogTitle.value = '编辑商品'
  resetForm()
  form.id = row.id
  form.code = row.code
  form.name = row.name
  form.category = row.category
  form.unit = row.unit
  form.spec = row.spec || ''
  form.barcode = row.barcode || ''
  form.purchase_price = row.purchase_price || 0
  form.sale_price = row.sale_price || 0
  form.retail_price = row.retail_price || 0
  form.min_stock = row.min_stock || 0
  form.max_stock = row.max_stock || 0
  form.status = row.status
  form.remark = row.remark || ''
  dialogVisible.value = true
}

const handleSubmit = async () => {
  if (!formRef.value) return
  
  try {
    await formRef.value.validate()
  } catch (error) {
    return
  }
  
  if (priceErrors.purchase_price || priceErrors.sale_price || priceErrors.retail_price) {
    ElMessage.warning('请检查价格输入')
    return
  }
  
  submitLoading.value = true
  try {
    const data = {
      code: form.code,
      name: form.name,
      category: form.category,
      unit: form.unit,
      spec: form.spec,
      barcode: form.barcode,
      purchase_price: form.purchase_price || 0,
      sale_price: form.sale_price || 0,
      retail_price: form.retail_price || 0,
      min_stock: form.min_stock || 0,
      max_stock: form.max_stock || 0,
      status: form.status,
      remark: form.remark
    }
    
    if (isEdit.value) {
      await updateGoods(form.id, data)
      ElMessage.success('修改成功')
    } else {
      await createGoods(data)
      ElMessage.success('新增成功')
    }
    
    dialogVisible.value = false
    loadGoods()
  } catch (error) {
    ElMessage.error(isEdit.value ? '修改失败' : '新增失败')
  } finally {
    submitLoading.value = false
  }
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm(`确定删除商品「${row.name}」？`, '确认删除', { type: 'warning' })
    await deleteGoods(row.id)
    ElMessage.success('删除成功')
    loadGoods()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const handleToggleStatus = async (row) => {
  toggleLoading.value = row.id
  try {
    await updateGoods(row.id, { status: row.status })
    ElMessage.success(row.status === 1 ? '已上架' : '已下架')
  } catch (error) {
    row.status = row.status === 1 ? 0 : 1
    ElMessage.error('操作失败')
  } finally {
    toggleLoading.value = null
  }
}

onMounted(() => {
  loadCategories()
  loadUnits()
  loadGoods()
  calculateTableHeight()
  window.addEventListener('resize', calculateTableHeight)
})

onUnmounted(() => {
  window.removeEventListener('resize', calculateTableHeight)
})
</script>

<style scoped>
.goods-page {
  padding: 0;
  background: #f5f7fa;
  min-height: calc(100vh - 64px);
}

.goods-page .page-content {
  padding: 16px;
}

.dual-card-container {
  display: flex;
  gap: 16px;
  height: calc(100vh - 96px);
}

.category-card {
  width: 260px;
  flex-shrink: 0;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.08);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.category-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 14px 16px;
  border-bottom: 1px solid #f0f0f0;
  background: linear-gradient(135deg, #fafbfc 0%, #f5f7fa 100%);
}

.category-title {
  font-size: 15px;
  font-weight: 600;
  color: #303133;
}

.category-tree-wrapper {
  flex: 1;
  overflow-y: auto;
  padding: 8px 0;
}

.category-tree {
  display: flex;
  flex-direction: column;
}

.category-node {
  position: relative;
}

.category-node.level-1 {
  margin-bottom: 2px;
}

.category-node.level-2 {
  position: relative;
}

.category-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 12px;
  cursor: pointer;
  transition: all 0.2s ease-in-out;
  border-radius: 6px;
  user-select: none;
  position: relative;
}

.category-item:hover {
  background: #f0f5ff;
}

.category-item.active {
  background: #e6f4ff;
  color: #165DFF;
  font-weight: 600;
}

.category-item .tree-line {
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 3px;
  background: transparent;
  border-radius: 3px 0 0 3px;
  transition: background 0.2s;
}

.category-item.active .tree-line {
  background: #165DFF;
}

.category-item .item-content {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1;
}

.category-item .expand-icon {
  font-size: 12px;
  color: #909399;
  transition: transform 0.2s ease-in-out;
  width: 16px;
  flex-shrink: 0;
}

.category-item .expand-icon.expanded {
  transform: rotate(90deg);
  color: #165DFF;
}

.category-item .expand-placeholder {
  width: 16px;
  flex-shrink: 0;
}

.category-item .category-icon {
  font-size: 16px;
  flex-shrink: 0;
}

.category-item .category-icon.folder {
  color: #faad14;
}

.category-item .category-icon.leaf {
  color: #165DFF;
}

.category-item .category-name {
  font-size: 14px;
  color: #303133;
  flex: 1;
}

.category-item.active .category-name {
  color: #165DFF;
  font-weight: 600;
}

.category-item .category-count {
  font-size: 12px;
  color: #909399;
  background: #f0f2f5;
  padding: 2px 8px;
  border-radius: 10px;
  flex-shrink: 0;
}

.category-item.active .category-count {
  background: #d9e8ff;
  color: #165DFF;
}

.children-container {
  position: relative;
  padding-left: 24px;
}

.children-container::before {
  content: '';
  position: absolute;
  left: 18px;
  top: 0;
  bottom: 12px;
  width: 1px;
  background: #d9d9d9;
}

.category-node.level-2 .category-item {
  padding: 8px 12px;
  position: relative;
}

.category-node.level-2 .category-item::before {
  content: '';
  position: absolute;
  left: -6px;
  top: 50%;
  width: 12px;
  height: 1px;
  background: #d9d9d9;
}

.category-node.level-2.last-child .category-item::after {
  content: '';
  position: absolute;
  left: -7px;
  top: 50%;
  bottom: 0;
  width: 3px;
  background: #fff;
}

.category-node.level-2 .line-connector {
  display: none;
}

.category-node.level-2 .category-icon.leaf {
  color: #165DFF;
}

.expand-icon {
  font-size: 12px;
  color: #909399;
  transition: transform 0.2s ease-in-out;
  width: 16px;
  flex-shrink: 0;
}

.expand-icon.expanded {
  transform: rotate(90deg);
  color: #165DFF;
}

.expand-icon.hidden {
  visibility: hidden;
}

.goods-card {
  flex: 1;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.08);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.goods-card .toolbar-card {
  padding: 14px 16px;
  border-bottom: 1px solid #f0f0f0;
  background: linear-gradient(135deg, #fafbfc 0%, #f5f7fa 100%);
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-shrink: 0;
}

.goods-card .toolbar-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.goods-card .toolbar-right {
  display: flex;
  align-items: center;
  gap: 8px;
}

.goods-card .search-box {
  position: relative;
  display: flex;
  align-items: center;
}

.goods-card .search-icon {
  position: absolute;
  left: 10px;
  color: #9ca3af;
  font-size: 14px;
}

.goods-card .search-input {
  width: 240px;
}

.goods-card .search-input :deep(.el-input__wrapper) {
  padding-left: 30px;
  border-radius: 6px;
}

.goods-card .table-card {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.goods-card .data-table {
  flex: 1;
}

.goods-card .data-table :deep(.el-table__row) {
  transition: all 0.2s ease-in-out;
}

.goods-card .data-table :deep(.el-table__row:hover) {
  outline: 1px solid #1890ff;
  outline-offset: -1px;
  background-color: #e6f7ff !important;
}

.goods-card .data-table :deep(.el-table__row:hover) .el-table__cell {
  border-top: 1px solid #1890ff;
  border-bottom: 1px solid #1890ff;
}

.goods-card .data-table :deep(.el-table__row:hover .el-table__cell:first-child) {
  border-left: 1px solid #1890ff;
}

.goods-card .data-table :deep(.el-table__row:hover .el-table__cell:last-child) {
  border-right: 1px solid #1890ff;
}

.goods-card .pagination-wrapper {
  padding: 12px 16px;
  border-top: 1px solid #f0f0f0;
  background: #fafbfc;
  flex-shrink: 0;
}

.code-badge {
  display: inline-block;
  padding: 2px 8px;
  background: #f0f5ff;
  color: #165DFF;
  font-size: 12px;
  font-weight: 500;
  border-radius: 4px;
  font-family: 'Monaco', 'Consolas', monospace;
}

.name-cell {
  display: flex;
  align-items: center;
  gap: 10px;
}

.goods-initials {
  width: 32px;
  height: 32px;
  background: linear-gradient(135deg, #165DFF 0%, #0E4FD9 100%);
  color: #fff;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 600;
  flex-shrink: 0;
}

.goods-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.goods-name {
  font-size: 13px;
  font-weight: 500;
  color: #303133;
}

.goods-category {
  font-size: 11px;
  color: #909399;
}

.spec-text {
  color: #606266;
}

.price-text {
  font-weight: 600;
  font-family: 'Monaco', 'Consolas', monospace;
}

.price-text.purchase {
  color: #909399;
}

.price-text.sale {
  color: #165DFF;
}

.price-text.profit {
  color: #52c41a;
}

.action-buttons {
  display: flex;
  justify-content: center;
  gap: 4px;
}

.goods-form .price-input-wrapper {
  position: relative;
}

.goods-form .price-input-wrapper .error-tip {
  position: absolute;
  bottom: -18px;
  left: 0;
  font-size: 11px;
  color: #f56c6c;
  white-space: nowrap;
}

.goods-form .price-input-wrapper.has-error {
  margin-bottom: 18px;
}

.goods-form .price-input :deep(.el-input__wrapper) {
  padding-left: 8px;
}

.goods-form .input-prefix {
  color: #909399;
  font-weight: 500;
}

.goods-form :deep(.el-divider__text) {
  font-size: 13px;
  color: #606266;
  font-weight: 500;
}

.category-actions {
  display: flex;
  gap: 8px;
}

.category-manage-dialog :deep(.el-dialog__body) {
  padding: 16px 20px;
}

.category-manage-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid #f0f0f0;
}

.category-manage-header .header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.category-table-wrapper {
  max-height: 450px;
  overflow-y: auto;
}

.category-drag-tree {
  width: 100%;
}

.category-drag-tree :deep(.el-tree-node__content) {
  height: auto;
  padding: 8px 12px;
  margin: 4px 0;
  border-radius: 6px;
  border: 1px solid transparent;
  transition: all 0.2s;
}

.category-drag-tree :deep(.el-tree-node__content:hover) {
  background-color: #f5f7fa;
  border-color: #dcdfe6;
}

.category-drag-tree :deep(.el-tree-node.is-drop-inner > .el-tree-node__content) {
  background-color: #e6f4ff;
  border-color: #165DFF;
}

.category-drag-tree :deep(.el-tree-node.is-drop-before > .el-tree-node__content::before) {
  content: '';
  position: absolute;
  top: -2px;
  left: 0;
  right: 0;
  height: 2px;
  background-color: #165DFF;
}

.category-drag-tree :deep(.el-tree-node.is-drop-after > .el-tree-node__content::after) {
  content: '';
  position: absolute;
  bottom: -2px;
  left: 0;
  right: 0;
  height: 2px;
  background-color: #165DFF;
}

.category-tree-node-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  padding: 4px 0;
}

.category-tree-node-content .node-left {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1;
}

.category-tree-node-content .drag-handle {
  cursor: move;
  color: #909399;
  font-size: 16px;
  padding: 4px;
  border-radius: 4px;
  transition: all 0.2s;
}

.category-tree-node-content .drag-handle:hover {
  color: #165DFF;
  background-color: #e6f4ff;
}

.category-tree-node-content .folder-icon {
  color: #faad14;
  font-size: 16px;
}

.category-tree-node-content .leaf-icon {
  color: #165DFF;
  font-size: 16px;
}

.category-tree-node-content .name-text {
  font-weight: 500;
  color: #303133;
}

.category-tree-node-content .code-tag {
  background: #f0f5ff;
  color: #165DFF;
  border: none;
  font-size: 11px;
  font-family: 'Monaco', 'Consolas', monospace;
  padding: 0 6px;
  height: 18px;
  line-height: 18px;
}

.category-tree-node-content .node-right {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-shrink: 0;
}

.category-tree-node-content .goods-count {
  display: inline-block;
  min-width: 24px;
  padding: 2px 8px;
  background: #f5f5f5;
  color: #909399;
  border-radius: 10px;
  font-size: 12px;
  font-weight: 500;
}

.category-tree-node-content .goods-count.has-goods {
  background: #e6f7ff;
  color: #165DFF;
}

.category-table-wrapper :deep(.el-table) {
  --el-table-border-color: #f0f0f0;
}

.category-table-wrapper :deep(.el-table__header th) {
  font-weight: 600;
  color: #303133;
  background: #fafafa !important;
}

.category-table-wrapper :deep(.el-table__row) {
  transition: background-color 0.2s;
}

.category-table-wrapper :deep(.el-table__row:hover > td) {
  background-color: #f5f7fa !important;
}

.category-name-cell {
  display: flex;
  align-items: center;
  gap: 8px;
}

.category-name-cell .folder-icon {
  color: #faad14;
  font-size: 16px;
}

.category-name-cell .leaf-icon {
  color: #165DFF;
  font-size: 16px;
}

.category-name-cell .name-text {
  font-weight: 500;
  color: #303133;
}

.category-name-cell .code-tag {
  background: #f0f5ff;
  color: #165DFF;
  border: none;
  font-size: 11px;
  font-family: 'Monaco', 'Consolas', monospace;
}

.goods-count {
  display: inline-block;
  min-width: 24px;
  padding: 2px 8px;
  background: #f5f5f5;
  color: #909399;
  border-radius: 10px;
  font-size: 12px;
  font-weight: 500;
}

.goods-count.has-goods {
  background: #e6f7ff;
  color: #165DFF;
}

.action-btns {
  display: flex;
  justify-content: center;
  gap: 4px;
}

.action-btns .el-button {
  padding: 4px 8px;
}

.category-form-dialog :deep(.el-dialog__body) {
  padding: 20px 24px 0;
}

.category-form-dialog :deep(.el-form-item) {
  margin-bottom: 18px;
}

.category-form-dialog :deep(.el-form-item__label) {
  font-weight: 500;
  color: #303133;
  padding-bottom: 6px;
}

.status-radio {
  display: flex;
  gap: 20px;
}

.status-radio :deep(.el-radio) {
  margin-right: 0;
}

.parent-category-select :deep(.el-tree-node__content) {
  height: auto;
  padding: 6px 8px;
  margin: 2px 0;
  border-radius: 4px;
}

.parent-category-select :deep(.el-tree-node__content:hover) {
  background-color: #f0f5ff;
}

.parent-category-select :deep(.el-tree-node.is-current > .el-tree-node__content) {
  background-color: #e6f4ff;
}

.category-tree-node {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  padding: 2px 0;
}

.category-tree-node.is-disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.category-tree-node .node-content {
  display: flex;
  align-items: center;
  gap: 8px;
}

.category-tree-node .node-icon {
  font-size: 16px;
  transition: transform 0.2s;
}

.category-tree-node .node-icon.is-folder {
  color: #faad14;
}

.category-tree-node .node-icon.is-leaf {
  color: #165DFF;
}

.category-tree-node .node-label {
  font-size: 13px;
  color: #303133;
  font-weight: 500;
}

.category-tree-node .node-code {
  background: #f0f5ff;
  color: #165DFF;
  border: none;
  font-size: 11px;
  font-family: 'Monaco', 'Consolas', monospace;
  padding: 0 6px;
  height: 18px;
  line-height: 18px;
}

.category-tree-node .check-icon {
  color: #165DFF;
  font-size: 14px;
  font-weight: bold;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.category-select-node {
  display: flex;
  align-items: center;
  gap: 6px;
}

.category-select-node.is-disabled {
  color: #909399;
}

.category-select-node .level-icon {
  color: #E6A23C;
  font-size: 14px;
}
</style>

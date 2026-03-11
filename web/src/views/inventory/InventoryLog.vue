<template>
  <div class="common-page inventory-log-page">
    <div class="page-content">
      <div class="toolbar-card">
        <div class="toolbar-left">
          <div class="search-box">
            <el-icon class="search-icon"><Search /></el-icon>
            <el-input
              v-model="searchKeyword"
              placeholder="搜索商品"
              class="search-input"
              clearable
              @keyup.enter="loadLogs"
            />
          </div>
          <el-select v-model="changeTypeFilter" placeholder="交易类型" clearable style="width: 140px" @change="loadLogs">
            <el-option label="全部" :value="''" />
            <el-option label="采购入库" value="purchase_in" />
            <el-option label="销售出库" value="sale_out" />
            <el-option label="调拨入库" value="transfer_in" />
            <el-option label="调拨出库" value="transfer_out" />
            <el-option label="库存调整" value="adjust" />
          </el-select>
        </div>
        <div class="toolbar-right">
          <el-button :icon="Refresh" @click="loadLogs">刷新</el-button>
        </div>
      </div>

      <div class="table-card">
        <el-table 
          :data="logList" 
          style="width: 100%" 
          v-loading="loading"
          class="data-table"
          stripe
          :height="tableHeight"
          :header-cell-style="{ background: 'var(--color-bg-light)' }"
        >
          <el-table-column label="时间" min-width="130">
            <template #default="{ row }">{{ formatDateTime(row.created_at) }}</template>
          </el-table-column>
          <el-table-column prop="goods_name" label="商品" min-width="120" show-overflow-tooltip />
          <el-table-column prop="warehouse_name" label="仓库" min-width="100" show-overflow-tooltip />
          <el-table-column label="交易类型" min-width="60" align="center">
            <template #default="{ row }">
              <el-tag :type="getTransactionType(row).color" size="small">
                {{ getTransactionType(row).text }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="变动" min-width="50" align="right">
            <template #default="{ row }">
              <span :class="row.change_type === 'inbound' ? 'text-success' : 'text-danger'">
                {{ formatChangeQuantity(row) }}
              </span>
            </template>
          </el-table-column>
          <el-table-column label="前" min-width="50" align="right">
            <template #default="{ row }">{{ formatQuantity(row.before_quantity) }}</template>
          </el-table-column>
          <el-table-column label="后" min-width="50" align="right">
            <template #default="{ row }">{{ formatQuantity(row.after_quantity) }}</template>
          </el-table-column>
          <el-table-column label="备注" min-width="160">
            <template #default="{ row }">
              <span v-html="formatRemark(row.remark)" @click="handleOrderClick($event)"></span>
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
            @size-change="loadLogs"
            @current-change="loadLogs"
          />
        </div>
      </div>
    </div>

    <!-- 订单详情弹窗 -->
    <el-dialog
      v-model="orderDetailVisible"
      width="700px"
      class="view-dialog"
      :show-close="false"
    >
      <template #header>
        <div class="dialog-header">
          <span class="dialog-title">{{ orderDetailTitle }}</span>
          <div class="status-badge small" :class="orderDetail?.status" v-if="orderDetail && orderType !== 'transfer'">
            <span class="status-dot"></span>
            {{ getStatusText(orderDetail?.status) }}
          </div>
        </div>
        <span class="close-btn" @click="orderDetailVisible = false">×</span>
      </template>
      
      <div class="detail-container" v-if="orderDetail" v-loading="orderDetailLoading">
        <!-- 采购订单详情 -->
        <template v-if="orderType === 'purchase'">
          <div class="info-section">
            <div class="info-row highlight-row">
              <div class="info-item-group">
                <span class="info-label">供应商</span>
                <span class="info-value">{{ orderDetail.supplier_name }}</span>
              </div>
              <div class="info-item-group">
                <span class="info-label">采购单号</span>
                <span class="info-value primary">{{ orderDetail.order_no }}</span>
              </div>
            </div>
            <div class="info-row highlight-row">
              <div class="info-item-group">
                <span class="info-label">仓库</span>
                <span class="info-value">{{ orderDetail.warehouse_name }}</span>
              </div>
              <div class="info-item-group">
                <span class="info-label">总金额</span>
                <span class="info-value price">¥{{ formatPrice(orderDetail.total_amount) }}</span>
              </div>
            </div>
            <div class="info-row">
              <div class="info-item">
                <span class="info-label">采购日期</span>
                <span class="info-value">{{ orderDetail.order_date }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">入库时间</span>
                <span class="info-value">{{ orderDetail.stock_in_time ? formatDateTime(orderDetail.stock_in_time) : '-' }}</span>
              </div>
            </div>
            <div class="info-row">
              <div class="info-item">
                <span class="info-label">创建人</span>
                <span class="info-value">{{ orderDetail.created_by_name || '-' }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">创建时间</span>
                <span class="info-value">{{ formatDateTime(orderDetail.created_at) }}</span>
              </div>
            </div>
          </div>
          
          <div class="remark-box" v-if="orderDetail.remark">
            <div class="remark-header">
              <el-icon class="remark-icon"><Document /></el-icon>
              <span>采购备注</span>
            </div>
            <div class="remark-text">{{ orderDetail.remark }}</div>
          </div>
          
          <div class="items-section">
            <div class="items-header" @click="itemsExpanded = !itemsExpanded">
              <div class="header-left">
                <el-icon class="expand-icon" :class="{ expanded: itemsExpanded }"><ArrowRight /></el-icon>
                <span class="header-title">采购明细</span>
                <span class="header-count">{{ orderDetail.items?.length || 0 }}项</span>
              </div>
              <span class="expand-hint">{{ itemsExpanded ? '收起' : '展开' }}</span>
            </div>
            <el-collapse-transition>
              <div class="items-body" v-show="itemsExpanded">
                <el-table :data="orderDetail.items || []" border size="small" class="detail-table">
                  <el-table-column prop="goods_name" label="商品名称" min-width="140">
                    <template #default="{ row }">
                      <span class="goods-name">{{ row.goods_name }}</span>
                    </template>
                  </el-table-column>
                  <el-table-column prop="goods_spec" label="规格" min-width="80" align="center">
                    <template #default="{ row }">
                      <span class="spec-text">{{ row.goods_spec || '-' }}</span>
                    </template>
                  </el-table-column>
                  <el-table-column prop="quantity" label="数量" min-width="90" align="center">
                    <template #default="{ row }">
                      <span class="quantity-cell">{{ formatQuantity(row.quantity) }}</span>
                      <span class="unit-text">{{ row.unit || '-' }}</span>
                    </template>
                  </el-table-column>
                  <el-table-column prop="price" label="单价" width="85" align="right">
                    <template #default="{ row }">¥{{ formatPrice(row.price) }}</template>
                  </el-table-column>
                  <el-table-column prop="amount" label="金额" width="95" align="right">
                    <template #default="{ row }">
                      <span class="amount-cell">¥{{ formatPrice(row.amount) }}</span>
                    </template>
                  </el-table-column>
                </el-table>
              </div>
            </el-collapse-transition>
          </div>
        </template>

        <!-- 销售订单详情 -->
        <template v-if="orderType === 'sale'">
          <div class="info-section">
            <div class="info-row highlight-row">
              <div class="info-item-group">
                <span class="info-label">客户</span>
                <span class="info-value">{{ orderDetail.customer_name }}</span>
              </div>
              <div class="info-item-group">
                <span class="info-label">销售单号</span>
                <span class="info-value primary">{{ orderDetail.order_no }}</span>
              </div>
            </div>
            <div class="info-row highlight-row">
              <div class="info-item-group">
                <span class="info-label">仓库</span>
                <span class="info-value">{{ orderDetail.warehouse_name }}</span>
              </div>
              <div class="info-item-group">
                <span class="info-label">总金额</span>
                <span class="info-value price">¥{{ formatPrice(orderDetail.total_amount) }}</span>
              </div>
            </div>
            <div class="info-row">
              <div class="info-item">
                <span class="info-label">销售日期</span>
                <span class="info-value">{{ orderDetail.order_date }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">出库时间</span>
                <span class="info-value">{{ orderDetail.stock_out_time ? formatDateTime(orderDetail.stock_out_time) : '-' }}</span>
              </div>
            </div>
            <div class="info-row">
              <div class="info-item">
                <span class="info-label">创建人</span>
                <span class="info-value">{{ orderDetail.created_by_name || '-' }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">创建时间</span>
                <span class="info-value">{{ formatDateTime(orderDetail.created_at) }}</span>
              </div>
            </div>
          </div>
          
          <div class="remark-box" v-if="orderDetail.remark">
            <div class="remark-header">
              <el-icon class="remark-icon"><Document /></el-icon>
              <span>销售备注</span>
            </div>
            <div class="remark-text">{{ orderDetail.remark }}</div>
          </div>
          
          <div class="items-section">
            <div class="items-header" @click="itemsExpanded = !itemsExpanded">
              <div class="header-left">
                <el-icon class="expand-icon" :class="{ expanded: itemsExpanded }"><ArrowRight /></el-icon>
                <span class="header-title">销售明细</span>
                <span class="header-count">{{ orderDetail.items?.length || 0 }}项</span>
              </div>
              <span class="expand-hint">{{ itemsExpanded ? '收起' : '展开' }}</span>
            </div>
            <el-collapse-transition>
              <div class="items-body" v-show="itemsExpanded">
                <el-table :data="orderDetail.items || []" border size="small" class="detail-table">
                  <el-table-column prop="goods_name" label="商品名称" min-width="140">
                    <template #default="{ row }">
                      <span class="goods-name">{{ row.goods_name }}</span>
                    </template>
                  </el-table-column>
                  <el-table-column prop="goods_spec" label="规格" min-width="80" align="center">
                    <template #default="{ row }">
                      <span class="spec-text">{{ row.goods_spec || '-' }}</span>
                    </template>
                  </el-table-column>
                  <el-table-column prop="quantity" label="数量" min-width="90" align="center">
                    <template #default="{ row }">
                      <span class="quantity-cell">{{ formatQuantity(row.quantity) }}</span>
                      <span class="unit-text">{{ row.unit || '-' }}</span>
                    </template>
                  </el-table-column>
                  <el-table-column prop="price" label="单价" width="85" align="right">
                    <template #default="{ row }">¥{{ formatPrice(row.price) }}</template>
                  </el-table-column>
                  <el-table-column prop="amount" label="金额" width="95" align="right">
                    <template #default="{ row }">
                      <span class="amount-cell">¥{{ formatPrice(row.amount) }}</span>
                    </template>
                  </el-table-column>
                </el-table>
              </div>
            </el-collapse-transition>
          </div>
        </template>

        <!-- 库存调整详情 -->
        <template v-if="orderType === 'adjust'">
          <div class="info-section">
            <div class="info-row highlight-row">
              <div class="info-item-group">
                <span class="info-label">调整单号</span>
                <span class="info-value primary">{{ orderDetail.order_no }}</span>
              </div>
              <div class="info-item-group">
                <span class="info-label">仓库</span>
                <span class="info-value">{{ orderDetail.warehouse_name }}</span>
              </div>
            </div>
            <div class="info-row">
              <div class="info-item">
                <span class="info-label">调整类型</span>
                <span class="info-value">{{ orderDetail.adjust_type_display }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">调整原因</span>
                <span class="info-value">{{ orderDetail.reason_display }}</span>
              </div>
            </div>
            <div class="info-row">
              <div class="info-item">
                <span class="info-label">创建人</span>
                <span class="info-value">{{ orderDetail.created_by_name || '-' }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">创建时间</span>
                <span class="info-value">{{ formatDateTime(orderDetail.created_at) }}</span>
              </div>
            </div>
          </div>
          
          <div class="remark-box" v-if="orderDetail.remark">
            <div class="remark-header">
              <el-icon class="remark-icon"><Document /></el-icon>
              <span>调整备注</span>
            </div>
            <div class="remark-text">{{ orderDetail.remark }}</div>
          </div>
          
          <div class="items-section">
            <div class="items-header" @click="itemsExpanded = !itemsExpanded">
              <div class="header-left">
                <el-icon class="expand-icon" :class="{ expanded: itemsExpanded }"><ArrowRight /></el-icon>
                <span class="header-title">调整明细</span>
                <span class="header-count">{{ orderDetail.items?.length || 0 }}项</span>
              </div>
              <span class="expand-hint">{{ itemsExpanded ? '收起' : '展开' }}</span>
            </div>
            <el-collapse-transition>
              <div class="items-body" v-show="itemsExpanded">
                <el-table :data="orderDetail.items || []" border size="small" class="detail-table">
                  <el-table-column prop="goods_name" label="商品名称" min-width="140">
                    <template #default="{ row }">
                      <span class="goods-name">{{ row.goods_name }}</span>
                    </template>
                  </el-table-column>
                  <el-table-column prop="goods_spec" label="规格" min-width="80" align="center">
                    <template #default="{ row }">
                      <span class="spec-text">{{ row.goods_spec || '-' }}</span>
                    </template>
                  </el-table-column>
                  <el-table-column label="调整前" min-width="90" align="center">
                    <template #default="{ row }">
                      <span class="quantity-cell">{{ formatQuantity(row.before_quantity) }}</span>
                      <span class="unit-text">{{ row.unit || '-' }}</span>
                    </template>
                  </el-table-column>
                  <el-table-column label="调整数量" min-width="90" align="center">
                    <template #default="{ row }">
                      <span :class="row.adjust_quantity >= 0 ? 'text-success' : 'text-danger'">
                        {{ row.adjust_quantity >= 0 ? '+' : '' }}{{ formatQuantity(row.adjust_quantity) }}
                      </span>
                      <span class="unit-text">{{ row.unit || '-' }}</span>
                    </template>
                  </el-table-column>
                  <el-table-column label="调整后" min-width="90" align="center">
                    <template #default="{ row }">
                      <span class="quantity-cell">{{ formatQuantity(row.after_quantity) }}</span>
                      <span class="unit-text">{{ row.unit || '-' }}</span>
                    </template>
                  </el-table-column>
                </el-table>
              </div>
            </el-collapse-transition>
          </div>
        </template>

        <!-- 库存调拨详情 -->
        <template v-if="orderType === 'transfer'">
          <div class="info-section">
            <div class="info-row highlight-row">
              <div class="info-item-group">
                <span class="info-label">调拨单号</span>
                <span class="info-value primary">{{ orderDetail.order_no }}</span>
              </div>
              <div class="info-item-group">
                <span class="info-label">状态</span>
                <div class="status-badge small" :class="orderDetail.status">
                  <span class="status-dot"></span>
                  {{ getStatusText(orderDetail.status) }}
                </div>
              </div>
            </div>
            <div class="info-row highlight-row">
              <div class="info-item-group">
                <span class="info-label">调出仓库</span>
                <span class="info-value">{{ orderDetail.from_warehouse_name }}</span>
              </div>
              <div class="info-item-group">
                <span class="info-label">调入仓库</span>
                <span class="info-value">{{ orderDetail.to_warehouse_name }}</span>
              </div>
            </div>
            <div class="info-row">
              <div class="info-item">
                <span class="info-label">创建人</span>
                <span class="info-value">{{ orderDetail.created_by_name || '-' }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">创建时间</span>
                <span class="info-value">{{ formatDateTime(orderDetail.created_at) }}</span>
              </div>
            </div>
          </div>
          
          <div class="remark-box" v-if="orderDetail.remark">
            <div class="remark-header">
              <el-icon class="remark-icon"><Document /></el-icon>
              <span>调拨备注</span>
            </div>
            <div class="remark-text">{{ orderDetail.remark }}</div>
          </div>
          
          <div class="items-section">
            <div class="items-header" @click="itemsExpanded = !itemsExpanded">
              <div class="header-left">
                <el-icon class="expand-icon" :class="{ expanded: itemsExpanded }"><ArrowRight /></el-icon>
                <span class="header-title">调拨明细</span>
                <span class="header-count">{{ orderDetail.items?.length || 0 }}项</span>
              </div>
              <span class="expand-hint">{{ itemsExpanded ? '收起' : '展开' }}</span>
            </div>
            <el-collapse-transition>
              <div class="items-body" v-show="itemsExpanded">
                <el-table :data="orderDetail.items || []" border size="small" class="detail-table">
                  <el-table-column prop="goods_name" label="商品名称" min-width="140">
                    <template #default="{ row }">
                      <span class="goods-name">{{ row.goods_name }}</span>
                    </template>
                  </el-table-column>
                  <el-table-column prop="goods_spec" label="规格" min-width="80" align="center">
                    <template #default="{ row }">
                      <span class="spec-text">{{ row.goods_spec || '-' }}</span>
                    </template>
                  </el-table-column>
                  <el-table-column prop="quantity" label="调拨数量" min-width="90" align="center">
                    <template #default="{ row }">
                      <span class="quantity-cell">{{ formatQuantity(row.quantity) }}</span>
                      <span class="unit-text">{{ row.unit || '-' }}</span>
                    </template>
                  </el-table-column>
                </el-table>
              </div>
            </el-collapse-transition>
          </div>
        </template>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Search, Refresh, Document, ArrowRight } from '@element-plus/icons-vue'
import { getInventoryLogs, getStockAdjustByNo, getStockTransferByNo } from '../../api/inventory'
import { getPurchaseOrderByNo } from '../../api/purchase'
import { getSaleOrderByNo } from '../../api/sale'

const loading = ref(false)
const logList = ref([])
const searchKeyword = ref('')
const changeTypeFilter = ref('')
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)
const tableHeight = ref(0)

const orderDetailVisible = ref(false)
const orderDetailLoading = ref(false)
const orderDetailTitle = ref('')
const orderDetail = ref(null)
const orderType = ref('')
const itemsExpanded = ref(true)

/**
 * 格式化日期时间，移除时区信息
 */
const formatDateTime = (datetime) => {
  if (!datetime) return '-'
  
  const date = new Date(datetime)
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  const hours = String(date.getHours()).padStart(2, '0')
  const minutes = String(date.getMinutes()).padStart(2, '0')
  const seconds = String(date.getSeconds()).padStart(2, '0')
  
  return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`
}

/**
 * 格式化数量，去除小数点
 */
const formatQuantity = (value) => {
  if (value === null || value === undefined) return '-'
  const num = Number(value)
  if (isNaN(num)) return '-'
  return Number.isInteger(num) ? num.toString() : num.toFixed(2).replace(/\.?0+$/, '')
}

/**
 * 格式化变动数量，添加正负符号
 */
const formatChangeQuantity = (row) => {
  const value = row.change_quantity
  if (value === null || value === undefined) return '-'
  const num = Number(value)
  if (isNaN(num)) return '-'
  
  const formattedNum = Number.isInteger(num) ? num.toString() : num.toFixed(2).replace(/\.?0+$/, '')
  
  // 入库显示 + 号，出库显示 - 号
  if (row.change_type === 'inbound') {
    return `+${formattedNum}`
  } else {
    return `-${formattedNum}`
  }
}

/**
 * 获取交易类型信息（文字和颜色）
 */
const getTransactionType = (row) => {
  const remark = row.remark || ''
  
  // 根据备注判断具体交易类型
  if (remark.includes('采购入库')) {
    return { text: '采购入库', color: 'success' }
  }
  if (remark.includes('销售出库')) {
    return { text: '销售出库', color: 'danger' }
  }
  if (remark.includes('调拨出库')) {
    return { text: '调拨出库', color: 'warning' }
  }
  if (remark.includes('调拨入库')) {
    return { text: '调拨入库', color: 'primary' }
  }
  if (remark.includes('库存调整')) {
    return { text: '库存调整', color: 'info' }
  }
  
  // 根据变动类型判断
  if (row.change_type === 'inbound') {
    return { text: '入库', color: 'success' }
  }
  if (row.change_type === 'outbound') {
    return { text: '出库', color: 'danger' }
  }
  
  return { text: row.change_type_display || '未知', color: 'info' }
}

/**
 * 格式化备注，将单号转为可点击链接
 */
const formatRemark = (remark) => {
  if (!remark) return '-'
  
  // 匹配单号格式：大写字母+数字组合（如 PO20260220001, SO20260220001 等）
  return remark.replace(/([A-Z]{2,3}\d+)/g, '<span class="order-link" data-order="$1">$1</span>')
}

/**
 * 处理订单号点击事件
 */
const handleOrderClick = async (event) => {
  const target = event.target
  if (!target.classList.contains('order-link')) return
  
  const orderNo = target.dataset.order
  if (!orderNo) return
  
  // 根据单号前缀判断订单类型
  const prefix = orderNo.substring(0, 2).toUpperCase()
  
  orderDetailVisible.value = true
  orderDetailLoading.value = true
  orderDetail.value = null
  orderType.value = ''
  
  try {
    let res = null
    
    if (prefix === 'PO') {
      // 采购订单
      orderDetailTitle.value = '采购订单详情'
      orderType.value = 'purchase'
      res = await getPurchaseOrderByNo(orderNo)
    } else if (prefix === 'SO') {
      // 销售订单
      orderDetailTitle.value = '销售订单详情'
      orderType.value = 'sale'
      res = await getSaleOrderByNo(orderNo)
    } else if (prefix === 'SA') {
      // 库存调整
      orderDetailTitle.value = '库存调整详情'
      orderType.value = 'adjust'
      res = await getStockAdjustByNo(orderNo)
    } else if (prefix === 'ST') {
      // 库存调拨
      orderDetailTitle.value = '库存调拨详情'
      orderType.value = 'transfer'
      res = await getStockTransferByNo(orderNo)
    } else {
      ElMessage.warning('未知的单据类型')
      orderDetailVisible.value = false
      return
    }
    
    orderDetail.value = res.data
  } catch (error) {
    ElMessage.error('获取订单详情失败：' + (error.message || '未知错误'))
    orderDetailVisible.value = false
  } finally {
    orderDetailLoading.value = false
  }
}

/**
 * 获取状态文本
 */
const getStatusText = (status) => {
  const textMap = {
    draft: '草稿',
    pending: '待处理',
    confirmed: '已确认',
    completed: '已完成',
    cancelled: '已取消',
    partial: '部分完成'
  }
  return textMap[status] || status
}

/**
 * 格式化价格
 */
const formatPrice = (value) => {
  if (value === null || value === undefined) return '-'
  const num = Number(value)
  if (isNaN(num)) return '-'
  return num.toFixed(2)
}

const loadLogs = async () => {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      page_size: pageSize.value
    }
    if (changeTypeFilter.value) {
      params.transaction_type = changeTypeFilter.value
    }
    if (searchKeyword.value) {
      params.search = searchKeyword.value
    }
    const res = await getInventoryLogs(params)
    logList.value = res.data.items || res.data.results || []
    total.value = res.data.count || 0
  } catch (error) {
    logList.value = []
    total.value = 0
    ElMessage.error('加载数据失败：' + (error.message || '未知错误'))
  } finally {
    loading.value = false
  }
}

const calculateTableHeight = () => {
  nextTick(() => {
    const toolbarCard = document.querySelector('.toolbar-card')
    const paginationWrapper = document.querySelector('.pagination-wrapper')
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

onMounted(() => {
  loadLogs()
  calculateTableHeight()
  window.addEventListener('resize', calculateTableHeight)
})

onUnmounted(() => {
  window.removeEventListener('resize', calculateTableHeight)
})
</script>

<style scoped>
.inventory-log-page .text-success {
  color: var(--color-success);
  font-weight: 600;
}

.inventory-log-page .text-danger {
  color: var(--color-danger);
  font-weight: 600;
}

.inventory-log-page :deep(.order-link) {
  color: var(--color-primary);
  text-decoration: underline;
  cursor: pointer;
  font-weight: 500;
  transition: color 0.2s;
}

.inventory-log-page :deep(.order-link:hover) {
  color: var(--color-primary-dark, #4080ff);
}

.inventory-log-page .view-dialog :deep(.el-dialog__header) {
  border-bottom: 1px solid var(--color-border-light);
  padding-bottom: var(--spacing-md);
}

.inventory-log-page .view-dialog :deep(.el-dialog__body) {
  padding: var(--spacing-lg);
}

.inventory-log-page .status-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 4px 12px;
  background-color: var(--color-bg-light);
  color: var(--color-text-secondary);
  font-size: var(--font-size-sm);
  border-radius: 20px;
  font-weight: 500;
}

.inventory-log-page .status-badge.draft {
  background-color: rgba(245, 158, 11, 0.1);
  color: var(--color-warning);
}

.inventory-log-page .status-badge.pending {
  background-color: rgba(59, 130, 246, 0.1);
  color: var(--color-primary);
}

.inventory-log-page .status-badge.confirmed {
  background-color: rgba(34, 197, 94, 0.1);
  color: var(--color-success);
}

.inventory-log-page .status-badge.completed {
  background-color: rgba(34, 197, 94, 0.1);
  color: var(--color-success);
}

.inventory-log-page .status-badge.cancelled {
  background-color: rgba(239, 68, 68, 0.1);
  color: var(--color-danger);
}

.inventory-log-page .status-badge.partial {
  background-color: rgba(245, 158, 11, 0.1);
  color: var(--color-warning);
}

.inventory-log-page .status-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background-color: currentColor;
}

.inventory-log-page .view-items-title {
  font-size: 15px;
  font-weight: 600;
  color: var(--color-text-primary);
  margin: var(--spacing-lg) 0 var(--spacing-md);
  padding-left: var(--spacing-sm);
  border-left: 3px solid var(--color-primary);
}

.inventory-log-page .view-dialog {
  --el-dialog-border-radius: 8px;
}

.inventory-log-page .view-dialog :deep(.el-dialog__header) {
  padding: 0;
  margin: 0;
  position: relative;
}

.inventory-log-page .view-dialog :deep(.el-dialog__body) {
  padding: 0;
}

.inventory-log-page .dialog-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 14px 16px;
  background: linear-gradient(135deg, #f0f5ff 0%, #e6f4ff 100%);
  border-bottom: 1px solid #bae0ff;
  border-radius: var(--el-dialog-border-radius) var(--el-dialog-border-radius) 0 0;
  padding-right: 50px;
}

.inventory-log-page .dialog-title {
  font-size: 16px;
  font-weight: 600;
  color: #333;
}

.inventory-log-page .close-btn {
  position: absolute;
  top: 0;
  right: 0;
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  font-weight: 300;
  color: #999;
  cursor: pointer;
  line-height: 1;
  transition: all 0.2s;
  border-radius: 0 var(--el-dialog-border-radius) 0 6px;
  background: transparent;
}

.inventory-log-page .close-btn:hover {
  color: #333;
  background: rgba(0, 0, 0, 0.04);
}

.inventory-log-page .detail-container {
  padding: 0;
}

.inventory-log-page .info-section {
  background: #fafafa;
  border-radius: 6px;
  margin: 12px 16px;
  padding: 0;
  border: 1px solid #e8e8e8;
  overflow: hidden;
}

.inventory-log-page .info-row {
  display: flex;
  gap: 0;
  padding: 8px 12px;
  border-bottom: 1px solid #f0f0f0;
}

.inventory-log-page .info-row:last-child {
  border-bottom: none;
}

.inventory-log-page .info-row.highlight-row {
  background: linear-gradient(135deg, #f0f5ff 0%, #f5f9ff 100%);
  border-bottom: 1px solid #e6f0ff;
}

.inventory-log-page .info-item {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1;
}

.inventory-log-page .info-item-group {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1;
  padding: 4px 8px;
}

.inventory-log-page .info-label {
  font-size: 12px;
  color: #999;
  min-width: 56px;
  flex-shrink: 0;
  text-align: right;
}

.inventory-log-page .info-value {
  font-size: 13px;
  color: #333;
  font-weight: 500;
}

.inventory-log-page .info-value.primary {
  font-weight: 700;
  color: var(--color-primary);
  font-family: 'Monaco', 'Consolas', monospace;
}

.inventory-log-page .info-value.price {
  font-weight: 700;
  color: var(--color-primary);
  font-family: 'Monaco', 'Consolas', monospace;
}

.inventory-log-page .remark-box {
  background: #fffbe6;
  border: 1px solid #ffe58f;
  border-radius: 6px;
  margin: 0 16px 12px;
  padding: 10px 12px;
}

.inventory-log-page .remark-header {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: #d48806;
  font-weight: 600;
  margin-bottom: 6px;
}

.inventory-log-page .remark-icon {
  font-size: 14px;
}

.inventory-log-page .remark-text {
  font-size: 13px;
  color: #614700;
  line-height: 1.6;
  padding-left: 20px;
}

.inventory-log-page .items-section {
  border: 1px solid #e8e8e8;
  border-radius: 6px;
  margin: 0 16px 16px;
  overflow: hidden;
}

.inventory-log-page .items-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 12px;
  background: #f5f5f5;
  cursor: pointer;
  transition: background 0.2s;
}

.inventory-log-page .items-header:hover {
  background: #efefef;
}

.inventory-log-page .header-left {
  display: flex;
  align-items: center;
  gap: 8px;
}

.inventory-log-page .expand-icon {
  font-size: 12px;
  color: #999;
  transition: transform 0.2s;
}

.inventory-log-page .expand-icon.expanded {
  transform: rotate(90deg);
}

.inventory-log-page .header-title {
  font-size: 13px;
  font-weight: 600;
  color: #333;
}

.inventory-log-page .header-count {
  font-size: 12px;
  color: #999;
}

.inventory-log-page .expand-hint {
  font-size: 12px;
  color: #999;
}

.inventory-log-page .items-body {
  border-top: 1px solid #e8e8e8;
  padding: 0;
}

.inventory-log-page .detail-table {
  --el-table-header-bg-color: #f5f7fa;
  --el-table-border-color: #ebeef5;
  --el-table-row-hover-bg-color: #f0f5ff;
  font-size: 13px;
}

.inventory-log-page .detail-table :deep(.el-table__header th) {
  font-weight: 600;
  font-size: 12px;
  color: #606266;
  padding: 10px 0;
  background: linear-gradient(180deg, #f8fafc 0%, #f0f4f8 100%);
  border-bottom: 2px solid #e0e6ed;
}

.inventory-log-page .detail-table :deep(.el-table__body td) {
  padding: 10px 0;
  border-bottom: 1px solid #f0f2f5;
}

.inventory-log-page .detail-table :deep(.el-table__body tr:hover > td) {
  background-color: #f5f9ff !important;
}

.inventory-log-page .goods-name {
  font-size: 13px;
  color: #303133;
  font-weight: 500;
}

.inventory-log-page .spec-text {
  font-size: 12px;
  color: #606266;
}

.inventory-log-page .quantity-cell {
  font-weight: 500;
}

.inventory-log-page .unit-text {
  font-size: 12px;
  color: #303133;
  margin-left: 4px;
}

.inventory-log-page .amount-cell {
  font-weight: 600;
  color: var(--color-primary);
  font-family: 'Monaco', 'Consolas', monospace;
}

.inventory-log-page .status-badge.small {
  padding: 2px 8px;
  font-size: 12px;
  gap: 4px;
}

.inventory-log-page .status-badge.small .status-dot {
  width: 5px;
  height: 5px;
}
</style>

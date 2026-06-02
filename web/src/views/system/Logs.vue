<template>
  <div class="common-page logs-page">
    <div class="page-content">
      <div class="toolbar-card">
        <div class="toolbar-left">
          <div class="search-box">
            <el-icon class="search-icon"><Search /></el-icon>
            <el-input
              v-model="searchKeyword"
              placeholder="搜索操作详情"
              class="search-input"
              clearable
              @keyup.enter="loadData"
            />
          </div>
          <el-select v-model="queryForm.action" placeholder="操作类型" clearable style="width: 140px" @change="handleSearch">
            <el-option label="全部" :value="''" />
            <el-option label="创建" value="create" />
            <el-option label="更新" value="update" />
            <el-option label="删除" value="delete" />
            <el-option label="登录" value="login" />
            <el-option label="登出" value="logout" />
            <el-option label="其他" value="other" />
          </el-select>
        </div>
        <div class="toolbar-right">
          <el-button :icon="Download" @click="handleExport" :loading="exportLoading">导出</el-button>
          <el-button type="danger" :icon="Delete" @click="handleClearLogs" :loading="clearLoading">清空日志</el-button>
          <el-button :icon="Refresh" @click="handleReset">重置</el-button>
          <el-button type="primary" :icon="Search" @click="handleSearch">查询</el-button>
        </div>
      </div>

      <div class="table-card">
        <el-table 
          :data="tableData" 
          style="width: 100%" 
          v-loading="loading"
          class="data-table"
          stripe
          :height="tableHeight"
        >
          <el-table-column label="操作用户" width="150">
            <template #default="{ row }">
              {{ row.user_name }}
            </template>
          </el-table-column>
          <el-table-column label="操作类型" width="100">
            <template #default="{ row }">
              <el-tag :type="getActionType(row.action)">
                {{ getActionText(row.action) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="module" label="操作模块" width="150" />
          <el-table-column label="操作详情" min-width="480">
            <template #default="{ row }">
              <div class="detail-content" v-html="renderDetail(row)"></div>
            </template>
          </el-table-column>
          <el-table-column prop="ip_address" label="IP 地址" width="150" />
          <el-table-column label="操作时间" width="160">
            <template #default="{ row }">
              {{ formatDateTime(row.created_at) }}
            </template>
          </el-table-column>
        </el-table>
        <div class="pagination-wrapper">
          <el-pagination
            v-model:current-page="pagination.page"
            v-model:page-size="pagination.pageSize"
            :page-sizes="[10, 20, 50, 100]"
            :total="pagination.total"
            layout="total, sizes, prev, pager, next, jumper"
            @size-change="loadData"
            @current-change="loadData"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick, onUnmounted } from 'vue'
import { getLogs, exportLogs, clearLogs } from '../../api/system'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Refresh, Download, Delete } from '@element-plus/icons-vue'

const loading = ref(false)
const exportLoading = ref(false)
const clearLoading = ref(false)
const searchKeyword = ref('')
const tableHeight = ref(0)

const queryForm = ref({
  action: ''
})

const tableData = ref([])

const pagination = ref({
  page: 1,
  pageSize: 20,
  total: 0
})

const getActionType = (action) => {
  const typeMap = {
    create: 'success',
    update: 'primary',
    delete: 'danger',
    login: 'info',
    logout: 'warning',
    other: ''
  }
  return typeMap[action] || ''
}

const getActionText = (action) => {
  const textMap = {
    create: '创建',
    update: '更新',
    delete: '删除',
    login: '登录',
    logout: '登出',
    other: '其他'
  }
  return textMap[action] || action
}

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
 * 获取操作对应的图标 SVG
 */
const ICON_SVG = {
  create: '<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="#67c23a" stroke-width="2.2"><circle cx="12" cy="12" r="10"/><path d="M12 8v8M8 12h8"/></svg>',
  update: '<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="#409eff" stroke-width="2.2"><path d="M12 20h9"/><path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z"/></svg>',
  delete: '<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="#f56c6c" stroke-width="2.2"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/></svg>',
  login: '<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="#909399" stroke-width="2.2"><path d="M15 3h4a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2h-4"/><polyline points="10 17 15 12 10 7"/><line x1="15" y1="12" x2="3" y2="12"/></svg>',
  logout: '<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="#e6a23c" stroke-width="2.2"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" y1="12" x2="9" y2="12"/></svg>',
  cancel: '<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="#f56c6c" stroke-width="2.2"><circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/></svg>',
  confirm: '<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="#67c23a" stroke-width="2.2"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>',
  confirm_inbound: '<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="#67c23a" stroke-width="2.2"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>',
  update_status: '<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="#409eff" stroke-width="2.2"><circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/></svg>',
  other: '<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="#909399" stroke-width="2.2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>',
  shield: '<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="#e6a23c" stroke-width="2.2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><line x1="9" y1="12" x2="11" y2="14"/><line x1="11" y1="14" x2="15" y2="10"/></svg>',
  bullet: '<svg viewBox="0 0 8 8" width="8" height="8"><circle cx="4" cy="4" r="3" fill="#909399" opacity="0.5"/></svg>'
}

const getActionIcon = (action) => {
  return ICON_SVG[action] || ICON_SVG.other
}

/**
 * 获取操作类型对应的颜色
 */
const getActionColor = (action) => {
  const colors = {
    create: '#67c23a',
    update: '#409eff',
    delete: '#f56c6c',
    login: '#909399',
    logout: '#e6a23c',
    cancel: '#f56c6c',
    confirm: '#67c23a',
    confirm_inbound: '#67c23a',
    update_status: '#409eff',
    other: '#909399'
  }
  return colors[action] || colors.other
}

/**
 * 获取操作动词
 */
const getActionVerb = (action) => {
  const verbs = {
    create: '创建',
    update: '更新',
    delete: '删除',
    login: '登录',
    logout: '登出',
    cancel: '取消',
    confirm: '确认',
    confirm_inbound: '确认入库',
    update_status: '状态变更',
    other: '操作'
  }
  return verbs[action] || verbs.other
}

/**
 * 解析变更详情中的单个变更项
 * 格式: 字段名: "旧值" → "新值"
 */
const parseChangeItem = (changeStr) => {
  const match = changeStr.match(/^(.+?):\s*"(.+?)"\s*→\s*"(.+?)"$/)
  if (!match) return { raw: changeStr }
  return {
    field: match[1].trim(),
    oldValue: match[2],
    newValue: match[3]
  }
}

/**
 * 解析操作详情文本，返回结构化数据
 */
const parseDetail = (row) => {
  const detail = row.detail || ''
  const action = row.action

  if (action === 'login') {
    return { action, icon: getActionIcon(action), color: getActionColor(action), verb: getActionVerb(action), module: '', target: '', changes: [], rawDetail: detail }
  }
  if (action === 'logout') {
    return { action, icon: getActionIcon(action), color: getActionColor(action), verb: getActionVerb(action), module: '', target: '', changes: [], rawDetail: detail }
  }

  const createMatch = detail.match(/^创建(.+?):\s*(.+)$/)
  if (createMatch) {
    return { action, icon: getActionIcon(action), color: getActionColor(action), verb: '创建', module: createMatch[1], target: createMatch[2], changes: [], rawDetail: detail }
  }

  const updateMatch = detail.match(/^更新(.+?)「(.+?)」:\s*(.+)$/)
  if (updateMatch) {
    const changesStr = updateMatch[3]
    let changes = []
    if (changesStr !== '无变更') {
      changes = changesStr.split('; ').map(parseChangeItem)
    }
    return { action, icon: getActionIcon(action), color: getActionColor(action), verb: '更新', module: updateMatch[1], target: updateMatch[2], changes, rawDetail: detail }
  }

  const deleteMatch = detail.match(/^删除(.+?):\s*(.+)$/)
  if (deleteMatch) {
    return { action, icon: getActionIcon(action), color: getActionColor(action), verb: '删除', module: deleteMatch[1], target: deleteMatch[2], changes: [], rawDetail: detail }
  }

  const cancelMatch = detail.match(/^取消(.+?):\s*(.+)$/)
  if (cancelMatch) {
    return { action, icon: getActionIcon(action), color: getActionColor(action), verb: '取消', module: cancelMatch[1], target: cancelMatch[2], changes: [], rawDetail: detail }
  }

  if (action === 'confirm_inbound') {
    const confirmInboundMatch = detail.match(/^确认入库(.+?):\s*(.+)$/)
    if (confirmInboundMatch) {
      return { action, icon: getActionIcon(action), color: getActionColor(action), verb: '确认入库', module: confirmInboundMatch[1], target: confirmInboundMatch[2], changes: [], rawDetail: detail }
    }
  }

  const confirmMatch = detail.match(/^确认(.+?):\s*(.+)$/)
  if (confirmMatch) {
    return { action, icon: getActionIcon(action), color: getActionColor(action), verb: '确认', module: confirmMatch[1], target: confirmMatch[2], changes: [], rawDetail: detail }
  }

  const resetPwdMatch = detail.match(/^重置(.+?):\s*(.+)$/)
  if (resetPwdMatch) {
    return { action, icon: getActionIcon(action), color: getActionColor(action), verb: '重置', module: resetPwdMatch[1], target: resetPwdMatch[2], changes: [], rawDetail: detail }
  }

  const statusMatch = detail.match(/^(启用|禁用)(.+?)「(.+?)」/)
  if (statusMatch) {
    return { action, icon: getActionIcon(action), color: getActionColor(action), verb: statusMatch[1], module: statusMatch[2], target: statusMatch[3], changes: [], rawDetail: detail }
  }

  return { action, icon: getActionIcon(action), color: getActionColor(action), verb: getActionVerb(action), module: '', target: '', changes: [], rawDetail: detail }
}

/**
 * 渲染操作详情为结构化、带图标和颜色区别的富文本 HTML
 */
const renderDetail = (row) => {
  const parsed = parseDetail(row)
  const { icon, color, verb, module, target, changes, rawDetail } = parsed
  const esc = escapeHtml

  if (!module && !target && changes.length === 0 && rawDetail) {
    return `<div class="dl-row dl-simple"><span class="dl-icon">${icon}</span><span class="dl-text">${esc(rawDetail)}</span></div>`
  }

  let html = '<div class="dl-card">'

  html += '<div class="dl-header">'
  html += `<span class="dl-icon">${icon}</span>`
  html += `<span class="dl-verb" style="color:${color}">${esc(verb)}</span>`

  if (target) {
    html += `<span class="dl-tag" style="background:${color}18;color:${color};border-color:${color}40">${esc(target)}</span>`
  }

  if (module && target) {
    html += `<span class="dl-ctx">${esc(module)}</span>`
  } else if (module && !target) {
    html += `<span class="dl-tag" style="background:${color}18;color:${color};border-color:${color}40">${esc(module)}</span>`
  }
  html += '</div>'

  if (changes.length > 0) {
    html += '<div class="dl-changes">'
    let permIdx = 0
    changes.forEach((change) => {
      const isP = change.field === '权限'
      const totalLen = (change.oldValue || '').length + (change.newValue || '').length
      const needFold = isP && totalLen > 60

      if (needFold) {
        const pid = `perm-${++permIdx}-${Date.now()}`
        const oldShort = change.oldValue.length > 40 ? change.oldValue.substring(0, 40) + '…' : change.oldValue
        const newShort = change.newValue.length > 40 ? change.newValue.substring(0, 40) + '…' : change.newValue

        html += `<details class="dl-details dl-details-perm" id="${pid}">`
        html += '<summary class="dl-details-summary">'
        html += `<span class="dl-change-icon">${ICON_SVG.shield}</span>`
        html += '<span class="dl-change-label dl-change-label-perm">权限</span>'
        html += `<span class="dl-change-old dl-change-old-fold">${esc(oldShort)}</span>`
        html += '<span class="dl-change-arrow">→</span>'
        html += `<span class="dl-change-new dl-change-new-fold">${esc(newShort)}</span>`
        html += '<span class="dl-fold-hint">展开全部 ▾</span>'
        html += '</summary>'

        html += '<div class="dl-details-body">'
        html += '<div class="dl-change dl-change-perm">'
        html += `<span class="dl-change-icon">${ICON_SVG.shield}</span>`
        html += '<span class="dl-change-label dl-change-label-perm">权限</span>'
        html += `<span class="dl-change-old">${esc(change.oldValue)}</span>`
        html += '<span class="dl-change-arrow">→</span>'
        html += `<span class="dl-change-new">${esc(change.newValue)}</span>`
        html += '</div>'
        html += '</div>'
        html += '</details>'
      } else if (isP) {
        html += '<div class="dl-change dl-change-perm">'
        html += `<span class="dl-change-icon">${ICON_SVG.shield}</span>`
        html += '<span class="dl-change-label dl-change-label-perm">权限</span>'
        html += `<span class="dl-change-old">${esc(change.oldValue)}</span>`
        html += '<span class="dl-change-arrow">→</span>'
        html += `<span class="dl-change-new">${esc(change.newValue)}</span>`
        html += '</div>'
      } else {
        html += '<div class="dl-change">'
        html += `<span class="dl-change-icon">${ICON_SVG.bullet}</span>`
        html += `<span class="dl-change-label">${esc(change.field)}</span>`
        html += `<span class="dl-change-old">${esc(change.oldValue)}</span>`
        html += '<span class="dl-change-arrow">→</span>'
        html += `<span class="dl-change-new">${esc(change.newValue)}</span>`
        html += '</div>'
      }
    })
    html += '</div>'
  }

  html += '</div>'
  return html
}

/**
 * HTML 转义，防止 XSS
 */
const escapeHtml = (str) => {
  if (!str) return ''
  const div = document.createElement('div')
  div.textContent = str
  return div.innerHTML
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

const loadData = async () => {
  loading.value = true
  try {
    const params = {
      ...queryForm.value,
      page: pagination.value.page,
      page_size: pagination.value.pageSize
    }
    if (searchKeyword.value) {
      params.search = searchKeyword.value
    }
    const res = await getLogs(params)
    tableData.value = res.data.results || res.data.items || []
    pagination.value.total = res.data.count || 0
  } catch (error) {
    tableData.value = []
    pagination.value.total = 0
    ElMessage.error('加载数据失败：' + (error.message || '未知错误'))
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  pagination.value.page = 1
  loadData()
}

const handleReset = () => {
  queryForm.value = { action: '' }
  searchKeyword.value = ''
  pagination.value.page = 1
  loadData()
}

/**
 * 导出操作日志为 CSV 文件
 */
const handleExport = async () => {
  exportLoading.value = true
  try {
    const params = {}
    if (queryForm.value.action) {
      params.action = queryForm.value.action
    }
    if (searchKeyword.value) {
      params.search = searchKeyword.value
    }
    const res = await exportLogs(params)
    const blob = new Blob([res.data], { type: 'text/csv; charset=utf-8' })
    const link = document.createElement('a')
    link.href = URL.createObjectURL(blob)
    link.download = `操作日志_${new Date().toISOString().slice(0, 10)}.csv`
    link.click()
    URL.revokeObjectURL(link.href)
    ElMessage.success('导出成功')
  } catch (error) {
    const errMsg = error.response?.data
    if (errMsg instanceof Blob) {
      errMsg.text().then(text => {
        try {
          const parsed = JSON.parse(text)
          ElMessage.error('导出失败：' + (parsed.msg || '服务器错误'))
        } catch {
          ElMessage.error('导出失败：服务器错误')
        }
      })
    } else {
      ElMessage.error('导出失败：' + (error.message || '未知错误'))
    }
  } finally {
    exportLoading.value = false
  }
}

/**
 * 清空操作日志 —— 需要管理员密码二次确认
 */
const handleClearLogs = async () => {
  try {
    await ElMessageBox.confirm(
      '此操作将清空所有操作日志，且不可恢复！请谨慎操作。是否继续？',
      '危险操作 - 清空日志',
      {
        confirmButtonText: '继续操作',
        cancelButtonText: '取消',
        type: 'error',
        distinguishCancelAndClose: true,
        closeOnClickModal: false
      }
    )
  } catch (action) {
    if (action === 'cancel' || action === 'close') {
      return
    }
  }

  try {
    const { value: password } = await ElMessageBox.prompt(
      '请输入当前管理员密码以确认清空操作：',
      '管理员身份验证',
      {
        confirmButtonText: '确认清空',
        cancelButtonText: '取消',
        inputType: 'password',
        inputPlaceholder: '请输入管理员密码',
        inputValidator: (val) => {
          if (!val) return '密码不能为空'
          return true
        },
        distinguishCancelAndClose: true,
        closeOnClickModal: false,
        type: 'warning'
      }
    )

    clearLoading.value = true
    try {
      const res = await clearLogs({ password })
      ElMessage.success(res.data?.msg || '操作日志已清空')
      pagination.value.page = 1
      await loadData()
    } catch (error) {
      ElMessage.error(error.response?.data?.msg || '清空失败，请检查密码是否正确')
    } finally {
      clearLoading.value = false
    }
  } catch (action) {
    if (action === 'cancel' || action === 'close') {
      return
    }
  }
}

onMounted(() => {
  loadData()
  calculateTableHeight()
  window.addEventListener('resize', calculateTableHeight)
})

onUnmounted(() => {
  window.removeEventListener('resize', calculateTableHeight)
})
</script>

<style scoped>
.logs-page .data-table {
  --el-table-header-bg-color: var(--color-bg-light);
}

.detail-content {
  line-height: 1.6;
  padding: 2px 0;
}

/* ── 操作概要行 ── */
.detail-content :deep(.dl-row) {
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

.detail-content :deep(.dl-card) {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

/* ── 头部：图标 + 动词 + 标签 ── */
.detail-content :deep(.dl-header) {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  flex-wrap: wrap;
}

.detail-content :deep(.dl-icon) {
  display: inline-flex;
  align-items: center;
  flex-shrink: 0;
}

.detail-content :deep(.dl-verb) {
  font-weight: 700;
  font-size: 14px;
  white-space: nowrap;
}

.detail-content :deep(.dl-tag) {
  display: inline-block;
  padding: 2px 10px;
  border-radius: 4px;
  font-size: 13px;
  font-weight: 600;
  border: 1px solid;
  line-height: 1.5;
  white-space: nowrap;
}

.detail-content :deep(.dl-ctx) {
  color: #909399;
  font-size: 12px;
}

.detail-content :deep(.dl-text) {
  font-size: 14px;
  color: #303133;
}

/* ── 变更列表容器 ── */
.detail-content :deep(.dl-changes) {
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding-left: 8px;
  border-left: 2px solid #ebeef5;
  overflow: visible;
}

/* ── 单条变更项 ── */
.detail-content :deep(.dl-change) {
  display: inline-flex;
  align-items: baseline;
  gap: 5px;
  font-size: 13px;
  flex-wrap: wrap;
  padding: 3px 8px;
  border-radius: 4px;
  background: #fafafa;
}

.detail-content :deep(.dl-change-perm) {
  background: #fdf6ec;
  border-left: 3px solid #e6a23c;
}

.detail-content :deep(.dl-change-icon) {
  display: inline-flex;
  align-items: center;
  flex-shrink: 0;
}

/* ── 变更字段标签 ── */
.detail-content :deep(.dl-change-label) {
  color: #909399;
  font-size: 12px;
  white-space: nowrap;
}

.detail-content :deep(.dl-change-label-perm) {
  color: #e6a23c;
  font-weight: 700;
  font-size: 13px;
}

/* ── 旧值 / 新值对比标签 ── */
.detail-content :deep(.dl-change-old) {
  display: inline;
  padding: 1px 8px;
  border-radius: 3px;
  background: #fef0f0;
  color: #f56c6c;
  font-size: 12px;
  line-height: 1.8;
  text-decoration: line-through;
  word-break: break-all;
}

.detail-content :deep(.dl-change-arrow) {
  color: #c0c4cc;
  font-weight: 700;
  font-size: 12px;
  flex-shrink: 0;
}

.detail-content :deep(.dl-change-new) {
  display: inline;
  padding: 1px 8px;
  border-radius: 3px;
  background: #f0f9eb;
  color: #67c23a;
  font-size: 12px;
  line-height: 1.8;
  font-weight: 600;
  word-break: break-all;
}

.detail-content :deep(svg) {
  vertical-align: middle;
}

/* ── 折叠展开（details / summary）── */
.detail-content :deep(.dl-details) {
  margin: 2px 0;
}

.detail-content :deep(.dl-details-perm) {
  border: 1px solid #f5dab1;
  border-radius: 6px;
  background: #fef9f0;
  overflow: hidden;
}

.detail-content :deep(.dl-details-summary) {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 4px 10px;
  cursor: pointer;
  user-select: none;
  list-style: none;
  font-size: 13px;
  flex-wrap: wrap;
}

.detail-content :deep(.dl-details-summary::-webkit-details-marker) {
  display: none;
}

.detail-content :deep(.dl-details-summary::marker) {
  display: none;
  content: '';
}

.detail-content :deep(.dl-fold-hint) {
  color: #e6a23c;
  font-size: 12px;
  font-weight: 600;
  white-space: nowrap;
  margin-left: 4px;
}

.detail-content :deep(.dl-details[open] .dl-fold-hint) {
  display: none;
}

/* 展开后隐藏 summary 中与 body 重复的元素，只保留可点击的折叠区域 */
.detail-content :deep(.dl-details-perm[open] .dl-details-summary .dl-change-icon),
.detail-content :deep(.dl-details-perm[open] .dl-details-summary .dl-change-label),
.detail-content :deep(.dl-details-perm[open] .dl-details-summary .dl-change-arrow),
.detail-content :deep(.dl-details-perm[open] .dl-details-summary .dl-fold-hint) {
  display: none;
}
.detail-content :deep(.dl-details-perm[open] .dl-details-summary) {
  padding: 2px 10px;
  min-height: 0;
}
.detail-content :deep(.dl-details-perm[open] .dl-details-summary::before) {
  content: '收起 ▲';
  color: #e6a23c;
  font-size: 12px;
  font-weight: 600;
}

.detail-content :deep(.dl-details-body) {
  padding: 0 10px 6px 10px;
}

.detail-content :deep(.dl-change-old-fold),
.detail-content :deep(.dl-change-new-fold) {
  max-width: 200px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  display: inline-block;
}

.detail-content :deep(.dl-details[open] .dl-change-old-fold),
.detail-content :deep(.dl-details[open] .dl-change-new-fold) {
  display: none;
}
</style>

<template>
  <el-container class="layout-container">
    <el-aside :width="isCollapse ? '65px' : '160px'" class="el-aside">
      <div class="logo">
        <svg class="logo-icon" viewBox="0 0 32 32" fill="none">
          <rect width="32" height="32" rx="8" fill="url(#logoGradient)"/>
          <path d="M8 12L16 6L24 12L16 18L8 12Z" fill="white"/>
          <path d="M8 20L16 14L24 20L16 26L8 20Z" fill="white" opacity="0.7"/>
          <defs>
            <linearGradient id="logoGradient" x1="0" y1="0" x2="32" y2="32">
              <stop stop-color="#165DFF"/>
              <stop offset="1" stop-color="#0E42D2"/>
            </linearGradient>
          </defs>
        </svg>
        <span v-if="!isCollapse" class="logo-text">豪威工贸</span>
      </div>
      <el-menu
        :default-active="activeMenu"
        :collapse="isCollapse"
        :collapse-transition="true"
        router
        class="sidebar-menu"
      >
        <el-menu-item index="/dashboard">
          <el-icon><DataLine /></el-icon>
          <template #title>概览</template>
        </el-menu-item>
        <el-sub-menu index="purchase">
          <template #title>
            <el-icon><ShoppingCart /></el-icon>
            <span>采购管理</span>
          </template>
          <el-menu-item index="/purchase/orders">采购订单</el-menu-item>
        </el-sub-menu>
        <el-sub-menu index="sale">
          <template #title>
            <el-icon><Sell /></el-icon>
            <span>销售管理</span>
          </template>
          <el-menu-item index="/sale/orders">销售订单</el-menu-item>
        </el-sub-menu>
        <el-sub-menu index="inventory">
          <template #title>
            <el-icon><Goods /></el-icon>
            <span>库存管理</span>
          </template>
          <el-menu-item index="/inventory/stock">库存查询</el-menu-item>
          <el-menu-item index="/inventory/adjust">库存调整</el-menu-item>
          <el-menu-item index="/inventory/transfer">库存调拨</el-menu-item>
          <el-menu-item index="/inventory/log">库存流水</el-menu-item>
        </el-sub-menu>
        <el-sub-menu index="finance">
          <template #title>
            <el-icon><Wallet /></el-icon>
            <span>财务管理</span>
          </template>
          <el-menu-item index="/finance/payments">收付款管理</el-menu-item>
        </el-sub-menu>
        <el-sub-menu index="reports">
          <template #title>
            <el-icon><Document /></el-icon>
            <span>报表中心</span>
          </template>
          <el-menu-item index="/reports/purchase">采购报表</el-menu-item>
          <el-menu-item index="/reports/sale">销售报表</el-menu-item>
          <el-menu-item index="/reports/inventory">库存报表</el-menu-item>
          <el-menu-item index="/reports/finance">财务报表</el-menu-item>
        </el-sub-menu>
        <el-sub-menu index="basic">
          <template #title>
            <el-icon><Box /></el-icon>
            <span>基础资料</span>
          </template>
          <el-menu-item index="/basic/params">参数设置</el-menu-item>
          <el-menu-item index="/basic/goods">商品管理</el-menu-item>
          <el-menu-item index="/basic/suppliers">供应商管理</el-menu-item>
          <el-menu-item index="/basic/customers">客户管理</el-menu-item>
        </el-sub-menu>
        <el-sub-menu index="system" v-if="isAdmin">
          <template #title>
            <el-icon><Setting /></el-icon>
            <span>系统管理</span>
          </template>
          <el-menu-item index="/system/roles">角色管理</el-menu-item>
          <el-menu-item index="/system/users">用户管理</el-menu-item>
          <el-menu-item index="/system/logs">操作日志</el-menu-item>
        </el-sub-menu>
      </el-menu>
    </el-aside>
    <el-container>
      <el-header class="el-header">
        <div class="header-content">
          <div class="header-left">
            <el-button :icon="isCollapse ? Expand : Fold" @click="toggleCollapse" circle class="collapse-btn" />
            <div class="breadcrumb-wrapper">
              <span class="breadcrumb-title">{{ currentPageTitle }}</span>
            </div>
          </div>
          <div class="header-right">
            <div class="header-actions">
              <el-button :icon="Bell" circle class="action-btn" />
              <el-button :icon="Refresh" circle class="action-btn" />
            </div>
            <div class="user-info">
              <el-dropdown @command="handleCommand">
                <span class="el-dropdown-link">
                  <div class="user-avatar">
                    <svg viewBox="0 0 24 24" fill="none">
                      <circle cx="12" cy="12" r="10" fill="url(#avatarGradient)"/>
                      <path d="M12 12C14.2091 12 16 10.2091 16 8C16 5.79086 14.2091 4 12 4C9.79086 4 8 5.79086 8 8C8 10.2091 9.79086 12 12 12Z" fill="white"/>
                      <path d="M18 18C16.9391 16.7851 15.308 16 13.5 16H10.5C8.69202 16 7.06089 16.7851 6 18" stroke="white" stroke-width="1.5" stroke-linecap="round"/>
                      <defs>
                        <linearGradient id="avatarGradient" x1="4" y1="4" x2="20" y2="20">
                          <stop stop-color="#165DFF"/>
                          <stop offset="1" stop-color="#0E42D2"/>
                        </linearGradient>
                      </defs>
                    </svg>
                  </div>
                  <span class="user-name">{{ userInfo.username || '用户' }}</span>
                  <el-icon class="dropdown-icon"><ArrowDown /></el-icon>
                </span>
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item command="profile">
                      <el-icon><User /></el-icon>
                      个人中心
                    </el-dropdown-item>
                    <el-dropdown-item command="settings">
                      <el-icon><Setting /></el-icon>
                      系统设置
                    </el-dropdown-item>
                    <el-dropdown-item divided command="logout">
                      <el-icon><SwitchButton /></el-icon>
                      退出登录
                    </el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
            </div>
          </div>
        </div>
      </el-header>
      <el-main class="el-main">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { DataLine, Box, ShoppingCart, Sell, Goods, Wallet, Document, Setting, Fold, Expand, Bell, Refresh, ArrowDown, User, SwitchButton } from '@element-plus/icons-vue'
import request from '../api/index'

const router = useRouter()
const route = useRoute()
const isCollapse = ref(false)
const userInfo = ref({})

const pageTitleMap = {
  '/dashboard': '控制台',
  '/basic/params': '参数设置',
  '/basic/goods': '商品管理',
  '/basic/suppliers': '供应商管理',
  '/basic/customers': '客户管理',
  '/purchase/orders': '采购订单',
  '/sale/orders': '销售订单',
  '/inventory/stock': '库存查询',
  '/inventory/adjust': '库存调整',
  '/inventory/transfer': '库存调拨',
  '/inventory/log': '库存流水',
  '/finance/payments': '收付款管理',
  '/reports/purchase': '采购报表',
  '/reports/sale': '销售报表',
  '/reports/inventory': '库存报表',
  '/reports/finance': '财务报表',
  '/system/roles': '角色管理',
  '/system/users': '用户管理',
  '/system/logs': '操作日志'
}

const activeMenu = computed(() => route.path)

const currentPageTitle = computed(() => pageTitleMap[route.path] || '页面')

const isAdmin = computed(() => {
  return userInfo.value.username === 'admin' || 
         userInfo.value.role_name === 'admin' || 
         userInfo.value.role_name === '管理员'
})

const toggleCollapse = () => {
  isCollapse.value = !isCollapse.value
}

const loadUserInfo = async () => {
  try {
    const res = await request.get('/auth/user/')
    userInfo.value = res.data.data || res.data
  } catch (error) {
    console.error('获取用户信息失败')
  }
}

const handleCommand = async (command) => {
  if (command === 'logout') {
    try {
      await ElMessageBox.confirm('确定要退出登录吗？', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      })
      localStorage.removeItem('token')
      localStorage.removeItem('refresh_token')
      ElMessage.success('已退出登录')
      router.push('/login')
    } catch {
    }
  } else if (command === 'profile') {
    ElMessage.info('个人中心功能开发中')
  } else if (command === 'settings') {
    ElMessage.info('系统设置功能开发中')
  }
}

onMounted(() => {
  loadUserInfo()
})
</script>

<style scoped>
.layout-container {
  width: 100%;
  height: 100vh;
  overflow: hidden;
  background-color: var(--color-bg-page);
}

/* 确保Element Plus容器完全铺满 */
.layout-container :deep(.el-container) {
  width: 100%;
  height: 100%;
}

.layout-container :deep(.el-container > .el-aside) {
  height: 100%;
}

.layout-container :deep(.el-container > .el-container) {
  width: 100%;
  height: 100%;
}

.el-aside {
  background-color: var(--color-white);
  color: var(--sidebar-text-primary);
  transition: width var(--transition-normal);
  overflow-x: hidden;
  overflow-y: auto;
  border-right: 1px solid var(--color-border-light);
  box-shadow: var(--shadow-sm);
}

.el-aside::-webkit-scrollbar {
  width: 4px;
}

.el-aside::-webkit-scrollbar-thumb {
  background-color: var(--color-border);
  border-radius: var(--border-radius-sm);
}



.logo {
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 var(--spacing-xs);
  gap: var(--spacing-xs);
  position: relative;
  border-bottom: 1px solid var(--color-border-light);
  overflow: hidden;
}

.logo-icon {
  width: 22px;
  height: 22px;
  flex-shrink: 0;
}

.logo-text {
  font-size: var(--font-size-base);
  font-weight: 600;
  color: var(--color-primary);
  letter-spacing: 0.2px;
  white-space: nowrap;
  overflow: hidden;
}

.sidebar-menu {
  border-right: none;
  background: transparent;
  margin-top: var(--spacing-xs);
}

.sidebar-menu:not(.el-menu--collapse) {
  padding: 0 var(--spacing-xs);
}

.sidebar-menu.el-menu--collapse {
  padding: 0;
}

.sidebar-menu .el-menu-item,
.sidebar-menu .el-sub-menu__title {
  color: var(--sidebar-text-secondary);
  border-radius: var(--border-radius-sm);
  margin: 4px 0;
  height: 36px;
  line-height: 36px;
  transition: all var(--transition-fast);
  position: relative;
  overflow: visible;
}

/* 父菜单项字体加粗 */
.sidebar-menu .el-sub-menu__title span {
  font-weight: 600;
}

.sidebar-menu:not(.el-menu--collapse) .el-menu-item,
.sidebar-menu:not(.el-menu--collapse) .el-sub-menu__title {
  padding: 0 var(--spacing-sm);
}

.sidebar-menu.el-menu--collapse .el-menu-item,
.sidebar-menu.el-menu--collapse .el-sub-menu__title {
  padding: 0;
  justify-content: center;
}

.sidebar-menu .el-menu-item:hover,
.sidebar-menu .el-sub-menu__title:hover {
  background-color: var(--color-primary-light);
  color: var(--sidebar-text-primary);
}

.sidebar-menu .el-menu-item.is-active {
  background-color: var(--color-primary-light);
  color: var(--color-primary);
  font-weight: 600;
}

.sidebar-menu:not(.el-menu--collapse) .el-menu-item.is-active::before {
  content: '';
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 2px;
  height: 16px;
  background-color: var(--color-primary);
  border-radius: 0 var(--border-radius-full) var(--border-radius-full) 0;
}

.sidebar-menu .el-menu-item.is-active .el-icon {
  color: var(--color-primary);
}

.sidebar-menu .el-icon {
  width: 18px;
  height: 18px;
  margin-right: var(--spacing-xs);
}

.sidebar-menu.el-menu--collapse .el-icon {
  margin-right: 0;
}

.sidebar-menu .el-sub-menu .el-menu {
  background: transparent;
  border: none;
}

.sidebar-menu .el-sub-menu .el-menu-item {
  background-color: var(--color-bg-light);
  margin: 2px var(--spacing-xs);
  color: var(--sidebar-text-secondary);
  padding-left: calc(var(--spacing-lg)) !important;
  height: 36px;
  line-height: 36px;
  overflow: visible;
  transition: all var(--transition-fast);
}

.sidebar-menu .el-sub-menu .el-menu-item::before {
  content: '•';
  margin-right: 6px;
  color: var(--color-text-tertiary);
}

.sidebar-menu .el-sub-menu .el-menu-item.is-active {
  background-color: #ADD8E6;
  color: var(--color-primary);
  font-weight: 500;
}

.sidebar-menu .el-sub-menu .el-menu-item.is-active::before {
  color: var(--color-primary);
}

.sidebar-menu.el-menu--collapse .el-sub-menu .el-menu-item {
  padding-left: 0 !important;
}

/* 确保菜单图标颜色正确 */
.sidebar-menu .el-menu-item .el-icon,
.sidebar-menu .el-sub-menu__title .el-icon {
  color: var(--sidebar-text-secondary);
}

.sidebar-menu .el-menu-item:hover .el-icon,
.sidebar-menu .el-sub-menu__title:hover .el-icon {
  color: var(--color-primary);
}

.sidebar-menu .el-menu-item.is-active .el-icon {
  color: var(--color-primary);
}

/* 确保子菜单展开时的文字颜色 */
.sidebar-menu .el-sub-menu.is-opened > .el-sub-menu__title {
  color: var(--sidebar-text-primary);
  background-color: var(--color-primary-light);
}

.sidebar-menu .el-sub-menu.is-opened > .el-sub-menu__title .el-icon {
  color: var(--color-primary);
}

/* 父菜单项选中状态联动（当子菜单项选中时）- 优先级高于展开状态 */
.sidebar-menu .el-sub-menu.is-active > .el-sub-menu__title {
  background-color: #8FBCD4;
  color: var(--color-primary);
}

.sidebar-menu .el-sub-menu.is-active > .el-sub-menu__title .el-icon {
  color: var(--color-primary);
}

/* 同时展开且选中时的样式 */
.sidebar-menu .el-sub-menu.is-active.is-opened > .el-sub-menu__title {
  background-color: #8FBCD4;
}

/* 覆盖Element Plus默认的菜单文字颜色 */
.sidebar-menu :deep(.el-menu-item span),
.sidebar-menu :deep(.el-sub-menu__title span) {
  color: inherit;
  overflow: visible;
  text-overflow: initial;
}

/* 确保菜单项文字完整显示 */
.sidebar-menu :deep(.el-menu-item span) {
  overflow: visible;
  text-overflow: initial;
}

/* 子菜单展开时的背景 */
.sidebar-menu .el-sub-menu .el-menu {
  padding: 4px 0;
}

/* 优化子菜单标题的布局 - 文字与箭头间距 */
.sidebar-menu :deep(.el-sub-menu__title) {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.sidebar-menu :deep(.el-sub-menu__title .el-icon:first-child) {
  flex-shrink: 0;
}

.sidebar-menu :deep(.el-sub-menu__title span) {
  flex: 1;
  margin-right: var(--spacing-xs);
  overflow: visible;
  white-space: nowrap;
}

.sidebar-menu :deep(.el-sub-menu__icon-arrow) {
  flex-shrink: 0;
  margin-left: var(--spacing-xs);
  transition: transform var(--transition-fast);
}

.el-header {
  background-color: var(--color-white);
  border-bottom: 1px solid var(--color-border-light);
  display: flex;
  align-items: center;
  padding: 0 var(--spacing-lg);
  height: 52px;
  box-shadow: var(--shadow-sm);
  position: relative;
  z-index: 99;
}

.header-content {
  width: 100%;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-left {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
}

.collapse-btn {
  background-color: var(--color-bg-light);
  border: none;
  color: var(--color-text-secondary);
  transition: all var(--transition-fast);
}

.collapse-btn:hover {
  background-color: var(--color-primary-light);
  color: var(--color-primary);
}

.breadcrumb-wrapper {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
}

.breadcrumb-title {
  font-size: var(--font-size-lg);
  font-weight: 600;
  color: var(--color-text-primary);
}

.header-right {
  display: flex;
  align-items: center;
  gap: var(--spacing-lg);
}

.header-actions {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
}

.action-btn {
  background-color: var(--color-bg-light);
  border: none;
  color: var(--color-text-secondary);
  transition: all var(--transition-fast);
}

.action-btn:hover {
  background-color: var(--color-primary-light);
  color: var(--color-primary);
  transform: translateY(-1px);
}

.user-info {
  display: flex;
  align-items: center;
}

.el-dropdown-link {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  cursor: pointer;
  padding: var(--spacing-xs) var(--spacing-sm);
  border-radius: var(--border-radius-md);
  transition: all var(--transition-fast);
}

.el-dropdown-link:hover {
  background-color: var(--color-bg-light);
}

.user-avatar {
  width: 36px;
  height: 36px;
  flex-shrink: 0;
}

.user-avatar svg {
  width: 100%;
  height: 100%;
}

.user-name {
  font-size: var(--font-size-sm);
  font-weight: 500;
  color: var(--color-text-primary);
}

.dropdown-icon {
  font-size: 12px;
  color: var(--color-text-tertiary);
  transition: transform var(--transition-fast);
}

.el-dropdown-link:hover .dropdown-icon {
  color: var(--color-primary);
}

.el-main {
  background-color: var(--color-bg-page);
  padding: var(--spacing-lg);
  overflow: auto;
  width: 100%;
  height: calc(100% - 52px);
}

/* 确保主内容区域完全铺满 */
.layout-container :deep(.el-main) {
  width: 100%;
  height: calc(100% - 52px);
}

.el-main::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

.el-main::-webkit-scrollbar-track {
  background-color: var(--color-bg-light);
  border-radius: var(--border-radius-sm);
}

.el-main::-webkit-scrollbar-thumb {
  background-color: var(--color-border);
  border-radius: var(--border-radius-sm);
  transition: background-color var(--transition-fast);
}

.el-main::-webkit-scrollbar-thumb:hover {
  background-color: var(--color-text-tertiary);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .el-aside {
    position: fixed;
    left: 0;
    top: 0;
    height: 100vh;
    z-index: 1000;
    transform: translateX(0);
    transition: transform var(--transition-normal);
  }
  
  .el-aside.el-aside--mobile-hidden {
    transform: translateX(-100%);
  }
  
  .el-container {
    margin-left: 0 !important;
  }
  
  .el-header {
    padding: 0 var(--spacing-md) !important;
  }
  
  .header-left {
    gap: var(--spacing-sm) !important;
  }
  
  .breadcrumb-title {
    font-size: var(--font-size-base) !important;
  }
  
  .header-actions {
    display: none !important;
  }
}

@media (max-width: 480px) {
  .el-aside {
    width: 140px !important;
  }
  
  .logo-text {
    font-size: var(--font-size-sm) !important;
  }
  
  .sidebar-menu .el-menu-item,
  .sidebar-menu .el-sub-menu__title {
    height: 36px !important;
    line-height: 36px !important;
  }
}
</style>

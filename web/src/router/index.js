import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/Login.vue')
  },
  {
    path: '/',
    name: 'Layout',
    component: () => import('../views/Layout.vue'),
    redirect: '/dashboard',
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('../views/Dashboard.vue')
      },
      {
        path: 'basic/goods',
        name: 'Goods',
        component: () => import('../views/basic/Goods.vue')
      },
      {
        path: 'basic/suppliers',
        name: 'Suppliers',
        component: () => import('../views/basic/Suppliers.vue')
      },
      {
        path: 'basic/customers',
        name: 'Customers',
        component: () => import('../views/basic/Customers.vue')
      },
      {
        path: 'basic/params',
        name: 'Params',
        component: () => import('../views/basic/Params.vue')
      },
      {
        path: 'purchase/orders',
        name: 'PurchaseOrders',
        component: () => import('../views/purchase/PurchaseOrders.vue')
      },
      {
        path: 'sale/orders',
        name: 'SaleOrders',
        component: () => import('../views/sale/SaleOrders.vue')
      },
      {
        path: 'inventory/stock',
        name: 'InventoryStock',
        component: () => import('../views/inventory/InventoryStock.vue')
      },
      {
        path: 'inventory/log',
        name: 'InventoryLog',
        component: () => import('../views/inventory/InventoryLog.vue')
      },
      {
        path: 'inventory/adjust',
        name: 'InventoryAdjust',
        component: () => import('../views/inventory/InventoryAdjust.vue')
      },
      {
        path: 'inventory/transfer',
        name: 'InventoryTransfer',
        component: () => import('../views/inventory/InventoryTransfer.vue')
      },
      {
        path: 'finance/payments',
        name: 'FinancePayments',
        component: () => import('../views/finance/Payments.vue')
      },
      {
        path: 'reports/purchase',
        name: 'PurchaseReport',
        component: () => import('../views/reports/PurchaseReport.vue')
      },
      {
        path: 'reports/sale',
        name: 'SaleReport',
        component: () => import('../views/reports/SaleReport.vue')
      },
      {
        path: 'reports/inventory',
        name: 'InventoryReport',
        component: () => import('../views/reports/InventoryReport.vue')
      },
      {
        path: 'reports/finance',
        name: 'FinanceReport',
        component: () => import('../views/reports/FinanceReport.vue')
      },
      {
        path: 'system/roles',
        name: 'SystemRoles',
        component: () => import('../views/system/Roles.vue')
      },
      {
        path: 'system/users',
        name: 'SystemUsers',
        component: () => import('../views/system/Users.vue')
      },
      {
        path: 'system/logs',
        name: 'SystemLogs',
        component: () => import('../views/system/Logs.vue')
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  if (to.path !== '/login' && !token) {
    next('/login')
  } else if (to.path === '/login' && token) {
    next('/')
  } else {
    next()
  }
})

export default router

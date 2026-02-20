<template>
  <div class="dashboard-page">
    <div class="page-header">
      <div class="header-title-section">
        <div class="title-icon">
          <el-icon :size="24"><DataAnalysis /></el-icon>
        </div>
        <div class="title-content">
          <h1 class="page-title">数据概览</h1>
          <p class="page-subtitle">查看系统运营数据和关键指标</p>
        </div>
      </div>
      <div class="header-stats">
        <div class="stat-item">
          <div class="stat-value">¥{{ formatPrice(dashboardData.today_sale) }}</div>
          <div class="stat-label">今日销售</div>
        </div>
      </div>
    </div>

    <div class="page-content">
      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-card-icon sale">
            <el-icon :size="28"><Money /></el-icon>
          </div>
          <div class="stat-card-content">
            <div class="stat-card-value">¥{{ formatPrice(dashboardData.today_sale) }}</div>
            <div class="stat-card-label">今日销售</div>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-card-icon purchase">
            <el-icon :size="28"><ShoppingCart /></el-icon>
          </div>
          <div class="stat-card-content">
            <div class="stat-card-value">{{ dashboardData.purchase_count || 0 }}</div>
            <div class="stat-card-label">采购订单</div>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-card-icon order">
            <el-icon :size="28"><Document /></el-icon>
          </div>
          <div class="stat-card-content">
            <div class="stat-card-value">{{ dashboardData.sale_count || 0 }}</div>
            <div class="stat-card-label">销售订单</div>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-card-icon goods">
            <el-icon :size="28"><Box /></el-icon>
          </div>
          <div class="stat-card-content">
            <div class="stat-card-value">{{ dashboardData.goods_count || 0 }}</div>
            <div class="stat-card-label">商品种类</div>
          </div>
        </div>
      </div>

      <div class="charts-row">
        <div class="chart-card">
          <div class="chart-header">
            <div class="chart-title">最近7天采购/销售趋势</div>
          </div>
          <div class="chart-content">
            <v-chart :option="trendChartOption" class="chart" autoresize />
          </div>
        </div>
        <div class="chart-card">
          <div class="chart-header">
            <div class="chart-title">库存价值分布</div>
          </div>
          <div class="chart-content">
            <v-chart :option="pieChartOption" class="chart" autoresize />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { LineChart, PieChart } from 'echarts/charts'
import {
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent
} from 'echarts/components'
import VChart from 'vue-echarts'
import { DataAnalysis, Money, ShoppingCart, Document, Box } from '@element-plus/icons-vue'
import { getDashboardData } from '../api/reports'

use([
  CanvasRenderer,
  LineChart,
  PieChart,
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent
])

const dashboardData = ref({
  today_purchase: 0,
  today_sale: 0,
  purchase_count: 0,
  sale_count: 0,
  goods_count: 0,
  total_inventory_value: 0,
  chart_7_days: {
    dates: [],
    sales: [],
    purchases: []
  },
  chart_category: {
    categories: [],
    values: []
  }
})

const formatPrice = (price) => {
  if (price === undefined || price === null) return '0.00'
  return Number(price).toFixed(2)
}

const trendChartOption = computed(() => {
  return {
    tooltip: {
      trigger: 'axis'
    },
    legend: {
      data: ['采购', '销售'],
      top: 0
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: dashboardData.value.chart_7_days.dates
    },
    yAxis: {
      type: 'value',
      axisLabel: {
        formatter: '¥{value}'
      }
    },
    series: [
      {
        name: '采购',
        type: 'line',
        smooth: true,
        data: dashboardData.value.chart_7_days.purchases,
        itemStyle: { color: '#165DFF' },
        areaStyle: {
          color: {
            type: 'linear',
            x: 0,
            y: 0,
            x2: 0,
            y2: 1,
            colorStops: [
              { offset: 0, color: 'rgba(22, 93, 255, 0.3)' },
              { offset: 1, color: 'rgba(22, 93, 255, 0.05)' }
            ]
          }
        }
      },
      {
        name: '销售',
        type: 'line',
        smooth: true,
        data: dashboardData.value.chart_7_days.sales,
        itemStyle: { color: '#36D399' },
        areaStyle: {
          color: {
            type: 'linear',
            x: 0,
            y: 0,
            x2: 0,
            y2: 1,
            colorStops: [
              { offset: 0, color: 'rgba(54, 211, 153, 0.3)' },
              { offset: 1, color: 'rgba(54, 211, 153, 0.05)' }
            ]
          }
        }
      }
    ]
  }
})

const pieChartOption = computed(() => {
  const data = dashboardData.value.chart_category.categories.map((cat, idx) => ({
    name: cat,
    value: dashboardData.value.chart_category.values[idx]
  }))
  
  return {
    tooltip: {
      trigger: 'item',
      formatter: '{b}: ¥{c} ({d}%)'
    },
    legend: {
      orient: 'vertical',
      left: 'left'
    },
    series: [
      {
        name: '库存价值',
        type: 'pie',
        radius: '60%',
        center: ['60%', '50%'],
        data: data,
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowOffsetX: 0,
            shadowColor: 'rgba(0, 0, 0, 0.5)'
          }
        }
      }
    ]
  }
})

const loadDashboard = async () => {
  try {
    const res = await getDashboardData()
    dashboardData.value = res.data
  } catch (error) {
    console.error('加载仪表盘数据失败', error)
  }
}

onMounted(() => {
  loadDashboard()
})
</script>

<style scoped>
.dashboard-page {
  height: 100%;
  display: flex;
  flex-direction: column;
  gap: var(--spacing-lg);
  overflow-y: auto;
  padding-bottom: var(--spacing-lg);
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: linear-gradient(135deg, var(--color-primary-light) 0%, rgba(22, 93, 255, 0.05) 100%);
  padding: var(--spacing-md) var(--spacing-lg);
  border-radius: var(--border-radius-lg);
  border: 1px solid var(--color-primary-light);
}

.header-title-section {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
}

.title-icon {
  width: 44px;
  height: 44px;
  background: linear-gradient(135deg, var(--color-primary) 0%, var(--color-primary-dark) 100%);
  border-radius: var(--border-radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-white);
  box-shadow: var(--shadow-primary);
}

.title-content {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.page-title {
  margin: 0;
  font-size: var(--font-size-xl);
  font-weight: 600;
  color: var(--color-text-primary);
  line-height: 1.2;
}

.page-subtitle {
  margin: 0;
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  line-height: 1.3;
}

.header-stats {
  display: flex;
  gap: var(--spacing-md);
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
}

.stat-value {
  font-size: var(--font-size-2xl);
  font-weight: 700;
  color: var(--color-primary);
  line-height: 1;
}

.stat-label {
  font-size: 12px;
  color: var(--color-text-tertiary);
  margin-top: 2px;
}

.page-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: var(--spacing-lg);
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: var(--spacing-lg);
}

.stat-card {
  background-color: var(--color-white);
  border-radius: var(--border-radius-lg);
  border: 1px solid var(--color-border-light);
  box-shadow: var(--shadow-sm);
  padding: var(--spacing-xl);
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
  transition: all var(--transition-base);
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
}

.stat-card-icon {
  width: 56px;
  height: 56px;
  border-radius: var(--border-radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-white);
  flex-shrink: 0;
}

.stat-card-icon.sale {
  background: linear-gradient(135deg, #36D399 0%, #22C55E 100%);
}

.stat-card-icon.purchase {
  background: linear-gradient(135deg, #165DFF 0%, #1E40AF 100%);
}

.stat-card-icon.order {
  background: linear-gradient(135deg, #F59E0B 0%, #D97706 100%);
}

.stat-card-icon.goods {
  background: linear-gradient(135deg, #8B5CF6 0%, #7C3AED 100%);
}

.stat-card-content {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-xs);
}

.stat-card-value {
  font-size: var(--font-size-2xl);
  font-weight: 700;
  color: var(--color-text-primary);
  line-height: 1;
}

.stat-card-label {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
}

.charts-row {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: var(--spacing-lg);
}

.chart-card {
  background-color: var(--color-white);
  border-radius: var(--border-radius-lg);
  border: 1px solid var(--color-border-light);
  box-shadow: var(--shadow-sm);
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.chart-header {
  padding: var(--spacing-lg) var(--spacing-xl);
  border-bottom: 1px solid var(--color-border-light);
}

.chart-title {
  font-size: var(--font-size-base);
  font-weight: 600;
  color: var(--color-text-primary);
}

.chart-content {
  padding: var(--spacing-lg);
  flex: 1;
}

.chart {
  height: 320px;
  width: 100%;
}

@media (max-width: 1200px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .charts-row {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .stats-grid {
    grid-template-columns: 1fr;
  }
}
</style>

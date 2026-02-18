<template>
  <div class="dashboard">
    <el-row :gutter="20">
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-value">¥{{ dashboardData.today_sale?.toFixed(2) || '0.00' }}</div>
            <div class="stat-label">今日销售</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-value">{{ dashboardData.purchase_count || 0 }}</div>
            <div class="stat-label">采购订单</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-value">{{ dashboardData.sale_count || 0 }}</div>
            <div class="stat-label">销售订单</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-value">{{ dashboardData.goods_count || 0 }}</div>
            <div class="stat-label">商品种类</div>
          </div>
        </el-card>
      </el-col>
    </el-row>
    
    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="16">
        <el-card>
          <template #header>
            <span>最近7天采购/销售趋势</span>
          </template>
          <v-chart :option="trendChartOption" class="chart" autoresize />
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card>
          <template #header>
            <span>库存价值分布</span>
          </template>
          <v-chart :option="pieChartOption" class="chart" autoresize />
        </el-card>
      </el-col>
    </el-row>
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
        itemStyle: { color: '#409EFF' },
        areaStyle: {
          color: {
            type: 'linear',
            x: 0,
            y: 0,
            x2: 0,
            y2: 1,
            colorStops: [
              { offset: 0, color: 'rgba(64, 158, 255, 0.3)' },
              { offset: 1, color: 'rgba(64, 158, 255, 0.05)' }
            ]
          }
        }
      },
      {
        name: '销售',
        type: 'line',
        smooth: true,
        data: dashboardData.value.chart_7_days.sales,
        itemStyle: { color: '#67C23A' },
        areaStyle: {
          color: {
            type: 'linear',
            x: 0,
            y: 0,
            x2: 0,
            y2: 1,
            colorStops: [
              { offset: 0, color: 'rgba(103, 194, 58, 0.3)' },
              { offset: 1, color: 'rgba(103, 194, 58, 0.05)' }
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
.dashboard {
  padding: 20px;
}

.stat-card {
  margin-bottom: 20px;
}

.stat-content {
  text-align: center;
}

.stat-value {
  font-size: 32px;
  font-weight: bold;
  color: #409EFF;
  margin-bottom: 10px;
}

.stat-label {
  font-size: 14px;
  color: #666;
}

.chart {
  height: 300px;
  width: 100%;
}
</style>

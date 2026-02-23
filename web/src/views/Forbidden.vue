<template>
  <div class="forbidden-page">
    <div class="forbidden-content">
      <el-icon class="forbidden-icon"><Lock /></el-icon>
      <h1 class="forbidden-title">访问受限</h1>
      <p class="forbidden-desc">您没有权限访问此页面</p>
      <p class="forbidden-detail" v-if="moduleName">当前模块：<strong>{{ moduleName }}</strong></p>
      <p class="forbidden-tip">如需访问，请联系管理员开通相应权限</p>
      <div class="forbidden-actions">
        <el-button type="primary" @click="goBack">返回上一页</el-button>
        <el-button @click="goHome">返回首页</el-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { Lock } from '@element-plus/icons-vue'

const router = useRouter()
const route = useRoute()

const moduleName = computed(() => route.query.module || '')

const goBack = () => {
  router.back()
}

const goHome = () => {
  router.push('/')
}
</script>

<style scoped>
.forbidden-page {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: calc(100vh - 64px);
  background: linear-gradient(135deg, #f5f7fa 0%, #e4e7ed 100%);
}

.forbidden-content {
  text-align: center;
  padding: 60px 80px;
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
}

.forbidden-icon {
  font-size: 80px;
  color: #f56c6c;
  margin-bottom: 24px;
}

.forbidden-title {
  font-size: 28px;
  font-weight: 600;
  color: #303133;
  margin: 0 0 16px 0;
}

.forbidden-desc {
  font-size: 16px;
  color: #606266;
  margin: 0 0 12px 0;
}

.forbidden-detail {
  font-size: 14px;
  color: #909399;
  margin: 0 0 8px 0;
}

.forbidden-detail strong {
  color: #165DFF;
}

.forbidden-tip {
  font-size: 13px;
  color: #909399;
  margin: 0 0 32px 0;
}

.forbidden-actions {
  display: flex;
  justify-content: center;
  gap: 16px;
}
</style>

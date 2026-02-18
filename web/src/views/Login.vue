<template>
  <div class="login-container">
    <div class="login-bg-shape shape-1"></div>
    <div class="login-bg-shape shape-2"></div>
    <div class="login-bg-shape shape-3"></div>
    
    <div class="login-card">
      <div class="login-header">
        <div class="logo-section">
          <div class="logo-icon">
            <svg viewBox="0 0 64 64" fill="none">
              <rect width="64" height="64" rx="16" fill="url(#logoGradient)"/>
              <path d="M16 24L32 12L48 24L32 36L16 24Z" fill="white"/>
              <path d="M16 40L32 28L48 40L32 52L16 40Z" fill="white" opacity="0.7"/>
              <defs>
                <linearGradient id="logoGradient" x1="0" y1="0" x2="64" y2="64">
                  <stop stop-color="#165DFF"/>
                  <stop offset="1" stop-color="#0E42D2"/>
                </linearGradient>
              </defs>
            </svg>
          </div>
          <h1 class="app-title">进销存管理系统</h1>
          <p class="app-subtitle">高效管理 · 智能决策</p>
        </div>
      </div>

      <div class="login-form-section">
        <el-form :model="loginForm" :rules="loginRules" ref="formRef" class="login-form">
          <el-form-item prop="username">
            <div class="input-wrapper">
              <el-icon class="input-icon"><User /></el-icon>
              <el-input 
                v-model="loginForm.username" 
                placeholder="请输入用户名"
                size="large"
                class="login-input"
              />
            </div>
          </el-form-item>
          
          <el-form-item prop="password">
            <div class="input-wrapper">
              <el-icon class="input-icon"><Lock /></el-icon>
              <el-input 
                v-model="loginForm.password" 
                type="password" 
                placeholder="请输入密码"
                size="large"
                class="login-input"
                show-password
                @keyup.enter="handleLogin"
              />
            </div>
          </el-form-item>
          
          <el-form-item>
            <el-button 
              type="primary" 
              @click="handleLogin" 
              :loading="loading"
              size="large"
              class="login-button"
            >
              <span v-if="!loading">登 录</span>
              <span v-else>登录中...</span>
            </el-button>
          </el-form-item>
        </el-form>

        <div class="login-tips">
          <p>默认账号：admin / admin123</p>
        </div>
      </div>

      <div class="login-footer">
        <p>© 2026 进销存管理系统</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { User, Lock } from '@element-plus/icons-vue'
import request from '../api/index'

const router = useRouter()
const formRef = ref(null)
const loading = ref(false)

const loginForm = ref({
  username: '',
  password: ''
})

const loginRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于6位', trigger: 'blur' }
  ]
}

const handleLogin = async () => {
  if (!formRef.value) return
  
  try {
    await formRef.value.validate()
    loading.value = true
    
    const res = await request.post('/auth/login/', loginForm.value)
    localStorage.setItem('token', res.data.access)
    ElMessage.success('登录成功，欢迎回来！')
    
    setTimeout(() => {
      router.push('/')
    }, 500)
  } catch (error) {
    if (error !== false) {
      ElMessage.error('登录失败，请检查用户名和密码')
    }
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  localStorage.removeItem('token')
})
</script>

<style scoped>
.login-container {
  width: 100%;
  height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background: linear-gradient(135deg, var(--color-bg-page) 0%, #f0f9ff 100%);
  position: relative;
  overflow: hidden;
}

.login-bg-shape {
  position: absolute;
  border-radius: 50%;
  opacity: 0.6;
  pointer-events: none;
}

.shape-1 {
  width: 600px;
  height: 600px;
  background: linear-gradient(135deg, var(--color-primary-light) 0%, rgba(22, 93, 255, 0) 100%);
  top: -200px;
  left: -200px;
  animation: float 20s ease-in-out infinite;
}

.shape-2 {
  width: 400px;
  height: 400px;
  background: linear-gradient(135deg, rgba(22, 93, 255, 0.15) 0%, rgba(22, 93, 255, 0) 100%);
  bottom: -100px;
  right: -100px;
  animation: float 25s ease-in-out infinite reverse;
}

.shape-3 {
  width: 300px;
  height: 300px;
  background: linear-gradient(135deg, rgba(22, 93, 255, 0.1) 0%, rgba(22, 93, 255, 0) 100%);
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  animation: pulse 15s ease-in-out infinite;
}

@keyframes float {
  0%, 100% {
    transform: translate(0, 0);
  }
  50% {
    transform: translate(30px, 30px);
  }
}

@keyframes pulse {
  0%, 100% {
    transform: translate(-50%, -50%) scale(1);
  }
  50% {
    transform: translate(-50%, -50%) scale(1.1);
  }
}

.login-card {
  width: 420px;
  background: var(--color-white);
  border-radius: var(--border-radius-xl);
  box-shadow: var(--shadow-xl);
  padding: var(--spacing-2xl);
  position: relative;
  z-index: 10;
  animation: slideUp 0.5s ease-out;
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.login-header {
  text-align: center;
  margin-bottom: var(--spacing-xl);
}

.logo-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--spacing-md);
}

.logo-icon {
  width: 72px;
  height: 72px;
  animation: logoBounce 2s ease-in-out infinite;
}

@keyframes logoBounce {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-8px);
  }
}

.logo-icon svg {
  width: 100%;
  height: 100%;
}

.app-title {
  margin: 0;
  font-size: var(--font-size-2xl);
  font-weight: 700;
  color: var(--color-text-primary);
  background: linear-gradient(135deg, var(--color-primary) 0%, var(--color-primary-dark) 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.app-subtitle {
  margin: 0;
  font-size: var(--font-size-sm);
  color: var(--color-text-tertiary);
  letter-spacing: 2px;
}

.login-form-section {
  margin-bottom: var(--spacing-lg);
}

.login-form {
  margin-top: var(--spacing-lg);
}

/* 确保所有表单项占满宽度 */
.login-form .el-form-item {
  margin-bottom: var(--spacing-lg);
}

.login-form .el-form-item:last-child {
  margin-bottom: 0;
}

/* 确保错误提示文字与输入框对齐 */
.login-form :deep(.el-form-item__error) {
  padding-left: 48px;
  padding-top: 4px;
}

.input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.input-icon {
  position: absolute;
  left: var(--spacing-md);
  color: var(--color-text-tertiary);
  z-index: 1;
  font-size: 20px;
}

.login-input {
  padding-left: 48px;
  width: 100%;
}

/* 确保输入框容器占满宽度 */
.input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
  width: 100%;
}

.input-wrapper :deep(.el-input) {
  width: 100%;
}

.input-wrapper :deep(.el-input__wrapper) {
  width: 100%;
}

.login-button {
  width: 100%;
  height: 48px;
  font-size: var(--font-size-base);
  font-weight: 600;
  background: linear-gradient(135deg, var(--color-primary) 0%, var(--color-primary-dark) 100%);
  border: none;
  box-shadow: var(--shadow-primary);
  transition: all var(--transition-fast);
}

.login-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(22, 93, 255, 0.4);
}

.login-button:active {
  transform: translateY(0);
}

.login-tips {
  text-align: center;
  margin-top: var(--spacing-lg);
  padding-top: var(--spacing-md);
  border-top: 1px solid var(--color-border-light);
}

.login-tips p {
  margin: 0;
  font-size: var(--font-size-sm);
  color: var(--color-text-tertiary);
}

.login-footer {
  text-align: center;
}

.login-footer p {
  margin: 0;
  font-size: var(--font-size-xs);
  color: var(--color-text-tertiary);
}
</style>

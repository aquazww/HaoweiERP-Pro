import { createApp } from 'vue'
import './style.css'
import './styles/variables.css'
import './styles/global.css'
import './styles/page-common.css'
import App from './App.vue'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import zhCn from 'element-plus/dist/locale/zh-cn.mjs'
import router from './router'
import { initTokenCheck } from './api/index'

const app = createApp(App)
app.use(ElementPlus, {
  locale: zhCn
})
app.use(router)
app.mount('#app')

initTokenCheck()

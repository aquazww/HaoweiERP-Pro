# 豪威ERP系统

## 项目简介

基于 Vue 3 + Django REST Framework 的企业资源管理系统，包含采购管理、销售管理、库存管理、财务管理等核心功能模块。

## 技术栈

### 前端
- **框架**: Vue 3 (Composition API)
- **构建工具**: Vite 5
- **UI组件库**: Element Plus
- **状态管理**: Pinia
- **路由**: Vue Router 4
- **HTTP客户端**: Axios
- **图表**: ECharts

### 后端
- **框架**: Django REST Framework
- **数据库**: MySQL 8.0+
- **认证**: JWT (HttpOnly Cookie)

## 项目结构

```
web/
├── src/
│   ├── api/              # API接口模块
│   ├── composables/      # 组合式函数
│   ├── components/       # 公共组件
│   │   └── print/        # 打印相关组件
│   ├── views/            # 页面视图
│   │   ├── basic/        # 基础设置
│   │   ├── purchase/     # 采购管理
│   │   ├── sale/         # 销售管理
│   │   ├── inventory/    # 库存管理
│   │   ├── finance/      # 财务管理
│   │   └── system/       # 系统管理
│   ├── router/           # 路由配置
│   ├── stores/           # Pinia状态管理
│   ├── utils/            # 工具函数
│   └── assets/           # 静态资源
├── public/               # 公共资源
└── vite.config.js        # Vite配置
```

## 功能模块

### 基础设置
- 商品管理：商品信息维护、分类管理
- 计量单位：单位增删改查
- 仓库管理：仓库信息维护
- 往来单位：供应商、客户管理
- 公司信息：公司基本资料设置

### 采购管理
- 采购订单：订单创建、审核、入库
- 采购明细：采购商品明细管理

### 销售管理
- 销售订单：订单创建、审核、出库
- 销售明细：销售商品明细管理

### 库存管理
- 库存查询：实时库存查看
- 入库管理：采购入库、其他入库
- 出库管理：销售出库、其他出库
- 库存调拨：仓库间调拨
- 库存盘点：库存盘点调整

### 财务管理
- 付款管理：采购付款、销售收款

### 系统管理
- 用户管理：用户增删改查、权限分配
- 操作日志：系统操作记录

## 开发指南

### 环境要求
- Node.js 18+
- npm 9+ 或 pnpm 8+

### 安装依赖
```bash
npm install
# 或使用国内镜像
npm install -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 开发运行
```bash
npm run dev
```

### 生产构建
```bash
npm run build
```

### 预览构建结果
```bash
npm run preview
```

## 代码规范

### 命名规范
- 组件文件：PascalCase (如 `GoodsForm.vue`)
- 组合式函数：camelCase + use前缀 (如 `useGoods.js`)
- API文件：小写字母 (如 `basic.js`)

### 注释规范
- 文件级注释：说明文件用途
- 函数级注释：JSDoc格式，包含参数和返回值说明
- 复杂逻辑：行内注释说明

### 组件规范
- 使用 `<script setup>` 语法
- 单文件组件代码量控制在500行以内
- 超过1000行的文件必须模块化拆分

## API接口规范

### RESTful设计
```
GET    /api/v1/goods           # 获取列表
GET    /api/v1/goods/123       # 获取详情
POST   /api/v1/goods           # 创建
PUT    /api/v1/goods/123       # 更新
DELETE /api/v1/goods/123       # 删除
```

### 响应格式
```json
{
  "code": 200,
  "message": "操作成功",
  "data": { },
  "meta": {
    "page": 1,
    "page_size": 20,
    "total": 100
  }
}
```

## 安全规范

- 敏感信息使用环境变量管理
- Token存储使用HttpOnly Cookie
- API请求使用参数化查询防止SQL注入
- 用户输入进行XSS过滤

## 许可证

MIT License

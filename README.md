# ERP 管理系统

基于 Django + Vue3 构建的企业资源计划管理系统。

## 技术栈

### 后端
- **框架**: Django 4.2
- **API**: Django REST Framework 3.14.0
- **认证**: djangorestframework-simplejwt 5.3.0
- **数据库**: MySQL / SQLite
- **跨域**: django-cors-headers

### 前端
- **框架**: Vue 3.5
- **UI**: Element Plus 2.13.2
- **路由**: Vue Router 5.0
- **构建**: Vite 7.3

## 项目结构

```
trae_projects/
├── erp/                    # 后端 Django 应用
│   ├── basic/              # 基础数据模块（商品、供应商、客户等）
│   ├── finance/            # 财务管理模块
│   ├── inventory/          # 库存管理模块
│   ├── purchase/           # 采购管理模块
│   ├── sale/               # 销售管理模块
│   ├── system/             # 系统管理模块（用户、权限）
│   ├── reports/            # 报表模块
│   ├── utils/              # 工具函数
│   └── erp/                # Django 配置
├── web/                    # 前端 Vue 应用
│   └── src/
│       ├── api/            # API 接口
│       ├── components/     # 公共组件
│       ├── composables/    # Vue 组合式函数
│       ├── views/          # 页面视图
│       ├── router/         # 路由配置
│       └── utils/          # 工具函数
├── docker-compose.yml      # Docker 编排配置
└── .gitignore             # Git 忽略配置
```

## 功能模块

| 模块 | 功能 |
|------|------|
| 基础数据 | 商品管理、供应商管理、客户管理、仓库管理、单位管理 |
| 采购管理 | 采购订单、采购入库 |
| 销售管理 | 销售订单、销售出库 |
| 库存管理 | 库存查询、库存调整、库存调拨、库存流水 |
| 财务管理 | 收款管理、付款管理 |
| 报表中心 | 采购报表、销售报表、库存报表、财务报表 |
| 系统管理 | 用户管理、日志管理 |

## 快速开始

### 环境要求
- Python 3.10+
- Node.js 18+
- Docker（可选）

### 本地开发

#### 后端启动

```bash
cd erp
# 创建虚拟环境
python -m venv .venv
source .venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 数据库迁移
python manage.py migrate

# 创建超级用户
python manage.py createsuperuser

# 启动开发服务器
python manage.py runserver 0.0.0.0:8000
```

#### 前端启动

```bash
cd web
# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

### Docker 部署

```bash
# 创建环境变量文件
cp .env.example .env

# 修改 .env 配置（特别是 SECRET_KEY 和 ADMIN_PASSWORD）

# 启动容器
docker-compose up -d
```

## API 接口

### 认证接口

| 方法 | 路径 | 描述 |
|------|------|------|
| POST | `/api/v1/auth/login/` | 用户登录 |
| POST | `/api/v1/auth/logout/` | 用户登出 |
| POST | `/api/v1/auth/refresh/` | 刷新 Token |

### 基础数据接口

| 模块 | 路径 |
|------|------|
| 商品 | `/api/v1/basic/goods/` |
| 供应商 | `/api/v1/basic/suppliers/` |
| 客户 | `/api/v1/basic/customers/` |
| 仓库 | `/api/v1/basic/warehouses/` |
| 单位 | `/api/v1/basic/units/` |

### 采购接口

| 模块 | 路径 |
|------|------|
| 采购订单 | `/api/v1/purchase/orders/` |

### 销售接口

| 模块 | 路径 |
|------|------|
| 销售订单 | `/api/v1/sale/orders/` |

### 库存接口

| 模块 | 路径 |
|------|------|
| 库存查询 | `/api/v1/inventory/stock/` |
| 库存流水 | `/api/v1/inventory/logs/` |
| 库存调整 | `/api/v1/inventory/adjust/` |
| 库存调拨 | `/api/v1/inventory/transfer/` |
| 销售出库 | `/api/v1/inventory/stockout/` |

### 财务接口

| 模块 | 路径 |
|------|------|
| 收款管理 | `/api/v1/finance/payments/` |

### 报表接口

| 模块 | 路径 |
|------|------|
| 采购报表 | `/api/v1/reports/purchase/` |
| 销售报表 | `/api/v1/reports/sale/` |
| 库存报表 | `/api/v1/reports/inventory/` |
| 财务报表 | `/api/v1/reports/finance/` |

## 环境变量

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| DEBUG | 调试模式 | False |
| SECRET_KEY | 密钥 | 必须设置 |
| DB_ENGINE | 数据库引擎 | sqlite3 |
| DB_NAME | 数据库名称 | /app/data/db.sqlite3 |
| ALLOWED_HOSTS | 允许的主机 | localhost,127.0.0.1 |
| CORS_ALLOWED_ORIGINS | 允许的跨域源 | http://localhost |
| ADMIN_PASSWORD | 管理员密码 | 必须设置 |
| WEB_PORT | 前端端口 | 8080 |

## 测试

```bash
cd erp
python manage.py test
```

## 代码规范

- Python: 遵循 PEP 8 规范
- JavaScript/Vue: 遵循 ESLint 规范
- 使用 `black` 格式化 Python 代码
- 使用 `prettier` 格式化前端代码

## 许可证

MIT License
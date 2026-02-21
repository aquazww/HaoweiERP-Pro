# HaoweiERP-Pro 企业资源管理系统

一套完整的企业ERP管理系统，涵盖采购管理、销售管理、库存管理、财务管理等核心业务模块。

## 项目简介

HaoweiERP-Pro 是基于 Django + Vue3 开发的企业资源管理系统，提供完整的进销存管理功能，支持多仓库、多供应商、多客户的业务场景。

### 主要功能

- **基础数据管理**：商品管理、供应商管理、客户管理、仓库管理、参数设置
- **采购管理**：采购订单创建、审核、入库、付款跟踪
- **销售管理**：销售订单创建、审核、出库、收款跟踪
- **库存管理**：库存查询、库存调拨、库存调整、库存流水
- **财务管理**：付款单管理、收款单管理
- **报表中心**：采购报表、销售报表、库存报表、财务报表
- **系统管理**：用户管理、角色管理、操作日志

## 技术栈

### 后端
- Python 3.10+
- Django 4.2
- Django REST Framework 3.14
- MySQL / PyMySQL
- JWT 认证 (djangorestframework-simplejwt)

### 前端
- Vue 3.5
- Vite 7
- Element Plus 2.13
- Vue Router 5
- Axios
- ECharts 6
- XLSX (Excel导出)

## 目录结构

```
haowei-erp/
├── erp/                          # 后端项目
│   ├── erp/                      # Django配置
│   │   ├── settings.py           # 项目配置
│   │   ├── urls.py               # 路由配置
│   │   └── wsgi.py               # WSGI配置
│   ├── basic/                    # 基础数据模块
│   │   ├── models.py             # 数据模型
│   │   ├── serializers.py        # 序列化器
│   │   ├── views.py              # 视图
│   │   └── urls.py               # 路由
│   ├── purchase/                 # 采购管理模块
│   ├── sale/                     # 销售管理模块
│   ├── inventory/                # 库存管理模块
│   ├── finance/                  # 财务管理模块
│   ├── reports/                  # 报表中心模块
│   ├── system/                   # 系统管理模块
│   ├── utils/                    # 公共工具
│   ├── manage.py                 # Django入口
│   └── requirements.txt          # Python依赖
├── web/                          # 前端项目
│   ├── src/
│   │   ├── api/                  # API接口
│   │   ├── router/               # 路由配置
│   │   ├── styles/               # 全局样式
│   │   ├── utils/                # 工具函数
│   │   ├── views/                # 页面组件
│   │   ├── App.vue               # 根组件
│   │   └── main.js               # 入口文件
│   ├── index.html                # HTML模板
│   ├── vite.config.js            # Vite配置
│   └── package.json              # 前端依赖
├── deploy/                       # 部署配置
│   ├── docker-compose.yml        # Docker编排
│   ├── backend/                  # 后端Docker配置
│   └── nginx/                    # Nginx配置
└── README.md                     # 项目说明
```

## 环境要求

### 后端环境
- Python 3.10 或更高版本
- MySQL 5.7 或更高版本
- pip 包管理器

### 前端环境
- Node.js 18.0 或更高版本
- npm 9.0 或更高版本

## 安装部署

### 1. 克隆项目

```bash
git clone https://github.com/aquazww/HaoweiERP-Pro.git
cd HaoweiERP-Pro
```

### 2. 后端配置

```bash
# 进入后端目录
cd erp

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt

# 配置数据库 (修改 erp/settings.py)
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.mysql',
#         'NAME': 'erp_db',
#         'USER': 'root',
#         'PASSWORD': 'your_password',
#         'HOST': 'localhost',
#         'PORT': '3306',
#     }
# }

# 创建数据库
mysql -u root -p -e "CREATE DATABASE erp_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"

# 执行数据库迁移
python manage.py makemigrations
python manage.py migrate

# 初始化系统数据
python manage.py init_system

# 创建超级管理员
python manage.py createsuperuser

# 启动开发服务器
python manage.py runserver 0.0.0.0:8000
```

### 3. 前端配置

```bash
# 进入前端目录
cd web

# 安装依赖
npm install

# 启动开发服务器
npm run dev

# 构建生产版本
npm run build
```

### 4. 访问系统

- 前端地址：http://localhost:5173
- 后端API：http://localhost:8000/api/v1/
- 管理后台：http://localhost:8000/admin/

默认管理员账号：admin / admin123

## API 接口

系统提供 RESTful API 接口，主要接口如下：

| 模块 | 接口路径 | 说明 |
|------|----------|------|
| 认证 | /api/v1/auth/ | 登录、刷新Token |
| 基础数据 | /api/v1/basic/ | 商品、供应商、客户、仓库 |
| 采购管理 | /api/v1/purchase/ | 采购单、采购明细 |
| 销售管理 | /api/v1/sale/ | 销售单、销售明细 |
| 库存管理 | /api/v1/inventory/ | 库存、调拨、调整 |
| 财务管理 | /api/v1/finance/ | 付款单、收款单 |
| 系统管理 | /api/v1/system/ | 用户、角色、日志 |

## 数据库设计

### 核心数据表

- **商品表 (goods)**：商品基本信息、规格、单位、价格
- **供应商表 (supplier)**：供应商信息、联系方式
- **客户表 (customer)**：客户信息、联系方式
- **仓库表 (warehouse)**：仓库信息、地址
- **采购单表 (purchase_order)**：采购订单主表
- **销售单表 (sale_order)**：销售订单主表
- **库存表 (inventory)**：商品库存信息
- **库存流水表 (inventory_log)**：库存变动记录

## 常见问题

### 1. 数据库连接失败

检查 MySQL 服务是否启动，确认 `settings.py` 中的数据库配置正确。

```bash
# 检查MySQL状态
mysql -u root -p -e "SELECT 1;"
```

### 2. 前端跨域问题

后端已配置 `django-cors-headers`，如需修改请编辑 `settings.py`：

```python
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]
```

### 3. Token 认证失败

检查请求头是否包含 Authorization：

```
Authorization: Bearer <your_access_token>
```

Token 有效期默认为 1 小时，可在 `settings.py` 中修改。

### 4. 静态文件加载失败

生产环境需配置静态文件：

```bash
python manage.py collectstatic
```

## 开发指南

### 添加新模块

1. 在 `erp/` 目录下创建新应用
2. 在 `settings.py` 的 `INSTALLED_APPS` 中注册
3. 创建 models、serializers、views、urls
4. 在主 `urls.py` 中引入路由

### 前端开发规范

- 组件使用 `<script setup>` 语法
- 样式使用 `<style scoped>` 作用域
- API 调用统一放在 `src/api/` 目录
- 遵循 Element Plus 组件库设计规范

## 版本历史

- **v1.0.0** - 初始版本，完成基础功能模块
- **v1.1.0** - 添加库存调拨、库存调整功能
- **v1.2.0** - 优化UI界面，统一详情页风格

## 许可证

MIT License

## 联系方式

如有问题或建议，请提交 Issue 或 Pull Request。

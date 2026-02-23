# ERP 进销存管理系统

一个基于 Django + Vue 3 的全栈进销存管理系统，适用于个人及小微企业的采购、销售、库存和财务管理。

## 项目简介

本系统是一个完整的ERP进销存解决方案，涵盖采购管理、销售管理、库存管理、财务管理及报表分析等核心功能模块。系统采用前后端分离架构，后端使用 Django REST Framework 提供 API 接口，前端使用 Vue 3 + Element Plus 构建现代化用户界面。

### 主要特性

- **采购管理**：采购订单创建、入库确认、供应商管理
- **销售管理**：销售订单创建、出库确认、客户管理
- **库存管理**：实时库存查询、库存流水、库存调拨、库存盘点
- **财务管理**：收付款管理、应收应付统计
- **报表中心**：采购报表、销售报表、库存报表、财务报表
- **系统管理**：用户管理、权限控制、操作日志

## 技术栈

### 后端技术

| 技术 | 版本 | 说明 |
|------|------|------|
| Python | 3.10+ | 开发语言 |
| Django | 4.2 LTS | Web框架 |
| Django REST Framework | 3.14+ | RESTful API框架 |
| MySQL | 8.0+ | 关系型数据库 |
| djangorestframework-simplejwt | 5.3+ | JWT认证 |
| django-filter | 23.5+ | 数据过滤 |
| django-cors-headers | 4.0+ | 跨域处理 |

### 前端技术

| 技术 | 版本 | 说明 |
|------|------|------|
| Vue | 3.x | 前端框架 |
| Vite | 4.x | 构建工具 |
| Element Plus | 2.x | UI组件库 |
| Vue Router | 4.x | 路由管理 |
| Axios | 1.x | HTTP客户端 |
| xlsx | 0.18+ | Excel导出 |

## 项目结构

```
trae_projects/
├── erp/                          # 后端项目
│   ├── erp/                      # 项目配置
│   │   ├── settings.py           # Django配置
│   │   ├── urls.py               # 主路由
│   │   └── wsgi.py               # WSGI配置
│   ├── system/                   # 系统模块
│   │   ├── models.py             # 用户、角色、日志模型
│   │   ├── views.py              # 认证、权限视图
│   │   ├── serializers.py        # 序列化器
│   │   └── urls.py               # 路由配置
│   ├── basic/                    # 基础资料模块
│   │   ├── models.py             # 商品、分类、供应商、客户、仓库、单位
│   │   ├── views.py              # CRUD视图
│   │   └── ...
│   ├── purchase/                 # 采购模块
│   │   ├── models.py             # 采购单、采购明细
│   │   └── ...
│   ├── sale/                     # 销售模块
│   │   ├── models.py             # 销售单、销售明细
│   │   └── ...
│   ├── inventory/                # 库存模块
│   │   ├── models.py             # 库存、库存流水、入库单、出库单
│   │   └── ...
│   ├── finance/                  # 财务模块
│   │   ├── models.py             # 收付款记录
│   │   └── ...
│   ├── reports/                  # 报表模块
│   │   └── views.py              # 各类报表视图
│   ├── utils/                    # 工具模块
│   │   ├── views.py              # 基础视图集
│   │   ├── permissions.py        # 权限类
│   │   └── ...
│   ├── manage.py                 # Django管理脚本
│   └── requirements.txt          # Python依赖
├── web/                          # 前端项目
│   ├── src/
│   │   ├── api/                  # API接口
│   │   ├── views/                # 页面组件
│   │   │   ├── basic/            # 基础资料页面
│   │   │   ├── purchase/         # 采购页面
│   │   │   ├── sale/             # 销售页面
│   │   │   ├── inventory/        # 库存页面
│   │   │   ├── finance/          # 财务页面
│   │   │   ├── reports/          # 报表页面
│   │   │   └── system/           # 系统管理页面
│   │   ├── router/               # 路由配置
│   │   ├── utils/                # 工具函数
│   │   └── styles/               # 样式文件
│   ├── package.json              # 前端依赖
│   └── vite.config.js            # Vite配置
├── deploy/                       # 部署配置
│   ├── docker-compose.yml        # Docker编排
│   ├── backend/                  # 后端Docker配置
│   └── web/                      # 前端Docker配置
└── README.md                     # 项目说明
```

## 快速开始

### 环境要求

- Python 3.10+
- Node.js 16+
- MySQL 8.0+

### 后端安装

```bash
# 进入后端目录
cd erp

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt

# 配置数据库（修改 erp/settings.py）
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.mysql',
#         'HOST': 'localhost',
#         'PORT': '3306',
#         'NAME': 'erp',
#         'USER': 'root',
#         'PASSWORD': 'your_password',
#     }
# }

# 数据库迁移
python manage.py migrate

# 创建管理员
python manage.py createsuperuser

# 初始化数据
python manage.py init_data

# 启动服务
python manage.py runserver
```

### 前端安装

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

### 访问系统

- 前端地址：http://localhost:5173
- 后端API：http://localhost:8000/api/v1/
- 管理后台：http://localhost:8000/admin/

默认管理员账号：`admin` / `admin123`

## 功能模块

### 1. 基础资料

- **商品管理**：商品CRUD、分类管理、规格设置、价格管理
- **商品分类**：多级分类、树形展示、拖拽排序
- **计量单位**：单位管理、单位换算
- **供应商管理**：供应商信息、应付余额
- **客户管理**：客户信息、应收余额
- **仓库管理**：仓库设置

### 2. 采购管理

- 创建采购订单
- 采购订单列表与详情
- 采购入库确认
- 库存自动增加
- 应付账款生成

### 3. 销售管理

- 创建销售订单
- 库存校验
- 销售出库确认
- 库存自动扣减
- 应收账款生成

### 4. 库存管理

- 实时库存查询
- 库存流水记录
- 库存调拨
- 库存盘点
- 库存预警

### 5. 财务管理

- 收款管理
- 付款管理
- 应收应付统计
- 收支记录

### 6. 报表中心

- 采购报表
- 销售报表
- 库存报表
- 财务报表
- 数据导出

### 7. 系统管理

- 用户管理
- 权限控制
- 操作日志

## API 接口

### 认证接口

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /api/v1/auth/login/ | 用户登录 |
| POST | /api/v1/auth/logout/ | 用户登出 |
| GET | /api/v1/auth/user/ | 获取当前用户 |
| POST | /api/v1/auth/refresh/ | 刷新Token |

### 业务接口

| 模块 | 路径 | 说明 |
|------|------|------|
| 商品 | /api/v1/basic/goods/ | 商品CRUD |
| 分类 | /api/v1/basic/categories/ | 分类CRUD |
| 供应商 | /api/v1/basic/suppliers/ | 供应商CRUD |
| 客户 | /api/v1/basic/customers/ | 客户CRUD |
| 采购单 | /api/v1/purchase/orders/ | 采购单CRUD |
| 销售单 | /api/v1/sale/orders/ | 销售单CRUD |
| 库存 | /api/v1/inventory/stock/ | 库存查询 |
| 收付款 | /api/v1/finance/payments/ | 收付款CRUD |

## 部署说明

### Docker 部署

```bash
# 进入部署目录
cd deploy

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件，配置数据库连接等

# 构建并启动
docker-compose up -d --build

# 数据库迁移
docker-compose exec backend python manage.py migrate

# 创建管理员
docker-compose exec backend python manage.py createsuperuser
```

### 生产环境配置

1. 修改 `erp/settings.py`：
   - `DEBUG = False`
   - `ALLOWED_HOSTS = ['your-domain.com']`
   - 配置静态文件收集

2. 配置 Nginx 反向代理

3. 使用 Gunicorn 运行：
   ```bash
   gunicorn --bind 0.0.0.0:8000 erp.wsgi:application
   ```

## 数据备份

```bash
# 备份数据库
mysqldump -u root -p erp > backup_$(date +%Y%m%d).sql

# 恢复数据库
mysql -u root -p erp < backup_20260224.sql
```

## 开发指南

### 代码规范

- Python：遵循 PEP 8 规范
- JavaScript：使用 ESLint 检查
- 提交信息：使用语义化提交

### 分支管理

- `main`：主分支，稳定版本
- `develop`：开发分支
- `feature/*`：功能分支
- `bugfix/*`：修复分支

## 常见问题

### Q: 登录后Token过期怎么办？

A: 系统默认Token有效期为2小时，Token过期后会自动刷新。如果刷新失败，请重新登录。

### Q: 如何添加新用户？

A: 使用管理员账号登录，进入「系统管理」→「用户管理」，点击「新增用户」。

### Q: 如何备份数据？

A: 使用MySQL的mysqldump命令进行备份，或配置定时任务自动备份。

## 贡献指南

1. Fork 本仓库
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

## 许可证

本项目采用 MIT 许可证。详见 [LICENSE](LICENSE) 文件。

## 联系方式

如有问题或建议，请提交 Issue 或 Pull Request。

---

**注意**：本项目仅供学习和参考使用，生产环境使用请进行充分测试和安全评估。

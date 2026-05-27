# ERP 进销存系统 - NAS 部署指南

## 部署架构
```
┌─────────────────────────────────────┐
│           Nginx (端口 8080)           │
│  ┌──────────┐    ┌────────────────┐  │
│  │  前端静态  │───▶│ Django :8000   │  │
│  │  文件     │    │ Gunicorn       │  │
│  └──────────┘    └──────┬─────────┘  │
│                         │             │
│                  ┌──────▼──────┐      │
│                  │   SQLite    │      │
│                  │ (持久化卷)   │      │
│                  └─────────────┘      │
└─────────────────────────────────────┘
```

## 一、文件结构
```
erp_project/
├── docker-compose.yml      # Docker Compose 编排
├── .env                     # 环境变量（可修改端口等）
├── erp/                     # 后端 Django 代码
│   ├── Dockerfile
│   ├── entrypoint.sh       # 启动脚本（自动迁移+创建管理员）
│   └── requirements.txt
└── web/                     # 前端 Vue 代码
    ├── Dockerfile
    └── nginx.conf
```

## 二、快速部署（Docker Compose）

### 1. 确保你的 NAS 支持 Docker
   - FNOS NAS 通常已内置 Docker/Podman
   - 打开 NAS 管理后台 → Docker 或容器管理

### 2. 上传项目到 NAS
   将整个项目目录上传到 NAS 的某个文件夹，如 `/share/docker/erp/`

### 3. 修改配置（可选）
   编辑 `.env` 文件：
   - `WEB_PORT=8080` → 改为你想要的端口
   - `SECRET_KEY` → 改为随机字符串

### 4. 启动
```bash
cd /share/docker/erp
docker compose up -d
```

### 5. 访问
   浏览器打开 `http://你的NAS_IP:8080`

### 6. 登录
   - 用户名: `admin`
   - 密码: `admin123`
   - **首次登录后请立即修改密码！**

## 三、默认账号
| 用户名 | 密码 | 角色 |
|--------|------|------|
| admin | admin123 | 系统管理员 |

## 四、数据持久化
所有数据保存在 Docker volumes 中：
- `erp-data`: SQLite 数据库文件
- `erp-media`: 上传的图片/文件
- `erp-logs`: 运行日志

## 五、使用 MySQL（可选）
若要使用 MySQL 替代 SQLite：
1. 编辑 `.env`，修改数据库配置
2. 取消 MySQL 相关行的注释
3. 重启容器：`docker compose down && docker compose up -d`

## 六、常用命令
```bash
# 启动
docker compose up -d

# 停止
docker compose down

# 查看日志
docker compose logs -f backend

# 重启
docker compose restart

# 进入后端容器
docker compose exec backend bash

# 备份数据库（SQLite）
docker compose cp erp-backend:/app/data/db.sqlite3 ./backup_$(date +%Y%m%d).sqlite3
```

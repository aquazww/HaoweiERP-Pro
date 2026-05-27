# 豪威ERP进销存 - Docker 部署指南

## 一、项目结构
```
erp/
├── docker-compose.yml      # 一键编排（后端+前端）
├── .env                     # 环境变量
├── DEPLOY.md                # 本文档
├── erp/                     # Django 后端
│   ├── Dockerfile
│   ├── entrypoint.sh       # 启动脚本（自动迁移+创管理员）
│   └── requirements.txt
└── web/                     # Vue 前端
    ├── Dockerfile
    └── nginx.conf           # 反向代理配置
```

## 二、快速部署

### 1. 上传项目到服务器
```bash
scp -r erp/ web/ docker-compose.yml .env .dockerignore user@server:/opt/erp/
```

### 2. 启动
```bash
cd /opt/erp
docker compose up -d --build
```
首次构建约 3-5 分钟（下载依赖），之后秒启动。

### 3. 访问
`http://服务器IP:8080`

| 账号 | 密码 | 角色 |
|------|------|------|
| admin | admin123 | 管理员 |

## 三、NAS 部署

### 飞牛 fnOS
```bash
# SSH 到 NAS，项目放到 /vol1/docker/erp/
cd /vol1/docker/erp
docker compose up -d --build
```
访问 `http://NAS_IP:8080`

### 群晖 DSM / 威联通 / 绿联 等
同样方式：上传项目 → `docker compose up -d --build`

## 四、常用命令

```bash
docker compose up -d           # 启动
docker compose down            # 停止
docker compose restart         # 重启
docker compose logs -f backend # 查看后端日志
docker compose logs -f frontend # 查看前端日志

# 备份数据库
docker compose cp backend:/app/data/db.sqlite3 ./backup_$(date +%Y%m%d).sqlite3

# 恢复数据库
docker compose cp backup.sqlite3 backend:/app/data/db.sqlite3
docker compose restart backend
```

## 五、配置修改

编辑 `.env` 文件：
```env
WEB_PORT=8080        # 访问端口
DEBUG=False          # 生产环境关闭
SECRET_KEY=xxx       # 修改为随机字符串
```

修改后重启：`docker compose down && docker compose up -d`

## 六、使用 MySQL（可选）

默认使用 SQLite 开箱即用。如需 MySQL：

1. 确保 MySQL 已运行
2. 修改 `.env`：
```env
DB_ENGINE=django.db.backends.mysql
DB_HOST=192.168.1.100
DB_PORT=3306
DB_NAME=erp
DB_USER=erp
DB_PASSWORD=your_password
```
3. 重启：`docker compose down -v && docker compose up -d --build`

> `-v` 会删除旧的 SQLite 数据卷，请先备份。


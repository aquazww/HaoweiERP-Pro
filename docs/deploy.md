# ERP 进销存 — 生产环境部署配置

## 一、nginx 反向代理与客户端 IP 溯源

### 1.1 为什么需要特殊配置

生产环境中 nginx 作为反向代理，Django 后端接收到的请求来源是 nginx 的 IP（通常是 `127.0.0.1` 或容器内网 IP），无法直接拿到真实客户端 IP。

本项目已通过 **两层协作** 解决此问题：

| 层 | 文件 | 职责 |
|---|------|------|
| nginx | [web/nginx.conf](../web/nginx.conf#L18-L44) | 通过 `proxy_set_header` 将真实 IP 写入 HTTP 头 |
| Django | [erp/utils/views.py](../erp/utils/views.py#L29-L40) | `get_client_ip()` 按优先级读取 Header 获取真实 IP |

### 1.2 nginx 端配置（项目已内置）

项目根目录下的 `web/nginx.conf` 已在每个反向代理 location 中配置了必需的 Header：

```nginx
location /api/ {
    proxy_pass http://backend:8000;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;              # ← 真实客户端 IP（单跳）
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;  # ← 代理链（多跳）
    proxy_set_header X-Forwarded-Proto $scheme;
    # ...
}
```

**关键参数说明**：

| 参数 | 变量 | 含义 |
|------|------|------|
| `X-Real-IP` | `$remote_addr` | nginx 直连的对端 IP（单级代理时即为客户端 IP） |
| `X-Forwarded-For` | `$proxy_add_x_forwarded_for` | 追加式代理链：`客户端IP, 代理1, 代理2, ...` |

### 1.3 Django 端 IP 获取逻辑

```python
# erp/utils/views.py - BaseModelViewSet.get_client_ip()
def get_client_ip(self, request):
    """获取客户端真实 IP 地址 —— 支持反向代理溯源"""
    # 优先级 1: X-Forwarded-For 链中的第一个 IP（真正的客户端）
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
        if ip:
            return ip
    # 优先级 2: X-Real-IP（nginx 单跳直传）
    x_real_ip = request.META.get('HTTP_X_REAL_IP')
    if x_real_ip:
        return x_real_ip.strip()
    # 优先级 3: REMOTE_ADDR（直连兜底）
    return request.META.get('REMOTE_ADDR', '0.0.0.0')
```

**优先级顺序**：

```
X-Forwarded-For（第一个） > X-Real-IP > REMOTE_ADDR
```

---

## 二、Django 端补充配置

### 2.1 信任代理 IP（强烈建议）

当 Django 运行在反向代理之后时，需要告诉 Django 信任代理服务器发来的 `X-Forwarded-*` 头，否则某些功能（如 `request.is_secure()`）无法正确工作。

在 `erp/erp/settings.py` 的**生产环境配置**中添加：

```python
# 信任反向代理（nginx / 负载均衡）
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
USE_X_FORWARDED_HOST = True
USE_X_FORWARDED_PORT = True
```

---

## 三、Docker Compose 部署（项目已内置）

### 3.1 docker-compose.yml 关键配置

```yaml
services:
  nginx:
    image: nginx:stable-alpine
    volumes:
      - ./web/nginx.conf:/etc/nginx/conf.d/default.conf:ro  # 挂载 nginx 配置
    ports:
      - "80:80"
    depends_on:
      - backend

  backend:
    build: ./erp
    expose:
      - "8000"
    # Django 不直接暴露端口，只通过 nginx 访问
```

### 3.2 启动与重载

```bash
# 首次启动
docker compose up -d

# 修改 nginx 配置后重载（不中断服务）
docker compose exec nginx nginx -s reload

# 验证配置语法
docker compose exec nginx nginx -t
```

---

## 四、验证 IP 溯源是否生效

### 4.1 方法一：直接查看操作日志

登录系统 → 执行任意操作 → 进入「操作日志」页面，查看 **IP 地址** 列：

- **正确结果**：显示你的公网/局域网真实 IP（如 `192.168.1.100`）
- **错误结果**：显示 `172.x.x.x`（Docker 内网 IP）或 `127.0.0.1`

### 4.2 方法二：检查 HTTP 头

在容器内验证 nginx 是否正确传递了 Header：

```bash
# 进入后端容器
docker compose exec backend python manage.py shell

# 模拟检查
import os
# 实际可通过日志或 debug 端点验证 Header 内容
```

### 4.3 方法三：临时 debug 端点

在开发阶段可临时添加一个 debug 视图查看所有 Header：

```python
# 临时使用，生产环境务必删除
from django.http import JsonResponse
def debug_headers(request):
    headers = {k: v for k, v in request.META.items() if k.startswith('HTTP_')}
    return JsonResponse({
        'remote_addr': request.META.get('REMOTE_ADDR'),
        'x_forwarded_for': request.META.get('HTTP_X_FORWARDED_FOR'),
        'x_real_ip': request.META.get('HTTP_X_REAL_IP'),
        'ip': BaseModelViewSet().get_client_ip(request),
    })
```

---

## 五、常见问题

### Q1：操作日志 IP 显示 `172.x.x.x` 或 `127.0.0.1`

**原因**：nginx 未正确配置 `proxy_set_header`，或请求绕过了 nginx。

**排查**：
1. 确认请求经过了 nginx（不是直接访问 Django 端口）
2. 检查 `nginx.conf` 中 `proxy_set_header X-Forwarded-For` 是否在正确的 location 中
3. `docker compose exec nginx nginx -t` 验证配置无语法错误
4. `docker compose restart nginx` 重启 nginx

### Q2：多层代理（CDN + nginx）下 IP 不正确

nginx 的 `$proxy_add_x_forwarded_for` 会正确追加上游 IP，Django 端取第一个即为真实客户端。

如果 CDN 在最前面（如 Cloudflare、阿里云 CDN），客户端 IP 在 `X-Forwarded-For` 链的最左端。但如果 CDN 提供了自定义 Header（如 `CF-Connecting-IP`），需要在 [get_client_ip()](../erp/utils/views.py#L29) 中增加对应的读取逻辑。

### Q3：HTTPS 下 `request.is_secure()` 返回 False

确保 `settings.py` 中已配置：

```python
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
```

且 nginx 传递了 `proxy_set_header X-Forwarded-Proto $scheme;`。

---

## 六、文件清单

| 文件 | 作用 |
|------|------|
| [web/nginx.conf](../web/nginx.conf) | nginx 站点配置（含 IP Header） |
| [erp/utils/views.py](../erp/utils/views.py#L29-L40) | Django 端 `get_client_ip()` 方法 |
| [erp/system/views.py](../erp/system/views.py#L319-L400) | 日志记录 ViewSet（调用 get_client_ip） |
| [web/src/views/system/Logs.vue](../web/src/views/system/Logs.vue) | 操作日志前端页面（显示 IP） |
| [docker-compose.yml](../docker-compose.yml) | 容器编排（挂载 nginx 配置） |

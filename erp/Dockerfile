FROM python:3.10-slim

WORKDIR /app

# 使用清华镜像源加速
RUN pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple

# 安装系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 创建非 root 用户
RUN addgroup --system --gid 1000 erp && \
    adduser --system --uid 1000 --gid 1000 erp

# 复制并安装 Python 依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目代码
COPY . .

# 创建数据和日志目录并设置权限
RUN mkdir -p /app/data /app/media /app/logs /app/static && \
    chown -R erp:erp /app

# 入口脚本
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 8000

# 切换到非 root 用户运行
USER erp

ENTRYPOINT ["/entrypoint.sh"]

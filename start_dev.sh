#!/bin/bash
# 开发环境启动脚本
# 用法: bash start_dev.sh

export SECRET_KEY="${SECRET_KEY:-erp-dev-secret-key-2024}"
export DEBUG=True
export ALLOWED_HOSTS="localhost,127.0.0.1,10.0.0.18,[::1]"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  ERP 系统 - 开发环境启动"
echo "  DEBUG: $DEBUG"
echo "  PORT:  8000 (后端) / 5173 (前端)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# 检查并终止已运行的旧进程（IPv4 + IPv6）
echo "[检查] 清理端口 8000 和 5173 上的旧进程..."
KILLED=0
for PORT in 8000 5173; do
  PIDS=$(lsof -ti:$PORT 2>/dev/null)
  if [ -n "$PIDS" ]; then
    echo "  → 发现端口 $PORT 占用 (PID: $PIDS)，正在终止..."
    kill -9 $PIDS 2>/dev/null
    KILLED=1
  fi
  # 同时清理 IPv6 端口占用
  PIDS6=$(lsof -ti TCP@\\[::\\]:$PORT 2>/dev/null)
  if [ -n "$PIDS6" ]; then
    echo "  → 发现端口 [::]:$PORT 占用 (PID: $PIDS6)，正在终止..."
    kill -9 $PIDS6 2>/dev/null
    KILLED=1
  fi
done
if [ "$KILLED" -eq 1 ]; then
  echo "  ✅ 旧进程已清理"
  sleep 1
else
  echo "  ✅ 端口空闲，无需清理"
fi
echo ""

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"

start_backend() {
  echo "[后端] 启动 Django 开发服务器..."
  cd "$PROJECT_DIR/erp"
  nohup python3 manage.py runserver '[::]:8000' > /dev/null 2>&1 &
}

start_frontend() {
  echo "[前端] 启动 Vite 开发服务器..."
  cd "$PROJECT_DIR/web"
  nohup npx vite --host :: > /dev/null 2>&1 &
}

start_backend
sleep 2

start_frontend

echo ""
echo "✅ 服务已启动:"
echo "   前端: http://localhost:5173/"
echo "   后端: http://localhost:8000/"
echo ""

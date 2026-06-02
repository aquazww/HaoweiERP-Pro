#!/bin/bash
set -e

PROJECT_ROOT="$(cd "$(dirname "$0")" && pwd)"
BACKEND_DIR="$PROJECT_ROOT/erp"
FRONTEND_DIR="$PROJECT_ROOT/web"
VENV_DIR="$PROJECT_ROOT/.venv"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info()  { echo -e "${BLUE}[INFO]${NC}  $1"; }
log_ok()    { echo -e "${GREEN}[OK]${NC}    $1"; }
log_warn()  { echo -e "${YELLOW}[WARN]${NC}  $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

cleanup() {
    log_info "正在关闭服务..."
    if [ -n "$BACKEND_PID" ] && kill -0 "$BACKEND_PID" 2>/dev/null; then
        kill "$BACKEND_PID" 2>/dev/null
        wait "$BACKEND_PID" 2>/dev/null || true
        log_ok "后端服务已关闭"
    fi
    if [ -n "$FRONTEND_PID" ] && kill -0 "$FRONTEND_PID" 2>/dev/null; then
        kill "$FRONTEND_PID" 2>/dev/null
        wait "$FRONTEND_PID" 2>/dev/null || true
        log_ok "前端服务已关闭"
    fi
    log_info "系统已停止"
}
trap cleanup EXIT INT TERM

echo "========================================"
echo "  ERP 进销存系统 - 本地开发启动"
echo "========================================"
echo ""

# ---- 检查依赖 ----
log_info "检查运行环境..."

if ! command -v python3 &> /dev/null; then
    log_error "未找到 python3，请先安装 Python 3.10+"
    exit 1
fi
PYTHON_VER=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
log_ok "Python 版本: $PYTHON_VER"

if ! command -v node &> /dev/null; then
    log_error "未找到 node，请先安装 Node.js 18+"
    exit 1
fi
NODE_VER=$(node --version)
log_ok "Node 版本: $NODE_VER"

if ! command -v npm &> /dev/null; then
    log_error "未找到 npm"
    exit 1
fi
NPM_VER=$(npm --version)
log_ok "npm 版本: $NPM_VER"

# ---- 后端初始化 ----
echo ""
log_info "===== 初始化后端 ====="

# 创建虚拟环境
if [ ! -d "$VENV_DIR" ]; then
    log_info "创建 Python 虚拟环境..."
    python3 -m venv "$VENV_DIR"
    log_ok "虚拟环境已创建: $VENV_DIR"
fi

log_info "激活虚拟环境..."
source "$VENV_DIR/bin/activate"

# 安装依赖
log_info "安装 Python 依赖..."
pip install -q --upgrade pip -i https://pypi.tuna.tsinghua.edu.cn/simple
pip install -q setuptools -i https://pypi.tuna.tsinghua.edu.cn/simple
pip install -q -r "$BACKEND_DIR/requirements.txt" -i https://pypi.tuna.tsinghua.edu.cn/simple
log_ok "Python 依赖已安装"

# 环境变量
export DJANGO_SETTINGS_MODULE=erp.settings
export DB_ENGINE=${DB_ENGINE:-django.db.backends.sqlite3}
export DB_NAME=${DB_NAME:-data/db.sqlite3}
export DEBUG=True
export SECRET_KEY=${SECRET_KEY:-dev-secret-key-change-in-production-$(python3 -c "import secrets; print(secrets.token_hex(16))")}
export ALLOWED_HOSTS=localhost,127.0.0.1
export CORS_ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173

log_info "SECRET_KEY=${SECRET_KEY:0:20}..."

# 创建必要目录
mkdir -p "$BACKEND_DIR/data" "$BACKEND_DIR/media" "$BACKEND_DIR/logs"

# 数据库迁移
log_info "执行数据库迁移..."
cd "$BACKEND_DIR"
python manage.py migrate --noinput
log_ok "数据库迁移完成"

# 创建管理员（如不存在）
log_info "检查管理员账户..."
python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    admin = User.objects.create_superuser('admin', password='admin123')
    admin.name = '系统管理员'
    admin.permissions = {
        'basic': {'view': True, 'add': True, 'edit': True, 'delete': True},
        'purchase': {'view': True, 'add': True, 'edit': True, 'delete': True},
        'sale': {'view': True, 'add': True, 'edit': True, 'delete': True},
        'inventory': {'view': True, 'add': True, 'edit': True, 'delete': True},
        'finance': {'view': True, 'add': True, 'edit': True, 'delete': True},
        'reports': {'view': True},
        'system': {'view': True, 'add': True, 'edit': True, 'delete': True}
    }
    admin.save()
    print('管理员账户已创建: admin / admin123')
" 2>&1
log_ok "管理员账户检查完成"

# ---- 前端初始化 ----
echo ""
log_info "===== 初始化前端 ====="

cd "$FRONTEND_DIR"
if [ ! -d "node_modules" ]; then
    log_info "安装前端依赖（首次运行可能需要几分钟）..."
    npm install --registry=https://registry.npmmirror.com
    log_ok "前端依赖已安装"
fi

# ---- 启动服务 ----
echo ""
echo "========================================"
echo "  启动服务"
echo "========================================"
echo ""

# 启动后端
cd "$BACKEND_DIR"
log_info "启动 Django 后端 (http://localhost:8000)..."
source "$VENV_DIR/bin/activate"
python manage.py runserver 0.0.0.0:8000 &
BACKEND_PID=$!
log_ok "后端已启动 (PID: $BACKEND_PID)"

# 等待后端就绪
sleep 2

# 启动前端
cd "$FRONTEND_DIR"
log_info "启动 Vue 前端 (http://localhost:5173)..."
npm run dev &
FRONTEND_PID=$!
log_ok "前端已启动 (PID: $FRONTEND_PID)"

echo ""
echo "========================================"
echo "  系统已就绪！"
echo "========================================"
echo ""
echo "  前端地址:     http://localhost:5173"
echo "  后端地址:     http://localhost:8000"
echo "  管理员账户:   admin / admin123"
echo ""
echo "  按 Ctrl+C 停止所有服务"
echo "========================================"

wait

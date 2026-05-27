#!/bin/bash
set -e

echo "========================================"
echo "  ERP 进销存系统 - 容器启动"
echo "========================================"

# 创建必要目录
mkdir -p /app/data /app/media /app/logs /app/static

# 运行数据库迁移
echo "[1/3] 执行数据库迁移..."
python manage.py migrate --noinput

# 创建管理员账户（如果不存在）
echo "[2/3] 检查管理员账户..."
python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', password='admin123')
    admin = User.objects.get(username='admin')
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

# 收集静态文件
echo "[3/3] 收集静态文件..."
python manage.py collectstatic --noinput 2>/dev/null || true

echo "========================================"
echo "  系统就绪，启动服务..."
echo "  默认管理员: admin / admin123"
echo "========================================"

# 启动 Gunicorn
exec gunicorn --bind 0.0.0.0:8000 \
    --workers 2 \
    --timeout 120 \
    --access-logfile /app/logs/access.log \
    --error-logfile /app/logs/error.log \
    erp.wsgi:application

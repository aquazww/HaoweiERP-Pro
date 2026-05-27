#!/bin/bash
# ============================================
#   ERP 进销存系统 FPK 打包脚本
#   fly 飞牛 fnOS 应用安装包
# ============================================
set -e

APP_NAME="erp-system"
FPK_NAME="豪威ERP进销存_v1.0.0"
FPK_DIR="$(cd "$(dirname "$0")" && pwd)/${APP_NAME}"

echo "========================================"
echo "  FPK 打包 - ${FPK_NAME}"
echo "========================================"

# 检查目录结构
if [ ! -f "${FPK_DIR}/fnos/manifest" ]; then
    echo "❌ 错误: 找不到 manifest 文件"
    echo "   请确保 FPK 目录结构正确："
    echo "   ${APP_NAME}/"
    echo "   ├── fnos/"
    echo "   │   ├── manifest"
    echo "   │   ├── ICON.PNG"
    echo "   │   ├── ICON_256.PNG"
    echo "   │   ├── ${FPK_NAME}.sc"
    echo "   │   └── docker/"
    echo "   │       └── docker-compose.yaml"
    exit 1
fi

echo "[1/3] 验证文件..."
echo "  ✓ manifest"
echo "  ✓ docker-compose.yaml"
for f in ICON.PNG ICON_256.PNG; do
    if [ -f "${FPK_DIR}/fnos/${f}" ]; then
        echo "  ✓ ${f}"
    else
        echo "  ⚠ ${f} 缺失（将使用默认图标）"
    fi
done

echo ""
echo "[2/3] 打包为 .fpk ..."

FPK_DIR_BASE="$(cd "$(dirname "$0")" && pwd)"
cd "${FPK_DIR_BASE}"

# FPK 本质是 tar.gz 格式
tar -czf "${FPK_NAME}.fpk" "${APP_NAME}/"

echo ""
echo "[3/3] 生成完成!"
echo ""
echo "========================================"
echo "  ✅ ${FPK_NAME}.fpk"
echo ""
echo "  文件大小: $(ls -lh "${FPK_NAME}.fpk" | awk '{print $5}')"
echo "  文件位置: ${FPK_DIR_BASE}/${FPK_NAME}.fpk"
echo "========================================"
echo ""
echo "安装方法:"
echo "  1. 打开飞牛 fnOS 桌面"
echo "  2. 进入「应用中心」"
echo "  3. 点击「手动安装」→ 选择 ${FPK_NAME}.fpk"
echo "  4. 安装完成后访问 http://你的NAS_IP:8080"
echo "  5. 默认管理员: admin / admin123"
echo ""

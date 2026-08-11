#!/usr/bin/env bash
# ============================================================
# QuantLab 便携启动脚本 (macOS / Linux)
# ============================================================

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo
echo " ============================================================"
echo "                 QuantLab 便携学习平台"
echo "             Quant Trading Course (offline)"
echo " ============================================================"
echo

# ---- 1. 检测 Node.js ----
if ! command -v node >/dev/null 2>&1; then
    echo "  ✗  未检测到 Node.js"
    echo
    echo "     QuantLab 需要 Node.js 来运行本地服务器（14+ 即可）"
    echo "     macOS  : brew install node"
    echo "     Linux  : sudo apt install nodejs  或  https://nodejs.org"
    echo
    read -p "按 Enter 关闭..."
    exit 1
fi

NODE_VER=$(node -v)
echo "  ✓  检测到 Node.js $NODE_VER"
echo
echo "  - 正在启动本地服务..."
echo

# ---- 2. 启动服务 ----
node serve.cjs
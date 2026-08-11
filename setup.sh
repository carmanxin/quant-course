#!/usr/bin/env bash
# ==========================================
# 量化交易课程 — 一键启动本地 Jupyter 环境
# 用法: bash setup.sh
# ==========================================
set -e

echo "🐍 量化交易课程 — 本地环境初始化"
echo "=================================="
echo ""

# 检查 Python
if command -v python3 &> /dev/null; then
    PYTHON=python3
elif command -v python &> /dev/null; then
    PYTHON=python
else
    echo "❌ 未找到 Python，请先安装 Python 3.10+"
    echo "   下载: https://www.python.org/downloads/"
    exit 1
fi

echo "✅ Python: $($PYTHON --version)"

# 创建虚拟环境
if [ ! -d "venv" ]; then
    echo "📦 创建虚拟环境..."
    $PYTHON -m venv venv
fi

# 激活虚拟环境
if [ -f "venv/Scripts/activate" ]; then
    source venv/Scripts/activate   # Windows (Git Bash)
elif [ -f "venv/bin/activate" ]; then
    source venv/bin/activate       # macOS / Linux
fi

# 升级 pip
echo "📦 升级 pip..."
pip install --upgrade pip -q

# 安装核心依赖
echo "📦 安装核心依赖 (numpy, pandas, scipy, matplotlib, scikit-learn)..."
pip install numpy pandas scipy matplotlib seaborn scikit-learn statsmodels -q

# 安装进阶依赖（跳过编译失败的包）
echo "📦 安装进阶依赖..."
pip install xgboost lightgbm pyarrow networkx requests tqdm jupyterlab notebook -q 2>/dev/null || true

# 尝试安装深度学习（可能较慢）
echo "📦 安装 PyTorch (CPU 版本，约 200MB)..."
pip install torch --index-url https://download.pytorch.org/whl/cpu -q 2>/dev/null || echo "⚠ PyTorch 安装失败，可稍后手动安装"

echo "📦 安装 transformers..."
pip install transformers -q 2>/dev/null || echo "⚠ transformers 安装失败"

# 数据获取
echo "📦 安装数据获取库..."
pip install akshare yfinance -q 2>/dev/null || echo "⚠ akshare/yfinance 安装失败"

# 可选
echo "📦 安装可选依赖..."
pip install hmmlearn kafka-python redis prometheus-client websocket-client -q 2>/dev/null || echo "⚠ 部分可选依赖安装失败"

# 验证核心包
echo ""
echo "🔍 验证核心包..."
$PYTHON -c "
packages = ['numpy', 'pandas', 'scipy', 'matplotlib', 'sklearn', 'statsmodels', 'jupyterlab']
for pkg in packages:
    try:
        __import__(pkg)
        print(f'  ✅ {pkg}')
    except ImportError:
        print(f'  ⚠ {pkg} 未安装')
"

echo ""
echo "=================================="
echo "✅ 环境初始化完成！"
echo ""
echo "启动 Jupyter Lab:"
echo "  source venv/bin/activate  (或 venv\\Scripts\\activate)"
echo "  jupyter lab"
echo ""
echo "或直接在当前目录打开:"
echo "  jupyter lab ."
echo "=================================="

@echo off
REM ==========================================
REM 量化交易课程 — 一键启动 (Windows)
REM 双击运行此文件
REM ==========================================
setlocal enabledelayedexpansion

echo 🐍 量化交易课程 — 本地环境初始化
echo ==================================
echo.

REM 检查 Python
where python >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ❌ 未找到 Python，请先安装 Python 3.10+
    echo    https://www.python.org/downloads/
    pause
    exit /b 1
)

python --version
echo.

REM 创建虚拟环境
if not exist "venv" (
    echo 📦 创建虚拟环境...
    python -m venv venv
)

REM 激活
call venv\Scripts\activate.bat

echo 📦 升级 pip...
pip install --upgrade pip -q

echo 📦 安装核心依赖...
pip install numpy pandas scipy matplotlib seaborn scikit-learn statsmodels -q

echo 📦 安装进阶依赖...
pip install xgboost lightgbm pyarrow networkx requests tqdm jupyterlab notebook -q

echo 📦 安装 PyTorch CPU 版...
pip install torch --index-url https://download.pytorch.org/whl/cpu -q

echo 📦 安装 transformers...
pip install transformers -q

echo 📦 安装数据获取库...
pip install akshare yfinance -q

echo 📦 安装可选依赖...
pip install hmmlearn kafka-python redis prometheus-client websocket-client -q

echo.
echo ==================================
echo ✅ 安装完成！启动 Jupyter Lab...
echo ==================================
jupyter lab .
pause

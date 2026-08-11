@echo off
chcp 65001 >nul
title QuantLab - 量化交易学习平台(离线版)

REM ============================================================
REM QuantLab 便携启动脚本 (Windows)
REM --------------------------------------------------------
REM  1. 检测 Node.js 是否安装
REM  2. 在 portable/ 目录下启动 serve.js
REM  3. 浏览器自动打开
REM ============================================================

echo.
echo  ============================================================
echo                 QuantLab 便携学习平台
echo             Quant Trading Course (offline)
echo  ============================================================
echo.

REM ---- 1. 检测 Node.js ----
where node >nul 2>nul
if %errorlevel% neq 0 (
    echo  X  未检测到 Node.js。
    echo.
    echo     QuantLab 需要 Node.js 来运行本地服务器（14+ 即可）。
    echo     请到 https://nodejs.org/zh-cn 下载安装 LTS 版本。
    echo     安装完成后再次双击 start.bat 即可。
    echo.
    pause
    exit /b 1
)

for /f "delims=" %%v in ('node -v') do set NODE_VER=%%v
echo  - 检测到 Node.js %NODE_VER%

REM ---- 2. 进入 portable 目录 ----
cd /d "%~dp0"

REM ---- 3. 启动服务 ----
echo  - 正在启动本地服务...
echo.
node serve.cjs
@echo off
chcp 65001 >nul
REM ============================================================
REM QuantLab 一键打包便携版
REM --------------------------------------------------------
REM  流程：
REM    1. 构建 dist/ （含本地 Pyodide）
REM    2. 复制 dist/ 到 portable/dist/
REM    3. 验证 portable/ 结构
REM    4. 输出大小报告
REM ============================================================

echo.
echo  ============================================================
echo          QuantLab 便携版 · 一键打包
echo  ============================================================
echo.

REM ---- 1. 进入项目根目录 ----
cd /d "%~dp0"

REM ---- 2. 清理旧 portable/dist ----
echo  - 清理旧的构建产物...
if exist portable\dist (
    rmdir /s /q portable\dist 2>nul
)

REM ---- 3. 构建 dist/ ----
echo  - 正在构建网站（含本地 Pyodide）...
echo.
call npm run build
if %errorlevel% neq 0 (
    echo.
    echo  X  构建失败，请检查上方错误
    pause
    exit /b 1
)

REM ---- 4. 复制到 portable/dist/ ----
echo.
echo  - 复制 dist 到 portable/dist...
xcopy /E /I /Y /Q dist portable\dist >nul 2>&1
if %errorlevel% neq 0 (
    echo  X  复制失败
    pause
    exit /b 1
)

REM ---- 5. 验证结构 ----
echo  - 验证 portable 结构...
if not exist portable\dist\index.html (
    echo  X  portable\dist\index.html 不存在
    pause
    exit /b 1
)
if not exist portable\pyodide\pyodide.js (
    echo  X  portable\pyodide\pyodide.js 不存在
    echo     请先 npm install pyodide@0.26.4 --no-save 然后重新打包
    pause
    exit /b 1
)
if not exist portable\serve.cjs (
    echo  X  portable\serve.cjs 不存在
    pause
    exit /b 1
)

REM ---- 6. 输出大小报告 ----
echo.
echo  ============================================================
echo  便携版构建完成!
echo  ============================================================
echo.
echo  位置: %CD%\portable\
echo.

REM 用 PowerShell 计算目录大小
powershell -NoProfile -Command "$size = (Get-ChildItem portable -Recurse -File | Measure-Object -Property Length -Sum).Sum / 1MB; Write-Host ('  总体积: {0:N1} MB' -f $size)"
powershell -NoProfile -Command "$size = (Get-ChildItem portable\dist -Recurse -File | Measure-Object -Property Length -Sum).Sum / 1MB; Write-Host ('  dist/:  {0:N1} MB' -f $size)"
powershell -NoProfile -Command "$size = (Get-ChildItem portable\pyodide -Recurse -File | Measure-Object -Property Length -Sum).Sum / 1MB; Write-Host ('  pyodide/: {0:N1} MB' -f $size)"

echo.
echo  下一步：
echo    1. 把 portable/ 文件夹拷贝到 U 盘 / 邮件附件 / 网盘
echo    2. 目标电脑装 Node.js 14+
echo    3. 双击 portable\start.bat 启动
echo.
echo  完成。
echo.
pause
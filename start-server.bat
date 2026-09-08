@echo off
cd /d "%~dp0portable"

set PORT=4179
if not "%~1"=="" set PORT=%~1

echo.
echo   QuantLab 本地服务启动中...
echo   地址: http://127.0.0.1:%PORT%/
echo.

where node >nul 2>&1
if errorlevel 1 (
    echo   [错误] 未检测到 node,请先安装 Node.js 并加入 PATH
    pause
    exit /b 1
)

echo   正在启动 node serve.cjs --port %PORT% ...
start /b "" node serve.cjs --port %PORT%

echo   等待端口 %PORT% 就绪...
set READY=0
for /l %%i in (1,1,30) do (
    timeout /t 1 /nobreak >nul
    netstat -ano | findstr /C:":%PORT% " | findstr "LISTENING" >nul
    if not errorlevel 1 (
        set READY=1
        goto ready
    )
)
:ready

if "%READY%"=="1" (
    timeout /t 1 /nobreak >nul
    echo   端口已就绪,正在打开浏览器...
    start "" "http://127.0.0.1:%PORT%/"
) else (
    echo   [警告] 30 秒内端口未就绪,请手动访问: http://127.0.0.1:%PORT%/
)

echo.
echo   服务运行中,请勿关闭此窗口。关闭窗口即停止服务。
echo.
pause

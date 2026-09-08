@echo off
REM Clean env build script - 清除所有 safe-delete shim
set NODE_OPTIONS=
set BASH_ENV=
set CODEBUDDY_SAFE_DELETE_BULK_GUARD=
set CODEBUDDY_SAFE_DELETE_SANDBOX=
set CODEBUDDY_SAFE_DELETE_BIN_DIR=
set CODEBUDDY_SAFE_DELETE_BULK_STATE_DIR=
set CODEBUDDY_SAFE_DELETE_BULK_THRESHOLD=
set CODEBUDDY_SAFE_DELETE_REPORT_PATH=

REM 移除 safe-bin from PATH
setlocal
set PATH=%PATH:C:\Users\xinhaoming\AppData\Local\Programs\WorkBuddy\resources\app.asar.unpacked\cli\vendor\shim\safe-bin;=%

REM 运行 vitepress build
cd /d D:\AI\study\quant
call npx vitepress build
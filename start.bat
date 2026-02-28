@echo off
chcp 65001 > nul
title Music Scraper

echo 🎵 启动音乐刮削器...
echo.

:: 检查虚拟环境
if not exist "venv" (
    echo ❌ 虚拟环境不存在，请先运行 setup.bat
    pause
    exit /b 1
)

:: 激活虚拟环境
echo 🔄 激活虚拟环境...
call venv\Scripts\activate.bat

:: 启动应用
echo 🚀 启动 Flask 应用...
echo 🌐 访问地址: http://localhost:5000
echo 🔗 本机地址: http://localhost:5000
echo.
echo 按Ctrl+C 停止服务
echo.

python app.py

pause
@echo off
chcp 65001 > nul
title Music Scraper Setup

echo 🎵 正在设置音乐刮削器...
echo.

:: 检查 Python 版本
python --version > nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python 未安装，请先安装 Python 3
    pause
    exit /b 1
)

:: 创建虚拟环境
echo 📦 创建虚拟环境...
python -m venv venv
if %errorlevel% neq 0 (
    echo ❌ 创建虚拟环境失败
    pause
    exit /b 1
)

:: 激活虚拟环境
echo 🔄 激活虚拟环境...
call venv\Scripts\activate.bat

:: 安装依赖
echo ⬇️  安装依赖包...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ❌ 安装依赖失败
    pause
    exit /b 1
)

:: 创建上传目录
if not exist "uploads" mkdir uploads

:: 创建数据库
echo 💾 初始化数据库...
if not exist "music_metadata.db" echo. > music_metadata.db

echo ✅ 设置完成！
echo.
echo 🚀 启动应用:
echo   start.bat
echo.
echo 🌐 访问地址: http://localhost:5000
echo.
pause
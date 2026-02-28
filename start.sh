#!/bin/bash

# Music Scraper Start Script
# 适用于 Linux/MacOS

echo "🎵 启动音乐刮削器..."

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "❌ 虚拟环境不存在，请先运行 setup.sh"
    exit 1
fi

# 激活虚拟环境
echo "🔄 激活虚拟环境..."
source venv/bin/activate

# 启动应用
echo "🚀 启动 Flask 应用..."
echo "🌐 访问地址: http://localhost:5000"
echo "🔗 网络地址: http://$(hostname -I | awk '{print $1}'):5000"
echo ""
echo "按 Ctrl+C 停止服务"
echo ""

python app.py
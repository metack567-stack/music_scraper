#!/bin/bash

# Music Scraper Setup Script
# 适用于 Linux/MacOS

echo "🎵 正在设置音乐刮削器..."

# 检查 Python 版本
python3 --version
if [ $? -ne 0 ]; then
    echo "❌ Python 3 未安装，请先安装 Python 3"
    exit 1
fi

# 创建虚拟环境
echo "📦 创建虚拟环境..."
python3 -m venv venv

# 激活虚拟环境
echo "🔄 激活虚拟环境..."
source venv/bin/activate

# 安装依赖
echo "⬇️  安装依赖包..."
pip install -r requirements.txt

# 创建上传目录
mkdir -p uploads

# 创建数据库
echo "💾 初始化数据库..."
touch music_metadata.db

echo "✅ 设置完成！"
echo ""
echo "🚀 启动应用:"
echo "  ./start.sh"
echo ""
echo "🌐 访问地址: http://localhost:5000"
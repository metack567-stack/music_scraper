# 🚀 部署指南

音乐刮削程序已经成功部署到 GitHub，可以通过多种方式进行部署。

## 🐳 Docker 部署 (推荐)

### 方法 1: Docker Compose (最简单)

```bash
# 克隆仓库
git clone https://github.com/metack567-stack/music_scraper.git
cd music_scraper

# 启动服务
docker-compose up -d

# 查看日志
docker-compose logs -f
```

### 方法 2: 直接使用 Docker

```bash
# 克隆仓库
git clone https://github.com/metack567-stack/music_scraper.git
cd music_scraper

# 构建镜像
docker build -t music-scraper .

# 运行容器
docker run -d -p 5000:5000 -v $(pwd)/uploads:/app/uploads -v $(pwd)/music_metadata.db:/app/music_metadata.db music-scraper
```

### 方法 3: Docker 网络

```bash
# 创建自定义网络
docker network create music-scraper-net

# 运行应用
docker run -d --name music-scraper --network music-scraper-net -p 5000:5000 -v $(pwd)/uploads:/app/uploads music-scraper

# 可选: 运行数据库 (如果需要)
docker run -d --name music-scraper-db --network music-scraper-net -v $(pwd)/data:/data sqlite3
```

## 💻 本地部署

### Linux/MacOS

```bash
# 克隆仓库
git clone https://github.com/metack567-stack/music_scraper.git
cd music_scraper

# 一键设置
chmod +x setup.sh
./setup.sh

# 启动应用
./start.sh
```

### Windows

```batch
# 克隆仓库
git clone https://github.com/metack567-stack/music_scraper.git
cd music_scraper

# 一键设置
setup.bat

# 启动应用
start.bat
```

### 手动安装

```bash
# 克隆仓库
git clone https://github.com/metack567-stack/music_scraper.git
cd music_scraper

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\\Scripts\\activate  # Windows

# 安装依赖
pip install -r requirements.txt

# 创建必要的目录
mkdir -p uploads

# 启动应用
python app.py
```

## ⚡ 快速启动脚本

### 一键启动 (所有平台)

```bash
# Linux/MacOS
curl -sSL https://raw.githubusercontent.com/metack567-stack/music_scraper/main/quick_start.sh | bash

# Windows
powershell -ExecutionPolicy Bypass -Command "iwr -useb https://raw.githubusercontent.com/metack567-stack/music_scraper/main/quick_start.ps1 | iex"
```

## 🔧 配置选项

### 环境变量

在 `.env` 文件中设置：

```env
FLASK_ENV=production
SECRET_KEY=your-production-secret-key-here
MAX_CONTENT_LENGTH=16777216  # 16MB
DATABASE_PATH=./music_metadata.db
```

### 配置文件

编辑 `config.py` 来自定义设置：

```python
class Config:
    # 文件上传限制
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    
    # 支持的音频格式
    ALLOWED_EXTENSIONS = {'mp3', 'flac', 'm4a', 'ogg', 'wav'}
    
    # 数据库路径
    DATABASE_PATH = 'music_metadata.db'
    
    # API 设置
    TIMEOUT = 30
    RETRY_COUNT = 3
```

## 🌐 访问应用

启动成功后，访问以下地址：

- **本地**: http://localhost:5000
- **网络**: http://your-server-ip:5000

## 🔍 监控和维护

### Docker 容器管理

```bash
# 查看容器状态
docker ps

# 查看日志
docker logs music-scraper

# 停止服务
docker-compose down

# 重启服务
docker-compose restart

# 更新到最新版本
docker-compose pull
docker-compose up -d
```

### 本地服务管理

```bash
# 查看进程
ps aux | grep app.py

# 停止服务
pkill -f app.py

# 查看日志
tail -f app.log
```

## 📊 性能优化

### 1. 生产环境配置

```python
# config.py
class ProductionConfig(Config):
    SECRET_KEY = os.environ.get('SECRET_KEY')
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = 'postgresql://user:password@localhost/music_scraper'
```

### 2. 反向代理配置 (Nginx)

```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 3. 负载均衡

```yaml
# docker-compose.yml
version: '3.8'
services:
  music-scraper:
    deploy:
      replicas: 3
    build: .
    ports:
      - "5000:5000"
```

## 🔐 安全配置

1. **修改默认密钥**:
   ```python
   SECRET_KEY = 'your-strong-secret-key-here'
   ```

2. **设置文件上传限制**:
   ```python
   MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
   ```

3. **使用 HTTPS**:
   ```python
   from flask_sslify import SSLify
   app.wsgi_app = SSLify(app)
   ```

## 🔄 备份和维护

### 数据库备份

```bash
# 备份数据库
cp music_metadata.db backup/music_metadata_$(date +%Y%m%d).db

# 自动备份脚本
crontab -e
# 添加: 0 2 * * * cp /path/to/music_metadata.db /backup/path/music_metadata_$(date +\%Y\%m\%d).db
```

### 日志轮转

```python
import logging
from logging.handlers import RotatingFileHandler

handler = RotatingFileHandler('app.log', maxBytes=10000, backupCount=3)
app.logger.addHandler(handler)
```

---

**享受音乐整理的乐趣！🎵**
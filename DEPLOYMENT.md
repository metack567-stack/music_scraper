# Docker部署指南

## 📦 快速开始

### 1. 基本部署（单容器）
```bash
# 克隆或复制项目到本地
git clone <repository-url>
cd music_scraper

# 构建并启动
docker-compose up -d

# 检查状态
docker-compose ps
```

### 2. 生产环境部署（带Nginx）
```bash
# 使用生产环境配置
docker-compose -f docker-compose.prod.yml up -d

# 包含Nginx反向代理
docker-compose -f docker-compose.prod.yml --profile nginx up -d
```

### 3. 开发环境
```bash
# 使用开发环境配置
docker-compose -f docker-compose.dev.yml up -d
```

## 🔧 配置说明

### 环境变量配置
```bash
# 复制环境变量模板
cp .env.example .env

# 编辑环境变量
vim .env
```

主要环境变量：
- `FLASK_ENV`: 运行环境 (development/production)
- `DATABASE_PATH`: 数据库文件路径
- `UPLOAD_FOLDER`: 上传文件目录
- `LOG_LEVEL`: 日志级别
- `MAX_CONTENT_LENGTH`: 最大文件上传大小

### 数据持久化
```bash
# 数据目录映射
./uploads:/app/uploads     # 上传文件
./database:/app/database   # 数据库文件
./logs:/app/logs           # 日志文件
```

## 🚀 使用方法

### 1. 查看服务状态
```bash
docker-compose ps
docker-compose logs -f music-scraper
```

### 2. 访问服务
- 本地访问：http://localhost:5000
- 带Nginx：http://localhost:80

### 3. 健康检查
```bash
# 检查服务状态
curl http://localhost:5000/api/stats

# 检查健康状态
curl http://localhost/health
```

### 4. 更新部署
```bash
# 拉取最新代码
git pull

# 重新构建并重启
docker-compose up -d --build

# 或者
docker-compose down
docker-compose up -d
```

## 🔧 高级配置

### 1. 自定义端口
```yaml
# docker-compose.yml
ports:
  - "8080:5000"  # 修改宿主机端口
```

### 2. 扩展服务
```yaml
# 扩展线程数
environment:
  - PROCESS_MAX_WORKERS=8
```

### 3. 自定义域名
```nginx
# nginx.conf
server_name your-domain.com;
```

## 📊 监控和维护

### 1. 日志管理
```bash
# 查看所有日志
docker-compose logs

# 查看特定服务日志
docker-compose logs -f music-scraper

# 查看最后100行
docker-compose logs --tail=100 music-scraper
```

### 2. 资源监控
```bash
# 查看容器资源使用情况
docker stats

# 查看容器详细信息
docker inspect music-scraper
```

### 3. 数据备份
```bash
# 备份数据库
docker exec music-scraper cp /app/database/music_metadata.db ./backup/

# 备份上传文件
docker cp music-scraper:/app/uploads ./backup/
```

### 4. 数据恢复
```bash
# 恢复数据库
docker exec music-scraper cp ./backup/music_metadata.db /app/database/

# 恢复上传文件
docker cp ./backup/uploads music-scraper:/app/
```

## 🛡️ 安全配置

### 1. 生产环境安全
```yaml
# 生产环境配置
environment:
  - FLASK_ENV=production
  - SECRET_KEY=your-secure-secret-key
  - LOG_LEVEL=ERROR

# 禁用调试模式
command: python app.py
```

### 2. 网络安全
```yaml
# 限制网络访问
ports:
  - "127.0.0.1:5000:5000"

# 或者使用SSH隧道
ssh -L 5000:localhost:5000 user@server
```

### 3. 文件权限
```bash
# 设置正确的文件权限
docker exec music-scraper chmod 755 /app
docker exec music-scraper chown -R www-data:www-data /app
```

## 🔧 故障排除

### 常见问题

1. **端口占用**
   ```bash
   # 检查端口占用
   netstat -tulpn | grep :5000
   
   # 修改端口映射
   ports:
     - "5001:5000"
   ```

2. **权限问题**
   ```bash
   # 检查容器权限
   docker exec music-scraper ls -la /app/uploads
   
   # 修复权限
   docker exec music-scraper chown -R www-data:www-data /app/uploads
   ```

3. **数据库问题**
   ```bash
   # 检查数据库文件
   docker exec music-scraper ls -la /app/database/
   
   # 重启服务
   docker-compose restart music-scraper
   ```

### 重置环境
```bash
# 完全重置
docker-compose down -v
docker-compose up -d --build
```

## 📚 相关文档

- [Docker Compose 文档](https://docs.docker.com/compose/)
- [Flask 文档](https://flask.palletsprojects.com/)
- [Nginx 反向代理配置](https://nginx.org/en/docs/)
- [Docker 最佳实践](https://docs.docker.com/develop/)
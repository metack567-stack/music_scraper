# 🎵 Music Scraper - 音乐刮削器

一个现代化的音乐元数据提取和管理工具，支持多种音频格式的自动标签提取和Web集成。

## ✨ 主要功能

- **🎵 多格式支持**: MP3, FLAC, M4A, OGG, WAV
- **🏷️ 自动提取**: 艺术家、标题、专辑、年份、流派、比特率、时长等
- **🌐 Web集成**: MusicBrainz API 获取增强元数据
- **🔍 智能搜索**: 按艺术家、歌曲、专辑实时搜索
- **📁 批量处理**: 整个文件夹的音乐文件扫描
- **💾 数据存储**: SQLite数据库持久化存储
- **🎨 现代界面**: 响应式Web界面，支持拖拽上传

## 🚀 快速开始

### 环境要求
- Python 3.8+
- pip 包管理器

### 安装步骤

1. **克隆仓库**
```bash
git clone https://github.com/metack567-stack/music_scraper.git
cd music_scraper
```

2. **创建虚拟环境**
```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\\Scripts\\activate  # Windows
```

3. **安装依赖**
```bash
pip install -r requirements.txt
```

4. **启动应用**
```bash
python app.py
```

5. **访问界面**
打开浏览器访问: http://localhost:5000

### Docker 部署

使用 Docker Compose 一键部署：

```bash
docker-compose up -d
```

或直接使用 Docker：
```bash
docker build -t music-scraper .
docker run -p 5000:5000 music-scraper
```

## 📁 项目结构

```
music_scraper/
├── app.py                    # 主应用程序
├── requirements.txt          # Python依赖
├── config.py                 # 配置设置
├── Dockerfile                # Docker构建文件
├── docker-compose.yml        # Docker Compose配置
├── README.md                 # 项目说明
├── utils/
│   ├── metadata.py          # 音乐元数据提取
│   ├── scraper.py           # 网络爬虫功能
│   └── database.py          # 数据库操作
├── templates/
│   └── index.html           # Web界面
└── static/
    ├── style.css            # 样式文件
    └── script.js            # 前端脚本
```

## 🎯 使用指南

### 1. 上传音乐文件
- 拖拽音乐文件到上传区域
- 支持批量上传
- 自动提取元数据

### 2. 搜索功能
- 在搜索框输入关键词
- 支持艺术家、歌曲、专辑搜索
- 实时搜索结果

### 3. 批量扫描文件夹
- 点击"扫描文件夹"按钮
- 输入文件夹路径
- 自动扫描并处理所有音乐文件

### 4. 查看统计信息
- 实时显示文件总数
- 支持的格式列表
- 数据库状态

## 🔧 API 端点

| 端点 | 方法 | 描述 |
|------|------|------|
| `/` | GET | 主页界面 |
| `/api/upload` | POST | 文件上传和元数据提取 |
| `/api/search` | GET | 搜索音乐文件 |
| `/api/files` | GET | 获取所有文件列表 |
| `/api/files/<id>` | GET | 获取特定文件详情 |
| `/api/stats` | GET | 应用统计信息 |
| `/api/scan-folder` | POST | 批量文件夹扫描 |
| `/api/cleanup` | POST | 数据库清理 |

## 🛠️ 技术栈

### 后端
- **Flask** - Web框架
- **SQLite3** - 数据库
- **mutagen** - 音频文件元数据提取
- **eyed3** - MP3文件处理
- **requests** - HTTP请求
- **beautifulsoup4** - HTML解析

### 前端
- **HTML5** - 页面结构
- **CSS3** - 样式设计
- **JavaScript** - 交互功能

## 🔌 外部集成

### MusicBrainz API
自动从 MusicBrainz 获取增强的元数据信息，包括：
- 更准确的艺术家信息
- 专辑详情
- 音乐分类和流派
- 发布日期

### 配置选项
在 `config.py` 中可以配置：
- 文件上传限制
- 支持的音频格式
- 数据库路径
- API超时设置

## 📝 开发说明

### 添加新的音频格式支持
1. 在 `config.py` 中添加新的文件扩展名
2. 在 `utils/metadata.py` 中实现对应的解析逻辑
3. 更新前端界面以支持新格式

### 自定义数据源
1. 在 `utils/scraper.py` 中添加新的数据源
2. 实现相应的搜索和提取逻辑
3. 更新数据库模式以支持新字段

## 🤝 贡献指南

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 📞 支持

如果您遇到问题或有建议，请：
1. 查看 Issues 页面
2. 创建新的 Issue
3. 或直接联系开发者

---

**享受音乐整理的乐趣！🎵**
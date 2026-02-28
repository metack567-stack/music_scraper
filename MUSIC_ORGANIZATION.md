# 音乐整理功能实现 - 批量管理音乐库

## 🎯 功能概述

**核心目标**: 完整的音乐库管理解决方案，包括批量处理、整理、清理等功能
**原则**: 高效、可靠、灵活，支持大规模音乐库整理

## ✅ 完整功能列表

### 1. 📂 目录扫描功能
- **递归扫描**: 深度遍历目录及其子目录
- **格式过滤**: 只处理支持的音乐格式 (MP3, FLAC, M4A, OGG, WAV)
- **智能识别**: 自动识别音乐文件并提取路径信息

### 2. 🚀 批量处理功能
- **并行处理**: 多线程同时处理多个文件
- **进度监控**: 实时显示处理进度
- **智能控制**: 可配置最大并发数，避免系统过载
- **错误处理**: 完善的异常处理和恢复机制

### 3. 🎵 元数据补全
- **歌词自动补全**: 自动搜索并写入歌词到文件标签
- **封面自动补全**: 多源搜索并写入封面到文件标签
- **质量保证**: 多源验证，确保数据准确性

### 4. 📁 文件整理功能
- **按艺术家整理**: 创建艺术家文件夹，整理相关音乐
- **按专辑整理**: 创建专辑文件夹，保持专辑完整性
- **智能重命名**: 保持文件名格式一致性

### 5. 🧹 清理功能
- **重复文件检测**: 基于文件名和大小检测重复
- **智能删除**: 保留质量较好的文件
- **数据库同步**: 清理数据库中的无效记录

### 6. 📊 统计分析功能
- **目录统计**: 文件数量、大小、格式分布
- **艺术家统计**: 艺术家数量、专辑数量
- **专辑统计**: 专辑数量、歌曲数量
- **时间统计**: 最旧/最新文件信息

## 🔧 技术实现

### 核心架构
```python
class MusicOrganizer:
    def __init__(self, db_path="music_metadata.db"):
        self.db = Database(db_path)              # 数据库操作
        self.metadata_extractor = MetadataExtractor()  # 元数据提取
        self.scraper = MusicScraper()              # 网络搜索
        self.running = False                      # 处理状态
```

### 批量处理流程
```python
def batch_process_files(self, file_paths: List[str], max_workers: int = 4):
    """批量处理音乐文件"""
    # 1. 并行处理
    # 2. 元数据提取
    # 3. 歌词搜索和写入
    # 4. 封面搜索和写入
    # 5. 数据库保存
    # 6. 状态更新
```

### 整理算法
```python
def organize_by_artist(self, target_directory: str):
    """按艺术家整理"""
    # 1. 获取艺术家分组
    # 2. 创建艺术家文件夹
    # 3. 移动文件到对应文件夹
    # 4. 更新数据库路径

def organize_by_album(self, target_directory: str):
    """按专辑整理"""
    # 1. 获取专辑分组
    # 2. 创建专辑文件夹
    # 3. 移动文件到对应文件夹
    # 4. 更新数据库路径
```

## 🚀 API 端点

### 1. 目录扫描
```bash
POST /api/organizer/scan-directory
{
    "directory": "/path/to/music",
    "recursive": true
}
```

### 2. 批量处理
```bash
POST /api/organizer/process-files
{
    "files": ["/path/to/file1.mp3", "/path/to/file2.flac"],
    "max_workers": 4
}
```

### 3. 按艺术家整理
```bash
POST /api/organizer/organize-by-artist
{
    "target_directory": "/path/to/organized"
}
```

### 4. 按专辑整理
```bash
POST /api/organizer/organize-by-album
{
    "target_directory": "/path/to/organized"
}
```

### 5. 清理重复文件
```bash
POST /api/organizer/cleanup-duplicates
# 无需参数
```

### 6. 目录统计
```bash
POST /api/organizer/directory-stats
{
    "directory": "/path/to/music"
}
```

### 7. 获取进度
```bash
GET /api/organizer/progress
```

## 📊 使用流程

### 1. 基础整理
```bash
# 1. 扫描目录
curl -X POST -d '{"directory": "/home/user/music", "recursive": true}' \
     http://localhost:5000/api/organizer/scan-directory

# 2. 批量处理
curl -X POST -d '{"files": ["/home/user/music/song1.mp3", "/home/user/music/song2.flac"]}' \
     http://localhost:5000/api/organizer/process-files

# 3. 按艺术家整理
curl -X POST -d '{"target_directory": "/home/user/organized_music"}' \
     http://localhost:5000/api/organizer/organize-by-artist
```

### 2. 高级整理
```bash
# 1. 扫描整个音乐库
curl -X POST -d '{"directory": "/home/user/music", "recursive": true}' \
     http://localhost:5000/api/organizer/scan-directory

# 2. 批量处理所有文件
curl -X POST -d '{"files": ["/home/user/music/**/*.mp3"], "max_workers": 8}' \
     http://localhost:5000/api/organizer/process-files

# 3. 按专辑整理
curl -X POST -d '{"target_directory": "/home/user/organized_music"}' \
     http://localhost:5000/api/organizer/organize-by-album

# 4. 清理重复文件
curl -X POST http://localhost:5000/api/organizer/cleanup-duplicates
```

## ⚡ 性能优化

### 1. 并发处理
- 多线程并行处理多个文件
- 可配置最大并发数，避免系统过载
- 智能任务调度，最大化处理效率

### 2. 缓存机制
- 数据库查询缓存
- 重复文件检测缓存
- 处理状态缓存

### 3. 错误恢复
- 单个文件处理失败不影响其他文件
- 自动重试机制
- 详细错误日志记录

### 4. 资源管理
- 内存使用优化
- 文件句柄管理
- 网络请求限制

## 🎯 实际应用场景

### 场景1: 大型音乐库整理
```
1. 扫描整个音乐库 (10,000+ 文件)
2. 并行处理所有文件
3. 按艺术家整理
4. 清理重复文件
5. 生成统计报告
```

### 场景2: 新增文件处理
```
1. 监听新文件上传
2. 自动提取元数据
3. 补全歌词和封面
4. 整理到对应文件夹
5. 更新数据库
```

### 场景3: 音乐库维护
```
1. 定期扫描检查
2. 处理缺失的元数据
3. 清理重复文件
4. 优化目录结构
5. 生成健康报告
```

## 🔍 详细功能说明

### 扫描功能
- **递归扫描**: 深度遍历所有子目录
- **格式过滤**: 只处理支持的音乐格式
- **路径验证**: 确保文件路径有效
- **权限检查**: 跳过无权限访问的文件

### 处理功能
- **元数据提取**: 提取文件的各种元数据
- **歌词搜索**: 自动搜索并写入歌词
- **封面搜索**: 多源搜索并写入封面
- **质量验证**: 验证写入的数据质量

### 整理功能
- **按艺术家**: 创建艺术家专用文件夹
- **按专辑**: 保持专辑完整性
- **智能命名**: 使用统一的命名规则
- **路径更新**: 自动更新数据库中的文件路径

### 清理功能
- **重复检测**: 基于文件名和大小
- **智能保留**: 保留质量较好的文件
- **数据库同步**: 清理无效的数据库记录
- **安全删除**: 确认删除前进行验证

### 统计功能
- **文件统计**: 数量、大小、格式分布
- **元数据统计**: 艺术家、专辑数量
- **时间统计**: 最旧/最新文件信息
- **健康度评估**: 音乐库完整性评估

---

**音乐整理功能：一站式音乐库管理解决方案！🎵**
# 歌词功能增强 - 更新总结

## ✅ 已完成的歌词功能增强

### 1. 数据库 Schema 更新
- ✅ 在 `metadata` 表中添加了歌词相关字段：
  - `lyrics TEXT` - 歌词文本内容
  - `lyrics_source TEXT` - 歌词来源网站
  - `lyrics_search_date TEXT` - 歌词搜索日期

### 2. 音频文件处理增强
- ✅ 更新了 `utils/metadata.py`:
  - 添加了 `write_lyrics_to_file()` 方法支持多种格式：
    - MP3: 使用 ID3 USLT 标签
    - FLAC: 使用 LYRICS 标签
    - M4A: 使用 iTunes 自定义标签
    - OGG: 使用 LYRICS 标签
  - 增强了 `extract_metadata()` 方法，现在会提取文件中已有的歌词

### 3. 应用逻辑更新
- ✅ 更新了 `app.py` 中的文件上传处理:
  - 自动搜索歌词并保存到数据库
  - 将歌词写入音频文件标签
  - 返回歌词搜索状态和来源信息

### 4. API 端点增强
- ✅ 新增了两个歌词相关的 API 端点：
  - `POST /api/search-lyrics/<file_id>` - 为特定文件搜索和保存歌词
  - `POST /api/update-lyrics/<file_id>` - 手动更新文件歌词

## 🎯 功能特点

### 自动歌词提取
1. **自动搜索**: 上传文件时自动搜索歌词
2. **多格式支持**: 支持 MP3、FLAC、M4A、OGG、WAV 格式
3. **持久化存储**: 歌词同时保存到数据库和音频文件标签

### 歌词来源
- **AZLyrics** - azlyrics.com
- **Genius** - genius.com
- **文件原有歌词** - 如果文件已有歌词会保留

### 存储机制
- **数据库**: 存储歌词文本、来源、搜索日期
- **音频文件**: 写入标准化的歌词标签
- **文件路径**: 保留原始文件引用

## 🚀 使用方式

### 自动方式 (推荐)
```bash
# 上传文件时自动搜索歌词
curl -X POST -F "file=@song.mp3" http://localhost:5000/api/upload
```

### 手动方式
```bash
# 为已有文件搜索歌词
curl -X POST http://localhost:5000/api/search-lyrics/1

# 手动更新歌词
curl -X POST -H "Content-Type: application/json" \
  -d '{"lyrics": "这是一首新歌曲的歌词...", "source": "manual"}' \
  http://localhost:5000/api/update-lyrics/1
```

## 📝 技术实现细节

### MP3 歌词标签
- 使用 `USLT` (Unsynchronized Lyrics) 标签
- 编码: UTF-8
- 语言: 英语
- 描述: 包含来源信息

### 歌词搜索策略
1. 搜索 AZLyrics 和 Genius 网站
2. 提取 HTML 中的歌词内容
3. 验证歌词长度和合理性
4. 保存来源信息用于版权追踪

### 错误处理
- 文件不存在检查
- 格式支持验证
- 网络超时处理
- 歌词内容验证

## 🔗 集成到现有系统

歌词功能现在完全集成到现有的音乐刮削系统中：
- **数据库**: 无缝集成到 SQLite 数据库
- **Web 界面**: 可以在文件详情中显示歌词
- **API**: 提供完整的歌词管理 API
- **Docker**: 支持容器化部署

## ⚠️ 版权说明

- 歌词提取仅供个人音乐整理使用
- 遵守相关网站的版权条款
- 建议仅用于个人音乐收藏管理
- 商业使用需要获得相应授权

---

**歌词功能已完成并集成到主应用中！🎵**
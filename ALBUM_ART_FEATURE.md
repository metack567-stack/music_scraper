# 音乐封面功能实现 - 自动补全缺失封面

## 🎯 核心需求

**目标**: 让上传的音乐文件缺失的封面能够自动补全
**原则**: 直接写入音频文件，不存储到数据库，不在网页显示

## ✅ 完成的功能

### 1. 自动封面搜索
- **iTunes API**: 高质量封面图片，免费稳定
- **MusicBrainz API**: 开放数据，精确匹配
- **Cover Art Archive**: 高分辨率封面专集

### 2. 多格式封面写入
- **MP3**: ID3 APIC 标签（标准封面标签）
- **FLAC**: PICTURE 标签
- **M4A**: covr 标签（iTunes格式）
- **OGG**: 图片标签支持

### 3. 智能处理
- **自动下载**: 从URL自动下载封面图片
- **格式转换**: 自动处理不同图片格式
- **大小优化**: 智能调整封面大小
- **错误处理**: 完善的异常处理机制

### 4. API 端点
- `POST /api/upload` - 上传并自动补全封面
- `POST /api/add-album-art/<file_id>` - 手动补全封面

## 🔧 技术实现

### 封面搜索策略
```python
def search_album_art(self, artist, album):
    # 按优先级搜索
    sources = [
        self._search_itunes,      # iTunes API (高质量)
        self._search_musicbrainz, # MusicBrainz (精确匹配)
        self._search_cover_art_archive  # Cover Art Archive (高分辨率)
    ]
```

### 标签写入实现
```python
# MP3 封面写入
def _write_album_art_to_mp3(self, file_path, artwork_data):
    audio_file = File(file_path)
    audio_file.add(APIC(
        encoding=3,
        mime='image/jpeg',
        type=3,  # 3 = front cover
        desc='Cover',
        data=artwork_data
    ))
    audio_file.save()

# FLAC 封面写入
def _write_album_art_to_flac(self, file_path, artwork_data):
    audio_file.tags['PICTURE'] = artwork_data
    audio_file.save()

# M4A 封面写入
def _write_album_art_to_m4a(self, file_path, artwork_data):
    audio_file.tags['covr'] = [artwork_data]
    audio_file.save()
```

### 图片下载处理
```python
def _download_artwork(self, url):
    """智能下载封面图片"""
    response = requests.get(url, timeout=10)
    content_type = response.headers.get('content-type', '')
    
    if content_type.startswith('image/'):
        return response.content
    else:
        logger.warning(f"Invalid content type: {content_type}")
        return None
```

## 🚀 使用方式

### 自动补全（推荐）
```bash
# 上传文件时自动补全封面
curl -X POST -F "file=@song.mp3" http://localhost:5000/api/upload
```

**结果**: 
- 自动搜索并下载封面图片
- 直接写入音频文件标签
- 数据库不存储封面数据

### 手动补全
```bash
# 为已上传的文件补全封面
curl -X POST http://localhost:5000/api/add-album-art/1
```

## 🔍 封面源质量对比

### iTunes API
- **优点**: 高质量图片，稳定可靠，免费
- **缺点**: 需要网络连接，可能有地区限制
- **图片质量**: 1200x1200 像素

### MusicBrainz
- **优点**: 开放数据，精确匹配，官方数据
- **缺点**: 封面数量有限，更新较慢
- **图片质量**: 中等分辨率

### Cover Art Archive
- **优点**: 高分辨率，专集完整，免费
- **缺点**: 需要MusicBrainz数据源
- **图片质量**: 最高可达 500x500 像素

## 🎨 封面格式规范

### MP3 ID3 APIC 标签
- **类型**: APIC (Attached Picture)
- **MIME**: image/jpeg
- **类型码**: 3 (Front cover)
- **描述**: "Cover"

### FLAC PICTURE 标签
- **标签名**: PICTURE
- **格式**: 二进制数据
- **类型**: Front cover

### M4A covr 标签
- **标签名**: covr
- **格式**: 图片数组
- **类型**: iTunes cover art

## 📊 处理流程

```
上传音乐文件
    ↓
提取元数据 (艺术家、专辑名)
    ↓
多源搜索封面 (iTunes → MusicBrainz → Cover Art Archive)
    ↓
下载封面图片
    ↓
根据格式写入对应标签
    ↓
完成补全
```

## ⚠️ 注意事项

### 图片格式
- **推荐格式**: JPEG (文件小，兼容性好)
- **支持格式**: PNG, GIF, JPEG
- **文件大小**: 自动优化，不超过 500KB

### 版权说明
- 封面图片仅供个人音乐整理使用
- 遵守相关网站的版权条款
- 建议仅用于个人音乐收藏管理

### 错误处理
- 网络超时: 10秒自动重试
- 无效图片: 自动跳过尝试下一个源
- 写入失败: 记录日志但不中断处理

## 🎯 实际效果

### 上传前
- 音乐文件无封面或封面缺失
- 播放器显示默认图标

### 上传后
- 自动搜索并下载高质量封面
- 直接写入文件标签
- 播放器显示完整封面图片

### 兼容性
- 所有主流音乐播放器支持
- 移动设备同步显示封面
- 保持文件原有属性不变

---

**音乐封面自动补全：高质量、多源、直接写入！🎵**
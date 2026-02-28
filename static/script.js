class MusicScraperApp {
    constructor() {
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.loadStats();
        this.loadFiles();
    }

    setupEventListeners() {
        // File upload
        const dropZone = document.getElementById('dropZone');
        const fileInput = document.getElementById('fileInput');

        dropZone.addEventListener('click', () => fileInput.click());
        fileInput.addEventListener('change', (e) => this.handleFileSelect(e));

        // Drag and drop
        dropZone.addEventListener('dragover', (e) => {
            e.preventDefault();
            dropZone.classList.add('dragover');
        });

        dropZone.addEventListener('dragleave', () => {
            dropZone.classList.remove('dragover');
        });

        dropZone.addEventListener('drop', (e) => {
            e.preventDefault();
            dropZone.classList.remove('dragover');
            this.handleDrop(e);
        });

        // Search
        const searchInput = document.getElementById('searchInput');
        searchInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.searchMusic();
            }
        });
    }

    handleFileSelect(event) {
        const files = event.target.files;
        if (files.length > 0) {
            this.uploadFiles(files);
        }
    }

    handleDrop(event) {
        const files = event.dataTransfer.files;
        this.uploadFiles(files);
    }

    async uploadFiles(files) {
        const uploadProgress = document.getElementById('uploadProgress');
        const progressFill = document.getElementById('progressFill');
        const uploadStatus = document.getElementById('uploadStatus');

        uploadProgress.classList.remove('hidden');

        for (let i = 0; i < files.length; i++) {
            const file = files[i];
            const progress = ((i + 1) / files.length) * 100;
            
            progressFill.style.width = progress + '%';
            uploadStatus.textContent = `正在处理 ${file.name} (${Math.round(progress)}%)`;

            try {
                await this.uploadFile(file);
            } catch (error) {
                console.error('Upload error:', error);
                this.showNotification(`上传失败: ${file.name}`, 'error');
            }
        }

        uploadStatus.textContent = '处理完成！';
        setTimeout(() => {
            uploadProgress.classList.add('hidden');
            progressFill.style.width = '0%';
            this.loadFiles();
            this.loadStats();
        }, 2000);
    }

    async uploadFile(file) {
        const formData = new FormData();
        formData.append('file', file);

        const response = await fetch('/api/upload', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Upload failed');
        }

        const result = await response.json();
        this.showNotification(`${file.name} 上传成功`, 'success');
        return result;
    }

    async searchMusic() {
        const searchInput = document.getElementById('searchInput');
        const query = searchInput.value.trim();
        
        if (!query) {
            this.showNotification('请输入搜索关键词', 'error');
            return;
        }

        const searchResults = document.getElementById('searchResults');
        searchResults.innerHTML = '<p>搜索中...</p>';

        try {
            const response = await fetch(`/api/search?q=${encodeURIComponent(query)}`);
            const data = await response.json();

            if (data.success) {
                this.displaySearchResults(data.results);
            } else {
                searchResults.innerHTML = '<p>搜索失败</p>';
                this.showNotification(data.error, 'error');
            }
        } catch (error) {
            searchResults.innerHTML = '<p>搜索失败</p>';
            this.showNotification('网络错误', 'error');
        }
    }

    displaySearchResults(results) {
        const searchResults = document.getElementById('searchResults');
        
        if (results.length === 0) {
            searchResults.innerHTML = '<p>没有找到相关音乐文件</p>';
            return;
        }

        const html = results.map(file => `
            <div class="file-item">
                <h4>${file.title || '未知标题'}</h4>
                <p><strong>艺术家:</strong> ${file.artist || '未知'}</p>
                <p><strong>专辑:</strong> ${file.album || '未知'}</p>
                <p class="meta-info">
                    <strong>文件:</strong> ${file.file_name} | 
                    <strong>格式:</strong> ${file.format} | 
                    <strong>大小:</strong> ${this.formatFileSize(file.file_size)}
                </p>
            </div>
        `).join('');

        searchResults.innerHTML = html;
    }

    async loadFiles() {
        const filesList = document.getElementById('filesList');
        filesList.innerHTML = '<p>加载中...</p>';

        try {
            const response = await fetch('/api/files');
            const data = await response.json();

            if (data.success) {
                this.displayFiles(data.files);
                document.getElementById('fileCount').textContent = `总计: ${data.total} 个文件`;
            } else {
                filesList.innerHTML = '<p>加载失败</p>';
                this.showNotification(data.error, 'error');
            }
        } catch (error) {
            filesList.innerHTML = '<p>加载失败</p>';
            this.showNotification('网络错误', 'error');
        }
    }

    displayFiles(files) {
        const filesList = document.getElementById('filesList');
        
        if (files.length === 0) {
            filesList.innerHTML = '<p>还没有音乐文件，请上传文件开始</p>';
            return;
        }

        const html = files.map(file => `
            <div class="file-item">
                <h4>${file.title || '未知标题'}</h4>
                <p><strong>艺术家:</strong> ${file.artist || '未知'}</p>
                <p><strong>专辑:</strong> ${file.album || '未知'}</p>
                <p class="meta-info">
                    <strong>文件:</strong> ${file.file_name} | 
                    <strong>格式:</strong> ${file.format} | 
                    <strong>大小:</strong> ${this.formatFileSize(file.file_size)} | 
                    <strong>时长:</strong> ${this.formatDuration(file.duration)}
                </p>
                <p class="meta-info">
                    <strong>处理时间:</strong> ${new Date(file.processed_at).toLocaleString()}
                </p>
            </div>
        `).join('');

        filesList.innerHTML = html;
    }

    async loadStats() {
        try {
            const response = await fetch('/api/stats');
            const data = await response.json();

            if (data.success) {
                document.getElementById('totalFiles').textContent = data.total_files;
            }
        } catch (error) {
            console.error('Failed to load stats:', error);
        }
    }

    showScanFolder() {
        const modal = document.getElementById('scanModal');
        modal.classList.remove('hidden');
    }

    closeScanModal() {
        const modal = document.getElementById('scanModal');
        modal.classList.add('hidden');
        document.getElementById('folderPath').value = '';
        document.getElementById('scanProgress').classList.add('hidden');
    }

    async scanFolder() {
        const folderPath = document.getElementById('folderPath').value.trim();
        
        if (!folderPath) {
            this.showNotification('请输入文件夹路径', 'error');
            return;
        }

        const scanProgress = document.getElementById('scanProgress');
        const scanProgressFill = document.getElementById('scanProgressFill');
        const scanStatus = document.getElementById('scanStatus');

        scanProgress.classList.remove('hidden');

        try {
            const response = await fetch('/api/scan-folder', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ folder_path: folderPath })
            });

            const data = await response.json();

            if (data.success) {
                scanStatus.textContent = `扫描完成: 找到 ${data.processed} 个文件`;
                this.showNotification(data.message, 'success');
                this.loadFiles();
                this.loadStats();
                setTimeout(() => this.closeScanModal(), 3000);
            } else {
                scanStatus.textContent = '扫描失败';
                this.showNotification(data.error, 'error');
            }
        } catch (error) {
            scanStatus.textContent = '扫描失败';
            this.showNotification('网络错误', 'error');
        }
    }

    formatFileSize(bytes) {
        if (bytes === 0) return '0 B';
        const k = 1024;
        const sizes = ['B', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    formatDuration(seconds) {
        if (!seconds) return '未知';
        const minutes = Math.floor(seconds / 60);
        const remainingSeconds = Math.floor(seconds % 60);
        return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
    }

    showNotification(message, type = 'info') {
        // Remove existing notification
        const existing = document.querySelector('.notification');
        if (existing) {
            existing.remove();
        }

        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.textContent = message;
        document.body.appendChild(notification);

        // Show notification
        setTimeout(() => notification.classList.add('show'), 100);

        // Hide notification after 3 seconds
        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => notification.remove(), 300);
        }, 3000);
    }
}

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new MusicScraperApp();
});
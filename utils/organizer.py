import os
import logging
import threading
import time
from typing import Dict, List
import sqlite3
from .database import Database
from .metadata import MetadataExtractor
from .scraper import MusicScraper

logger = logging.getLogger(__name__)

class MusicOrganizer:
    """音乐整理核心类"""
    
    def __init__(self, db_path="music_metadata.db"):
        self.db = Database(db_path)
        self.metadata_extractor = MetadataExtractor()
        self.scraper = MusicScraper()
        self.running = False
        self.tasks = []
        
        # Add processing status column to music_files table if not exists
        self._ensure_processing_status_column()
        
    def scan_directory(self, directory: str, recursive: bool = True):
        """扫描目录中的音乐文件"""
        try:
            logger.info(f"开始扫描目录: {directory}")
            found_files = []
            
            if recursive:
                for root, dirs, files in os.walk(directory):
                    for file in files:
                        if self._is_music_file(file):
                            file_path = os.path.join(root, file)
                            found_files.append(file_path)
            else:
                for file in os.listdir(directory):
                    if self._is_music_file(file):
                        file_path = os.path.join(directory, file)
                        found_files.append(file_path)
            
            logger.info(f"找到 {len(found_files)} 个音乐文件")
            return found_files
            
        except Exception as e:
            logger.error(f"扫描目录时出错: {str(e)}")
            return []
    
    def _is_music_file(self, filename: str) -> bool:
        """检查文件是否为音乐文件"""
        ext = os.path.splitext(filename)[1].lower()
        return ext in ('.mp3', '.flac', '.m4a', '.ogg', '.wav')
    
    def process_file(self, file_path: str):
        """处理单个音乐文件"""
        try:
            # 更新状态为处理中
            file_id = self.db.get_file_by_path(file_path)
            if file_id:
                self.db.update_music_file(file_id, {'processing_status': 'processing'})
            
            # 提取元数据
            metadata = self.metadata_extractor.extract_metadata(file_path)
            
            # 搜索并添加歌词
            lyrics_added = False
            if metadata.get('artist') and metadata.get('title'):
                lyrics_result = self.scraper.search_lyrics(metadata['artist'], metadata['title'])
                if lyrics_result.get('found'):
                    self.metadata_extractor.write_lyrics_to_file(file_path, lyrics_result['lyrics'], 'web')
                    lyrics_added = True
                    logger.info(f"歌词已添加到 {file_path}")
            
            # 搜索并添加封面
            album_art_added = False
            if metadata.get('artist') and metadata.get('album'):
                artwork_result = self.scraper.search_album_art(metadata['artist'], metadata['album'])
                if artwork_result.get('found'):
                    artwork_data = self.metadata_extractor._download_artwork(artwork_result['url'])
                    if artwork_data:
                        success = self.metadata_extractor.write_album_art(file_path, artwork_result['url'], artwork_data)
                        if success:
                            album_art_added = True
                            logger.info(f"封面已添加到 {file_path}")
            
            # 保存到数据库
            file_info = self.metadata_extractor.get_file_info(file_path)
            file_id = self.db.add_music_file(file_info)
            self.db.add_metadata(file_id, metadata)
            
            # 更新状态为已完成
            self.db.update_music_file(file_id, {
                'processing_status': 'completed',
                'processed_at': time.strftime('%Y-%m-%d %H:%M:%S')
            })
            
            return {
                'file_path': file_path,
                'file_id': file_id,
                'lyrics_added': lyrics_added,
                'album_art_added': album_art_added,
                'success': True
            }
            
        except Exception as e:
            logger.error(f"处理文件 {file_path} 时出错: {str(e)}")
            
            # 更新状态为失败
            file_id = self.db.get_file_by_path(file_path)
            if file_id:
                self.db.update_music_file(file_id, {'processing_status': 'failed'})
            
            return {
                'file_path': file_path,
                'success': False,
                'error': str(e)
            }
    
    def batch_process_files(self, file_paths: List[str], max_workers: int = 4):
        """批量处理音乐文件"""
        try:
            self.running = True
            results = []
            processed_count = 0
            success_count = 0
            error_count = 0
            
            # 使用线程池进行并行处理
            def process_file_wrapper(file_path):
                nonlocal processed_count, success_count, error_count
                
                if not self.running:
                    return
                
                result = self.process_file(file_path)
                results.append(result)
                
                if result['success']:
                    success_count += 1
                else:
                    error_count += 1
                
                processed_count += 1
                logger.info(f"进度: {processed_count}/{len(file_paths)} (成功: {success_count}, 失败: {error_count})")
            
            # 简单的线程池实现
            import threading
            
            threads = []
            for i, file_path in enumerate(file_paths):
                if not self.running:
                    break
                
                # 创建线程处理文件
                thread = threading.Thread(
                    target=process_file_wrapper,
                    args=(file_path,)
                )
                threads.append(thread)
                thread.start()
                
                # 控制并发线程数
                if len(threads) >= max_workers:
                    for t in threads:
                        t.join()
                    threads = []
                
                # 添加延迟以避免服务器过载
                time.sleep(0.1)
            
            # 等待剩余线程完成
            for thread in threads:
                thread.join()
            
            return {
                'total_files': len(file_paths),
                'processed_files': processed_count,
                'success_files': success_count,
                'error_files': error_count,
                'results': results
            }
            
        except Exception as e:
            logger.error(f"批量处理时出错: {str(e)}")
            return {
                'total_files': len(file_paths),
                'processed_files': 0,
                'success_files': 0,
                'error_files': 0,
                'results': [],
                'error': str(e)
            }
    
    def organize_by_artist(self, target_directory: str):
        """按艺术家整理音乐文件"""
        try:
            logger.info(f"开始按艺术家整理到: {target_directory}")
            
            # 获取所有按艺术家分组的文件
            files_by_artist = self.db.get_files_grouped_by_artist()
            
            organized_count = 0
            for artist, files in files_by_artist.items():
                if not artist:
                    artist = "未知艺术家"
                
                artist_dir = os.path.join(target_directory, artist)
                os.makedirs(artist_dir, exist_ok=True)
                
                for file_info in files:
                    try:
                        source_path = file_info['file_path']
                        dest_path = os.path.join(artist_dir, os.path.basename(source_path))
                        
                        if source_path != dest_path:
                            os.rename(source_path, dest_path)
                            organized_count += 1
                            
                            # 更新数据库中的路径
                            file_id = file_info['id']
                            self.db.update_music_file(file_id, {'file_path': dest_path})
                            
                    except Exception as e:
                        logger.error(f"整理文件时出错: {str(e)}")
            
            logger.info(f"完成整理，共移动了 {organized_count} 个文件")
            return {
                'success': True,
                'organized_files': organized_count,
                'message': f"完成整理，共移动了 {organized_count} 个文件"
            }
            
        except Exception as e:
            logger.error(f"按艺术家整理时出错: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def organize_by_album(self, target_directory: str):
        """按专辑整理音乐文件"""
        try:
            logger.info(f"开始按专辑整理到: {target_directory}")
            
            # 获取所有按专辑分组的文件
            files_by_album = self.db.get_files_grouped_by_album()
            
            organized_count = 0
            for album, files in files_by_album.items():
                if not album:
                    album = "未知专辑"
                
                album_dir = os.path.join(target_directory, album)
                os.makedirs(album_dir, exist_ok=True)
                
                for file_info in files:
                    try:
                        source_path = file_info['file_path']
                        dest_path = os.path.join(album_dir, os.path.basename(source_path))
                        
                        if source_path != dest_path:
                            os.rename(source_path, dest_path)
                            organized_count += 1
                            
                            # 更新数据库中的路径
                            file_id = file_info['id']
                            self.db.update_music_file(file_id, {'file_path': dest_path})
                            
                    except Exception as e:
                        logger.error(f"整理文件时出错: {str(e)}")
            
            logger.info(f"完成整理，共移动了 {organized_count} 个文件")
            return {
                'success': True,
                'organized_files': organized_count,
                'message': f"完成整理，共移动了 {organized_count} 个文件"
            }
            
        except Exception as e:
            logger.error(f"按专辑整理时出错: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def cleanup_duplicate_files(self):
        """清理重复文件"""
        try:
            logger.info("开始清理重复文件")
            
            # 基于文件名和文件大小查找重复文件
            duplicates = self.db.find_duplicate_files()
            removed_count = 0
            
            for group in duplicates:
                # 保留第一个文件，删除其余的
                for i, file_info in enumerate(group[1:]):  # 跳过第一个文件
                    try:
                        os.remove(file_info['file_path'])
                        removed_count += 1
                        
                        # 从数据库中删除
                        self.db.delete_music_file(file_info['id'])
                        
                        logger.info(f"删除重复文件: {file_info['file_path']}")
                        
                    except Exception as e:
                        logger.error(f"删除文件时出错: {str(e)}")
            
            logger.info(f"完成清理，共删除了 {removed_count} 个重复文件")
            return {
                'success': True,
                'removed_files': removed_count,
                'message': f"完成清理，共删除了 {removed_count} 个重复文件"
            }
            
        except Exception as e:
            logger.error(f"清理重复文件时出错: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_directory_stats(self, directory: str):
        """获取目录统计信息"""
        try:
            stats = {
                'total_files': 0,
                'total_size': 0,
                'files_by_format': {},
                'artists': set(),
                'albums': set(),
                'oldest_file': None,
                'newest_file': None
            }
            
            # 扫描目录
            for root, dirs, files in os.walk(directory):
                for file in files:
                    if self._is_music_file(file):
                        file_path = os.path.join(root, file)
                        stats['total_files'] += 1
                        
                        # 获取文件大小
                        file_size = os.path.getsize(file_path)
                        stats['total_size'] += file_size
                        
                        # 获取格式
                        ext = os.path.splitext(file)[1].lower()
                        stats['files_by_format'][ext] = stats['files_by_format'].get(ext, 0) + 1
                        
                        # 从数据库获取元数据
                        file_id = self.db.get_file_by_path(file_path)
                        if file_id:
                            metadata = self.db.get_metadata(file_id)
                            if metadata.get('artist'):
                                stats['artists'].add(metadata['artist'])
                            if metadata.get('album'):
                                stats['albums'].add(metadata['album'])
                        
                        # 更新最旧/最新文件
                        if not stats['oldest_file'] or os.path.getmtime(file_path) < os.path.getmtime(stats['oldest_file']):
                            stats['oldest_file'] = file_path
                        if not stats['newest_file'] or os.path.getmtime(file_path) > os.path.getmtime(stats['newest_file']):
                            stats['newest_file'] = file_path
            
            # 转换统计信息
            stats['artists'] = len(stats['artists'])
            stats['albums'] = len(stats['albums'])
            stats['total_size_mb'] = round(stats['total_size'] / (1024 * 1024), 2)
            
            return {
                'success': True,
                'stats': stats
            }
            
        except Exception as e:
            logger.error(f"获取目录统计时出错: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _ensure_processing_status_column(self):
        """Ensure processing_status column exists in music_files table"""
        try:
            with sqlite3.connect(self.db.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    PRAGMA table_info(music_files)
                ''')
                columns = [column[1] for column in cursor.fetchall()]
                
                if 'processing_status' not in columns:
                    cursor.execute('''
                        ALTER TABLE music_files ADD COLUMN processing_status TEXT DEFAULT 'pending'
                    ''')
                    conn.commit()
                    logger.info("Added processing_status column to music_files table")
                    
        except sqlite3.Error as e:
            logger.error(f"Error ensuring processing_status column: {str(e)}")
    
    def stop_processing(self):
        """停止处理"""
        self.running = False
        logger.info("已停止处理")
    
    def get_processing_progress(self):
        """获取处理进度"""
        try:
            return self.db.get_processing_stats()
        except Exception as e:
            logger.error(f"获取处理进度时出错: {str(e)}")
            return None
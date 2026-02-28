import sqlite3
import logging
import json
from datetime import datetime
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

class MusicDatabase:
    """Database operations for music metadata"""
    
    def __init__(self, db_path="music_metadata.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize database tables"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Create music_files table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS music_files (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        file_path TEXT UNIQUE NOT NULL,
                        file_name TEXT NOT NULL,
                        file_size INTEGER,
                        format TEXT,
                        duration REAL,
                        bitrate INTEGER,
                        created_at TEXT,
                        modified_at TEXT,
                        processed_at TEXT
                    )
                ''')
                
                # Create metadata table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS metadata (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        file_id INTEGER,
                        title TEXT,
                        artist TEXT,
                        album TEXT,
                        date TEXT,
                        genre TEXT,
                        album_artist TEXT,
                        composer TEXT,
                        track_number INTEGER,
                        total_tracks INTEGER,
                        disc_number INTEGER,
                        total_discs INTEGER,
                        FOREIGN KEY (file_id) REFERENCES music_files (id)
                    )
                ''')
                
                # Create web_results table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS web_results (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        file_id INTEGER,
                        source TEXT,
                        query TEXT,
                        results TEXT,  -- JSON stored as text
                        search_date TEXT,
                        FOREIGN KEY (file_id) REFERENCES music_files (id)
                    )
                ''')
                
                # Create indexes for better performance
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_music_files_path ON music_files(file_path)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_metadata_artist ON metadata(artist)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_metadata_title ON metadata(title)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_metadata_album ON metadata(album)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_web_results_file_id ON web_results(file_id)')
                
                conn.commit()
                
        except sqlite3.Error as e:
            logger.error(f"Database initialization error: {str(e)}")
            raise
    
    def add_music_file(self, file_info: Dict) -> int:
        """Add a music file to the database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT OR REPLACE INTO music_files 
                    (file_path, file_name, file_size, format, duration, bitrate, 
                     created_at, modified_at, processed_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    file_info.get('file_path'),
                    file_info.get('file_name'),
                    file_info.get('file_size'),
                    file_info.get('format'),
                    file_info.get('duration'),
                    file_info.get('bitrate'),
                    file_info.get('created_at'),
                    file_info.get('modified_at'),
                    datetime.now().isoformat()
                ))
                
                file_id = cursor.lastrowid
                conn.commit()
                
                return file_id
                
        except sqlite3.Error as e:
            logger.error(f"Error adding music file: {str(e)}")
            raise
    
    def add_metadata(self, file_id: int, metadata: Dict) -> int:
        """Add metadata for a music file"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT OR REPLACE INTO metadata 
                    (file_id, title, artist, album, date, genre, album_artist, 
                     composer, track_number, total_tracks, disc_number, total_discs,
                     lyrics, lyrics_source, lyrics_search_date)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    file_id,
                    metadata.get('title'),
                    metadata.get('artist'),
                    metadata.get('album'),
                    metadata.get('date'),
                    metadata.get('genre'),
                    metadata.get('album_artist'),
                    metadata.get('composer'),
                    metadata.get('track_number'),
                    metadata.get('total_tracks'),
                    metadata.get('disc_number'),
                    metadata.get('total_discs'),
                    metadata.get('lyrics'),
                    metadata.get('lyrics_source'),
                    metadata.get('lyrics_search_date')
                ))
                
                metadata_id = cursor.lastrowid
                conn.commit()
                
                return metadata_id
                
        except sqlite3.Error as e:
            logger.error(f"Error adding metadata: {str(e)}")
            raise
    
    def add_web_search_results(self, file_id: int, source: str, query: str, results: List[Dict]) -> int:
        """Add web search results to database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO web_results (file_id, source, query, results, search_date)
                    VALUES (?, ?, ?, ?, ?)
                ''', (
                    file_id,
                    source,
                    query,
                    json.dumps(results),
                    datetime.now().isoformat()
                ))
                
                result_id = cursor.lastrowid
                conn.commit()
                
                return result_id
                
        except sqlite3.Error as e:
            logger.error(f"Error adding web search results: {str(e)}")
            raise
    
    def get_file_info(self, file_path: str) -> Optional[Dict]:
        """Get file information by path"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT * FROM music_files WHERE file_path = ?
                ''', (file_path,))
                
                row = cursor.fetchone()
                if row:
                    columns = [desc[0] for desc in cursor.description]
                    return dict(zip(columns, row))
                
                return None
                
        except sqlite3.Error as e:
            logger.error(f"Error getting file info: {str(e)}")
            return None
    
    def get_all_files(self) -> List[Dict]:
        """Get all music files"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT mf.*, m.title, m.artist, m.album 
                    FROM music_files mf
                    LEFT JOIN metadata m ON mf.id = m.file_id
                    ORDER BY mf.processed_at DESC
                ''')
                
                rows = cursor.fetchall()
                if rows:
                    columns = [desc[0] for desc in cursor.description]
                    return [dict(zip(columns, row)) for row in rows]
                
                return []
                
        except sqlite3.Error as e:
            logger.error(f"Error getting all files: {str(e)}")
            return []
    
    def search_files(self, query: str) -> List[Dict]:
        """Search for files by title, artist, or album"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                sql = '''
                    SELECT mf.*, m.title, m.artist, m.album 
                    FROM music_files mf
                    LEFT JOIN metadata m ON mf.id = m.file_id
                    WHERE m.title LIKE ? OR m.artist LIKE ? OR m.album LIKE ?
                    ORDER BY m.title, m.artist, m.album
                '''
                
                search_term = f"%{query}%"
                cursor.execute(sql, (search_term, search_term, search_term))
                
                rows = cursor.fetchall()
                if rows:
                    columns = [desc[0] for desc in cursor.description]
                    return [dict(zip(columns, row)) for row in rows]
                
                return []
                
        except sqlite3.Error as e:
            logger.error(f"Error searching files: {str(e)}")
            return []
    
    def get_file_count(self) -> int:
        """Get total number of music files"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('SELECT COUNT(*) FROM music_files')
                return cursor.fetchone()[0]
                
        except sqlite3.Error as e:
            logger.error(f"Error getting file count: {str(e)}")
            return 0
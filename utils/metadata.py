import os
import logging
from mutagen import File
from mutagen.id3 import ID3, TIT2, TPE1, TALB, TDRC, TCON
from mutagen.mp4 import MP4, MP4Cover
import eyed3
from datetime import datetime

logger = logging.getLogger(__name__)

class MusicMetadataExtractor:
    """Extract metadata from music files"""
    
    def __init__(self):
        self.supported_formats = ['mp3', 'flac', 'm4a', 'ogg', 'wav']
    
    def extract_metadata(self, file_path):
        """Extract metadata from music file"""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        file_ext = os.path.splitext(file_path)[1].lower()[1:]
        
        if file_ext not in self.supported_formats:
            raise ValueError(f"Unsupported file format: {file_ext}")
        
        metadata = {
            'file_path': file_path,
            'file_name': os.path.basename(file_path),
            'file_size': os.path.getsize(file_path),
            'format': file_ext,
            'extracted_at': datetime.now().isoformat()
        }
        
        try:
            # Use mutagen for primary metadata extraction
            audio_file = File(file_path)
            
            if audio_file is not None:
                # Basic info
                metadata['duration'] = getattr(audio_file, 'length', 0)
                metadata['bitrate'] = getattr(audio_file, 'bitrate', 0)
                
                # Extract common tags
                if hasattr(audio_file, 'tags') and audio_file.tags:
                    self._extract_mutagen_tags(audio_file, metadata)
            
            # Use eyed3 for additional MP3 metadata
            if file_ext == 'mp3':
                self._extract_eyed3_metadata(file_path, metadata)
                
        except Exception as e:
            logger.error(f"Error extracting metadata from {file_path}: {str(e)}")
            metadata['extraction_error'] = str(e)
        
        return metadata
    
    def _extract_mutagen_tags(self, audio_file, metadata):
        """Extract tags using mutagen"""
        tag_map = {
            'title': ['TIT2', '\xa9nam'],
            'artist': ['TPE1', '\xa9ART'],
            'album': ['TALB', '\xa9alb'],
            'date': ['TDRC', '\xa9day'],
            'genre': ['TCON', '\xa9gen'],
            'albumartist': ['TPE2', 'aART'],
            'composer': ['TCOM', '\xa9wrt'],
        }
        
        for tag_name, mutagen_tags in tag_map.items():
            for mutagen_tag in mutagen_tags:
                if mutagen_tag in audio_file.tags:
                    value = audio_file.tags[mutagen_tag]
                    if hasattr(value, 'text'):
                        metadata[tag_name] = str(value.text[0])
                    else:
                        metadata[tag_name] = str(value)
                    break
    
    def _extract_eyed3_metadata(self, file_path, metadata):
        """Extract additional MP3 metadata using eyed3"""
        try:
            audiofile = eyed3.load(file_path)
            if audiofile and audiofile.tag:
                # Additional MP3-specific tags
                if audiofile.tag.album:
                    metadata['album'] = metadata.get('album', str(audiofile.tag.album))
                if audiofile.tag.artist:
                    metadata['artist'] = metadata.get('artist', str(audiofile.tag.artist))
                if audiofile.tag.title:
                    metadata['title'] = metadata.get('title', str(audiofile.tag.title))
                if audiofile.tag.genre:
                    metadata['genre'] = metadata.get('genre', str(audiofile.tag.genre))
                if audiofile.tag.recording_date:
                    metadata['date'] = metadata.get('date', str(audiofile.tag.recording_date))
                    
                # Additional info
                if audiofile.info:
                    metadata['bitrate'] = audiofile.info.bit_rate
                    metadata['duration'] = audiofile.info.time_seconds
                    
        except Exception as e:
            logger.error(f"Error extracting eyed3 metadata: {str(e)}")
    
    def get_file_info(self, file_path):
        """Get basic file information"""
        if not os.path.exists(file_path):
            return None
        
        stat = os.stat(file_path)
        return {
            'path': file_path,
            'name': os.path.basename(file_path),
            'size': stat.st_size,
            'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
            'created': datetime.fromtimestamp(stat.st_ctime).isoformat()
        }
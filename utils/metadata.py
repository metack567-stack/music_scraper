import os
import logging
from mutagen import File
from mutagen.id3 import ID3, TIT2, TPE1, TALB, TDRC, TCON, USLT, APIC
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
    
    def write_lyrics_to_file(self, file_path, lyrics):
        """Write lyrics to audio file tags"""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        try:
            file_ext = os.path.splitext(file_path)[1].lower()[1:]
            audio_file = File(file_path)
            
            if audio_file is None:
                raise ValueError(f"Unsupported audio format: {file_ext}")
            
            if file_ext == 'mp3':
                self._write_lyrics_mp3(file_path, lyrics)
            elif file_ext == 'flac':
                self._write_lyrics_flac(audio_file, lyrics)
            elif file_ext == 'm4a':
                self._write_lyrics_m4a(audio_file, lyrics)
            else:
                logger.warning(f"Lyrics writing not supported for format: {file_ext}")
                
            logger.info(f"Successfully wrote lyrics to {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error writing lyrics to {file_path}: {str(e)}")
            return False
    
    def _write_lyrics_mp3(self, file_path, lyrics):
        """Write lyrics to MP3 file using ID3 tags"""
        try:
            audiofile = eyed3.load(file_path)
            if audiofile is None:
                audiofile = eyed3.load(file_path)
                audiofile.initTag()
            
            if audiofile.tag:
                # Clear existing lyrics
                audiofile.tag.lyrics.set([])
                # Add new lyrics
                audiofile.tag.lyrics.set([lyrics])
                audiofile.tag.save()
            
            # Also use mutagen for compatibility
            audio_file = File(file_path)
            if isinstance(audio_file, ID3):
                audio_file.add(USLT(encoding=3, lang='eng', desc='Lyrics', text=lyrics))
                audio_file.save()
                
        except Exception as e:
            logger.error(f"Error writing lyrics to MP3: {str(e)}")
            raise
    
    def _write_lyrics_flac(self, audio_file, lyrics):
        """Write lyrics to FLAC file using Vorbis comments"""
        if hasattr(audio_file, 'tags') and audio_file.tags:
            audio_file.tags['LYRICS'] = lyrics
            audio_file.save()
    
    def _write_lyrics_m4a(self, audio_file, lyrics):
        """Write lyrics to M4A file using iTunes-style tags"""
        if hasattr(audio_file, 'tags') and audio_file.tags:
            # Use iTunes lyrics tag
            audio_file.tags['----:com.apple.iTunes:Lyrics'] = lyrics
            audio_file.save()
    
    def write_lyrics_to_file(self, file_path, lyrics, lyrics_source="web"):
        """Write lyrics to audio file tags"""
        try:
            if not os.path.exists(file_path):
                return False
            
            file_ext = os.path.splitext(file_path)[1].lower()[1:]
            audio_file = File(file_path)
            
            if audio_file is None:
                return False
            
            # Write lyrics based on file format
            if file_ext == 'mp3':
                return self._write_lyrics_to_mp3(file_path, lyrics, lyrics_source)
            elif file_ext == 'flac':
                return self._write_lyrics_to_flac(file_path, lyrics, lyrics_source)
            elif file_ext == 'm4a':
                return self._write_lyrics_to_m4a(file_path, lyrics, lyrics_source)
            elif file_ext == 'ogg':
                return self._write_lyrics_to_ogg(file_path, lyrics, lyrics_source)
            else:
                logger.warning(f"Unsupported format for lyrics writing: {file_ext}")
                return False
                
        except Exception as e:
            logger.error(f"Error writing lyrics to file: {str(e)}")
            return False
    
    def _write_lyrics_to_mp3(self, file_path, lyrics, source):
        """Write lyrics to MP3 file using ID3 tags"""
        try:
            audio_file = File(file_path)
            if isinstance(audio_file, ID3):
                # Add unsynchronized lyrics
                audio_file.add(USLT(encoding=3, lang='eng', desc=f'Lyrics ({source})', text=lyrics))
                audio_file.save()
                return True
            else:
                # Add ID3 tag if none exists
                audio_file.add_tags()
                audio_file.add(USLT(encoding=3, lang='eng', desc=f'Lyrics ({source})', text=lyrics))
                audio_file.save()
                return True
        except Exception as e:
            logger.error(f"Error writing lyrics to MP3: {str(e)}")
            return False
    
    def _write_lyrics_to_flac(self, file_path, lyrics, source):
        """Write lyrics to FLAC file"""
        try:
            audio_file = File(file_path)
            if hasattr(audio_file, 'tags') and audio_file.tags:
                audio_file.tags['LYRICS'] = lyrics
                audio_file.tags['LYRICSSOURCE'] = source
                audio_file.save()
                return True
        except Exception as e:
            logger.error(f"Error writing lyrics to FLAC: {str(e)}")
            return False
    
    def _write_lyrics_to_m4a(self, file_path, lyrics, source):
        """Write lyrics to M4A file"""
        try:
            audio_file = File(file_path)
            if hasattr(audio_file, 'tags') and audio_file.tags:
                # MP4 format uses custom tags
                audio_file.tags['----:com.apple.iTunes:Lyrics'] = lyrics
                audio_file.tags['----:com.apple.iTunes:LyricsSource'] = source
                audio_file.save()
                return True
        except Exception as e:
            logger.error(f"Error writing lyrics to M4A: {str(e)}")
            return False
    
    def _write_lyrics_to_ogg(self, file_path, lyrics, source):
        """Write lyrics to OGG file"""
        try:
            audio_file = File(file_path)
            if hasattr(audio_file, 'tags') and audio_file.tags:
                audio_file.tags['LYRICS'] = lyrics
                audio_file.tags['LYRICSSOURCE'] = source
                audio_file.save()
                return True
        except Exception as e:
            logger.error(f"Error writing lyrics to OGG: {str(e)}")
            return False
    
    def write_album_art(self, file_path, artwork_url, artwork_data=None):
        """Write album artwork to audio file"""
        try:
            if not os.path.exists(file_path):
                return False
            
            file_ext = os.path.splitext(file_path)[1].lower()[1:]
            
            # Download artwork if URL provided and no data available
            if artwork_url and not artwork_data:
                artwork_data = self._download_artwork(artwork_url)
                if not artwork_data:
                    return False
            
            if not artwork_data:
                return False
            
            # Write artwork based on file format
            if file_ext == 'mp3':
                return self._write_album_art_to_mp3(file_path, artwork_data)
            elif file_ext == 'flac':
                return self._write_album_art_to_flac(file_path, artwork_data)
            elif file_ext == 'm4a':
                return self._write_album_art_to_m4a(file_path, artwork_data)
            else:
                logger.warning(f"Unsupported format for album art: {file_ext}")
                return False
                
        except Exception as e:
            logger.error(f"Error writing album art to file: {str(e)}")
            return False
    
    def _download_artwork(self, url):
        """Download artwork from URL"""
        try:
            import requests
            
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            # Validate image
            content_type = response.headers.get('content-type', '')
            if content_type.startswith('image/'):
                return response.content
            else:
                logger.warning(f"Invalid content type: {content_type}")
                return None
                
        except Exception as e:
            logger.error(f"Error downloading artwork: {str(e)}")
            return None
    
    def _write_album_art_to_mp3(self, file_path, artwork_data):
        """Write album art to MP3 file using ID3 APIC tag"""
        try:
            audio_file = File(file_path)
            if isinstance(audio_file, ID3):
                # Remove existing album art
                audio_file.delall('APIC')
                
                # Add new album art
                audio_file.add(APIC(
                    encoding=3,
                    mime='image/jpeg',
                    type=3,  # 3 = front cover
                    desc='Cover',
                    data=artwork_data
                ))
                audio_file.save()
                return True
            else:
                # Add ID3 tag if none exists
                audio_file.add_tags()
                audio_file.add(APIC(
                    encoding=3,
                    mime='image/jpeg',
                    type=3,  # 3 = front cover
                    desc='Cover',
                    data=artwork_data
                ))
                audio_file.save()
                return True
        except Exception as e:
            logger.error(f"Error writing album art to MP3: {str(e)}")
            return False
    
    def _write_album_art_to_flac(self, file_path, artwork_data):
        """Write album art to FLAC file"""
        try:
            audio_file = File(file_path)
            if hasattr(audio_file, 'tags') and audio_file.tags:
                # Remove existing pictures
                if 'PICTURE' in audio_file.tags:
                    del audio_file.tags['PICTURE']
                
                # Add new picture
                audio_file.tags['PICTURE'] = artwork_data
                audio_file.save()
                return True
        except Exception as e:
            logger.error(f"Error writing album art to FLAC: {str(e)}")
            return False
    
    def _write_album_art_to_m4a(self, file_path, artwork_data):
        """Write album art to M4A file"""
        try:
            audio_file = File(file_path)
            if hasattr(audio_file, 'tags') and audio_file.tags:
                # Remove existing artwork
                keys_to_remove = [k for k in audio_file.tags.keys() if k.startswith('covr')]
                for key in keys_to_remove:
                    del audio_file.tags[key]
                
                # Add new artwork
                audio_file.tags['covr'] = [artwork_data]
                audio_file.save()
                return True
        except Exception as e:
            logger.error(f"Error writing album art to M4A: {str(e)}")
            return False
    
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
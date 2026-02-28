import os

class Config:
    # Application settings
    SECRET_KEY = 'your-secret-key-here'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    
    # Database settings
    DATABASE_PATH = 'music_metadata.db'
    
    # Upload settings
    UPLOAD_FOLDER = 'uploads'
    ALLOWED_EXTENSIONS = {'mp3', 'flac', 'm4a', 'ogg', 'wav'}
    
    # Music metadata sources
    MUSIC_BRAINZ_API = 'https://musicbrainz.org/ws/2/'
    LASTFM_API_KEY = os.environ.get('LASTFM_API_KEY', '')
    SPOTIFY_API_KEY = os.environ.get('SPOTIFY_API_KEY', '')
    
    # Web scraping settings
    TIMEOUT = 30
    RETRY_COUNT = 3

def allowed_file(filename):
    """Check if file has allowed extension"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS
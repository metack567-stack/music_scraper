import os
import logging
from flask import Flask, render_template, request, jsonify, flash, redirect, url_for
from werkzeug.utils import secure_filename
import json
from datetime import datetime

# Import our modules
from config import Config, allowed_file
from utils.metadata import MusicMetadataExtractor
from utils.organizer import MusicOrganizer
from utils.scraper import MusicScraper
from utils.database import MusicDatabase
from utils.organizer import MusicOrganizer

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config.from_object(Config)

# Initialize components
metadata_extractor = MusicMetadataExtractor()
scraper = MusicScraper()
db = MusicDatabase(app.config['DATABASE_PATH'])

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize organizer
organizer = MusicOrganizer(app.config['DATABASE_PATH'])

@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """Handle file upload"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            
            # Extract metadata
            metadata = metadata_extractor.extract_metadata(file_path)
            
            # Search for lyrics and write directly to file
            lyrics_added = False
            if metadata.get('artist') and metadata.get('title'):
                lyrics_result = scraper.search_lyrics(metadata['artist'], metadata['title'])
                if lyrics_result.get('found'):
                    # Write lyrics directly to audio file (no database storage)
                    metadata_extractor.write_lyrics_to_file(file_path, lyrics_result['lyrics'], 'web')
                    lyrics_added = True
                    logger.info(f"Lyrics added to {file_path} from {lyrics_result['source']}")
            
            # Search for album artwork and write directly to file
            album_art_added = False
            if metadata.get('artist') and metadata.get('album'):
                artwork_result = scraper.search_album_art(metadata['artist'], metadata['album'])
                if artwork_result.get('found'):
                    # Download and write album art directly to file
                    artwork_data = metadata_extractor._download_artwork(artwork_result['url'])
                    if artwork_data:
                        success = metadata_extractor.write_album_art(file_path, artwork_result['url'], artwork_data)
                        if success:
                            album_art_added = True
                            logger.info(f"Album art added to {file_path} from {artwork_result['source']}")
            
            # Store in database (without lyrics or album art)
            file_id = db.add_music_file(metadata_extractor.get_file_info(file_path))
            db.add_metadata(file_id, metadata)
            
            # Search for additional metadata
            if metadata.get('artist') and metadata.get('title'):
                search_results = scraper.search_musicbrainz(
                    metadata.get('artist', ''), 
                    metadata.get('title', '')
                )
                if search_results:
                    db.add_web_search_results(file_id, 'musicbrainz', 
                                            f"{metadata.get('artist')} {metadata.get('title')}", 
                                            search_results)
            
            return jsonify({
                'success': True,
                'file_id': file_id,
                'metadata': metadata,
                'message': 'File uploaded and processed successfully',
                'lyrics_added': lyrics_added,
                'album_art_added': album_art_added,
                'lyrics_source': 'web' if lyrics_added else None,
                'album_art_source': 'web' if album_art_added else None
            })
        
        return jsonify({'error': 'Invalid file type'}), 400
        
    except Exception as e:
        logger.error(f"Upload error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/search')
def search_files():
    """Search for music files"""
    try:
        query = request.args.get('q', '')
        if not query:
            return jsonify({'error': 'Search query required'}), 400
        
        results = db.search_files(query)
        return jsonify({
            'success': True,
            'results': results,
            'total': len(results)
        })
        
    except Exception as e:
        logger.error(f"Search error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/files')
def get_files():
    """Get all music files"""
    try:
        files = db.get_all_files()
        return jsonify({
            'success': True,
            'files': files,
            'total': len(files)
        })
        
    except Exception as e:
        logger.error(f"Get files error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/files/<int:file_id>')
def get_file(file_id):
    """Get specific file information"""
    try:
        # This would need to be implemented in the database class
        return jsonify({'error': 'Not implemented'}), 500
        
    except Exception as e:
        logger.error(f"Get file error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/stats')
def get_stats():
    """Get application statistics"""
    try:
        total_files = db.get_file_count()
        
        # Get processing progress if organizer is available
        processing_progress = None
        try:
            organizer = MusicOrganizer()
            processing_progress = organizer.get_processing_progress()
        except:
            pass
        
        return jsonify({
            'success': True,
            'total_files': total_files,
            'supported_formats': list(Config.ALLOWED_EXTENSIONS),
            'database_path': app.config['DATABASE_PATH'],
            'upload_folder': app.config['UPLOAD_FOLDER'],
            'processing_progress': processing_progress
        })
        
    except Exception as e:
        logger.error(f"Stats error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/scan-folder', methods=['POST'])
def scan_folder():
    """Scan a folder for music files"""
    try:
        data = request.get_json()
        folder_path = data.get('folder_path')
        
        if not folder_path or not os.path.exists(folder_path):
            return jsonify({'error': 'Invalid folder path'}), 400
        
        found_files = []
        scanned_count = 0
        processed_count = 0
        
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                if allowed_file(file):
                    scanned_count += 1
                    file_path = os.path.join(root, file)
                    
                    try:
                        # Extract metadata
                        metadata = metadata_extractor.extract_metadata(file_path)
                        
                        # Store in database
                        file_info = metadata_extractor.get_file_info(file_path)
                        file_id = db.add_music_file(file_info)
                        db.add_metadata(file_id, metadata)
                        
                        found_files.append({
                            'file_path': file_path,
                            'filename': file,
                            'file_id': file_id
                        })
                        
                        processed_count += 1
                        
                    except Exception as e:
                        logger.error(f"Error processing {file_path}: {str(e)}")
                        continue
        
        return jsonify({
            'success': True,
            'scanned': scanned_count,
            'processed': processed_count,
            'found_files': found_files,
            'message': f'Scan completed. Found {processed_count} of {scanned_count} files.'
        })
        
    except Exception as e:
        logger.error(f"Scan folder error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/cleanup')
def cleanup_database():
    """Clean up database entries"""
    try:
        # This would need to be implemented
        return jsonify({'error': 'Not implemented'}), 500
        
    except Exception as e:
        logger.error(f"Cleanup error: {str(e)}")
        return jsonify({'error': str(e)}), 500

# Music Organization Routes
@app.route('/api/organizer/scan-directory', methods=['POST'])
def scan_directory():
    """Scan a directory for music files"""
    try:
        data = request.get_json()
        directory = data.get('directory', '')
        recursive = data.get('recursive', True)
        
        if not directory:
            return jsonify({'error': 'Directory path is required'}), 400
        
        if not os.path.exists(directory):
            return jsonify({'error': 'Directory does not exist'}), 400
        
        # Scan directory
        organizer = MusicOrganizer()
        found_files = organizer.scan_directory(directory, recursive)
        
        return jsonify({
            'success': True,
            'found_files': len(found_files),
            'files': found_files,
            'message': f'Found {len(found_files)} music files'
        })
        
    except Exception as e:
        logger.error(f"Scan directory error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/organizer/process-files', methods=['POST'])
def process_files():
    """Process multiple music files"""
    try:
        data = request.get_json()
        file_paths = data.get('files', [])
        max_workers = data.get('max_workers', 4)
        
        if not file_paths:
            return jsonify({'error': 'No files to process'}), 400
        
        # Process files
        organizer = MusicOrganizer()
        results = organizer.batch_process_files(file_paths, max_workers)
        
        return jsonify({
            'success': True,
            **results,
            'message': f'Processed {results["processed_files"]} files'
        })
        
    except Exception as e:
        logger.error(f"Process files error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/organizer/organize-by-artist', methods=['POST'])
def organize_by_artist():
    """Organize music files by artist"""
    try:
        data = request.get_json()
        target_directory = data.get('target_directory', '/tmp/organized_music')
        
        if not target_directory:
            return jsonify({'error': 'Target directory is required'}), 400
        
        # Create target directory if it doesn't exist
        os.makedirs(target_directory, exist_ok=True)
        
        # Organize files
        organizer = MusicOrganizer()
        result = organizer.organize_by_artist(target_directory)
        
        return jsonify({
            'success': True,
            **result
        })
        
    except Exception as e:
        logger.error(f"Organize by artist error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/organizer/organize-by-album', methods=['POST'])
def organize_by_album():
    """Organize music files by album"""
    try:
        data = request.get_json()
        target_directory = data.get('target_directory', '/tmp/organized_music')
        
        if not target_directory:
            return jsonify({'error': 'Target directory is required'}), 400
        
        # Create target directory if it doesn't exist
        os.makedirs(target_directory, exist_ok=True)
        
        # Organize files
        organizer = MusicOrganizer()
        result = organizer.organize_by_album(target_directory)
        
        return jsonify({
            'success': True,
            **result
        })
        
    except Exception as e:
        logger.error(f"Organize by album error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/organizer/cleanup-duplicates', methods=['POST'])
def cleanup_duplicates():
    """Clean up duplicate files"""
    try:
        # Clean up duplicates
        organizer = MusicOrganizer()
        result = organizer.cleanup_duplicate_files()
        
        return jsonify({
            'success': True,
            **result
        })
        
    except Exception as e:
        logger.error(f"Cleanup duplicates error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/organizer/directory-stats', methods=['POST'])
def directory_stats():
    """Get directory statistics"""
    try:
        data = request.get_json()
        directory = data.get('directory', '')
        
        if not directory:
            return jsonify({'error': 'Directory is required'}), 400
        
        if not os.path.exists(directory):
            return jsonify({'error': 'Directory does not exist'}), 400
        
        # Get directory statistics
        organizer = MusicOrganizer()
        result = organizer.get_directory_stats(directory)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Directory stats error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/organizer/progress')
def get_progress():
    """Get processing progress"""
    try:
        organizer = MusicOrganizer()
        progress = organizer.get_processing_progress()
        
        return jsonify({
            'success': True,
            'progress': progress
        })
        
    except Exception as e:
        logger.error(f"Get progress error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/add-lyrics/<int:file_id>', methods=['POST'])
def add_lyrics(file_id):
    """Add lyrics directly to a specific file - no database storage"""
    try:
        # Get file info to update the file
        file_info = db.get_music_file(file_id)
        if not file_info:
            return jsonify({'error': 'File not found'}), 404
        
        # Extract existing metadata to get artist and title
        metadata = db.get_metadata(file_id)
        if not metadata:
            return jsonify({'error': 'Metadata not found'}), 404
        
        artist = metadata.get('artist', '')
        title = metadata.get('title', '')
        
        if not artist or not title:
            return jsonify({'error': 'Artist or title not available'}), 400
        
        # Search for lyrics
        lyrics_result = scraper.search_lyrics(artist, title)
        
        if lyrics_result.get('found'):
            # Write lyrics directly to file (no database storage)
            success = metadata_extractor.write_lyrics_to_file(file_info['file_path'], lyrics_result['lyrics'], 'web')
            
            if success:
                logger.info(f"Lyrics added to {file_info['file_path']} from {lyrics_result['source']}")
                return jsonify({
                    'success': True,
                    'source': lyrics_result['source'],
                    'message': f'Lyrics added from {lyrics_result["source"]}'
                })
            else:
                return jsonify({
                    'success': False,
                    'message': 'Failed to write lyrics to file'
                })
        else:
            return jsonify({
                'success': False,
                'message': 'No lyrics found for this song'
            })
        
    except Exception as e:
        logger.error(f"Lyrics add error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/add-album-art/<int:file_id>', methods=['POST'])
def add_album_art(file_id):
    """Add album artwork directly to a specific file - no database storage"""
    try:
        # Get file info to update the file
        file_info = db.get_music_file(file_id)
        if not file_info:
            return jsonify({'error': 'File not found'}), 404
        
        # Extract existing metadata to get artist and album
        metadata = db.get_metadata(file_id)
        if not metadata:
            return jsonify({'error': 'Metadata not found'}), 404
        
        artist = metadata.get('artist', '')
        album = metadata.get('album', '')
        
        if not artist or not album:
            return jsonify({'error': 'Artist or album not available'}), 400
        
        # Search for album artwork
        artwork_result = scraper.search_album_art(artist, album)
        
        if artwork_result.get('found'):
            # Download and write album art directly to file
            artwork_data = metadata_extractor._download_artwork(artwork_result['url'])
            if artwork_data:
                success = metadata_extractor.write_album_art(file_info['file_path'], artwork_result['url'], artwork_data)
                
                if success:
                    logger.info(f"Album art added to {file_info['file_path']} from {artwork_result['source']}")
                    return jsonify({
                        'success': True,
                        'source': artwork_result['source'],
                        'message': f'Album art added from {artwork_result["source"]}'
                    })
                else:
                    return jsonify({
                        'success': False,
                        'message': 'Failed to write album art to file'
                    })
            else:
                return jsonify({
                    'success': False,
                    'message': 'Failed to download album art'
                })
        else:
            return jsonify({
                'success': False,
                'message': 'No album art found for this album'
            })
        
    except Exception as e:
        logger.error(f"Album art add error: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
import os
import logging
from flask import Flask, render_template, request, jsonify, flash, redirect, url_for
from werkzeug.utils import secure_filename
import json
from datetime import datetime

# Import our modules
from config import Config, allowed_file
from utils.metadata import MusicMetadataExtractor
from utils.scraper import MusicScraper
from utils.database import MusicDatabase

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
            
            # Search for lyrics
            if metadata.get('artist') and metadata.get('title'):
                lyrics_result = scraper.search_lyrics(metadata['artist'], metadata['title'])
                if lyrics_result.get('found'):
                    metadata['lyrics'] = lyrics_result['lyrics']
                    metadata['lyrics_source'] = lyrics_result['source']
                    metadata['lyrics_search_date'] = datetime.now().isoformat()
                    
                    # Write lyrics to audio file
                    metadata_extractor.write_lyrics_to_file(file_path, metadata['lyrics'], metadata['lyrics_source'])
            
            # Store in database
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
                'lyrics_found': bool(metadata.get('lyrics')),
                'lyrics_source': metadata.get('lyrics_source')
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
        
        return jsonify({
            'success': True,
            'total_files': total_files,
            'supported_formats': list(Config.ALLOWED_EXTENSIONS),
            'database_path': app.config['DATABASE_PATH'],
            'upload_folder': app.config['UPLOAD_FOLDER']
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

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
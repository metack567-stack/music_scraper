import requests
import logging
from bs4 import BeautifulSoup
import json
import time
from urllib.parse import quote

logger = logging.getLogger(__name__)

class MusicScraper:
    """Web scraping for music metadata"""
    
    def __init__(self, api_key=None):
        self.api_key = api_key
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'MusicScraper/1.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
        })
    
    def search_musicbrainz(self, artist, title, limit=5):
        """Search MusicBrainz for music metadata"""
        try:
            base_url = "https://musicbrainz.org/ws/2/recording/"
            
            # Search query
            query = f"artist:\"{artist}\" recording:\"{title}\""
            params = {
                'query': query,
                'limit': limit,
                'fmt': 'json'
            }
            
            response = self.session.get(base_url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            recordings = data.get('recordings', [])
            
            results = []
            for recording in recordings:
                result = {
                    'title': recording.get('title', ''),
                    'artist': self._get_artist_name(recording),
                    'album': self._get_album_name(recording),
                    'date': self._get_release_date(recording),
                    'genre': self._get_genre(recording),
                    'musicbrainz_id': recording.get('id', ''),
                    'score': recording.get('score', 0)
                }
                results.append(result)
            
            return results
            
        except requests.exceptions.RequestException as e:
            logger.error(f"MusicBrainz search error: {str(e)}")
            return []
    
    def _get_artist_name(self, recording):
        """Extract artist name from recording"""
        try:
            for artist_credit in recording.get('artist-credit', []):
                if 'artist' in artist_credit:
                    return artist_credit['artist'].get('name', '')
        except:
            pass
        return ''
    
    def _get_album_name(self, recording):
        """Extract album name from recording"""
        try:
            for release in recording.get('releases', []):
                return release.get('title', '')
        except:
            pass
        return ''
    
    def _get_release_date(self, recording):
        """Extract release date from recording"""
        try:
            for release in recording.get('releases', []):
                if 'date' in release:
                    return release['date']
        except:
            pass
        return ''
    
    def _get_genre(self, recording):
        """Extract genre from recording"""
        try:
            for release in recording.get('releases', []):
                for tag in release.get('tags', []):
                    if tag.get('name') and tag.get('count', 0) > 0:
                        return tag['name']
        except:
            pass
        return ''
    
    def search_lyrics(self, artist, title):
        """Search for lyrics (be careful with copyright)"""
        try:
            # Note: This is for educational purposes only
            lyrics_sites = [
                f"https://www.azlyrics.com/lyrics/{self._clean_artist(artist)}/{self._clean_title(title)}.html",
                f"https://genius.com/{self._clean_artist(artist)}-{self._clean_title(title)}-lyrics"
            ]
            
            for site in lyrics_sites:
                try:
                    response = self.session.get(site, timeout=5)
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.text, 'html.parser')
                        lyrics = self._extract_lyrics(soup)
                        if lyrics:
                            return {
                                'source': site,
                                'lyrics': lyrics,
                                'found': True
                            }
                except:
                    continue
            
            return {'source': None, 'lyrics': None, 'found': False}
            
        except Exception as e:
            logger.error(f"Lyrics search error: {str(e)}")
            return {'source': None, 'lyrics': None, 'found': False}
    
    def _clean_artist(self, artist):
        """Clean artist name for URL"""
        return artist.replace(' ', '-').lower().replace('\'', '').replace('&', 'and')
    
    def _clean_title(self, title):
        """Clean title for URL"""
        return title.replace(' ', '-').lower().replace('\'', '').replace('(', '').replace(')', '')
    
    def _extract_lyrics(self, soup):
        """Extract lyrics from HTML (basic implementation)"""
        try:
            # Try to find lyrics in common containers
            selectors = [
                'div.lyrics', 'div#lyrics', 'div.song-lyrics',
                'div[role="main"]', 'div[data-lyrics-container="true"]'
            ]
            
            for selector in selectors:
                element = soup.select_one(selector)
                if element:
                    text = element.get_text(strip=True)
                    if len(text) > 100:  # Reasonable length for lyrics
                        return text
            
            return None
            
        except Exception as e:
            logger.error(f"Error extracting lyrics: {str(e)}")
            return None
    
    def search_album_art(self, artist, album):
        """Search for album artwork using multiple sources"""
        try:
            # Clean input
            clean_artist = self._clean_artist(artist)
            clean_album = self._clean_album(album)
            
            # Try different sources in order
            sources = [
                self._search_itunes,
                self._search_musicbrainz,
                self._search_cover_art_archive
            ]
            
            for source_func in sources:
                try:
                    result = source_func(artist, album)
                    if result.get('found'):
                        logger.info(f"Found album art from {result['source']}")
                        return result
                except Exception as e:
                    logger.warning(f"Source {source_func.__name__} failed: {str(e)}")
                    continue
            
            return {'found': False, 'url': None, 'source': None}
            
        except Exception as e:
            logger.error(f"Album art search error: {str(e)}")
            return {'found': False, 'url': None, 'source': None}
    
    def _search_itunes(self, artist, album):
        """Search iTunes API for album artwork"""
        try:
            base_url = "https://itunes.apple.com/search"
            
            query = f"{artist} {album}"
            params = {
                'term': query,
                'media': 'music',
                'entity': 'album',
                'limit': 5
            }
            
            response = self.session.get(base_url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            results = data.get('results', [])
            
            if results:
                # Get the first result (highest relevance)
                result = results[0]
                artwork_url = result.get('artworkUrl100', '').replace('100x100', '1200x1200')
                
                return {
                    'found': True,
                    'url': artwork_url,
                    'source': 'itunes',
                    'raw_data': result
                }
            
            return {'found': False, 'url': None, 'source': None}
            
        except Exception as e:
            logger.error(f"iTunes search error: {str(e)}")
            return {'found': False, 'url': None, 'source': None}
    
    def _search_musicbrainz(self, artist, album):
        """Search MusicBrainz for album artwork"""
        try:
            base_url = "https://musicbrainz.org/ws/2/release/"
            
            # Search for release
            query = f"artist:\"{artist}\" release:\"{album}\""
            params = {
                'query': query,
                'limit': 5,
                'fmt': 'json'
            }
            
            response = self.session.get(base_url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            releases = data.get('releases', [])
            
            if releases:
                release_id = releases[0].get('id')
                return self._get_release_artwork(release_id)
            
            return {'found': False, 'url': None, 'source': None}
            
        except Exception as e:
            logger.error(f"MusicBrainz search error: {str(e)}")
            return {'found': False, 'url': None, 'source': None}
    
    def _get_release_artwork(self, release_id):
        """Get artwork for a specific MusicBrainz release"""
        try:
            base_url = f"https://musicbrainz.org/ws/2/release/{release_id}"
            params = {
                'inc': 'release-rels',
                'fmt': 'json'
            }
            
            response = self.session.get(base_url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # Look for artwork URLs in release relations
            for relation in data.get('relations', []):
                if relation.get('type') == 'release cover art':
                    url = relation.get('url')
                    if url:
                        return {
                            'found': True,
                            'url': url,
                            'source': 'musicbrainz',
                            'release_id': release_id
                        }
            
            return {'found': False, 'url': None, 'source': None}
            
        except Exception as e:
            logger.error(f"Release artwork fetch error: {str(e)}")
            return {'found': False, 'url': None, 'source': None}
    
    def _search_cover_art_archive(self, artist, album):
        """Search Cover Art Archive for album artwork"""
        try:
            base_url = "https://musicbrainz.org/ws/2/release/"
            
            # Search for release
            query = f"artist:\"{artist}\" release:\"{album}\""
            params = {
                'query': query,
                'limit': 1,
                'fmt': 'json'
            }
            
            response = self.session.get(base_url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            releases = data.get('releases', [])
            
            if releases:
                release_id = releases[0].get('id')
                caa_url = f"https://coverartarchive.org/release/{release_id}"
                
                return {
                    'found': True,
                    'url': caa_url,
                    'source': 'coverartarchive',
                    'release_id': release_id
                }
            
            return {'found': False, 'url': None, 'source': None}
            
        except Exception as e:
            logger.error(f"Cover Art Archive search error: {str(e)}")
            return {'found': False, 'url': None, 'source': None}
    
    def _clean_artist(self, artist):
        """Clean artist name for URL"""
        return artist.replace(' ', '-').lower().replace('\'', '').replace('&', 'and')
    
    def _clean_album(self, album):
        """Clean album name for URL"""
        return album.replace(' ', '-').lower().replace('\'', '').replace('(', '').replace(')', '').replace('&', 'and')
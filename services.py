"""
Business logic services for Songs CLI application
"""

import logging
from typing import List, Optional
from bson import ObjectId

from database import DatabaseManager, DatabaseError
from models import Song, HistoryEntry

logger = logging.getLogger(__name__)

class SongsService:
    """Service layer for song operations"""
    
    def add_song(self, username: str, title: str, artist: str, 
                 genre: Optional[str] = None, year: Optional[int] = None, 
                 duration: Optional[int] = None) -> bool:
        """Add a new song"""
        try:
            # Create song model
            song = Song(
                title=title,
                artist=artist,
                username=username,
                genre=genre,
                year=year,
                duration=duration
            )
            
            with DatabaseManager() as db:
                # Add song to database
                song_id = db.add_song(song)
                
                # Log to history
                self._log_history(db, username, "added", title, artist)
                
                logger.info(f"Song '{title}' by {artist} added successfully for user {username}")
                return True
                
        except ValueError as e:
            logger.error(f"Invalid song data: {e}")
            raise ValueError(f"Invalid song data: {e}")
        except DatabaseError as e:
            logger.error(f"Database error adding song: {e}")
            raise DatabaseError(f"Failed to add song: {e}")
        except Exception as e:
            logger.error(f"Unexpected error adding song: {e}")
            raise Exception(f"Unexpected error: {e}")
    
    def list_songs(self, username: Optional[str] = None, limit: Optional[int] = None) -> List[Song]:
        """List songs, optionally filtered by username"""
        try:
            with DatabaseManager() as db:
                songs = db.get_songs(username, limit)
                logger.debug(f"Retrieved {len(songs)} songs")
                return songs
                
        except DatabaseError as e:
            logger.error(f"Database error listing songs: {e}")
            raise DatabaseError(f"Failed to list songs: {e}")
        except Exception as e:
            logger.error(f"Unexpected error listing songs: {e}")
            raise Exception(f"Unexpected error: {e}")
    
    def search_songs(self, username: str, search_term: str) -> List[Song]:
        """Search songs by title or artist"""
        try:
            if not search_term.strip():
                raise ValueError("Search term cannot be empty")
            
            with DatabaseManager() as db:
                songs = db.search_songs(username, search_term.strip())
                logger.debug(f"Found {len(songs)} songs matching '{search_term}'")
                return songs
                
        except ValueError as e:
            logger.error(f"Invalid search term: {e}")
            raise ValueError(f"Invalid search: {e}")
        except DatabaseError as e:
            logger.error(f"Database error searching songs: {e}")
            raise DatabaseError(f"Failed to search songs: {e}")
        except Exception as e:
            logger.error(f"Unexpected error searching songs: {e}")
            raise Exception(f"Unexpected error: {e}")
    
    def get_song(self, username: str, song_id: str) -> Optional[Song]:
        """Get a specific song by ID"""
        try:
            with DatabaseManager() as db:
                song = db.get_song_by_id(username, song_id)
                if song:
                    # Log view action
                    self._log_history(db, username, "viewed", song.title, song.artist)
                return song
                
        except DatabaseError as e:
            logger.error(f"Database error getting song: {e}")
            raise DatabaseError(f"Failed to get song: {e}")
        except Exception as e:
            logger.error(f"Unexpected error getting song: {e}")
            raise Exception(f"Unexpected error: {e}")
    
    def update_song(self, username: str, song_id: str, **kwargs) -> bool:
        """Update a song"""
        try:
            # Remove None values
            update_data = {k: v for k, v in kwargs.items() if v is not None}
            
            if not update_data:
                raise ValueError("No update data provided")
            
            with DatabaseManager() as db:
                # Get original song for history
                original_song = db.get_song_by_id(username, song_id)
                if not original_song:
                    return False
                
                # Update song
                success = db.update_song(username, song_id, **update_data)
                
                if success:
                    # Log to history
                    self._log_history(db, username, "updated", original_song.title, original_song.artist)
                    logger.info(f"Song {song_id} updated successfully for user {username}")
                
                return success
                
        except ValueError as e:
            logger.error(f"Invalid update data: {e}")
            raise ValueError(f"Invalid update: {e}")
        except DatabaseError as e:
            logger.error(f"Database error updating song: {e}")
            raise DatabaseError(f"Failed to update song: {e}")
        except Exception as e:
            logger.error(f"Unexpected error updating song: {e}")
            raise Exception(f"Unexpected error: {e}")
    
    def delete_song(self, username: str, song_id: str) -> bool:
        """Delete a song"""
        try:
            with DatabaseManager() as db:
                deleted_song = db.delete_song(username, song_id)
                
                if deleted_song:
                    # Log to history
                    self._log_history(db, username, "deleted", deleted_song.title, deleted_song.artist)
                    logger.info(f"Song {song_id} deleted successfully for user {username}")
                    return True
                
                return False
                
        except DatabaseError as e:
            logger.error(f"Database error deleting song: {e}")
            raise DatabaseError(f"Failed to delete song: {e}")
        except Exception as e:
            logger.error(f"Unexpected error deleting song: {e}")
            raise Exception(f"Unexpected error: {e}")
    
    def get_history(self, username: str, limit: int = 10) -> List[HistoryEntry]:
        """Get user's activity history"""
        try:
            with DatabaseManager() as db:
                history = db.get_history(username, limit)
                logger.debug(f"Retrieved {len(history)} history entries for user {username}")
                return history
                
        except DatabaseError as e:
            logger.error(f"Database error getting history: {e}")
            raise DatabaseError(f"Failed to get history: {e}")
        except Exception as e:
            logger.error(f"Unexpected error getting history: {e}")
            raise Exception(f"Unexpected error: {e}")
    
    def _log_history(self, db, username: str, action: str, title: str, artist: str):
        """Log user action to history"""
        try:
            entry = HistoryEntry(
                username=username,
                action=action,
                song_title=title,
                song_artist=artist
            )
            
            db.add_history_entry(entry)
            
        except Exception as e:
            # Don't fail the main operation if history logging fails
            logger.warning(f"Failed to log history: {e}")

class PlaybackService:
    """Service for song playback operations (future enhancement)"""
    
    def play_song(self, username: str, song_id: str) -> bool:
        """Play a song (placeholder for future implementation)"""
        try:
            songs_service = SongsService()
            song = songs_service.get_song(username, song_id)
            
            if song:
                with DatabaseManager() as db:
                    # Log play action
                    songs_service._log_history(db, username, "played", song.title, song.artist)
                
                logger.info(f"Playing '{song.title}' by {song.artist} for user {username}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error playing song: {e}")
            return False

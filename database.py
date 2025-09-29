"""
Database operations for Songs CLI application
"""

import logging
from typing import List, Optional, Dict, Any
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError, DuplicateKeyError
from bson import ObjectId
from bson.errors import InvalidId

from config import config
from models import Song, HistoryEntry

logger = logging.getLogger(__name__)

class DatabaseError(Exception):
    """Custom exception for database operations"""
    pass

class SongsDatabase:
    """MongoDB connection and operations for Songs"""
    
    def __init__(self):
        self.client: Optional[MongoClient] = None
        self.db = None
        self.songs_collection = None
        self.history_collection = None
        self._connected = False
    
    def connect(self) -> bool:
        """Connect to MongoDB database"""
        try:
            logger.info("Connecting to MongoDB...")
            
            self.client = MongoClient(
                config.database.connection_string,
                serverSelectionTimeoutMS=config.database.server_selection_timeout,
                connectTimeoutMS=config.database.connection_timeout,
                socketTimeoutMS=config.database.socket_timeout
            )
            
            # Test connection
            self.client.admin.command('ping')
            logger.info("Successfully connected to MongoDB!")
            
            # Select database and collections
            self.db = self.client[config.database.database_name]
            self.songs_collection = self.db['songs']
            self.history_collection = self.db['history']
            
            # Create indexes for better performance
            self._create_indexes()
            
            self._connected = True
            return True
            
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise DatabaseError(f"Database connection failed: {e}")
        except Exception as e:
            logger.error(f"Unexpected error connecting to MongoDB: {e}")
            raise DatabaseError(f"Unexpected database error: {e}")
    
    def _create_indexes(self):
        """Create database indexes for better performance"""
        try:
            # Songs collection indexes
            self.songs_collection.create_index("title")
            self.songs_collection.create_index("artist")
            self.songs_collection.create_index("username")
            self.songs_collection.create_index([("username", 1), ("title", 1), ("artist", 1)])
            
            # History collection indexes
            self.history_collection.create_index("username")
            self.history_collection.create_index("timestamp")
            self.history_collection.create_index([("username", 1), ("timestamp", -1)])
            
            logger.debug("Database indexes created successfully")
            
        except Exception as e:
            logger.warning(f"Failed to create indexes: {e}")
    
    def close(self):
        """Close MongoDB connection"""
        if self.client:
            self.client.close()
            self._connected = False
            logger.info("MongoDB connection closed")
    
    def _ensure_connected(self):
        """Ensure database is connected"""
        if not self._connected:
            raise DatabaseError("Database not connected. Call connect() first.")
    
    def add_song(self, song: Song) -> ObjectId:
        """Add a new song to the database"""
        self._ensure_connected()
        
        try:
            song_data = song.to_dict()
            result = self.songs_collection.insert_one(song_data)
            
            if result.inserted_id:
                logger.debug(f"Song added with ID: {result.inserted_id}")
                return result.inserted_id
            else:
                raise DatabaseError("Failed to insert song")
                
        except DuplicateKeyError as e:
            raise DatabaseError(f"Song already exists: {e}")
        except Exception as e:
            logger.error(f"Error adding song: {e}")
            raise DatabaseError(f"Failed to add song: {e}")
    
    def get_songs(self, username: Optional[str] = None, limit: Optional[int] = None) -> List[Song]:
        """Get songs from database"""
        self._ensure_connected()
        
        try:
            query = {}
            if username:
                query["username"] = username
            
            cursor = self.songs_collection.find(query).sort("created_at", -1)
            if limit:
                cursor = cursor.limit(limit)
            
            songs = []
            for song_data in cursor:
                songs.append(Song.from_dict(song_data))
            
            return songs
            
        except Exception as e:
            logger.error(f"Error getting songs: {e}")
            raise DatabaseError(f"Failed to get songs: {e}")
    
    def search_songs(self, username: str, search_term: str) -> List[Song]:
        """Search songs by title or artist"""
        self._ensure_connected()
        
        try:
            query = {
                "username": username,
                "$or": [
                    {"title": {"$regex": search_term, "$options": "i"}},
                    {"artist": {"$regex": search_term, "$options": "i"}}
                ]
            }
            
            songs = []
            for song_data in self.songs_collection.find(query):
                songs.append(Song.from_dict(song_data))
            
            return songs
            
        except Exception as e:
            logger.error(f"Error searching songs: {e}")
            raise DatabaseError(f"Failed to search songs: {e}")
    
    def get_song_by_id(self, username: str, song_id: str) -> Optional[Song]:
        """Get a specific song by ID"""
        self._ensure_connected()
        
        try:
            object_id = ObjectId(song_id)
            song_data = self.songs_collection.find_one({
                "_id": object_id,
                "username": username
            })
            
            if song_data:
                return Song.from_dict(song_data)
            return None
            
        except InvalidId:
            raise DatabaseError(f"Invalid song ID format: {song_id}")
        except Exception as e:
            logger.error(f"Error getting song: {e}")
            raise DatabaseError(f"Failed to get song: {e}")
    
    def update_song(self, username: str, song_id: str, **kwargs) -> bool:
        """Update a song"""
        self._ensure_connected()
        
        try:
            # Get existing song
            song = self.get_song_by_id(username, song_id)
            if not song:
                return False
            
            # Update song fields
            song.update_fields(**kwargs)
            
            # Update in database
            object_id = ObjectId(song_id)
            result = self.songs_collection.update_one(
                {"_id": object_id, "username": username},
                {"$set": song.to_dict()}
            )
            
            return result.modified_count > 0
            
        except InvalidId:
            raise DatabaseError(f"Invalid song ID format: {song_id}")
        except Exception as e:
            logger.error(f"Error updating song: {e}")
            raise DatabaseError(f"Failed to update song: {e}")
    
    def delete_song(self, username: str, song_id: str) -> Optional[Song]:
        """Delete a song and return the deleted song"""
        self._ensure_connected()
        
        try:
            # Get song before deletion
            song = self.get_song_by_id(username, song_id)
            if not song:
                return None
            
            # Delete song
            object_id = ObjectId(song_id)
            result = self.songs_collection.delete_one({
                "_id": object_id,
                "username": username
            })
            
            if result.deleted_count > 0:
                return song
            return None
            
        except InvalidId:
            raise DatabaseError(f"Invalid song ID format: {song_id}")
        except Exception as e:
            logger.error(f"Error deleting song: {e}")
            raise DatabaseError(f"Failed to delete song: {e}")
    
    def add_history_entry(self, entry: HistoryEntry) -> ObjectId:
        """Add a history entry"""
        self._ensure_connected()
        
        try:
            entry_data = entry.to_dict()
            result = self.history_collection.insert_one(entry_data)
            
            if result.inserted_id:
                logger.debug(f"History entry added with ID: {result.inserted_id}")
                return result.inserted_id
            else:
                raise DatabaseError("Failed to insert history entry")
                
        except Exception as e:
            logger.error(f"Error adding history entry: {e}")
            raise DatabaseError(f"Failed to add history entry: {e}")
    
    def get_history(self, username: str, limit: int = 10) -> List[HistoryEntry]:
        """Get user's activity history"""
        self._ensure_connected()
        
        try:
            history_data = self.history_collection.find(
                {"username": username}
            ).sort("timestamp", -1).limit(limit)
            
            history = []
            for entry_data in history_data:
                history.append(HistoryEntry.from_dict(entry_data))
            
            return history
            
        except Exception as e:
            logger.error(f"Error getting history: {e}")
            raise DatabaseError(f"Failed to get history: {e}")

# Context manager for database operations
class DatabaseManager:
    """Context manager for database operations"""
    
    def __init__(self):
        self.db = SongsDatabase()
    
    def __enter__(self) -> SongsDatabase:
        self.db.connect()
        return self.db
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.db.close()
        if exc_type:
            logger.error(f"Database operation failed: {exc_val}")
        return False

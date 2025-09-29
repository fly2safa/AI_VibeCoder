#!/usr/bin/env python3
"""
Songs CLI CRUD Application
A command-line interface for managing songs with MongoDB backend
"""

import os
import sys
import argparse
from datetime import datetime, timezone
from typing import List, Dict, Optional
import json
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SongsDatabase:
    """MongoDB connection and operations for Songs"""
    
    def __init__(self):
        self.client = None
        self.db = None
        self.songs_collection = None
        self.history_collection = None
        
        # Get MongoDB URL from environment
        self.connection_string = os.getenv('project_db_url')
        if not self.connection_string:
            raise ValueError("project_db_url environment variable not found!")
        
        logger.info(f"Connecting to MongoDB...")
    
    def connect(self):
        """Connect to MongoDB database"""
        try:
            self.client = MongoClient(
                self.connection_string,
                serverSelectionTimeoutMS=5000,
                connectTimeoutMS=5000,
                socketTimeoutMS=5000
            )
            
            # Test connection
            self.client.admin.command('ping')
            logger.info("Successfully connected to MongoDB!")
            
            # Select database and collections
            self.db = self.client['songs_db']
            self.songs_collection = self.db['songs']
            self.history_collection = self.db['history']
            
            # Create indexes for better performance
            self.songs_collection.create_index("title")
            self.songs_collection.create_index("artist")
            self.songs_collection.create_index("username")
            self.history_collection.create_index("username")
            self.history_collection.create_index("timestamp")
            
            return True
            
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error connecting to MongoDB: {e}")
            return False
    
    def close(self):
        """Close MongoDB connection"""
        if self.client:
            self.client.close()
            logger.info("MongoDB connection closed")

class SongsManager:
    """Main class for managing songs and operations"""
    
    def __init__(self):
        self.db = SongsDatabase()
        if not self.db.connect():
            sys.exit(1)
    
    def add_song(self, username: str, title: str, artist: str, genre: str = None, 
                 year: int = None, duration: int = None) -> bool:
        """Add a new song"""
        try:
            song_data = {
                "title": title,
                "artist": artist,
                "genre": genre,
                "year": year,
                "duration": duration,  # in seconds
                "username": username,
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc)
            }
            
            # Remove None values
            song_data = {k: v for k, v in song_data.items() if v is not None}
            
            result = self.db.songs_collection.insert_one(song_data)
            
            if result.inserted_id:
                # Log to history
                self._log_history(username, "added", title, artist)
                print(f"✅ Song '{title}' by {artist} added successfully!")
                return True
            else:
                print("❌ Failed to add song")
                return False
                
        except Exception as e:
            logger.error(f"Error adding song: {e}")
            print(f"❌ Error adding song: {e}")
            return False
    
    def list_songs(self, username: str = None, limit: int = None) -> List[Dict]:
        """List songs, optionally filtered by username"""
        try:
            query = {}
            if username:
                query["username"] = username
            
            cursor = self.db.songs_collection.find(query).sort("created_at", -1)
            if limit:
                cursor = cursor.limit(limit)
            
            songs = list(cursor)
            return songs
            
        except Exception as e:
            logger.error(f"Error listing songs: {e}")
            return []
    
    def search_songs(self, username: str, search_term: str) -> List[Dict]:
        """Search songs by title or artist"""
        try:
            query = {
                "username": username,
                "$or": [
                    {"title": {"$regex": search_term, "$options": "i"}},
                    {"artist": {"$regex": search_term, "$options": "i"}}
                ]
            }
            
            songs = list(self.db.songs_collection.find(query))
            return songs
            
        except Exception as e:
            logger.error(f"Error searching songs: {e}")
            return []
    
    def get_song(self, username: str, song_id: str) -> Optional[Dict]:
        """Get a specific song by ID"""
        try:
            from bson import ObjectId
            song = self.db.songs_collection.find_one({
                "_id": ObjectId(song_id),
                "username": username
            })
            return song
            
        except Exception as e:
            logger.error(f"Error getting song: {e}")
            return None
    
    def update_song(self, username: str, song_id: str, **kwargs) -> bool:
        """Update a song"""
        try:
            from bson import ObjectId
            
            # Remove None values and add updated_at
            update_data = {k: v for k, v in kwargs.items() if v is not None}
            update_data["updated_at"] = datetime.now(timezone.utc)
            
            result = self.db.songs_collection.update_one(
                {"_id": ObjectId(song_id), "username": username},
                {"$set": update_data}
            )
            
            if result.modified_count > 0:
                # Get song info for history
                song = self.get_song(username, song_id)
                if song:
                    self._log_history(username, "updated", song["title"], song["artist"])
                print(f"✅ Song updated successfully!")
                return True
            else:
                print("❌ Song not found or no changes made")
                return False
                
        except Exception as e:
            logger.error(f"Error updating song: {e}")
            print(f"❌ Error updating song: {e}")
            return False
    
    def delete_song(self, username: str, song_id: str) -> bool:
        """Delete a song"""
        try:
            from bson import ObjectId
            
            # Get song info before deletion for history
            song = self.get_song(username, song_id)
            
            result = self.db.songs_collection.delete_one({
                "_id": ObjectId(song_id),
                "username": username
            })
            
            if result.deleted_count > 0:
                if song:
                    self._log_history(username, "deleted", song["title"], song["artist"])
                print(f"✅ Song deleted successfully!")
                return True
            else:
                print("❌ Song not found")
                return False
                
        except Exception as e:
            logger.error(f"Error deleting song: {e}")
            print(f"❌ Error deleting song: {e}")
            return False
    
    def get_history(self, username: str, limit: int = 10) -> List[Dict]:
        """Get user's activity history"""
        try:
            history = list(
                self.db.history_collection.find({"username": username})
                .sort("timestamp", -1)
                .limit(limit)
            )
            return history
            
        except Exception as e:
            logger.error(f"Error getting history: {e}")
            return []
    
    def _log_history(self, username: str, action: str, title: str, artist: str):
        """Log user action to history"""
        try:
            history_entry = {
                "username": username,
                "action": action,
                "song_title": title,
                "song_artist": artist,
                "timestamp": datetime.now(timezone.utc)
            }
            
            self.db.history_collection.insert_one(history_entry)
            
        except Exception as e:
            logger.error(f"Error logging history: {e}")
    
    def close(self):
        """Close database connection"""
        self.db.close()

def format_song_display(song: Dict) -> str:
    """Format song for display"""
    song_id = str(song["_id"])
    title = song.get("title", "Unknown")
    artist = song.get("artist", "Unknown")
    genre = song.get("genre", "N/A")
    year = song.get("year", "N/A")
    duration = song.get("duration", "N/A")
    
    if duration != "N/A" and isinstance(duration, int):
        minutes, seconds = divmod(duration, 60)
        duration = f"{minutes}:{seconds:02d}"
    
    return f"""
🎵 {title} - {artist}
   Genre: {genre} | Year: {year} | Duration: {duration}
   ID: {song_id}
"""

def format_history_display(entry: Dict) -> str:
    """Format history entry for display"""
    timestamp = entry["timestamp"].strftime("%Y-%m-%d %H:%M:%S")
    action = entry["action"]
    title = entry["song_title"]
    artist = entry["song_artist"]
    
    action_emoji = {
        "added": "➕",
        "updated": "✏️",
        "deleted": "🗑️",
        "played": "▶️"
    }.get(action, "📝")
    
    return f"{action_emoji} {timestamp} - {action} '{title}' by {artist}"

def main():
    """Main CLI application"""
    parser = argparse.ArgumentParser(
        description="Songs CLI - Manage your music collection",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python songs_cli.py --user Safa add --title "Song 1" --artist "Artist Name"
  python songs_cli.py --user Safa list
  python songs_cli.py --user Safa search "Song"
  python songs_cli.py --user Safa history
  python songs_cli.py --user Safa update <song_id> --title "New Title"
  python songs_cli.py --user Safa delete <song_id>
        """
    )
    
    parser.add_argument("--user", required=True, help="Username")
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Add command
    add_parser = subparsers.add_parser("add", help="Add a new song")
    add_parser.add_argument("--title", required=True, help="Song title")
    add_parser.add_argument("--artist", required=True, help="Artist name")
    add_parser.add_argument("--genre", help="Song genre")
    add_parser.add_argument("--year", type=int, help="Release year")
    add_parser.add_argument("--duration", type=int, help="Duration in seconds")
    
    # List command
    list_parser = subparsers.add_parser("list", help="List songs")
    list_parser.add_argument("--limit", type=int, help="Limit number of results")
    
    # Search command
    search_parser = subparsers.add_parser("search", help="Search songs")
    search_parser.add_argument("term", help="Search term")
    
    # Get command
    get_parser = subparsers.add_parser("get", help="Get a specific song")
    get_parser.add_argument("song_id", help="Song ID")
    
    # Update command
    update_parser = subparsers.add_parser("update", help="Update a song")
    update_parser.add_argument("song_id", help="Song ID")
    update_parser.add_argument("--title", help="New title")
    update_parser.add_argument("--artist", help="New artist")
    update_parser.add_argument("--genre", help="New genre")
    update_parser.add_argument("--year", type=int, help="New year")
    update_parser.add_argument("--duration", type=int, help="New duration")
    
    # Delete command
    delete_parser = subparsers.add_parser("delete", help="Delete a song")
    delete_parser.add_argument("song_id", help="Song ID")
    
    # History command
    history_parser = subparsers.add_parser("history", help="Show user history")
    history_parser.add_argument("--limit", type=int, default=10, help="Limit number of results")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Initialize songs manager
    try:
        songs_manager = SongsManager()
    except ValueError as e:
        print(f"❌ Configuration error: {e}")
        print("Make sure to set the 'project_db_url' environment variable")
        return
    except Exception as e:
        print(f"❌ Failed to initialize: {e}")
        return
    
    try:
        username = args.user
        
        if args.command == "add":
            songs_manager.add_song(
                username=username,
                title=args.title,
                artist=args.artist,
                genre=args.genre,
                year=args.year,
                duration=args.duration
            )
        
        elif args.command == "list":
            songs = songs_manager.list_songs(username, args.limit)
            if songs:
                print(f"\n🎵 Songs for {username}:")
                for song in songs:
                    print(format_song_display(song))
            else:
                print(f"No songs found for {username}")
        
        elif args.command == "search":
            songs = songs_manager.search_songs(username, args.term)
            if songs:
                print(f"\n🔍 Search results for '{args.term}':")
                for song in songs:
                    print(format_song_display(song))
            else:
                print(f"No songs found matching '{args.term}'")
        
        elif args.command == "get":
            song = songs_manager.get_song(username, args.song_id)
            if song:
                print(f"\n🎵 Song details:")
                print(format_song_display(song))
            else:
                print("Song not found")
        
        elif args.command == "update":
            update_data = {}
            if args.title:
                update_data["title"] = args.title
            if args.artist:
                update_data["artist"] = args.artist
            if args.genre:
                update_data["genre"] = args.genre
            if args.year:
                update_data["year"] = args.year
            if args.duration:
                update_data["duration"] = args.duration
            
            if update_data:
                songs_manager.update_song(username, args.song_id, **update_data)
            else:
                print("No update fields provided")
        
        elif args.command == "delete":
            songs_manager.delete_song(username, args.song_id)
        
        elif args.command == "history":
            history = songs_manager.get_history(username, args.limit)
            if history:
                print(f"\n📜 History for {username}:")
                for entry in history:
                    print(format_history_display(entry))
            else:
                print(f"No history found for {username}")
    
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        print(f"❌ Unexpected error: {e}")
    finally:
        songs_manager.close()

if __name__ == "__main__":
    main()

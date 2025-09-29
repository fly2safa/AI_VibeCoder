"""
Data models for Songs CLI application
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional, Dict, Any
from bson import ObjectId
import logging

logger = logging.getLogger(__name__)

@dataclass
class Song:
    """Song data model with validation"""
    title: str
    artist: str
    username: str
    genre: Optional[str] = None
    year: Optional[int] = None
    duration: Optional[int] = None  # Duration in seconds
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    id: Optional[ObjectId] = None
    
    def __post_init__(self):
        """Validate song data after initialization"""
        self._validate()
    
    def _validate(self):
        """Validate song data"""
        if not self.title or not self.title.strip():
            raise ValueError("Song title cannot be empty")
        
        if not self.artist or not self.artist.strip():
            raise ValueError("Artist name cannot be empty")
        
        if not self.username or not self.username.strip():
            raise ValueError("Username cannot be empty")
        
        if self.year is not None and (self.year < 1000 or self.year > 3000):
            raise ValueError("Year must be between 1000 and 3000")
        
        if self.duration is not None and self.duration < 0:
            raise ValueError("Duration cannot be negative")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert song to dictionary for MongoDB storage"""
        data = {
            "title": self.title.strip(),
            "artist": self.artist.strip(),
            "username": self.username.strip(),
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
        
        # Add optional fields if they exist
        if self.genre:
            data["genre"] = self.genre.strip()
        if self.year is not None:
            data["year"] = self.year
        if self.duration is not None:
            data["duration"] = self.duration
        if self.id:
            data["_id"] = self.id
            
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Song':
        """Create Song instance from dictionary"""
        return cls(
            title=data.get("title", ""),
            artist=data.get("artist", ""),
            username=data.get("username", ""),
            genre=data.get("genre"),
            year=data.get("year"),
            duration=data.get("duration"),
            created_at=data.get("created_at", datetime.now(timezone.utc)),
            updated_at=data.get("updated_at", datetime.now(timezone.utc)),
            id=data.get("_id")
        )
    
    def update_fields(self, **kwargs):
        """Update song fields and set updated_at timestamp"""
        for key, value in kwargs.items():
            if hasattr(self, key) and value is not None:
                setattr(self, key, value)
        
        self.updated_at = datetime.now(timezone.utc)
        self._validate()

@dataclass
class HistoryEntry:
    """History entry data model"""
    username: str
    action: str
    song_title: str
    song_artist: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    id: Optional[ObjectId] = None
    
    def __post_init__(self):
        """Validate history entry after initialization"""
        self._validate()
    
    def _validate(self):
        """Validate history entry data"""
        if not self.username or not self.username.strip():
            raise ValueError("Username cannot be empty")
        
        if not self.action or not self.action.strip():
            raise ValueError("Action cannot be empty")
        
        valid_actions = {"added", "updated", "deleted", "played", "viewed"}
        if self.action not in valid_actions:
            logger.warning(f"Unusual action type: {self.action}")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert history entry to dictionary for MongoDB storage"""
        data = {
            "username": self.username.strip(),
            "action": self.action.strip(),
            "song_title": self.song_title.strip(),
            "song_artist": self.song_artist.strip(),
            "timestamp": self.timestamp
        }
        
        if self.id:
            data["_id"] = self.id
            
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'HistoryEntry':
        """Create HistoryEntry instance from dictionary"""
        return cls(
            username=data.get("username", ""),
            action=data.get("action", ""),
            song_title=data.get("song_title", ""),
            song_artist=data.get("song_artist", ""),
            timestamp=data.get("timestamp", datetime.now(timezone.utc)),
            id=data.get("_id")
        )

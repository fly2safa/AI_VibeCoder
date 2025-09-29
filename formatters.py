"""
Output formatters for Songs CLI application
"""

from typing import Dict, List
from models import Song, HistoryEntry

class SongFormatter:
    """Formatter for song display"""
    
    @staticmethod
    def format_song(song: Song) -> str:
        """Format a single song for display"""
        song_id = str(song.id) if song.id else "N/A"
        title = song.title or "Unknown"
        artist = song.artist or "Unknown"
        genre = song.genre or "N/A"
        year = song.year or "N/A"
        duration = song.duration
        
        # Format duration
        if duration is not None and isinstance(duration, int):
            minutes, seconds = divmod(duration, 60)
            duration_str = f"{minutes}:{seconds:02d}"
        else:
            duration_str = "N/A"
        
        return f"""
🎵 {title} - {artist}
   Genre: {genre} | Year: {year} | Duration: {duration_str}
   ID: {song_id}
"""
    
    @staticmethod
    def format_song_list(songs: List[Song], username: str = None) -> str:
        """Format a list of songs for display"""
        if not songs:
            user_text = f" for {username}" if username else ""
            return f"No songs found{user_text}"
        
        header = f"\n🎵 Songs{f' for {username}' if username else ''}:"
        formatted_songs = [SongFormatter.format_song(song) for song in songs]
        
        return header + "".join(formatted_songs)
    
    @staticmethod
    def format_song_table(songs: List[Song]) -> str:
        """Format songs as a table (for large lists)"""
        if not songs:
            return "No songs found"
        
        # Header
        header = f"{'Title':<30} {'Artist':<25} {'Genre':<15} {'Year':<6} {'Duration':<8}"
        separator = "-" * len(header)
        
        # Rows
        rows = []
        for song in songs:
            title = (song.title[:27] + "...") if len(song.title) > 30 else song.title
            artist = (song.artist[:22] + "...") if len(song.artist) > 25 else song.artist
            genre = (song.genre[:12] + "...") if song.genre and len(song.genre) > 15 else (song.genre or "N/A")
            year = str(song.year) if song.year else "N/A"
            
            if song.duration:
                minutes, seconds = divmod(song.duration, 60)
                duration = f"{minutes}:{seconds:02d}"
            else:
                duration = "N/A"
            
            row = f"{title:<30} {artist:<25} {genre:<15} {year:<6} {duration:<8}"
            rows.append(row)
        
        return f"\n{header}\n{separator}\n" + "\n".join(rows)

class HistoryFormatter:
    """Formatter for history display"""
    
    @staticmethod
    def format_history_entry(entry: HistoryEntry) -> str:
        """Format a single history entry for display"""
        timestamp = entry.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        action = entry.action
        title = entry.song_title
        artist = entry.song_artist
        
        action_emoji = {
            "added": "➕",
            "updated": "✏️",
            "deleted": "🗑️",
            "played": "▶️",
            "viewed": "👁️"
        }.get(action, "📝")
        
        return f"{action_emoji} {timestamp} - {action} '{title}' by {artist}"
    
    @staticmethod
    def format_history_list(history: List[HistoryEntry], username: str) -> str:
        """Format a list of history entries for display"""
        if not history:
            return f"No history found for {username}"
        
        header = f"\n📜 History for {username}:"
        formatted_entries = [HistoryFormatter.format_history_entry(entry) for entry in history]
        
        return header + "\n" + "\n".join(formatted_entries)

class MessageFormatter:
    """Formatter for system messages"""
    
    @staticmethod
    def success(message: str) -> str:
        """Format success message"""
        return f"✅ {message}"
    
    @staticmethod
    def error(message: str) -> str:
        """Format error message"""
        return f"❌ {message}"
    
    @staticmethod
    def warning(message: str) -> str:
        """Format warning message"""
        return f"⚠️ {message}"
    
    @staticmethod
    def info(message: str) -> str:
        """Format info message"""
        return f"ℹ️ {message}"
    
    @staticmethod
    def search_results(songs: List[Song], search_term: str) -> str:
        """Format search results"""
        if not songs:
            return f"No songs found matching '{search_term}'"
        
        header = f"\n🔍 Search results for '{search_term}':"
        formatted_songs = [SongFormatter.format_song(song) for song in songs]
        
        return header + "".join(formatted_songs)

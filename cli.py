"""
Command-line interface for Songs CLI application
"""

import sys
import argparse
import logging
from typing import Optional

from config import config
from services import SongsService, PlaybackService
from formatters import SongFormatter, HistoryFormatter, MessageFormatter
from database import DatabaseError

# Set up logging
logging.basicConfig(
    level=getattr(logging, config.app.log_level.upper()),
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SongsCLI:
    """Main CLI application class"""
    
    def __init__(self):
        self.songs_service = SongsService()
        self.playback_service = PlaybackService()
    
    def create_parser(self) -> argparse.ArgumentParser:
        """Create and configure argument parser"""
        parser = argparse.ArgumentParser(
            description="Songs CLI - Manage your music collection",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  %(prog)s --user Safa add --title "Song 1" --artist "Artist Name"
  %(prog)s --user Safa list
  %(prog)s --user Safa search "Song"
  %(prog)s --user Safa history
  %(prog)s --user Safa update <song_id> --title "New Title"
  %(prog)s --user Safa delete <song_id>
  %(prog)s --user Safa play <song_id>
            """
        )
        
        parser.add_argument("--user", required=True, help="Username")
        parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose output")
        
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
        list_parser.add_argument("--all", action="store_true", help="List all users' songs")
        list_parser.add_argument("--table", action="store_true", help="Display as table")
        
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
        delete_parser.add_argument("--confirm", action="store_true", help="Skip confirmation prompt")
        
        # History command
        history_parser = subparsers.add_parser("history", help="Show user history")
        history_parser.add_argument("--limit", type=int, default=10, help="Limit number of results")
        
        # Play command (future enhancement)
        play_parser = subparsers.add_parser("play", help="Play a song")
        play_parser.add_argument("song_id", help="Song ID")
        
        return parser
    
    def handle_add(self, args) -> int:
        """Handle add command"""
        try:
            success = self.songs_service.add_song(
                username=args.user,
                title=args.title,
                artist=args.artist,
                genre=args.genre,
                year=args.year,
                duration=args.duration
            )
            
            if success:
                print(MessageFormatter.success(f"Song '{args.title}' by {args.artist} added successfully!"))
                return 0
            else:
                print(MessageFormatter.error("Failed to add song"))
                return 1
                
        except ValueError as e:
            print(MessageFormatter.error(f"Invalid input: {e}"))
            return 1
        except DatabaseError as e:
            print(MessageFormatter.error(f"Database error: {e}"))
            return 1
        except Exception as e:
            print(MessageFormatter.error(f"Unexpected error: {e}"))
            return 1
    
    def handle_list(self, args) -> int:
        """Handle list command"""
        try:
            username = None if args.all else args.user
            songs = self.songs_service.list_songs(username, args.limit)
            
            if args.table and songs:
                print(SongFormatter.format_song_table(songs))
            else:
                print(SongFormatter.format_song_list(songs, username))
            
            return 0
            
        except DatabaseError as e:
            print(MessageFormatter.error(f"Database error: {e}"))
            return 1
        except Exception as e:
            print(MessageFormatter.error(f"Unexpected error: {e}"))
            return 1
    
    def handle_search(self, args) -> int:
        """Handle search command"""
        try:
            songs = self.songs_service.search_songs(args.user, args.term)
            print(MessageFormatter.search_results(songs, args.term))
            return 0
            
        except ValueError as e:
            print(MessageFormatter.error(f"Invalid search: {e}"))
            return 1
        except DatabaseError as e:
            print(MessageFormatter.error(f"Database error: {e}"))
            return 1
        except Exception as e:
            print(MessageFormatter.error(f"Unexpected error: {e}"))
            return 1
    
    def handle_get(self, args) -> int:
        """Handle get command"""
        try:
            song = self.songs_service.get_song(args.user, args.song_id)
            
            if song:
                print(f"\n🎵 Song details:")
                print(SongFormatter.format_song(song))
                return 0
            else:
                print(MessageFormatter.error("Song not found"))
                return 1
                
        except DatabaseError as e:
            print(MessageFormatter.error(f"Database error: {e}"))
            return 1
        except Exception as e:
            print(MessageFormatter.error(f"Unexpected error: {e}"))
            return 1
    
    def handle_update(self, args) -> int:
        """Handle update command"""
        try:
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
            
            if not update_data:
                print(MessageFormatter.error("No update fields provided"))
                return 1
            
            success = self.songs_service.update_song(args.user, args.song_id, **update_data)
            
            if success:
                print(MessageFormatter.success("Song updated successfully!"))
                return 0
            else:
                print(MessageFormatter.error("Song not found or no changes made"))
                return 1
                
        except ValueError as e:
            print(MessageFormatter.error(f"Invalid update: {e}"))
            return 1
        except DatabaseError as e:
            print(MessageFormatter.error(f"Database error: {e}"))
            return 1
        except Exception as e:
            print(MessageFormatter.error(f"Unexpected error: {e}"))
            return 1
    
    def handle_delete(self, args) -> int:
        """Handle delete command"""
        try:
            # Confirmation prompt (unless --confirm flag is used)
            if not args.confirm:
                # Get song details for confirmation
                song = self.songs_service.get_song(args.user, args.song_id)
                if not song:
                    print(MessageFormatter.error("Song not found"))
                    return 1
                
                response = input(f"Are you sure you want to delete '{song.title}' by {song.artist}? (y/N): ")
                if response.lower() not in ['y', 'yes']:
                    print(MessageFormatter.info("Delete cancelled"))
                    return 0
            
            success = self.songs_service.delete_song(args.user, args.song_id)
            
            if success:
                print(MessageFormatter.success("Song deleted successfully!"))
                return 0
            else:
                print(MessageFormatter.error("Song not found"))
                return 1
                
        except DatabaseError as e:
            print(MessageFormatter.error(f"Database error: {e}"))
            return 1
        except Exception as e:
            print(MessageFormatter.error(f"Unexpected error: {e}"))
            return 1
    
    def handle_history(self, args) -> int:
        """Handle history command"""
        try:
            history = self.songs_service.get_history(args.user, args.limit)
            print(HistoryFormatter.format_history_list(history, args.user))
            return 0
            
        except DatabaseError as e:
            print(MessageFormatter.error(f"Database error: {e}"))
            return 1
        except Exception as e:
            print(MessageFormatter.error(f"Unexpected error: {e}"))
            return 1
    
    def handle_play(self, args) -> int:
        """Handle play command"""
        try:
            success = self.playback_service.play_song(args.user, args.song_id)
            
            if success:
                print(MessageFormatter.success("Song played successfully!"))
                return 0
            else:
                print(MessageFormatter.error("Song not found"))
                return 1
                
        except Exception as e:
            print(MessageFormatter.error(f"Error playing song: {e}"))
            return 1
    
    def run(self, args: Optional[list] = None) -> int:
        """Run the CLI application"""
        parser = self.create_parser()
        parsed_args = parser.parse_args(args)
        
        # Set verbose logging if requested
        if parsed_args.verbose:
            logging.getLogger().setLevel(logging.DEBUG)
        
        if not parsed_args.command:
            parser.print_help()
            return 0
        
        # Route to appropriate handler
        handlers = {
            "add": self.handle_add,
            "list": self.handle_list,
            "search": self.handle_search,
            "get": self.handle_get,
            "update": self.handle_update,
            "delete": self.handle_delete,
            "history": self.handle_history,
            "play": self.handle_play
        }
        
        handler = handlers.get(parsed_args.command)
        if handler:
            try:
                return handler(parsed_args)
            except KeyboardInterrupt:
                print(MessageFormatter.info("\nOperation cancelled by user"))
                return 130  # Standard exit code for SIGINT
        else:
            print(MessageFormatter.error(f"Unknown command: {parsed_args.command}"))
            return 1

def main():
    """Main entry point"""
    try:
        cli = SongsCLI()
        exit_code = cli.run()
        sys.exit(exit_code)
        
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        print(MessageFormatter.error(f"Fatal error: {e}"))
        sys.exit(1)

if __name__ == "__main__":
    main()

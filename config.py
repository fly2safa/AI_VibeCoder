"""
Configuration management for Songs CLI application
"""

import os
from dataclasses import dataclass
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

@dataclass
class DatabaseConfig:
    """Database configuration settings"""
    connection_string: str
    database_name: str = "songs_db"
    connection_timeout: int = 5000
    server_selection_timeout: int = 5000
    socket_timeout: int = 5000

@dataclass
class AppConfig:
    """Application configuration settings"""
    log_level: str = "INFO"
    max_history_entries: int = 100
    default_list_limit: int = 50

class Config:
    """Main configuration class"""
    
    def __init__(self):
        self._validate_environment()
        
        self.database = DatabaseConfig(
            connection_string=os.getenv('project_db_url'),
            database_name=os.getenv('DB_NAME', 'songs_db')
        )
        
        self.app = AppConfig(
            log_level=os.getenv('LOG_LEVEL', 'INFO'),
            max_history_entries=int(os.getenv('MAX_HISTORY_ENTRIES', '100')),
            default_list_limit=int(os.getenv('DEFAULT_LIST_LIMIT', '50'))
        )
    
    def _validate_environment(self):
        """Validate required environment variables"""
        required_vars = ['project_db_url']
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        
        if missing_vars:
            raise ValueError(
                f"Missing required environment variables: {', '.join(missing_vars)}\n"
                "Please check your .env file or environment configuration."
            )

# Global config instance
config = Config()

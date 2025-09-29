# Songs CLI Application - Refactored Version 🎵

A modern, modular Python CLI application for managing songs with MongoDB backend. This refactored version features improved architecture, better error handling, and enhanced maintainability.

## 🚀 What's New in the Refactored Version

### ✨ **Modular Architecture**
- **Separation of Concerns**: Clear separation between database, business logic, and CLI layers
- **Reusable Components**: Each module can be used independently
- **Better Testing**: Easier to unit test individual components

### 🏗️ **Project Structure**
```
songs_cli_refactored/
├── config.py              # Configuration management
├── models.py               # Data models (Song, HistoryEntry)
├── database.py             # Database operations and connection management
├── services.py             # Business logic services
├── formatters.py           # Output formatting utilities
├── cli.py                  # Command-line interface
├── songs_cli_refactored.py # Main entry point
├── __init__.py             # Package initialization
└── requirements_refactored.txt # Dependencies
```

### 🔧 **Key Improvements**

1. **Configuration Management**
   - Centralized configuration in `config.py`
   - Environment variable validation
   - Type-safe configuration with dataclasses

2. **Data Models with Validation**
   - `Song` and `HistoryEntry` models with built-in validation
   - Type hints throughout the codebase
   - Automatic timestamp management

3. **Robust Database Layer**
   - Context manager for database operations
   - Comprehensive error handling
   - Connection pooling and timeout management
   - Automatic index creation

4. **Service Layer**
   - Clean separation of business logic
   - Consistent error handling
   - Automatic history logging
   - Future-ready for additional features

5. **Enhanced CLI**
   - Better argument parsing
   - Improved error messages
   - Confirmation prompts for destructive operations
   - Verbose mode support
   - Table format for large lists

6. **Professional Formatting**
   - Consistent output formatting
   - Color-coded messages
   - Multiple display formats (list, table)

## 📦 Installation

```bash
# Install dependencies
pip install -r requirements_refactored.txt

# Set up environment (use existing .env file)
# Make sure your .env file has: project_db_url=mongodb+srv://...
```

## 🎯 Usage

### Basic Commands
```bash
# Add a song
python songs_cli_refactored.py --user Jo add --title "Bohemian Rhapsody" --artist "Queen" --genre "Rock" --year 1975

# List songs
python songs_cli_refactored.py --user Jo list

# List in table format
python songs_cli_refactored.py --user Jo list --table

# Search songs
python songs_cli_refactored.py --user Jo search "Queen"

# Get specific song
python songs_cli_refactored.py --user Jo get <song_id>

# Update song
python songs_cli_refactored.py --user Jo update <song_id> --title "New Title"

# Delete song (with confirmation)
python songs_cli_refactored.py --user Jo delete <song_id>

# Delete song (skip confirmation)
python songs_cli_refactored.py --user Jo delete <song_id> --confirm

# View history
python songs_cli_refactored.py --user Jo history

# Play song (logs play action)
python songs_cli_refactored.py --user Jo play <song_id>
```

### Advanced Options
```bash
# Verbose output
python songs_cli_refactored.py --user Jo --verbose list

# List all users' songs
python songs_cli_refactored.py --user Jo list --all

# Limit results
python songs_cli_refactored.py --user Jo list --limit 5

# Extended history
python songs_cli_refactored.py --user Jo history --limit 20
```

## 🏛️ Architecture Overview

### 1. **Configuration Layer** (`config.py`)
- Manages all application settings
- Validates environment variables
- Provides type-safe configuration objects

### 2. **Data Layer** (`models.py`)
- Defines `Song` and `HistoryEntry` data models
- Built-in validation and serialization
- Type hints for better IDE support

### 3. **Database Layer** (`database.py`)
- Handles all MongoDB operations
- Connection management with context managers
- Comprehensive error handling
- Automatic indexing for performance

### 4. **Service Layer** (`services.py`)
- Contains business logic
- `SongsService` for CRUD operations
- `PlaybackService` for future enhancements
- Automatic history logging

### 5. **Presentation Layer** (`formatters.py`, `cli.py`)
- `formatters.py`: Output formatting utilities
- `cli.py`: Command-line interface logic
- Clean separation of concerns

## 🔒 Error Handling

The refactored version includes comprehensive error handling:

- **Configuration Errors**: Missing environment variables
- **Validation Errors**: Invalid song data
- **Database Errors**: Connection issues, invalid queries
- **User Errors**: Invalid commands, missing arguments

## 🔄 Compatibility with Original Version

Both versions work side by side:

- **Original**: `python songs_cli.py --user Jo add --title "Song" --artist "Artist"`
- **Refactored**: `python songs_cli_refactored.py --user Jo add --title "Song" --artist "Artist"`

Same database, same functionality, improved architecture!

## 🚀 Future Enhancements

The modular architecture enables easy addition of:

- **Playlist Management**: Create and manage playlists
- **Music Streaming**: Integration with streaming services
- **Recommendations**: AI-powered song recommendations
- **Web Interface**: REST API and web frontend
- **Mobile App**: React Native or Flutter app
- **Analytics**: Usage statistics and insights

## 🤝 Contributing

The refactored codebase follows Python best practices:

- **PEP 8**: Code style compliance
- **Type Hints**: Full type annotation
- **Docstrings**: Comprehensive documentation
- **Modular Design**: Easy to extend and maintain

## 📊 Performance Improvements

- **Database Indexing**: Automatic index creation for fast queries
- **Connection Pooling**: Efficient database connections
- **Lazy Loading**: Load data only when needed
- **Caching**: Future-ready for caching layers

## 🔧 Development Tools

Recommended development setup:

```bash
# Code formatting
black .

# Linting
flake8 .

# Type checking
mypy .

# Testing (when test files are created)
pytest --cov=. tests/
```

---

**The refactored version maintains all original functionality while providing a solid foundation for future enhancements and easier maintenance. Perfect for archiving as a professional-grade CLI application!**

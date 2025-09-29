# Songs CLI - Architecture Documentation

## Overview

The Songs CLI application follows a layered architecture pattern with clear separation of concerns. This document outlines the architectural decisions and design patterns used in the refactored version.

## Architecture Layers

### 1. Configuration Layer
**File**: `config.py`

**Purpose**: Centralized configuration management

**Components**:
- `DatabaseConfig`: Database connection settings
- `AppConfig`: Application-level settings
- `Config`: Main configuration class with validation

**Key Features**:
- Environment variable validation
- Type-safe configuration with dataclasses
- Default value management
- Error handling for missing configuration

### 2. Data Model Layer
**File**: `models.py`

**Purpose**: Data representation and validation

**Components**:
- `Song`: Song entity with validation
- `HistoryEntry`: User action tracking

**Key Features**:
- Built-in data validation
- Automatic timestamp management
- MongoDB serialization/deserialization
- Type hints for IDE support

### 3. Database Layer
**File**: `database.py`

**Purpose**: Data persistence and database operations

**Components**:
- `SongsDatabase`: Core database operations
- `DatabaseManager`: Context manager for connections
- `DatabaseError`: Custom exception handling

**Key Features**:
- Connection pooling and timeout management
- Automatic index creation
- Context manager pattern for resource management
- Comprehensive error handling
- Query optimization

### 4. Service Layer
**File**: `services.py`

**Purpose**: Business logic and orchestration

**Components**:
- `SongsService`: Core CRUD operations
- `PlaybackService`: Future enhancement placeholder

**Key Features**:
- Business rule enforcement
- Automatic history logging
- Transaction management
- Error propagation and handling

### 5. Presentation Layer
**Files**: `formatters.py`, `cli.py`

**Purpose**: User interface and output formatting

**Components**:
- `SongFormatter`: Song display formatting
- `HistoryFormatter`: History display formatting
- `MessageFormatter`: System message formatting
- `SongsCLI`: Command-line interface

**Key Features**:
- Multiple output formats (list, table)
- Consistent message formatting
- Interactive prompts
- Command routing and validation

## Design Patterns

### 1. Context Manager Pattern
Used in `DatabaseManager` for automatic resource cleanup:

```python
with DatabaseManager() as db:
    # Database operations
    pass  # Connection automatically closed
```

### 2. Factory Pattern
Used in model classes for object creation:

```python
song = Song.from_dict(data)
entry = HistoryEntry.from_dict(data)
```

### 3. Strategy Pattern
Used in formatters for different output strategies:

```python
# Different formatting strategies
SongFormatter.format_song_list(songs)
SongFormatter.format_song_table(songs)
```

### 4. Command Pattern
Used in CLI for command handling:

```python
handlers = {
    "add": self.handle_add,
    "list": self.handle_list,
    # ...
}
```

## Data Flow

### 1. Command Processing Flow
```
CLI Input → Argument Parsing → Command Handler → Service Layer → Database Layer → Response
```

### 2. Error Handling Flow
```
Database Error → Service Layer → CLI Handler → User Message
```

### 3. Data Validation Flow
```
User Input → Model Validation → Service Validation → Database Storage
```

## Database Design

### Collections

#### Songs Collection
```json
{
  "_id": "ObjectId",
  "title": "string",
  "artist": "string",
  "genre": "string (optional)",
  "year": "number (optional)",
  "duration": "number (optional, seconds)",
  "username": "string",
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

#### History Collection
```json
{
  "_id": "ObjectId",
  "username": "string",
  "action": "string (added|updated|deleted|played|viewed)",
  "song_title": "string",
  "song_artist": "string",
  "timestamp": "datetime"
}
```

### Indexes
- Songs: `title`, `artist`, `username`, `(username, title, artist)`
- History: `username`, `timestamp`, `(username, timestamp)`

## Error Handling Strategy

### 1. Exception Hierarchy
```
Exception
├── ValueError (validation errors)
├── DatabaseError (custom database errors)
│   ├── ConnectionFailure
│   ├── ServerSelectionTimeoutError
│   └── InvalidId
└── KeyboardInterrupt (user cancellation)
```

### 2. Error Propagation
- Database Layer: Catches MongoDB exceptions, raises DatabaseError
- Service Layer: Catches validation/business logic errors
- CLI Layer: Catches all exceptions, formats user messages

### 3. Logging Strategy
- DEBUG: Detailed operation logs
- INFO: Major operations (connect, add, update, delete)
- WARNING: Non-critical issues (unusual actions)
- ERROR: Operation failures

## Configuration Management

### Environment Variables
- `project_db_url`: MongoDB connection string (required)
- `DB_NAME`: Database name (optional, default: 'songs_db')
- `LOG_LEVEL`: Logging level (optional, default: 'INFO')
- `MAX_HISTORY_ENTRIES`: History limit (optional, default: 100)
- `DEFAULT_LIST_LIMIT`: Default list limit (optional, default: 50)

### Configuration Validation
- Required variables checked at startup
- Type conversion with defaults
- Clear error messages for missing configuration

## Testing Strategy

### Unit Testing
- Model validation testing
- Service layer business logic testing
- Formatter output testing

### Integration Testing
- Database operations testing
- End-to-end CLI testing
- Error handling testing

### Test Structure
```
tests/
├── test_models.py
├── test_database.py
├── test_services.py
├── test_formatters.py
├── test_cli.py
└── conftest.py (pytest fixtures)
```

## Performance Considerations

### Database Optimization
- Automatic index creation
- Query optimization with proper indexes
- Connection pooling
- Timeout management

### Memory Management
- Context managers for resource cleanup
- Lazy loading where appropriate
- Efficient data structures

### Scalability
- Modular architecture for horizontal scaling
- Stateless service design
- Database-agnostic service layer

## Security Considerations

### Input Validation
- Model-level validation
- SQL injection prevention (MongoDB)
- Input sanitization

### Configuration Security
- Environment variable usage
- No hardcoded credentials
- Connection string validation

### Error Information
- No sensitive data in error messages
- Sanitized logging output

## Future Enhancements

### Planned Features
1. **Playlist Management**: Additional models and services
2. **User Authentication**: User management layer
3. **REST API**: Web service layer
4. **Caching**: Redis integration
5. **Analytics**: Reporting services

### Architecture Extensions
1. **Message Queue**: Async processing
2. **Microservices**: Service decomposition
3. **Event Sourcing**: Event-driven architecture
4. **CQRS**: Command/Query separation

## Deployment Considerations

### Environment Setup
- Virtual environment management
- Dependency management
- Configuration management

### Monitoring
- Application logging
- Performance metrics
- Error tracking

### Maintenance
- Database migrations
- Backup strategies
- Update procedures

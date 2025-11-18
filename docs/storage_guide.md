# Storage Guide

This guide explains the storage abstraction layer in telegram-bot-stack and how to choose and use different storage backends.

## Overview

The telegram-bot-stack framework provides a unified storage interface that allows you to switch between different storage backends without changing your bot code. This enables smooth scaling from development to production.

### Available Backends

| Backend           | Type       | Use Case                | Persistence | Performance |
| ----------------- | ---------- | ----------------------- | ----------- | ----------- |
| **MemoryStorage** | In-memory  | Testing, temporary data | No          | Fastest     |
| **JSONStorage**   | File-based | Development, small bots | Yes         | Fast        |
| **SQLStorage**    | Database   | Production, large bots  | Yes         | Scalable    |

## Storage Interface

All storage backends implement the same interface (`StorageBackend`):

```python
from telegram_bot_stack.storage import StorageBackend

# All backends support these methods:
storage.save(key: str, data: Any) -> bool
storage.load(key: str, default: Any = None) -> Any
storage.exists(key: str) -> bool
storage.delete(key: str) -> bool
```

## MemoryStorage

In-memory storage for testing and temporary data. Data is lost when the bot stops.

### When to Use

- Unit testing
- Development without persistence needs
- Temporary caching
- CI/CD environments

### Usage

```python
from telegram_bot_stack.storage import create_storage, MemoryStorage

# Using factory
storage = create_storage("memory")

# Or direct instantiation
storage = MemoryStorage()

# Use the storage
storage.save("users", {"user1": {"name": "John"}})
data = storage.load("users")
```

### Pros & Cons

**Pros:**

- Fastest performance
- No file system or database setup
- Perfect for testing

**Cons:**

- No persistence
- Data lost on restart
- Limited by RAM

## JSONStorage

File-based storage using JSON files. Each key is stored in a separate `.json` file.

### When to Use

- Development and prototyping
- Small to medium bots (<10k users)
- Simple deployment without database
- Local testing with persistence

### Usage

```python
from telegram_bot_stack.storage import create_storage, JSONStorage

# Using factory
storage = create_storage("json", base_dir="data")

# Or direct instantiation
storage = JSONStorage(base_dir="data")

# Use the storage
storage.save("users", {"user1": {"name": "John"}})
data = storage.load("users")
```

### File Structure

```
data/
├── users.json
├── admins.json
└── settings.json
```

### Pros & Cons

**Pros:**

- Simple setup (no database required)
- Human-readable files
- Easy to inspect and debug
- Good for small bots

**Cons:**

- Not suitable for high concurrency
- Performance degrades with large files
- No transactions or atomic operations
- Limited query capabilities

## SQLStorage

SQL database storage using SQLAlchemy. Supports SQLite and PostgreSQL.

### When to Use

- Production deployments
- Large bots (>10k users)
- High concurrency requirements
- Need for transactions and data integrity
- Complex data queries

### Installation

```bash
# SQLite support (included by default)
pip install telegram-bot-stack[database]

# PostgreSQL support
pip install telegram-bot-stack[database,postgres]
```

### Usage - SQLite

Perfect for production bots with moderate scale:

```python
from telegram_bot_stack.storage import create_storage, SQLStorage

# Using factory with default SQLite database
storage = create_storage("sqlite")  # Creates bot.db

# Or specify custom database file
storage = create_storage("sqlite", database_url="sqlite:///mybot.db")

# Or direct instantiation
storage = SQLStorage(database_url="sqlite:///bot.db")

# Use the storage (same interface!)
storage.save("users", {"user1": {"name": "John"}})
data = storage.load("users")
```

### Usage - PostgreSQL

For large-scale production deployments:

```python
from telegram_bot_stack.storage import create_storage

# Using factory
storage = create_storage(
    "postgres",
    database_url="postgresql://user:password@localhost/bot_db",
    pool_size=10,
    max_overflow=20
)

# Or direct instantiation
from telegram_bot_stack.storage import SQLStorage

storage = SQLStorage(
    database_url="postgresql://user:password@localhost/bot_db",
    pool_size=10,
    max_overflow=20
)
```

### Configuration Options

```python
storage = SQLStorage(
    database_url="sqlite:///bot.db",  # Required: database URL
    echo=False,                        # Optional: log SQL queries
    pool_size=5,                       # Optional: connection pool size (PostgreSQL)
    max_overflow=10                    # Optional: max overflow connections (PostgreSQL)
)
```

### Database Schema

SQLStorage automatically creates this table:

```sql
CREATE TABLE storage (
    key VARCHAR(255) PRIMARY KEY,
    data TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Pros & Cons

**Pros:**

- Production-ready with transactions
- Excellent concurrency support
- Scalable to millions of records
- ACID guarantees
- Connection pooling (PostgreSQL)
- Backup and replication support

**Cons:**

- Requires database setup
- More complex deployment
- Slightly slower than JSON for small data

## Choosing a Backend

### Development Flow

```
MemoryStorage (testing) → JSONStorage (development) → SQLStorage (production)
```

### Decision Matrix

| Requirement            | Recommended Backend   |
| ---------------------- | --------------------- |
| Unit testing           | MemoryStorage         |
| Local development      | JSONStorage           |
| <1k users              | JSONStorage           |
| 1k-10k users           | JSONStorage or SQLite |
| >10k users             | SQLite or PostgreSQL  |
| High concurrency       | SQLite or PostgreSQL  |
| Distributed deployment | PostgreSQL            |
| Simple deployment      | JSONStorage or SQLite |

## Migration Between Backends

### Switching Backends in Code

The beauty of the storage abstraction is that you only need to change one line:

```python
# Development with JSON
storage = create_storage("json", base_dir="data")

# Production with SQLite (just change this line!)
storage = create_storage("sqlite", database_url="sqlite:///bot.db")

# All your bot code remains the same!
bot = MyBot(storage=storage)
```

### Migrating Data: JSON → SQL

Use the included migration tool:

```bash
# Dry run (preview migration)
python scripts/migrate_json_to_sql.py \
    --json-dir data \
    --database-url sqlite:///bot.db \
    --dry-run

# Actual migration
python scripts/migrate_json_to_sql.py \
    --json-dir data \
    --database-url sqlite:///bot.db

# Verify migration
python scripts/migrate_json_to_sql.py \
    --json-dir data \
    --database-url sqlite:///bot.db \
    --verify
```

### Migration to PostgreSQL

```bash
# Migrate to PostgreSQL
python scripts/migrate_json_to_sql.py \
    --json-dir data \
    --database-url postgresql://user:pass@localhost/bot_db \
    --verbose
```

## Best Practices

### 1. Use Factory Function

Prefer `create_storage()` over direct instantiation for flexibility:

```python
# Good: Easy to switch backends via config
backend = os.getenv("STORAGE_BACKEND", "json")
storage = create_storage(backend, base_dir="data")

# Less flexible: Hard-coded backend
storage = JSONStorage(base_dir="data")
```

### 2. Environment-Based Configuration

```python
import os
from telegram_bot_stack.storage import create_storage

# Determine backend from environment
if os.getenv("ENV") == "production":
    storage = create_storage(
        "postgres",
        database_url=os.getenv("DATABASE_URL")
    )
elif os.getenv("ENV") == "development":
    storage = create_storage("json", base_dir="data")
else:
    storage = create_storage("memory")  # Testing
```

### 3. Close SQL Connections

Always close SQL storage when done (especially in long-running apps):

```python
storage = SQLStorage(database_url="sqlite:///bot.db")

try:
    # Use storage
    storage.save("key", data)
finally:
    storage.close()  # Clean up connections
```

Or use context manager pattern in your bot:

```python
class MyBot(BotBase):
    def shutdown(self):
        """Called when bot stops."""
        if hasattr(self.storage, 'close'):
            self.storage.close()
        super().shutdown()
```

### 4. Handle Optional Dependencies

```python
from telegram_bot_stack.storage import create_storage

try:
    storage = create_storage("sqlite", database_url="sqlite:///bot.db")
except ImportError:
    print("SQLStorage not available. Install with: pip install telegram-bot-stack[database]")
    storage = create_storage("json", base_dir="data")
```

### 5. Data Structure Consistency

All backends store data as JSON-serializable structures. Keep your data consistent:

```python
# Good: JSON-serializable
storage.save("users", {
    "user1": {"name": "John", "age": 30},
    "user2": {"name": "Jane", "age": 25}
})

# Bad: Non-serializable objects
storage.save("users", {
    "user1": User(name="John")  # Custom class won't serialize
})
```

## Performance Considerations

### MemoryStorage

- **Read/Write**: O(1) - Instant
- **Memory**: Limited by RAM
- **Concurrency**: Thread-safe with locks

### JSONStorage

- **Read**: O(n) - Loads entire file
- **Write**: O(n) - Writes entire file
- **Disk**: One file per key
- **Concurrency**: File system dependent

### SQLStorage

- **Read**: O(log n) - Indexed lookup
- **Write**: O(log n) - Indexed insert/update
- **Disk**: Efficient storage with indexes
- **Concurrency**: Excellent with connection pooling

### Benchmarks (Approximate)

| Operation       | Memory | JSON | SQLite | PostgreSQL |
| --------------- | ------ | ---- | ------ | ---------- |
| Save 1KB        | <1ms   | 5ms  | 2ms    | 3ms        |
| Load 1KB        | <1ms   | 5ms  | 2ms    | 3ms        |
| Save 100KB      | <1ms   | 50ms | 10ms   | 15ms       |
| Load 100KB      | <1ms   | 50ms | 10ms   | 15ms       |
| 1000 operations | 10ms   | 5s   | 2s     | 3s         |

## Troubleshooting

### SQLite "database is locked" Error

This occurs with high concurrency. Solutions:

1. Use PostgreSQL for high concurrency
2. Increase SQLite timeout:
   ```python
   storage = SQLStorage(
       database_url="sqlite:///bot.db?timeout=30"
   )
   ```

### PostgreSQL Connection Pool Exhausted

Increase pool size:

```python
storage = SQLStorage(
    database_url="postgresql://...",
    pool_size=20,      # Increase from default 5
    max_overflow=40    # Increase from default 10
)
```

### JSON Files Growing Too Large

Switch to SQL storage:

```bash
# Migrate to SQLite
python scripts/migrate_json_to_sql.py \
    --json-dir data \
    --database-url sqlite:///bot.db
```

### Import Error: SQLStorage Not Available

Install database dependencies:

```bash
pip install telegram-bot-stack[database]
```

## Examples

### Example 1: Simple Bot with JSON Storage

```python
from telegram_bot_stack import BotBase
from telegram_bot_stack.storage import create_storage

storage = create_storage("json", base_dir="data")
bot = BotBase(token="YOUR_TOKEN", storage=storage, admin_ids=[123456])

# Bot automatically uses storage for users and admins
bot.run()
```

### Example 2: Production Bot with PostgreSQL

```python
import os
from telegram_bot_stack import BotBase
from telegram_bot_stack.storage import create_storage

storage = create_storage(
    "postgres",
    database_url=os.getenv("DATABASE_URL"),
    pool_size=10
)

bot = BotBase(
    token=os.getenv("BOT_TOKEN"),
    storage=storage,
    admin_ids=[int(os.getenv("ADMIN_ID"))]
)

try:
    bot.run()
finally:
    storage.close()
```

### Example 3: Testing with Memory Storage

```python
import pytest
from telegram_bot_stack import BotBase
from telegram_bot_stack.storage import create_storage

@pytest.fixture
def bot():
    storage = create_storage("memory")
    return BotBase(token="test_token", storage=storage, admin_ids=[123])

def test_user_registration(bot):
    bot.user_manager.add_user(456)
    assert bot.user_manager.user_exists(456)
```

## See Also

- [API Reference](api_reference.md) - Full storage API documentation
- [Quickstart Guide](quickstart.md) - Getting started with the framework
- [Migration Guide](migration_guide.md) - Migrating from Phase 0
- [Examples](../examples/) - Example bots using different storage backends

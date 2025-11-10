# Scripts Directory

Utility scripts for managing the ICCT26 backend.

## Available Scripts

### migrate_to_neon.py
Database migration script for Neon PostgreSQL setup.

**Purpose:** Initialize database schema and create tables

**Usage:**
```bash
python scripts/migrate_to_neon.py
```

**What it does:**
1. Loads database URL from environment variables (.env.local)
2. Creates connection to Neon database
3. Creates `teams` table with proper schema
4. Creates `players` table with proper schema
5. Sets up indexes for performance
6. Verifies tables were created successfully

**Requirements:**
- `.env.local` file with DATABASE_URL set
- Neon project created and active
- Network access to Neon database

**Output:**
```
✅ Database tables initialized
✅ Teams table created
✅ Players table created
```

**Troubleshooting:**
- If SSL error: Verify DATABASE_URL includes `ssl=require`
- If connection timeout: Check .env.local DATABASE_URL
- If tables already exist: Script will verify and continue

## How to Add New Scripts

1. Create Python file in this directory: `script_name.py`
2. Add shebang at top: `#!/usr/bin/env python3`
3. Add docstring explaining purpose
4. Add usage instructions here in README.md

## Running Scripts

### From root directory:
```bash
python scripts/script_name.py
```

### From tests directory:
```bash
python ../scripts/script_name.py
```

### Within virtual environment:
```bash
venv\Scripts\activate  # Windows
python scripts/script_name.py
```

## Common Patterns

### Accessing configuration:
```python
import os
from dotenv import load_dotenv

load_dotenv('.env.local')
db_url = os.environ.get('DATABASE_URL')
```

### Async database operations:
```python
import asyncio
from database import async_engine, async_session

async def do_something():
    async with async_session() as session:
        # Database operations here
        pass

asyncio.run(do_something())
```

### Error handling:
```python
try:
    # Script operations
    pass
except Exception as e:
    print(f"❌ Error: {e}")
    exit(1)
print("✅ Success!")
```

## Scripts List

| Script | Purpose | Frequency |
|--------|---------|-----------|
| migrate_to_neon.py | Initialize database schema | Once per environment |

---

**Add new scripts as needed for common tasks.**

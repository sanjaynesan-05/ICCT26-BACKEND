# ICCT26 Backend - Simple PostgreSQL Integration

## ✅ Project Successfully Created!

This is a clean, working FastAPI backend connected to PostgreSQL 17.

### 📂 Project Structure
```
ICCT26-BACKEND/
├── database.py         # SQLAlchemy database configuration
├── models.py           # ORM models (Team table)
├── init_db.py          # Database initialization script
├── simple_main.py      # FastAPI application
├── scripts/
│   └── test_simple_api.py  # API test script
└── venv/               # Virtual environment
```

### ⚙️ Database Configuration
- **Database**: `icct26_db`
- **User**: `postgres`
- **Password**: `icctpg`
- **Host**: `localhost`
- **Port**: `5432`

### 🚀 Quick Start

#### 1. Install Dependencies
```bash
pip install fastapi uvicorn psycopg2-binary sqlalchemy
```

#### 2. Initialize Database
```bash
python init_db.py
```

#### 3. Run the Server
```bash
uvicorn simple_main:app --reload --port 8001
```

#### 4. Test the API
```bash
python scripts/test_simple_api.py
```

### 🌐 API Endpoints

#### GET `/`
Root endpoint - health check

**Response:**
```json
{
  "message": "ICCT26 Backend connected to PostgreSQL successfully"
}
```

#### POST `/register/team`
Register a new cricket team

**Parameters:**
- `name` (string): Team name
- `captain` (string): Captain name

**Example Request:**
```bash
curl -X POST "http://localhost:8001/register/team?name=Warriors&captain=John%20Doe"
```

**Response:**
```json
{
  "id": 1,
  "name": "Warriors",
  "captain": "John Doe"
}
```

### 📊 Database Schema

#### teams Table
| Column | Type | Description |
|--------|------|-------------|
| id | Integer | Primary key (auto-increment) |
| name | String(100) | Team name (not null) |
| captain | String(100) | Captain name (not null) |
| registered_on | DateTime | Registration timestamp (auto) |

### 🧪 Testing

#### Using Swagger UI
Open your browser: http://localhost:8001/docs

#### Using psql
```bash
psql -U postgres -d icct26_db
```

```sql
-- View all teams
SELECT * FROM teams;

-- View table structure
\d teams

-- Count teams
SELECT COUNT(*) FROM teams;
```

### ✅ Verification Results

**Test Output:**
```
✅ Root endpoint working
✅ Team registration successful
✅ Data saved to PostgreSQL
✅ Auto-increment ID working
✅ Timestamp auto-generated
```

**Database Verification:**
```
 id |       name        |  captain   |          registered_on
----+-------------------+------------+----------------------------------
  1 | Test Warriors     | John Doe   | 2025-11-05 15:14:23.77741+05:30
  2 | Cricket Champions | Jane Smith | 2025-11-05 15:14:25.833467+05:30
```

### 🔧 Key Components

#### database.py
- Handles PostgreSQL connection using SQLAlchemy
- Creates database engine and session
- Provides `Base` class for ORM models

#### models.py
- Defines the `Team` model
- Maps Python class to PostgreSQL table
- Includes auto-timestamp functionality

#### simple_main.py
- FastAPI application setup
- Dependency injection for database sessions
- REST API endpoints for team registration

#### init_db.py
- One-time database initialization
- Creates all tables from models
- Must be run before starting the API

### 💡 Next Steps

1. **Add More Models**: Create `Player`, `Match`, `Score` models following the same pattern

2. **Add GET Endpoints**: 
   ```python
   @app.get("/teams")
   def get_teams(db: Session = Depends(get_db)):
       return db.query(Team).all()
   ```

3. **Add Validation**: Use Pydantic models for request/response validation

4. **Add Relationships**: Link players to teams with foreign keys

5. **Add Authentication**: Secure endpoints with JWT tokens

### 🎯 Production Deployment

- Set up environment variables for database credentials
- Use connection pooling for better performance
- Add database migrations with Alembic
- Implement proper error handling and logging
- Set up CORS for frontend integration

---

**Server Status**: ✅ Running on http://localhost:8001
**Database**: ✅ Connected to PostgreSQL 17
**API Docs**: http://localhost:8001/docs

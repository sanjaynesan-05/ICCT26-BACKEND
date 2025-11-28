# Database Schema - Match Score URL Field

## Updated PostgreSQL Schema

### Matches Table
```sql
CREATE TABLE matches (
    id SERIAL PRIMARY KEY,
    round VARCHAR(50) NOT NULL,
    round_number INTEGER NOT NULL,
    match_number INTEGER NOT NULL,
    team1_id INTEGER NOT NULL REFERENCES teams(id) ON DELETE RESTRICT,
    team2_id INTEGER NOT NULL REFERENCES teams(id) ON DELETE RESTRICT,
    status VARCHAR(20) NOT NULL DEFAULT 'scheduled',
    
    -- Toss Details
    toss_winner_id INTEGER REFERENCES teams(id) ON DELETE SET NULL,
    toss_choice VARCHAR(10),
    
    -- Match Timing
    scheduled_start_time TIMESTAMP,
    actual_start_time TIMESTAMP,
    match_end_time TIMESTAMP,
    
    -- Innings Scores
    team1_first_innings_score INTEGER,
    team2_first_innings_score INTEGER,
    team1_second_innings_score INTEGER,
    team2_second_innings_score INTEGER,
    
    -- Match Score URL (NEW FIELD)
    match_score_url VARCHAR(500),
    
    -- Match Result
    winner_id INTEGER REFERENCES teams(id) ON DELETE SET NULL,
    margin INTEGER,
    margin_type VARCHAR(20),
    won_by_batting_first BOOLEAN,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraints
    UNIQUE(round_number, match_number),
    CONSTRAINT chk_status CHECK (status IN ('scheduled', 'live', 'completed'))
);

-- Indexes
CREATE INDEX idx_match_status ON matches(status);
CREATE INDEX idx_match_round ON matches(round_number);
CREATE INDEX idx_match_team1 ON matches(team1_id);
CREATE INDEX idx_match_team2 ON matches(team2_id);
CREATE INDEX idx_match_score_url ON matches(match_score_url);
```

## New Field Specification

### Column Definition
```sql
match_score_url VARCHAR(500) NULL
```

### Properties
| Property | Value |
|----------|-------|
| Column Name | match_score_url |
| Data Type | VARCHAR(500) |
| Nullable | YES (NULL allowed) |
| Default | NULL |
| Max Length | 500 characters |
| Index | Yes (idx_match_score_url) |
| Foreign Key | No |
| Unique | No |

## Migration Applied

### Migration Command
```sql
ALTER TABLE matches
ADD COLUMN match_score_url VARCHAR(500) NULL;

CREATE INDEX idx_match_score_url ON matches(match_score_url);
```

### Status
✅ Successfully applied to production database (Neon PostgreSQL)

## Sample Data

### Before (match_score_url is NULL)
```sql
SELECT id, team1_id, team2_id, match_score_url 
FROM matches 
WHERE id = 1;

-- Result:
-- id | team1_id | team2_id | match_score_url
-- 1  | 1        | 2        | NULL
```

### After (match_score_url is SET)
```sql
UPDATE matches 
SET match_score_url = 'https://cricketlive.example.com/match/123/scorecard'
WHERE id = 1;

SELECT id, team1_id, team2_id, match_score_url 
FROM matches 
WHERE id = 1;

-- Result:
-- id | team1_id | team2_id | match_score_url
-- 1  | 1        | 2        | https://cricketlive.example.com/match/123/scorecard
```

## SQLAlchemy ORM Definition

```python
from sqlalchemy import Column, String

class Match(Base):
    __tablename__ = "matches"
    
    # ... other columns ...
    
    # Match Score URL (NEW)
    match_score_url = Column(String(500), nullable=True)
    
    # ... rest of class ...
```

## Query Examples

### Get match with URL
```sql
SELECT id, round, team1_id, team2_id, match_score_url
FROM matches
WHERE id = 1;
```

### Find matches with scorecard URLs
```sql
SELECT id, round, match_score_url
FROM matches
WHERE match_score_url IS NOT NULL
ORDER BY updated_at DESC;
```

### Update match scorecard URL
```sql
UPDATE matches
SET match_score_url = 'https://example.com/match/123/scorecard',
    updated_at = CURRENT_TIMESTAMP
WHERE id = 1;
```

### Clear match scorecard URL
```sql
UPDATE matches
SET match_score_url = NULL,
    updated_at = CURRENT_TIMESTAMP
WHERE id = 1;
```

### Find matches matching URL pattern
```sql
SELECT id, round, match_score_url
FROM matches
WHERE match_score_url LIKE '%cricketlive%'
ORDER BY created_at DESC;
```

## Backward Compatibility

✅ **Fully Backward Compatible:**
- New column is NULLABLE (default NULL)
- Existing matches unaffected
- No data loss
- No constraints that require field population
- Optional in API requests

## Database Validation

### Column Constraints
- Maximum 500 characters (matches application validation)
- Nullable (no default value required)
- No unique constraint (multiple matches can have same URL)
- No foreign key constraint

### Application Validation
- URL must start with http:// or https://
- Enforced at API schema level (Pydantic validation)
- Rejected before database update

## Performance Considerations

✅ **Index Created:**
```sql
CREATE INDEX idx_match_score_url ON matches(match_score_url);
```

**Benefits:**
- Fast lookups by URL
- Efficient filtering by URL patterns
- Optimized for queries searching URLs
- Minimal storage overhead (VARCHAR(500) index)

## Migration Verification

### Check if column exists
```sql
SELECT EXISTS (
    SELECT 1 FROM information_schema.columns 
    WHERE table_name='matches' AND column_name='match_score_url'
);
```

### Check column definition
```sql
SELECT column_name, data_type, is_nullable, character_maximum_length
FROM information_schema.columns
WHERE table_name='matches' AND column_name='match_score_url';
```

### Check index exists
```sql
SELECT indexname FROM pg_indexes
WHERE tablename='matches' AND indexname='idx_match_score_url';
```

## Related Columns

This field complements other match tracking columns:

| Column | Type | Purpose |
|--------|------|---------|
| scheduled_start_time | TIMESTAMP | When match is scheduled |
| actual_start_time | TIMESTAMP | When match actually started |
| match_end_time | TIMESTAMP | When match ended |
| team1_first_innings_score | INTEGER | Team 1 score |
| team2_first_innings_score | INTEGER | Team 2 score |
| match_score_url | VARCHAR(500) | **Link to scorecard** |

---

**Last Updated:** November 28, 2025  
**Status:** ✅ Migration Applied  
**Database:** Neon PostgreSQL

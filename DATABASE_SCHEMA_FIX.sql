# FIX DATABASE SCHEMA - SQL COMMANDS FOR RENDER
================================================

## ⚠️ PROBLEM IDENTIFIED

Your **code is correct** (uses Text columns), but your **database has old schema** (VARCHAR(20)).

## 🔧 SOLUTION: Run These SQL Commands

### Option 1: ALTER Existing Tables (Preserves Data)

Connect to your Render PostgreSQL database and run:

```sql
-- Fix Teams table
ALTER TABLE teams 
ALTER COLUMN payment_receipt TYPE text;

ALTER TABLE teams 
ALTER COLUMN pastor_letter TYPE text;

-- Fix Players table
ALTER TABLE players 
ALTER COLUMN aadhar_file TYPE text;

ALTER TABLE players 
ALTER COLUMN subscription_file TYPE text;

-- Verify changes
\d teams
\d players
```

### Option 2: Drop & Recreate (Testing Only - DELETES DATA!)

⚠️ **WARNING: This deletes all data!**

```sql
-- Drop existing tables
DROP TABLE players CASCADE;
DROP TABLE teams CASCADE;

-- Then restart your FastAPI backend
-- It will auto-create tables with the correct schema
```

---

## 📋 How to Run These Commands

### Method 1: Render Dashboard (Easiest)

1. Go to https://dashboard.render.com/
2. Select your PostgreSQL database
3. Click "Connect" → "External Connection"
4. Use psql or any SQL client:
   ```bash
   psql postgresql://[connection_string_from_render]
   ```
5. Paste the ALTER commands above
6. Type `\q` to exit

### Method 2: Render Shell

1. In Render dashboard → Database → Shell
2. Paste the ALTER commands
3. Press Enter to execute

### Method 3: SQL Editor (if available)

1. Use Render's built-in SQL editor
2. Paste and execute commands

---

## ✅ Verification

After running the ALTER commands:

```sql
-- Check column types
\d teams

-- Should show:
-- payment_receipt | text |
-- pastor_letter   | text |

\d players

-- Should show:
-- aadhar_file       | text |
-- subscription_file | text |
```

---

## 🧪 Test After Fix

```bash
# Test registration
POST https://icct26-backend.onrender.com/api/register/team

# Expected: ✅ 201 Created
# No more "value too long" errors!
```

---

## 📝 Why This Happened

1. Your original database was created with VARCHAR(20) columns
2. You updated models.py to use Text columns
3. But PostgreSQL doesn't auto-migrate existing tables
4. You need to manually ALTER the existing columns

---

## 🚀 Quick Commands for Copy-Paste

```sql
-- QUICK FIX (Run all at once)
ALTER TABLE teams ALTER COLUMN payment_receipt TYPE text;
ALTER TABLE teams ALTER COLUMN pastor_letter TYPE text;
ALTER TABLE players ALTER COLUMN aadhar_file TYPE text;
ALTER TABLE players ALTER COLUMN subscription_file TYPE text;
```

---

**Status:** Ready to execute
**Risk:** Low (ALTER is safe, preserves data)
**Time:** < 1 minute

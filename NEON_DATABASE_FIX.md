# FIX DATABASE SCHEMA IN NEON - COMPLETE GUIDE
============================================

## 🎯 Objective

Fix the `VARCHAR(20)` → `TEXT` column conversion for file uploads in your **Neon PostgreSQL** database.

---

## 🔧 Method 1: Neon Console (Easiest - Recommended)

### Step 1: Open Neon Dashboard

1. Go to https://console.neon.tech/
2. Sign in to your account
3. Select your project (ICCT26 or similar)
4. Click on your **database** (usually `neondb` or your project name)

### Step 2: Open SQL Editor

1. Click **"SQL Editor"** tab (or **"Query Editor"**)
2. You'll see a text area for SQL commands

### Step 3: Run ALTER Commands

Copy and paste ALL 4 commands at once:

```sql
ALTER TABLE teams ALTER COLUMN payment_receipt TYPE text;
ALTER TABLE teams ALTER COLUMN pastor_letter TYPE text;
ALTER TABLE players ALTER COLUMN aadhar_file TYPE text;
ALTER TABLE players ALTER COLUMN subscription_file TYPE text;
```

### Step 4: Execute

Click **"Execute"** button (or press `Ctrl+Enter`)

### Step 5: Verify Success

You should see: **"Query executed successfully"** ✅

---

## 🔧 Method 2: psql Command Line

### Step 1: Get Neon Connection String

1. In Neon dashboard, go to **"Connection string"**
2. Copy the **"Connection string"** (looks like):
   ```
   postgresql://user:password@host/dbname
   ```

### Step 2: Connect via psql

Open your local terminal/PowerShell:

```bash
psql "postgresql://[user]:[password]@[host]/[dbname]?sslmode=require"
```

Replace the values from your Neon connection string.

### Step 3: Run ALTER Commands

```sql
ALTER TABLE teams ALTER COLUMN payment_receipt TYPE text;
ALTER TABLE teams ALTER COLUMN pastor_letter TYPE text;
ALTER TABLE players ALTER COLUMN aadhar_file TYPE text;
ALTER TABLE players ALTER COLUMN subscription_file TYPE text;
```

### Step 4: Verify

```sql
\d teams
\d players
```

You should see all file columns as `text` type. ✅

---

## 🔧 Method 3: Using DBeaver (GUI Tool)

### Step 1: Download & Install DBeaver

- Download from https://dbeaver.io/download/
- Install and open

### Step 2: Create Connection

1. Click **"New Database Connection"**
2. Select **PostgreSQL**
3. Fill in connection details from Neon:
   - **Server Host:** From Neon connection string
   - **Port:** 5432
   - **Database:** Your database name
   - **Username:** Your username
   - **Password:** Your password
   - **SSL:** Enable SSL (required for Neon)

### Step 3: Test Connection

Click **"Test Connection"** → Should succeed ✅

### Step 4: Run ALTER Commands

1. Right-click your database → **"SQL Editor"**
2. Paste all 4 ALTER commands
3. Click **"Execute"** (or Ctrl+Enter)

### Step 5: Verify

```sql
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'teams' 
AND column_name IN ('payment_receipt', 'pastor_letter');
```

Should show `text` type for both columns. ✅

---

## ✅ Verification Steps (All Methods)

After running ALTER commands, verify in Neon SQL Editor:

```sql
-- Check Teams table
SELECT column_name, data_type, character_maximum_length
FROM information_schema.columns
WHERE table_name = 'teams'
AND column_name IN ('payment_receipt', 'pastor_letter')
ORDER BY column_name;

-- Check Players table
SELECT column_name, data_type, character_maximum_length
FROM information_schema.columns
WHERE table_name = 'players'
AND column_name IN ('aadhar_file', 'subscription_file')
ORDER BY column_name;
```

**Expected Results:**
```
column_name      | data_type | character_maximum_length
-----------------|-----------|-----------------------
aadhar_file      | text      | (null)
pastor_letter    | text      | (null)
payment_receipt  | text      | (null)
subscription_file| text      | (null)
```

All should show `text` with `character_maximum_length = (null)` (meaning unlimited) ✅

---

## 🧪 Test After Fix

Once schema is updated, test your backend:

```bash
# Test team registration with Base64 files
curl -X POST https://icct26-backend.onrender.com/api/register/team \
  -H "Content-Type: application/json" \
  -d '{
    "team_name": "Test Team",
    "church_name": "Test Church",
    "captain_name": "John Doe",
    "captain_phone": "9876543210",
    "captain_email": "john@example.com",
    "captain_whatsapp": "9876543210",
    "vice_captain_name": "Jane Doe",
    "vice_captain_phone": "9876543210",
    "vice_captain_email": "jane@example.com",
    "vice_captain_whatsapp": "9876543210",
    "payment_receipt": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQEAYABgAAD/...",
    "pastor_letter": "data:application/pdf;base64,JVBERi0xLjQ..."
  }'
```

**Expected:**
- ✅ Status: `201 Created` or `200 OK`
- ✅ No "value too long" errors
- ✅ Files saved successfully
- ✅ Response includes new team data

---

## 📋 Neon Dashboard Quick Links

| Feature | URL |
|---------|-----|
| **Main Dashboard** | https://console.neon.tech/ |
| **SQL Editor** | Dashboard → SQL Editor tab |
| **Connection Info** | Dashboard → Connection string |
| **Database Settings** | Dashboard → Settings |

---

## ⚡ Quick Checklist

- [ ] Open Neon dashboard
- [ ] Go to SQL Editor
- [ ] Copy & paste all 4 ALTER commands
- [ ] Click Execute
- [ ] See "Query executed successfully"
- [ ] Verify columns are now `text` type
- [ ] Test registration with files
- [ ] Confirm no truncation errors
- [ ] Mark todo as complete ✅

---

## 🆘 Troubleshooting

### Issue: "Column does not exist"
**Cause:** Column names are different or typo  
**Solution:** Run verification query to see actual column names

### Issue: "Permission denied"
**Cause:** User doesn't have ALTER permission  
**Solution:** Use Neon owner/admin account

### Issue: "Cannot change TEXT back to VARCHAR"
**Cause:** Trying to reverse the change  
**Solution:** Not needed - keep as TEXT

### Issue: Still getting truncation errors after ALTER
**Cause:** Database not reloaded in application  
**Solution:** Restart your backend or clear connection pool

---

## 📝 SQL Commands for Copy-Paste

```sql
-- All 4 commands (run together)
ALTER TABLE teams ALTER COLUMN payment_receipt TYPE text;
ALTER TABLE teams ALTER COLUMN pastor_letter TYPE text;
ALTER TABLE players ALTER COLUMN aadhar_file TYPE text;
ALTER TABLE players ALTER COLUMN subscription_file TYPE text;
```

---

## ✅ After Successful Fix

Your database will now:
- ✅ Accept unlimited Base64 strings
- ✅ Store large files without truncation
- ✅ Support 5MB+ file uploads
- ✅ Handle JPEG, PNG, PDF formats
- ✅ Work with your FastAPI code

**Time to fix:** ~5 minutes
**Data loss:** None (ALTER preserves data)
**Downtime:** None (Neon handles transparently)

---

**Status:** Ready to execute
**Tool:** Neon SQL Editor (easiest)
**Risk:** Low
**Impact:** Immediate ✅

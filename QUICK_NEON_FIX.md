# 🚀 NEON DATABASE FIX - QUICK START GUIDE

## ⚡ 5-Minute Fix for VARCHAR(20) Truncation Error

### 🎯 Problem
```
PostgreSQL Error: value too long for type character varying(20)
```

Your **Neon database** has old `VARCHAR(20)` columns, but your code uses `Text`.

---

## ✅ Solution (Fastest Way)

### Step 1: Open Neon Console
```
https://console.neon.tech/
```

### Step 2: Go to SQL Editor
1. Select your project
2. Click **"SQL Editor"** tab
3. Paste these 4 commands:

```sql
ALTER TABLE teams ALTER COLUMN payment_receipt TYPE text;
ALTER TABLE teams ALTER COLUMN pastor_letter TYPE text;
ALTER TABLE players ALTER COLUMN aadhar_file TYPE text;
ALTER TABLE players ALTER COLUMN subscription_file TYPE text;
```

### Step 3: Execute
Click **"Execute"** or press `Ctrl+Enter`

### Step 4: Verify Success
You should see: **"Query executed successfully"** ✅

---

## 🧪 Test After Fix

```bash
# Your team registration will now work with large Base64 files!
POST https://icct26-backend.onrender.com/api/register/team

# Expected: ✅ 201 Created
# No more truncation errors!
```

---

## 📋 What This Does

| Column | Before | After |
|--------|--------|-------|
| `payment_receipt` | VARCHAR(20) ❌ | TEXT ✅ |
| `pastor_letter` | VARCHAR(20) ❌ | TEXT ✅ |
| `aadhar_file` | VARCHAR(20) ❌ | TEXT ✅ |
| `subscription_file` | VARCHAR(20) ❌ | TEXT ✅ |

Now all columns support **unlimited size** for Base64 files!

---

## 🎉 Done!

Your Neon database will now work perfectly with:
- ✅ Large Base64 image files
- ✅ PDF uploads
- ✅ Multiple files per team/player
- ✅ No truncation errors
- ✅ Production ready!

---

**Time:** 5 minutes  
**Risk:** None (preserves data)  
**Status:** Ready to fix!

-- ============================================
-- VERIFICATION SQL QUERIES
-- ============================================
-- Run these queries AFTER migration to verify all base64 has been converted to Cloudinary URLs

-- ============================================
-- 1. CHECK TEAMS TABLE
-- ============================================

-- Check if pastor_letter contains URLs (should all be Cloudinary URLs)
SELECT 
    team_id,
    CASE 
        WHEN pastor_letter IS NULL THEN 'NULL'
        WHEN pastor_letter LIKE 'https://res.cloudinary.com/%' THEN 'CLOUDINARY_URL'
        WHEN pastor_letter LIKE 'data:%' THEN 'BASE64 (NOT MIGRATED!)'
        ELSE 'UNKNOWN'
    END as pastor_letter_status,
    LENGTH(pastor_letter) as pastor_letter_length,
    SUBSTRING(pastor_letter, 1, 50) as pastor_letter_preview
FROM teams
ORDER BY team_id;

-- Check if payment_receipt contains URLs
SELECT 
    team_id,
    CASE 
        WHEN payment_receipt IS NULL THEN 'NULL'
        WHEN payment_receipt LIKE 'https://res.cloudinary.com/%' THEN 'CLOUDINARY_URL'
        WHEN payment_receipt LIKE 'data:%' THEN 'BASE64 (NOT MIGRATED!)'
        ELSE 'UNKNOWN'
    END as payment_receipt_status,
    LENGTH(payment_receipt) as payment_receipt_length,
    SUBSTRING(payment_receipt, 1, 50) as payment_receipt_preview
FROM teams
ORDER BY team_id;

-- Check if group_photo contains URLs
SELECT 
    team_id,
    CASE 
        WHEN group_photo IS NULL THEN 'NULL'
        WHEN group_photo LIKE 'https://res.cloudinary.com/%' THEN 'CLOUDINARY_URL'
        WHEN group_photo LIKE 'data:%' THEN 'BASE64 (NOT MIGRATED!)'
        ELSE 'UNKNOWN'
    END as group_photo_status,
    LENGTH(group_photo) as group_photo_length,
    SUBSTRING(group_photo, 1, 50) as group_photo_preview
FROM teams
ORDER BY team_id;

-- Summary: Count teams by file status
SELECT 
    'pastor_letter' as field_name,
    COUNT(CASE WHEN pastor_letter LIKE 'https://res.cloudinary.com/%' THEN 1 END) as cloudinary_urls,
    COUNT(CASE WHEN pastor_letter LIKE 'data:%' THEN 1 END) as base64_remaining,
    COUNT(CASE WHEN pastor_letter IS NULL THEN 1 END) as null_values
FROM teams
UNION ALL
SELECT 
    'payment_receipt' as field_name,
    COUNT(CASE WHEN payment_receipt LIKE 'https://res.cloudinary.com/%' THEN 1 END) as cloudinary_urls,
    COUNT(CASE WHEN payment_receipt LIKE 'data:%' THEN 1 END) as base64_remaining,
    COUNT(CASE WHEN payment_receipt IS NULL THEN 1 END) as null_values
FROM teams
UNION ALL
SELECT 
    'group_photo' as field_name,
    COUNT(CASE WHEN group_photo LIKE 'https://res.cloudinary.com/%' THEN 1 END) as cloudinary_urls,
    COUNT(CASE WHEN group_photo LIKE 'data:%' THEN 1 END) as base64_remaining,
    COUNT(CASE WHEN group_photo IS NULL THEN 1 END) as null_values
FROM teams;

-- ============================================
-- 2. CHECK PLAYERS TABLE
-- ============================================

-- Check if aadhar_file contains URLs
SELECT 
    player_id,
    team_id,
    CASE 
        WHEN aadhar_file IS NULL THEN 'NULL'
        WHEN aadhar_file LIKE 'https://res.cloudinary.com/%' THEN 'CLOUDINARY_URL'
        WHEN aadhar_file LIKE 'data:%' THEN 'BASE64 (NOT MIGRATED!)'
        ELSE 'UNKNOWN'
    END as aadhar_file_status,
    LENGTH(aadhar_file) as aadhar_file_length,
    SUBSTRING(aadhar_file, 1, 50) as aadhar_file_preview
FROM players
ORDER BY team_id, player_id;

-- Check if subscription_file contains URLs
SELECT 
    player_id,
    team_id,
    CASE 
        WHEN subscription_file IS NULL THEN 'NULL'
        WHEN subscription_file LIKE 'https://res.cloudinary.com/%' THEN 'CLOUDINARY_URL'
        WHEN subscription_file LIKE 'data:%' THEN 'BASE64 (NOT MIGRATED!)'
        ELSE 'UNKNOWN'
    END as subscription_file_status,
    LENGTH(subscription_file) as subscription_file_length,
    SUBSTRING(subscription_file, 1, 50) as subscription_file_preview
FROM players
ORDER BY team_id, player_id;

-- Summary: Count players by file status
SELECT 
    'aadhar_file' as field_name,
    COUNT(CASE WHEN aadhar_file LIKE 'https://res.cloudinary.com/%' THEN 1 END) as cloudinary_urls,
    COUNT(CASE WHEN aadhar_file LIKE 'data:%' THEN 1 END) as base64_remaining,
    COUNT(CASE WHEN aadhar_file IS NULL THEN 1 END) as null_values
FROM players
UNION ALL
SELECT 
    'subscription_file' as field_name,
    COUNT(CASE WHEN subscription_file LIKE 'https://res.cloudinary.com/%' THEN 1 END) as cloudinary_urls,
    COUNT(CASE WHEN subscription_file LIKE 'data:%' THEN 1 END) as base64_remaining,
    COUNT(CASE WHEN subscription_file IS NULL THEN 1 END) as null_values
FROM players;

-- ============================================
-- 3. OVERALL MIGRATION STATUS
-- ============================================

-- Check if ANY base64 strings remain (should return 0)
SELECT 
    'BASE64 REMAINING IN TEAMS' as check_type,
    COUNT(*) as count
FROM teams
WHERE pastor_letter LIKE 'data:%' 
   OR payment_receipt LIKE 'data:%' 
   OR group_photo LIKE 'data:%'
UNION ALL
SELECT 
    'BASE64 REMAINING IN PLAYERS' as check_type,
    COUNT(*) as count
FROM players
WHERE aadhar_file LIKE 'data:%' 
   OR subscription_file LIKE 'data:%';

-- Check total Cloudinary URLs (should match number of non-NULL files)
SELECT 
    'CLOUDINARY URLS IN TEAMS' as check_type,
    COUNT(*) as count
FROM teams
WHERE pastor_letter LIKE 'https://res.cloudinary.com/%' 
   OR payment_receipt LIKE 'https://res.cloudinary.com/%' 
   OR group_photo LIKE 'https://res.cloudinary.com/%'
UNION ALL
SELECT 
    'CLOUDINARY URLS IN PLAYERS' as check_type,
    COUNT(*) as count
FROM players
WHERE aadhar_file LIKE 'https://res.cloudinary.com/%' 
   OR subscription_file LIKE 'https://res.cloudinary.com/%';

-- ============================================
-- 4. SAMPLE DATA INSPECTION
-- ============================================

-- View full Cloudinary URLs for first 5 teams
SELECT 
    team_id,
    pastor_letter as pastor_letter_url,
    payment_receipt as payment_receipt_url,
    group_photo as group_photo_url
FROM teams
WHERE pastor_letter IS NOT NULL 
   OR payment_receipt IS NOT NULL 
   OR group_photo IS NOT NULL
LIMIT 5;

-- View full Cloudinary URLs for first 10 players
SELECT 
    player_id,
    team_id,
    aadhar_file as aadhar_url,
    subscription_file as subscription_url
FROM players
WHERE aadhar_file IS NOT NULL 
   OR subscription_file IS NOT NULL
LIMIT 10;

-- ============================================
-- 5. DATA SIZE COMPARISON (Before vs After)
-- ============================================

-- Check average length of URLs vs base64 (should be much smaller)
SELECT 
    'teams.pastor_letter' as field,
    AVG(LENGTH(pastor_letter)) as avg_length,
    MIN(LENGTH(pastor_letter)) as min_length,
    MAX(LENGTH(pastor_letter)) as max_length
FROM teams
WHERE pastor_letter IS NOT NULL
UNION ALL
SELECT 
    'teams.payment_receipt' as field,
    AVG(LENGTH(payment_receipt)) as avg_length,
    MIN(LENGTH(payment_receipt)) as min_length,
    MAX(LENGTH(payment_receipt)) as max_length
FROM teams
WHERE payment_receipt IS NOT NULL
UNION ALL
SELECT 
    'teams.group_photo' as field,
    AVG(LENGTH(group_photo)) as avg_length,
    MIN(LENGTH(group_photo)) as min_length,
    MAX(LENGTH(group_photo)) as max_length
FROM teams
WHERE group_photo IS NOT NULL
UNION ALL
SELECT 
    'players.aadhar_file' as field,
    AVG(LENGTH(aadhar_file)) as avg_length,
    MIN(LENGTH(aadhar_file)) as min_length,
    MAX(LENGTH(aadhar_file)) as max_length
FROM players
WHERE aadhar_file IS NOT NULL
UNION ALL
SELECT 
    'players.subscription_file' as field,
    AVG(LENGTH(subscription_file)) as avg_length,
    MIN(LENGTH(subscription_file)) as min_length,
    MAX(LENGTH(subscription_file)) as max_length
FROM players
WHERE subscription_file IS NOT NULL;

-- ============================================
-- EXPECTED RESULTS AFTER SUCCESSFUL MIGRATION
-- ============================================
-- ✅ All columns should show "CLOUDINARY_URL" status
-- ✅ No "BASE64 (NOT MIGRATED!)" entries
-- ✅ URLs should start with: https://res.cloudinary.com/dplaeuuqk/
-- ✅ Average length should be ~100-200 chars (not 50000+ like base64)
-- ✅ BASE64 REMAINING queries should return 0

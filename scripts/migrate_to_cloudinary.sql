-- Migration: Convert file storage from Base64 to Cloudinary URLs
-- Date: 2025-11-17
-- Description: Change all file columns to TEXT type to store Cloudinary URLs instead of Base64

-- Update teams table file columns to TEXT (for Cloudinary URLs)
ALTER TABLE teams
  ALTER COLUMN pastor_letter TYPE TEXT,
  ALTER COLUMN payment_receipt TYPE TEXT,
  ALTER COLUMN group_photo TYPE TEXT;

-- Update players table file columns to TEXT (for Cloudinary URLs)
ALTER TABLE players
  ALTER COLUMN aadhar_file TYPE TEXT,
  ALTER COLUMN subscription_file TYPE TEXT;

-- Verify changes
SELECT 
    table_name,
    column_name, 
    data_type,
    character_maximum_length,
    is_nullable
FROM 
    information_schema.columns 
WHERE 
    table_name IN ('teams', 'players')
    AND column_name IN ('pastor_letter', 'payment_receipt', 'group_photo', 'aadhar_file', 'subscription_file')
ORDER BY 
    table_name, ordinal_position;

-- Note: Existing Base64 data will remain, but new uploads will be Cloudinary URLs
-- Cloudinary URLs format: https://res.cloudinary.com/dplaeuuqk/image/upload/v1234567890/ICCT26/folder/file.ext

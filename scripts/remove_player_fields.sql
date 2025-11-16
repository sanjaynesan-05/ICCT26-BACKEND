-- Migration: Remove age, phone, and jersey_number columns from players table
-- Date: 2025-11-17
-- Description: These fields were removed from the Player model and are no longer needed

-- Remove age column
ALTER TABLE players DROP COLUMN IF EXISTS age;

-- Remove phone column
ALTER TABLE players DROP COLUMN IF EXISTS phone;

-- Remove jersey_number column
ALTER TABLE players DROP COLUMN IF EXISTS jersey_number;

-- Verify the changes
SELECT 
    column_name, 
    data_type, 
    is_nullable
FROM 
    information_schema.columns 
WHERE 
    table_name = 'players'
ORDER BY 
    ordinal_position;

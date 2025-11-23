-- Migration: Make player role column optional
-- This allows players to be registered without specifying a role

-- Make the role column nullable
ALTER TABLE players 
ALTER COLUMN role DROP NOT NULL;

-- Add comment explaining the change
COMMENT ON COLUMN players.role IS 'Player role (optional) - e.g., Batsman, Bowler, All-Rounder, Wicket-Keeper';

-- Verify the change
SELECT 
    column_name, 
    is_nullable, 
    data_type,
    character_maximum_length
FROM information_schema.columns 
WHERE table_name = 'players' 
AND column_name = 'role';

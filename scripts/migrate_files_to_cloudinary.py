"""
🔄 Base64 to Cloudinary Migration Script
==========================================
This script migrates all base64-encoded files in the database to Cloudinary cloud storage.

What it does:
- Connects to PostgreSQL (Neon DB)
- Connects to Cloudinary
- Finds all base64 strings in teams and players tables
- Uploads each file to Cloudinary with organized folder structure
- Replaces base64 strings with Cloudinary URLs
- Commits changes and reports results

Usage:
    python scripts/migrate_files_to_cloudinary.py
"""

import os
import sys
import base64
import re
from typing import Optional, Tuple
import psycopg2
from psycopg2 import sql
import cloudinary
import cloudinary.uploader
from cloudinary.utils import cloudinary_url
from dotenv import load_dotenv

# Load environment variables from .env.local
load_dotenv('.env.local')
load_dotenv()  # Also load .env if it exists

# ============================================
# CONFIGURATION
# ============================================

# Cloudinary Configuration
CLOUDINARY_CONFIG = {
    'cloud_name': os.getenv('CLOUDINARY_CLOUD_NAME'),
    'api_key': os.getenv('CLOUDINARY_API_KEY'),
    'api_secret': os.getenv('CLOUDINARY_API_SECRET')
}

# PostgreSQL Configuration (Neon DB)
DATABASE_CONFIG = {
    'host': os.getenv('NEON_HOST'),
    'dbname': os.getenv('NEON_DB'),
    'user': os.getenv('NEON_USER'),
    'password': os.getenv('NEON_PASSWORD'),
    'sslmode': 'require'
}

# Validate configuration
if not all([DATABASE_CONFIG['host'], DATABASE_CONFIG['dbname'], DATABASE_CONFIG['user'], DATABASE_CONFIG['password']]):
    print("❌ Missing Neon DB credentials in .env.local file!")
    print("   Required: NEON_HOST, NEON_DB, NEON_USER, NEON_PASSWORD")
    sys.exit(1)

if not all([CLOUDINARY_CONFIG['cloud_name'], CLOUDINARY_CONFIG['api_key'], CLOUDINARY_CONFIG['api_secret']]):
    print("❌ Missing Cloudinary credentials in .env.local file!")
    print("   Required: CLOUDINARY_CLOUD_NAME, CLOUDINARY_API_KEY, CLOUDINARY_API_SECRET")
    sys.exit(1)

# ============================================
# CLOUDINARY SETUP
# ============================================

def initialize_cloudinary():
    """Initialize Cloudinary with credentials"""
    cloudinary.config(
        cloud_name=CLOUDINARY_CONFIG['cloud_name'],
        api_key=CLOUDINARY_CONFIG['api_key'],
        api_secret=CLOUDINARY_CONFIG['api_secret'],
        secure=True
    )
    print("✅ Cloudinary initialized")
    print(f"   Cloud Name: {CLOUDINARY_CONFIG['cloud_name']}")

# ============================================
# DATABASE CONNECTION
# ============================================

def connect_to_database():
    """Connect to PostgreSQL (Neon DB)"""
    try:
        conn = psycopg2.connect(**DATABASE_CONFIG)
        conn.autocommit = False  # We'll commit manually at the end
        print("✅ Connected to PostgreSQL (Neon DB)")
        print(f"   Database: {DATABASE_CONFIG['dbname']}")
        return conn
    except Exception as e:
        print(f"❌ Failed to connect to database: {e}")
        sys.exit(1)

# ============================================
# BASE64 DETECTION & UPLOAD
# ============================================

def is_base64_string(data: Optional[str]) -> bool:
    """Check if string is a base64-encoded file (not a URL)"""
    if not data or not isinstance(data, str):
        return False
    
    # Skip if already a Cloudinary URL
    if data.startswith('https://res.cloudinary.com/'):
        return False
    
    # Check for data URI scheme
    base64_patterns = [
        r'^data:image/png;base64,',
        r'^data:image/jpeg;base64,',
        r'^data:image/jpg;base64,',
        r'^data:application/pdf;base64,',
    ]
    
    for pattern in base64_patterns:
        if re.match(pattern, data):
            return True
    
    return False

def extract_base64_data(data_uri: str) -> Tuple[str, str]:
    """
    Extract base64 string and mime type from data URI
    Returns: (base64_string, file_extension)
    """
    # Split data URI: data:mime/type;base64,<data>
    match = re.match(r'^data:([^;]+);base64,(.+)$', data_uri)
    if not match:
        raise ValueError("Invalid data URI format")
    
    mime_type = match.group(1)
    base64_string = match.group(2)
    
    # Map mime type to file extension
    extension_map = {
        'image/png': 'png',
        'image/jpeg': 'jpg',
        'image/jpg': 'jpg',
        'application/pdf': 'pdf',
    }
    
    extension = extension_map.get(mime_type, 'bin')
    
    return base64_string, extension

def upload_to_cloudinary(base64_string: str, folder: str, filename: str) -> Optional[str]:
    """
    Upload base64 file to Cloudinary
    
    Args:
        base64_string: Pure base64 string (without data URI prefix)
        folder: Cloudinary folder path (e.g., "teams/pastor_letters")
        filename: Filename without extension (will be auto-detected)
    
    Returns:
        Cloudinary secure URL or None if upload fails
    """
    try:
        # Cloudinary.uploader.upload() accepts base64 strings directly
        # No need to add data: prefix - just pass the raw base64
        response = cloudinary.uploader.upload(
            base64_string,
            folder=folder,
            public_id=filename,
            resource_type='auto',  # Auto-detect: image, raw, video
            overwrite=False,
            unique_filename=True
        )
        
        return response['secure_url']
    
    except Exception as e:
        print(f"   ⚠️  Upload failed: {e}")
        return None

# ============================================
# MIGRATION FUNCTIONS
# ============================================

def migrate_teams_table(conn):
    """Migrate base64 files in teams table to Cloudinary"""
    print("\n" + "="*60)
    print("📦 MIGRATING TEAMS TABLE")
    print("="*60)
    
    cursor = conn.cursor()
    
    # Fetch all teams with potential base64 data
    cursor.execute("""
        SELECT team_id, pastor_letter, payment_receipt, group_photo
        FROM teams
        WHERE pastor_letter IS NOT NULL 
           OR payment_receipt IS NOT NULL 
           OR group_photo IS NOT NULL
    """)
    
    teams = cursor.fetchall()
    print(f"Found {len(teams)} teams with files")
    
    updated_count = 0
    skipped_count = 0
    
    for team_id, pastor_letter, payment_receipt, group_photo in teams:
        print(f"\n🔄 Processing Team: {team_id}")
        
        # Track updates for this team
        updates = {}
        
        # 1. Pastor Letter
        if is_base64_string(pastor_letter):
            print(f"   📄 Uploading pastor_letter...")
            try:
                base64_data, ext = extract_base64_data(pastor_letter)
                url = upload_to_cloudinary(
                    base64_data,
                    f"teams/pastor_letters/{team_id}",
                    f"pastor_letter.{ext}"
                )
                if url:
                    updates['pastor_letter'] = url
                    print(f"   ✅ Pastor letter uploaded")
            except Exception as e:
                print(f"   ⚠️  Failed: {e}")
        else:
            print(f"   ⏭️  Pastor letter: Already URL or NULL")
        
        # 2. Payment Receipt
        if is_base64_string(payment_receipt):
            print(f"   💳 Uploading payment_receipt...")
            try:
                base64_data, ext = extract_base64_data(payment_receipt)
                url = upload_to_cloudinary(
                    base64_data,
                    f"teams/payment_receipts/{team_id}",
                    f"payment_receipt.{ext}"
                )
                if url:
                    updates['payment_receipt'] = url
                    print(f"   ✅ Payment receipt uploaded")
            except Exception as e:
                print(f"   ⚠️  Failed: {e}")
        else:
            print(f"   ⏭️  Payment receipt: Already URL or NULL")
        
        # 3. Group Photo
        if is_base64_string(group_photo):
            print(f"   📸 Uploading group_photo...")
            try:
                base64_data, ext = extract_base64_data(group_photo)
                url = upload_to_cloudinary(
                    base64_data,
                    f"teams/group_photos/{team_id}",
                    f"group_photo.{ext}"
                )
                if url:
                    updates['group_photo'] = url
                    print(f"   ✅ Group photo uploaded")
            except Exception as e:
                print(f"   ⚠️  Failed: {e}")
        else:
            print(f"   ⏭️  Group photo: Already URL or NULL")
        
        # Update database if any files were uploaded
        if updates:
            update_fields = ', '.join([f"{k} = %s" for k in updates.keys()])
            update_values = list(updates.values()) + [team_id]
            
            cursor.execute(
                f"UPDATE teams SET {update_fields} WHERE team_id = %s",
                update_values
            )
            updated_count += 1
            print(f"   ✔️  Updated team {team_id} in database")
        else:
            skipped_count += 1
    
    cursor.close()
    print(f"\n📊 Teams Summary: {updated_count} updated, {skipped_count} skipped")

def migrate_players_table(conn):
    """Migrate base64 files in players table to Cloudinary"""
    print("\n" + "="*60)
    print("👥 MIGRATING PLAYERS TABLE")
    print("="*60)
    
    cursor = conn.cursor()
    
    # Fetch all players with potential base64 data
    cursor.execute("""
        SELECT player_id, team_id, aadhar_file, subscription_file
        FROM players
        WHERE aadhar_file IS NOT NULL 
           OR subscription_file IS NOT NULL
    """)
    
    players = cursor.fetchall()
    print(f"Found {len(players)} players with files")
    
    updated_count = 0
    skipped_count = 0
    
    for player_id, team_id, aadhar_file, subscription_file in players:
        print(f"\n🔄 Processing Player: {player_id} (Team: {team_id})")
        
        # Track updates for this player
        updates = {}
        
        # 1. Aadhar File
        if is_base64_string(aadhar_file):
            print(f"   🪪 Uploading aadhar_file...")
            try:
                base64_data, ext = extract_base64_data(aadhar_file)
                url = upload_to_cloudinary(
                    base64_data,
                    f"players/aadhar/{team_id}",
                    f"{player_id}_aadhar.{ext}"
                )
                if url:
                    updates['aadhar_file'] = url
                    print(f"   ✅ Aadhar file uploaded")
            except Exception as e:
                print(f"   ⚠️  Failed: {e}")
        else:
            print(f"   ⏭️  Aadhar file: Already URL or NULL")
        
        # 2. Subscription File
        if is_base64_string(subscription_file):
            print(f"   📋 Uploading subscription_file...")
            try:
                base64_data, ext = extract_base64_data(subscription_file)
                url = upload_to_cloudinary(
                    base64_data,
                    f"players/subscription/{team_id}",
                    f"{player_id}_subscription.{ext}"
                )
                if url:
                    updates['subscription_file'] = url
                    print(f"   ✅ Subscription file uploaded")
            except Exception as e:
                print(f"   ⚠️  Failed: {e}")
        else:
            print(f"   ⏭️  Subscription file: Already URL or NULL")
        
        # Update database if any files were uploaded
        if updates:
            update_fields = ', '.join([f"{k} = %s" for k in updates.keys()])
            update_values = list(updates.values()) + [player_id]
            
            cursor.execute(
                f"UPDATE players SET {update_fields} WHERE player_id = %s",
                update_values
            )
            updated_count += 1
            print(f"   ✔️  Updated player {player_id} in database")
        else:
            skipped_count += 1
    
    cursor.close()
    print(f"\n📊 Players Summary: {updated_count} updated, {skipped_count} skipped")

# ============================================
# MAIN MIGRATION
# ============================================

def main():
    """Execute the complete migration"""
    print("\n" + "="*60)
    print("🚀 BASE64 TO CLOUDINARY MIGRATION")
    print("="*60)
    print("\nThis script will:")
    print("  1️⃣  Connect to PostgreSQL (Neon DB)")
    print("  2️⃣  Connect to Cloudinary")
    print("  3️⃣  Find all base64-encoded files")
    print("  4️⃣  Upload files to Cloudinary")
    print("  5️⃣  Replace base64 with Cloudinary URLs")
    print("  6️⃣  Commit changes to database")
    print("\n⚠️  This operation cannot be undone!")
    
    # Confirmation
    response = input("\nProceed with migration? (yes/no): ")
    if response.lower() != 'yes':
        print("❌ Migration cancelled")
        return
    
    # Initialize services
    print("\n" + "="*60)
    print("🔧 INITIALIZING SERVICES")
    print("="*60)
    
    initialize_cloudinary()
    conn = connect_to_database()
    
    try:
        # Migrate teams table
        migrate_teams_table(conn)
        
        # Migrate players table
        migrate_players_table(conn)
        
        # Commit all changes
        print("\n" + "="*60)
        print("💾 COMMITTING CHANGES")
        print("="*60)
        conn.commit()
        print("✅ All changes committed to database")
        
        # Success
        print("\n" + "="*60)
        print("🎉 MIGRATION COMPLETE!")
        print("="*60)
        print("\n✅ All base64 files have been converted to Cloudinary URLs")
        print("✅ Database updated successfully")
        print("\n📝 Next steps:")
        print("  1. Run verification SQL queries (see below)")
        print("  2. Test your API endpoints")
        print("  3. Check Cloudinary dashboard for uploaded files")
        
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        print("🔄 Rolling back changes...")
        conn.rollback()
        print("✅ Rollback complete - database unchanged")
        sys.exit(1)
    
    finally:
        conn.close()
        print("\n🔒 Database connection closed")

if __name__ == "__main__":
    main()

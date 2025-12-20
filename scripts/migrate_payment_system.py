#!/usr/bin/env python3
"""
Database Migration Script for UPI Payment System
Adds payment-related columns to teams table

Usage:
    python scripts/migrate_payment_system.py
    
This script:
1. Checks if columns already exist (safe to run multiple times)
2. Adds 8 new columns to teams table
3. Sets appropriate indexes for query performance
4. Logs all operations
5. Provides rollback instructions if needed
"""

import asyncio
import logging
from datetime import datetime
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Database configuration - adjust to match your setup
# For Neon PostgreSQL:
DATABASE_URL = "postgresql+asyncpg://user:password@host/database"
# Or load from environment:
import os
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://localhost/icct26"
)


async def check_column_exists(session: AsyncSession, table: str, column: str) -> bool:
    """Check if a column already exists in the table"""
    query = text(f"""
        SELECT EXISTS(
            SELECT 1 FROM information_schema.columns 
            WHERE table_name = '{table}' AND column_name = '{column}'
        )
    """)
    result = await session.execute(query)
    return result.scalar()


async def migrate_payment_system():
    """Main migration function"""
    
    # Create async engine
    engine = create_async_engine(
        DATABASE_URL,
        echo=False,
        pool_size=10,
        max_overflow=20,
        connect_args={'timeout': 10}
    )
    
    # Create session factory
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    logger.info("=" * 60)
    logger.info("ICCT26 UPI Payment System - Database Migration")
    logger.info("=" * 60)
    logger.info(f"Database: {DATABASE_URL.split('@')[1] if '@' in DATABASE_URL else 'unknown'}")
    logger.info(f"Timestamp: {datetime.now().isoformat()}")
    logger.info("")
    
    try:
        async with async_session() as session:
            
            # =====================================================
            # Check existing columns
            # =====================================================
            logger.info("Checking for existing columns...")
            
            columns_to_add = [
                "status",
                "payment_date",
                "payment_screenshot",
                "approval_date",
                "rejection_date",
                "rejection_reason",
                "approved_by",
                "rejected_by"
            ]
            
            existing_columns = []
            for column in columns_to_add:
                exists = await check_column_exists(session, "teams", column)
                if exists:
                    existing_columns.append(column)
                    logger.info(f"  ✓ Column '{column}' already exists")
                else:
                    logger.info(f"  ✗ Column '{column}' not found (will be created)")
            
            if len(existing_columns) == len(columns_to_add):
                logger.warning("\n⚠️  All columns already exist. Migration not needed.")
                await engine.dispose()
                return
            
            logger.info(f"\n{len(columns_to_add) - len(existing_columns)} columns to add\n")
            
            # =====================================================
            # Add columns
            # =====================================================
            logger.info("Adding columns to teams table...")
            
            # Status column with default
            if "status" not in existing_columns:
                try:
                    await session.execute(text("""
                        ALTER TABLE teams 
                        ADD COLUMN status VARCHAR(50) NOT NULL DEFAULT 'PENDING_PAYMENT'
                    """))
                    logger.info("  ✓ Added column: status (VARCHAR(50), DEFAULT 'PENDING_PAYMENT')")
                    await session.commit()
                except Exception as e:
                    logger.error(f"  ✗ Failed to add status: {e}")
                    await session.rollback()
                    raise
            
            # Payment date column
            if "payment_date" not in existing_columns:
                try:
                    await session.execute(text("""
                        ALTER TABLE teams 
                        ADD COLUMN payment_date TIMESTAMP NULL
                    """))
                    logger.info("  ✓ Added column: payment_date (TIMESTAMP)")
                    await session.commit()
                except Exception as e:
                    logger.error(f"  ✗ Failed to add payment_date: {e}")
                    await session.rollback()
                    raise
            
            # Payment screenshot column
            if "payment_screenshot" not in existing_columns:
                try:
                    await session.execute(text("""
                        ALTER TABLE teams 
                        ADD COLUMN payment_screenshot TEXT NULL
                    """))
                    logger.info("  ✓ Added column: payment_screenshot (TEXT)")
                    await session.commit()
                except Exception as e:
                    logger.error(f"  ✗ Failed to add payment_screenshot: {e}")
                    await session.rollback()
                    raise
            
            # Approval date column
            if "approval_date" not in existing_columns:
                try:
                    await session.execute(text("""
                        ALTER TABLE teams 
                        ADD COLUMN approval_date TIMESTAMP NULL
                    """))
                    logger.info("  ✓ Added column: approval_date (TIMESTAMP)")
                    await session.commit()
                except Exception as e:
                    logger.error(f"  ✗ Failed to add approval_date: {e}")
                    await session.rollback()
                    raise
            
            # Rejection date column
            if "rejection_date" not in existing_columns:
                try:
                    await session.execute(text("""
                        ALTER TABLE teams 
                        ADD COLUMN rejection_date TIMESTAMP NULL
                    """))
                    logger.info("  ✓ Added column: rejection_date (TIMESTAMP)")
                    await session.commit()
                except Exception as e:
                    logger.error(f"  ✗ Failed to add rejection_date: {e}")
                    await session.rollback()
                    raise
            
            # Rejection reason column
            if "rejection_reason" not in existing_columns:
                try:
                    await session.execute(text("""
                        ALTER TABLE teams 
                        ADD COLUMN rejection_reason TEXT NULL
                    """))
                    logger.info("  ✓ Added column: rejection_reason (TEXT)")
                    await session.commit()
                except Exception as e:
                    logger.error(f"  ✗ Failed to add rejection_reason: {e}")
                    await session.rollback()
                    raise
            
            # Approved by column
            if "approved_by" not in existing_columns:
                try:
                    await session.execute(text("""
                        ALTER TABLE teams 
                        ADD COLUMN approved_by VARCHAR(100) NULL
                    """))
                    logger.info("  ✓ Added column: approved_by (VARCHAR(100))")
                    await session.commit()
                except Exception as e:
                    logger.error(f"  ✗ Failed to add approved_by: {e}")
                    await session.rollback()
                    raise
            
            # Rejected by column
            if "rejected_by" not in existing_columns:
                try:
                    await session.execute(text("""
                        ALTER TABLE teams 
                        ADD COLUMN rejected_by VARCHAR(100) NULL
                    """))
                    logger.info("  ✓ Added column: rejected_by (VARCHAR(100))")
                    await session.commit()
                except Exception as e:
                    logger.error(f"  ✗ Failed to add rejected_by: {e}")
                    await session.rollback()
                    raise
            
            # =====================================================
            # Create indexes for performance
            # =====================================================
            logger.info("\nCreating indexes...")
            
            indexes = [
                ("idx_team_status", "status", "Status queries for pending approvals"),
                ("idx_payment_date", "payment_date", "Sorting by payment date"),
            ]
            
            for index_name, column, description in indexes:
                try:
                    # Check if index exists
                    result = await session.execute(text(f"""
                        SELECT EXISTS(
                            SELECT 1 FROM pg_indexes 
                            WHERE indexname = '{index_name}'
                        )
                    """))
                    
                    if not result.scalar():
                        await session.execute(text(f"""
                            CREATE INDEX {index_name} ON teams({column})
                        """))
                        logger.info(f"  ✓ Created index: {index_name} ({description})")
                        await session.commit()
                    else:
                        logger.info(f"  ✓ Index '{index_name}' already exists")
                
                except Exception as e:
                    logger.warning(f"  ⚠️  Could not create index {index_name}: {e}")
                    await session.rollback()
            
            # =====================================================
            # Verify migration
            # =====================================================
            logger.info("\nVerifying migration...")
            
            result = await session.execute(text("""
                SELECT COUNT(*) FROM information_schema.columns 
                WHERE table_name = 'teams' AND column_name IN (
                    'status', 'payment_date', 'payment_screenshot',
                    'approval_date', 'rejection_date', 'rejection_reason',
                    'approved_by', 'rejected_by'
                )
            """))
            
            new_columns_count = result.scalar()
            logger.info(f"  ✓ {new_columns_count}/8 payment columns exist in teams table")
            
            if new_columns_count == 8:
                logger.info("\n" + "=" * 60)
                logger.info("✅ MIGRATION SUCCESSFUL")
                logger.info("=" * 60)
                logger.info("\nDatabase is now ready for UPI Payment System")
                logger.info("Next steps:")
                logger.info("1. Verify new fields in models.py are in place")
                logger.info("2. Deploy payment.py and payment_admin.py")
                logger.info("3. Test payment endpoints")
                logger.info("4. Enable payment flow in frontend")
                
            else:
                logger.warning(f"\n⚠️  Only {new_columns_count} columns found. Check logs above.")
    
    except Exception as e:
        logger.error(f"\n❌ MIGRATION FAILED: {e}")
        logger.error("\nRollback instructions:")
        logger.error("""
        If you need to rollback this migration, run these commands:
        
        ALTER TABLE teams DROP COLUMN IF EXISTS status;
        ALTER TABLE teams DROP COLUMN IF EXISTS payment_date;
        ALTER TABLE teams DROP COLUMN IF EXISTS payment_screenshot;
        ALTER TABLE teams DROP COLUMN IF EXISTS approval_date;
        ALTER TABLE teams DROP COLUMN IF EXISTS rejection_date;
        ALTER TABLE teams DROP COLUMN IF EXISTS rejection_reason;
        ALTER TABLE teams DROP COLUMN IF EXISTS approved_by;
        ALTER TABLE teams DROP COLUMN IF EXISTS rejected_by;
        
        DROP INDEX IF EXISTS idx_team_status;
        DROP INDEX IF EXISTS idx_payment_date;
        """)
        raise
    
    finally:
        await engine.dispose()


if __name__ == "__main__":
    # Run the migration
    try:
        asyncio.run(migrate_payment_system())
    except KeyboardInterrupt:
        logger.warning("\n\nMigration cancelled by user")
    except Exception as e:
        logger.error(f"\n\nFatal error: {e}")
        exit(1)

"""
Database Migration Script: Convert plaintext PINs to hashed PINs
This script migrates existing wallets from plaintext PIN storage to bcrypt hashed PINs.

IMPORTANT: Run this script AFTER updating the database schema to add pin_hash column.

Usage:
    python migrate_pins.py
"""

import sys
import os

# Add parent directory to path to import app modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database.db import SessionLocal, engine
from app.database.models import Base, Wallet
from app.core.crypto import hash_pin
from sqlalchemy import text

def migrate_pins_to_hashed():
    """
    Migrate all existing plaintext PINs to hashed PINs.
    
    Steps:
    1. Add pin_hash column if it doesn't exist
    2. Hash all existing PINs
    3. Drop old pin column
    """
    
    db = SessionLocal()
    
    try:
        print("🔐 Starting PIN migration to bcrypt hashed format...")
        
        # Step 1: Add pin_hash column if it doesn't exist
        print("\n📝 Step 1: Checking database schema...")
        try:
            # Check if pin_hash column exists
            result = db.execute(text(
                "SELECT column_name FROM information_schema.columns "
                "WHERE table_name='wallets' AND column_name='pin_hash'"
            ))
            
            if not result.fetchone():
                print("   Adding pin_hash column...")
                db.execute(text("ALTER TABLE wallets ADD COLUMN pin_hash VARCHAR(255)"))
                db.commit()
                print("   ✅ pin_hash column added")
            else:
                print("   ✅ pin_hash column already exists")
        except Exception as e:
            print(f"   ⚠️  Schema check error: {e}")
            print("   Continuing with migration...")
        
        # Step 2: Migrate existing PINs
        print("\n📝 Step 2: Migrating existing PINs...")
        
        # Check if old 'pin' column still exists
        try:
            result = db.execute(text(
                "SELECT column_name FROM information_schema.columns "
                "WHERE table_name='wallets' AND column_name='pin'"
            ))
            
            if result.fetchone():
                # Old column exists, migrate data
                wallets = db.query(Wallet).all()
                
                if not wallets:
                    print("   ℹ️  No wallets found to migrate")
                else:
                    migrated_count = 0
                    for wallet in wallets:
                        try:
                            # Get plaintext PIN from old column
                            old_pin = db.execute(
                                text("SELECT pin FROM wallets WHERE id = :id"),
                                {"id": wallet.id}
                            ).fetchone()[0]
                            
                            if old_pin and len(old_pin) == 4:
                                # Hash the PIN
                                hashed = hash_pin(old_pin)
                                
                                # Update pin_hash
                                db.execute(
                                    text("UPDATE wallets SET pin_hash = :hash WHERE id = :id"),
                                    {"hash": hashed, "id": wallet.id}
                                )
                                migrated_count += 1
                                print(f"   ✅ Migrated wallet {wallet.id}")
                        except Exception as e:
                            print(f"   ❌ Error migrating wallet {wallet.id}: {e}")
                            continue
                    
                    db.commit()
                    print(f"\n   ✅ Successfully migrated {migrated_count} wallet(s)")
                
                # Step 3: Drop old pin column
                print("\n📝 Step 3: Removing old pin column...")
                try:
                    db.execute(text("ALTER TABLE wallets DROP COLUMN pin"))
                    db.commit()
                    print("   ✅ Old pin column removed")
                except Exception as e:
                    print(f"   ⚠️  Could not remove old column: {e}")
                    print("   You may need to manually drop the 'pin' column")
            else:
                print("   ℹ️  Old 'pin' column not found - migration may have already been completed")
                
        except Exception as e:
            print(f"   ❌ Migration error: {e}")
            db.rollback()
            raise
        
        print("\n✅ PIN migration completed successfully!")
        print("\n⚠️  IMPORTANT: Please restart your application for changes to take effect")
        
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        db.rollback()
        return False
    finally:
        db.close()
    
    return True


def verify_migration():
    """Verify that migration was successful"""
    db = SessionLocal()
    
    try:
        print("\n🔍 Verifying migration...")
        
        # Check that all wallets have pin_hash
        wallets = db.query(Wallet).all()
        
        if not wallets:
            print("   ℹ️  No wallets to verify")
            return True
        
        all_valid = True
        for wallet in wallets:
            if not wallet.pin_hash or len(wallet.pin_hash) < 50:
                print(f"   ❌ Wallet {wallet.id} has invalid pin_hash")
                all_valid = False
            else:
                print(f"   ✅ Wallet {wallet.id} has valid hashed PIN")
        
        if all_valid:
            print("\n✅ All wallets have valid hashed PINs!")
        else:
            print("\n❌ Some wallets have invalid PINs - please review")
        
        return all_valid
        
    finally:
        db.close()


if __name__ == "__main__":
    print("=" * 60)
    print("   PIN MIGRATION SCRIPT - Plaintext to Bcrypt Hashed")
    print("=" * 60)
    
    # Confirm before proceeding
    response = input("\n⚠️  This will modify your database. Continue? (yes/no): ")
    
    if response.lower() != 'yes':
        print("Migration cancelled.")
        sys.exit(0)
    
    # Run migration
    success = migrate_pins_to_hashed()
    
    if success:
        # Verify migration
        verify_migration()
        print("\n" + "=" * 60)
        print("Migration complete! Your PINs are now securely hashed.")
        print("=" * 60)
    else:
        print("\n❌ Migration failed. Please check errors above.")
        sys.exit(1)

"""
Migration script to add new WooCommerce columns to existing integrations table.
This is needed because SQLite doesn't automatically add columns with SQLAlchemy's create_all.
"""
import sqlite3
import os

db_path = os.path.join(os.path.dirname(__file__), 'saas_bot.db')

print(f"Migration: Adding WooCommerce columns to integrations table...")
print(f"Database: {db_path}")

# Connect to database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Get existing columns
cursor.execute('PRAGMA table_info(integrations)')
existing_columns = [col[1] for col in cursor.fetchall()]

print(f"Existing columns: {', '.join(existing_columns)}")

# New columns to add
new_columns = [
    ('woocommerce_url', 'VARCHAR(255)'),
    ('woo_products_cached', 'BOOLEAN DEFAULT 0'),
    ('woo_categories_cached', 'TEXT'),  # JSON stored as TEXT
    ('woo_products_count', 'INTEGER DEFAULT 0'),
]

# Add missing columns
for col_name, col_type in new_columns:
    if col_name not in existing_columns:
        try:
            cursor.execute(f'ALTER TABLE integrations ADD COLUMN {col_name} {col_type}')
            print(f"✅ Added column: {col_name} ({col_type})")
        except Exception as e:
            print(f"⚠️  Error adding {col_name}: {e}")
    else:
        print(f"⏭️  Column already exists: {col_name}")

conn.commit()

# Verify
cursor.execute('PRAGMA table_info(integrations)')
final_columns = [col[1] for col in cursor.fetchall()]
print(f"\n✅ Final columns: {', '.join(final_columns)}")

conn.close()
print("\n✅ Migration completed successfully!")

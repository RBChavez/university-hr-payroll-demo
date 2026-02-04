import sqlite3
import os

# The DB is actually in the root directory based on list_dir
DB_NAME = 'mock_banner.db'
db_path = os.path.join(os.getcwd(), DB_NAME)

def migrate():
    if not os.path.exists(db_path):
        # Try relative to script if cwd fails
        db_path_alt = os.path.join(os.path.dirname(__file__), DB_NAME)
        if os.path.exists(db_path_alt):
            path = db_path_alt
        else:
            print(f"Database not found at {db_path} or {db_path_alt}")
            return
    else:
        path = db_path

    print(f"Migrating database at: {path}")
    conn = sqlite3.connect(path)
    cursor = conn.cursor()
    
    # Check PHRPAYRO columns
    cursor.execute("PRAGMA table_info(PHRPAYRO)")
    columns = [row[1] for row in cursor.fetchall()]
    
    new_columns = [
        ('PHRPAYRO_FED_TAX', 'REAL'),
        ('PHRPAYRO_STATE_TAX', 'REAL'),
        ('PHRPAYRO_NET_PAY', 'REAL')
    ]
    
    for col_name, col_type in new_columns:
        if col_name not in columns:
            print(f"Adding column {col_name} to PHRPAYRO")
            cursor.execute(f"ALTER TABLE PHRPAYRO ADD COLUMN {col_name} {col_type}")
    
    conn.commit()
    conn.close()
    print("Migration complete")

if __name__ == '__main__':
    migrate()

import os
import sqlite3
import psycopg2
from core.config import settings

DATABASE_URL = settings.DATABASE_URL
PATH_DATABASE_LOCAL = settings.PATH_DATABASE_LOCAL

SQLITE_TABLES = ["Cards"]


def upload_tables_to_neon(db_path: str = None) -> None:
    """
    Upload SQLite tables to Neon PostgreSQL.
    Drops and recreates tables, then inserts all rows.
    """
    if db_path is None:
        db_path = os.path.join(PATH_DATABASE_LOCAL, "cards.db")

    if not os.path.exists(db_path):
        print(f"SQLite database not found at: {db_path}")
        return

    try:
        # Connect to SQLite
        sqlite_conn = sqlite3.connect(db_path)
        sqlite_conn.row_factory = sqlite3.Row
        sqlite_cur = sqlite_conn.cursor()

        # Connect to Neon
        neon_conn = psycopg2.connect(DATABASE_URL)
        neon_cur = neon_conn.cursor()

        print("Connected to Neon PostgreSQL")

        for table_name in SQLITE_TABLES:
            print(f"\nProcessing table: {table_name}")

            sqlite_cur.execute(f"SELECT * FROM {table_name}")
            rows = sqlite_cur.fetchall()

            if not rows:
                print(f"  No data found in {table_name}")
                continue

            columns = [desc[0] for desc in sqlite_cur.description]

            # Drop and recreate table
            neon_cur.execute(f'DROP TABLE IF EXISTS "{table_name}" CASCADE;')

            column_defs = ", ".join(f'"{col}" TEXT' for col in columns)
            neon_cur.execute(f'''
                CREATE TABLE "{table_name}" (
                    {column_defs}
                );
            ''')

            neon_conn.commit()
            print(f"  Recreated table: {table_name}")

            # Insert data
            cols_quoted = ", ".join(f'"{col}"' for col in columns)
            placeholders = ", ".join(["%s"] * len(columns))

            insert_query = f'''
                INSERT INTO "{table_name}" ({cols_quoted})
                VALUES ({placeholders});
            '''

            for row in rows:
                neon_cur.execute(insert_query, [row[col] for col in columns])

            neon_conn.commit()
            print(f"  Inserted {len(rows)} rows into {table_name}")

        sqlite_conn.close()
        neon_conn.close()
        print("\nAll tables uploaded to Neon successfully!")

    except Exception as e:
        print(f"Error: {e}")

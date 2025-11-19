import os
import psycopg2
from dotenv import load_dotenv
import pandas as pd

# Loading environment variables from .env file
load_dotenv()

# Get the connection string from the environment variable
conn_string = os.getenv("DATABASE_URL")
conn = None


def read_all_h5_sets(directory="app/info") -> dict[str, dict[str, pd.DataFrame]]:
    """
    Read all HDF5 files in the specified directory and return a dictionary of dictionaries of DataFrames.
    """
    all_dfs = {}
    set_names = [
        "main_sets_df",
        "starter_sets_df",
        "extra_sets_df",
        "best_sets_df",
        "other_sets_df",
    ]
    for set_name in set_names:
        set_dict = {}
        with pd.HDFStore(
            os.path.join(directory, f"{set_name}_sets.h5"), mode="r"
        ) as store:
            for key in store.keys():
                set_dict[key.strip("/")] = store[key]
        all_dfs[set_name] = set_dict
        print(f"Loaded {set_name} with {len(set_dict)} tables.")
    return all_dfs


def create_all_tables(
    dfs: dict[str, dict[str, pd.DataFrame]],
) -> None:
    """
    Creates and populates SQL tables based on the dictionary produced by read_all_h5_sets().
    Outer dict key  -> table name
    Inner dict key  -> set_key (column in SQL)
    All DataFrames inside each outer key share identical columns.
    """
    try:
        with psycopg2.connect(conn_string) as conn:
            print("Connected to Neon")

            with conn.cursor() as cur:
                for table_name, sets_dict in dfs.items():
                    print(f"\nProcessing table: {table_name}")

                    # --------------------------
                    # 1. Pick one DF for schema
                    # --------------------------
                    sample_df = next(iter(sets_dict.values()))
                    df_columns = list(sample_df.columns)

                    # SQL column definitions (TEXT is safest)
                    sql_columns = ", ".join(f'"{col}" TEXT' for col in df_columns)

                    # --------------------------
                    # 2. Drop & recreate table
                    # --------------------------
                    cur.execute(f'DROP TABLE IF EXISTS "{table_name}" CASCADE;')
                    cur.execute(
                        f'''
                        CREATE TABLE "{table_name}" (
                            id SERIAL PRIMARY KEY,
                            set_key TEXT,
                            {sql_columns}
                        );
                        '''
                    )
                    print(f"Created table: {table_name}")

                    # --------------------------
                    # 3. Insert all rows
                    # --------------------------
                    for set_key, df in sets_dict.items():
                        print(f"  Inserting rows for: {set_key}")

                        # Add the set_key column
                        df_to_upload = df.copy()
                        df_to_upload.insert(0, "set_key", set_key)

                        cols = ", ".join(f'"{c}"' for c in df_to_upload.columns)
                        placeholders = ", ".join(["%s"] * len(df_to_upload.columns))

                        insert_query = (
                            f'INSERT INTO "{table_name}" ({cols}) '
                            f"VALUES ({placeholders});"
                        )

                        # Insert row by row (safe & simple)
                        for _, row in df_to_upload.iterrows():
                            cur.execute(insert_query, list(row.values))

                conn.commit()
                print("\nAll tables created and populated successfully.")

    except Exception as e:
        print("Error in create_all_tables:")
        print(e)


if __name__ == "__main__":
    all_sets = read_all_h5_sets()
    create_all_tables(all_sets)

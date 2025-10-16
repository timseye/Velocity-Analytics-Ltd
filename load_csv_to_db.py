import pandas as pd
from connection import F1DatabaseConnector
import os
from sqlalchemy import create_engine, text

def load_csv_to_db(csv_filepath, table_name):
    connector = F1DatabaseConnector()
    if not connector.connect():
        print("Failed to connect to database.")
        return

    try:
        df = pd.read_csv(csv_filepath)
        df.columns = [c.lower() for c in df.columns] # PostgreSQL prefers lowercase column names

        # Ensure 'date' column is in correct format if it exists
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'])

        # Create table and insert data
        engine = create_engine(f"postgresql+psycopg2://{connector.user}:{connector.password}@{connector.host}:{connector.port}/{connector.database}")

        # Drop table if it exists (for easy re-runs)
        with engine.connect() as conn:
            conn.execute(text(f"DROP TABLE IF EXISTS {table_name};"))
            conn.commit()

        df.to_sql(table_name, engine, if_exists='replace', index=False)
        print(f"Successfully loaded {len(df)} rows from {csv_filepath} into table {table_name}.")

    except Exception as e:
        print(f"Error loading CSV to database: {e}")
    finally:
        connector.disconnect()

if __name__ == "__main__":
    csv_file = os.path.join(os.path.dirname(__file__), "exports", "results_growth.csv")
    db_table_name = "results_growth_csv" # This will be the new table name in your DB

    if not os.path.exists(csv_file):
        print(f"Error: CSV file not found at {csv_file}. Please ensure you have exported it from Superset SQL Lab first.")
    else:
        load_csv_to_db(csv_file, db_table_name)

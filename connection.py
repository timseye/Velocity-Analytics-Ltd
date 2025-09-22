#!/usr/bin/env python3
"""PostgreSQL connection for the F1 database."""

import psycopg2
from psycopg2 import Error
import os
from dotenv import load_dotenv

class F1DatabaseConnector:
    def __init__(self):
        """Load DB settings from `.env`."""
        load_dotenv()
        self.host = os.getenv('DB_HOST')
        self.database = os.getenv('DB_NAME')
        self.user = os.getenv('DB_USER')
        self.password = os.getenv('DB_PASSWORD')
        self.port = os.getenv('DB_PORT')
        self.connection = None
        
    def connect(self):
        """Connect to PostgreSQL."""
        try:
            self.connection = psycopg2.connect(
                host=self.host,
                database=self.database,
                user=self.user,
                password=self.password,
                port=self.port
            )
            
            if self.connection:
                cursor = self.connection.cursor()
                cursor.execute("SELECT version();")
                db_version = cursor.fetchone()
                print("Successfully connected to PostgreSQL")
                print(f"Database version: {db_version[0]}")
                
                cursor.execute("SELECT current_database();")
                database_name = cursor.fetchone()
                print(f"Connected to database: {database_name[0]}")
                cursor.close()
                return True
                
        except Error as e:
            print(f"Error while connecting to PostgreSQL: {e}")
            return False
    
    def disconnect(self):
        """Close connection."""
        if self.connection:
            self.connection.close()
            print("PostgreSQL connection closed")

def main():
    """Quick connection test."""
    print("F1 Database Connection Test")
    db = F1DatabaseConnector()
    if db.connect():
        print("Connection successful!")
        db.disconnect()
    else:
        print("Failed to connect to database. Please check your connection settings.")

if __name__ == "__main__":
    try:
        import psycopg2
        from dotenv import load_dotenv
    except ImportError as e:
        print(f"Missing required package: {e}")
        print("Install with: pip install -r requirements.txt")
        exit(1)
    
    main()
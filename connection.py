#!/usr/bin/env python3
"""
Simple F1 Database Connection Script
This script connects to the F1 PostgreSQL database
"""

import psycopg2
from psycopg2 import Error
import os
from dotenv import load_dotenv

class F1DatabaseConnector:
    def __init__(self):
        """Initialize database connection parameters from .env file"""
        load_dotenv()
        self.host = os.getenv('DB_HOST')
        self.database = os.getenv('DB_NAME')
        self.user = os.getenv('DB_USER')
        self.password = os.getenv('DB_PASSWORD')
        self.port = os.getenv('DB_PORT')
        self.connection = None
        
    def connect(self):
        """Establish connection to PostgreSQL database"""
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
                print(f"Successfully connected to PostgreSQL")
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
        """Close database connection"""
        if self.connection:
            self.connection.close()
            print("PostgreSQL connection closed")

def main():
    """Main function to test database connection"""
    print("F1 Database Connection Test")
    print("=" * 40)
    
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
        print("Please install required packages:")
        print("For Ubuntu: sudo apt install python3-psycopg2")
        print("For dotenv: pip install python-dotenv --break-system-packages")
        exit(1)
    
    main()
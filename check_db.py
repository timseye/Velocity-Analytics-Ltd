#!/usr/bin/env python3
"""Check F1 database structure and sample data."""

from connection import F1DatabaseConnector

def check_database():
    connector = F1DatabaseConnector()
    if not connector.connect():
        return
    
    try:
        cur = connector.connection.cursor()
        
        # List all tables
        cur.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            ORDER BY table_name
        """)
        tables = cur.fetchall()
        
        print("📋 F1 Database Tables:")
        print("=" * 60)
        for table in tables:
            table_name = table[0]
            cur.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cur.fetchone()[0]
            print(f"  {table_name:30s} - {count:6d} rows")
        
        print("\n" + "=" * 60)
        
        # Sample data from key tables
        print("\n📊 Sample Data - Recent Races:")
        cur.execute("""
            SELECT r.year, r.round, r.name, c.name as circuit
            FROM races r
            JOIN circuits c ON c.circuitid = r.circuitid
            WHERE r.year >= 2020
            ORDER BY r.year DESC, r.round DESC
            LIMIT 5
        """)
        for row in cur.fetchall():
            print(f"  {row[0]} Round {row[1]:2d}: {row[2]:30s} ({row[3]})")
        
        print("\n📊 Sample Data - Top Drivers by Points:")
        cur.execute("""
            SELECT d.forename || ' ' || d.surname AS driver, 
                   SUM(r.points) AS total_points
            FROM results r
            JOIN drivers d ON d.driverid = r.driverid
            GROUP BY d.driverid, driver
            ORDER BY total_points DESC
            LIMIT 5
        """)
        for row in cur.fetchall():
            print(f"  {row[0]:30s} - {row[1]:6.0f} points")
        
        cur.close()
        
    finally:
        connector.disconnect()

if __name__ == "__main__":
    check_database()

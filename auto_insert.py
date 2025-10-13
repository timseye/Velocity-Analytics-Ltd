#!/usr/bin/env python3
"""Auto-insert script: adds new F1 race results every 10 seconds."""

import time
import random
from connection import F1DatabaseConnector
from datetime import datetime

def get_random_race_data(connector):
    """Get random valid data for inserting results."""
    cur = connector.connection.cursor()
    
    # Get a random recent race
    cur.execute("""
        SELECT raceid FROM races 
        WHERE year >= 2020 
        ORDER BY RANDOM() 
        LIMIT 1
    """)
    race = cur.fetchone()
    if not race:
        return None
    race_id = race[0]
    
    # Get random driver who doesn't have result for this race yet
    cur.execute("""
        SELECT d.driverid 
        FROM drivers d
        WHERE NOT EXISTS (
            SELECT 1 FROM results r 
            WHERE r.driverid = d.driverid 
            AND r.raceid = %s
        )
        ORDER BY RANDOM()
        LIMIT 1
    """, (race_id,))
    driver = cur.fetchone()
    if not driver:
        return None
    driver_id = driver[0]
    
    # Get random constructor
    cur.execute("""
        SELECT constructorid FROM constructors 
        ORDER BY RANDOM() 
        LIMIT 1
    """)
    constructor = cur.fetchone()
    constructor_id = constructor[0]
    
    # Get finished status
    cur.execute("""
        SELECT statusid FROM status 
        WHERE status = 'Finished' 
        LIMIT 1
    """)
    status = cur.fetchone()
    status_id = status[0]
    
    cur.close()
    
    return {
        'race_id': race_id,
        'driver_id': driver_id,
        'constructor_id': constructor_id,
        'status_id': status_id
    }

def insert_new_result(connector):
    """Insert a new race result."""
    data = get_random_race_data(connector)
    if not data:
        print("⚠️  No available data to insert")
        return False
    
    cur = connector.connection.cursor()
    
    # Generate realistic race data
    position = random.randint(1, 20)
    points = [25, 18, 15, 12, 10, 8, 6, 4, 2, 1] if position <= 10 else [0]
    points_value = points[0] if position <= 10 else 0
    
    grid = random.randint(1, 20)
    laps = random.randint(50, 70)
    milliseconds = random.randint(5400000, 6000000)  # ~90-100 minutes
    
    try:
        # Get next resultId
        cur.execute("SELECT MAX(resultid) FROM results")
        max_id = cur.fetchone()[0]
        next_id = (max_id or 0) + 1
        
        cur.execute("""
            INSERT INTO results (
                resultid, raceid, driverid, constructorid, 
                number, grid, position, positiontext, positionorder,
                points, laps, time, milliseconds, 
                fastestlap, rank, fastestlaptime, fastestlapspeed, statusid
            ) VALUES (
                %s, %s, %s, %s,
                %s, %s, %s, %s, %s,
                %s, %s, NULL, %s,
                NULL, NULL, NULL, NULL, %s
            )
        """, (
            next_id, data['race_id'], data['driver_id'], data['constructor_id'],
            random.randint(1, 99), grid, position, str(position), position,
            points_value, laps, milliseconds,
            data['status_id']
        ))
        
        connector.connection.commit()
        cur.close()
        
        print(f"✅ Inserted result #{next_id}: Driver {data['driver_id']} in Race {data['race_id']}, "
              f"Position {position}, Points {points_value}")
        return True
        
    except Exception as e:
        connector.connection.rollback()
        cur.close()
        print(f"❌ Error inserting result: {e}")
        return False

def main():
    print("🏎️  F1 Auto-Insert Script Started")
    print("=" * 60)
    print("Inserting new race results every 10 seconds...")
    print("Press Ctrl+C to stop")
    print("=" * 60)
    
    connector = F1DatabaseConnector()
    if not connector.connect():
        print("Failed to connect to database")
        return
    
    try:
        count = 0
        while True:
            success = insert_new_result(connector)
            if success:
                count += 1
                print(f"📊 Total inserted: {count} | {datetime.now().strftime('%H:%M:%S')}\n")
            
            time.sleep(10)  # Wait 10 seconds
            
    except KeyboardInterrupt:
        print("\n\n🛑 Auto-insert stopped")
        print(f"Total records inserted: {count}")
    finally:
        connector.disconnect()

if __name__ == "__main__":
    main()

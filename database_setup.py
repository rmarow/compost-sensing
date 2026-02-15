#!/usr/bin/env python3
"""
Database Setup Script - Updated for DS18B20 + DHT11
Creates SQLite database with sensor_type field
"""

import sqlite3
import os
from datetime import datetime
import config_updated as config

def create_database():
    """Create SQLite database and tables"""
    
    # Ensure directory exists
    db_dir = os.path.dirname(config.DATABASE_PATH)
    if not os.path.exists(db_dir):
        os.makedirs(db_dir)
    
    # Connect to database
    conn = sqlite3.connect(config.DATABASE_PATH)
    cursor = conn.cursor()
    
    # Create sensor_readings table with sensor_type
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sensor_readings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME NOT NULL,
            sensor_id TEXT NOT NULL,
            sensor_location TEXT NOT NULL,
            sensor_type TEXT NOT NULL,
            temperature_c REAL NOT NULL,
            temperature_f REAL NOT NULL,
            humidity REAL,
            notes TEXT
        )
    ''')
    
    # Create indexes
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_timestamp 
        ON sensor_readings(timestamp DESC)
    ''')
    
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_sensor_id 
        ON sensor_readings(sensor_id)
    ''')
    
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_sensor_type 
        ON sensor_readings(sensor_type)
    ''')
    
    # Create alerts table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME NOT NULL,
            sensor_id TEXT NOT NULL,
            alert_type TEXT NOT NULL,
            message TEXT NOT NULL,
            value REAL NOT NULL,
            threshold REAL NOT NULL,
            acknowledged BOOLEAN DEFAULT 0,
            acknowledged_at DATETIME
        )
    ''')
    
    # Create system_status table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS system_status (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME NOT NULL,
            status_type TEXT NOT NULL,
            message TEXT,
            details TEXT
        )
    ''')
    
    # Create sync_log table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sync_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME NOT NULL,
            sync_type TEXT NOT NULL,
            records_synced INTEGER,
            status TEXT NOT NULL,
            error_message TEXT
        )
    ''')
    
    # Commit changes
    conn.commit()
    
    # Log database creation
    cursor.execute('''
        INSERT INTO system_status (timestamp, status_type, message)
        VALUES (?, 'database_init', 'Database initialized for DS18B20 + DHT11')
    ''', (datetime.now(),))
    
    conn.commit()
    conn.close()
    
    print(f"✅ Database created successfully at: {config.DATABASE_PATH}")
    print("\nTables created:")
    print("  - sensor_readings: Stores temp/humidity from all sensors")
    print("    (includes sensor_type: DS18B20 or DHT11)")
    print("  - alerts: Tracks threshold violations")
    print("  - system_status: System health and events")
    print("  - sync_log: Google Sheets sync history")

def verify_database():
    """Verify database structure"""
    conn = sqlite3.connect(config.DATABASE_PATH)
    cursor = conn.cursor()
    
    # Get table list
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    
    print("\n📊 Database verification:")
    print(f"Location: {config.DATABASE_PATH}")
    print(f"Tables: {len(tables)}")
    
    for table in tables:
        table_name = table[0]
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cursor.fetchone()[0]
        print(f"  - {table_name}: {count} records")
    
    conn.close()

def add_test_data():
    """Add sample data for testing dashboard"""
    conn = sqlite3.connect(config.DATABASE_PATH)
    cursor = conn.cursor()
    
    print("\n🧪 Adding test data...")
    
    from datetime import timedelta
    now = datetime.now()
    
    # Add DS18B20 test readings
    for i in range(10):
        timestamp = now - timedelta(minutes=i*5)
        temp_c = 55 + (i % 5)  # Vary between 55-59°C
        temp_f = temp_c * (9/5) + 32
        
        cursor.execute('''
            INSERT INTO sensor_readings 
            (timestamp, sensor_id, sensor_location, sensor_type,
             temperature_c, temperature_f, humidity, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (timestamp, 'bin1_probe', 'Bin 1 - Compost Core', 'DS18B20',
              temp_c, temp_f, None, 'Test data'))
    
    # Add DHT11 test readings
    for i in range(10):
        timestamp = now - timedelta(minutes=i*5)
        temp_c = 20 + (i % 3)  # Vary between 20-22°C
        temp_f = temp_c * (9/5) + 32
        humidity = 50 + (i % 10)  # Vary between 50-59%
        
        cursor.execute('''
            INSERT INTO sensor_readings 
            (timestamp, sensor_id, sensor_location, sensor_type,
             temperature_c, temperature_f, humidity, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (timestamp, 'bin1_ambient', 'Bin 1 - Ambient', 'DHT11',
              temp_c, temp_f, humidity, 'Test data'))
    
    conn.commit()
    conn.close()
    print("✅ Test data added (10 DS18B20 + 10 DHT11 readings)")

if __name__ == "__main__":
    print("=" * 60)
    print("Farm Monitoring System - Database Setup")
    print("Updated for DS18B20 + DHT11 Sensors")
    print("=" * 60)
    
    # Check if database exists
    if os.path.exists(config.DATABASE_PATH):
        response = input(f"\n⚠️  Database already exists at {config.DATABASE_PATH}\nRecreate? (y/N): ")
        if response.lower() != 'y':
            print("Exiting without changes")
            exit()
        os.remove(config.DATABASE_PATH)
    
    # Create database
    create_database()
    
    # Verify
    verify_database()
    
    # Ask about test data
    response = input("\nAdd test data for dashboard testing? (y/N): ")
    if response.lower() == 'y':
        add_test_data()
        verify_database()
    
    print("\n✅ Setup complete! You can now run data_collector_updated.py")

#!/usr/bin/env python3
"""
Database Setup — Milk & Honey Farm Compost Monitoring
Builds all tables from scratch. Run once before first deployment.

Tables created:
  compost_readings  — DS18B20 temperature data (two probes: shallow + deep)
  weather_readings  — Ecowitt GW1100 + WS69 weather station data
  alerts            — Threshold violation history
  system_status     — System health and lifecycle events
  sync_log          — Google Sheets sync history
"""

import sqlite3
import os
from datetime import datetime, timedelta

try:
    from config_local import *
except ImportError:
    from config import *


# ============================================================
# CREATE
# ============================================================

def create_database():
    db_dir = os.path.dirname(DATABASE_PATH)
    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir)

    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()

    # ---- Compost temperature readings -----------------------
    # One row per probe reading. Two probes on the same 1-Wire bus:
    #   probe_id      → human label: "shallow" or "deep"
    #   probe_address → 1-Wire hardware ID (e.g. "28-0000XXXXXXXX")
    #                   lets you trace exactly which physical sensor
    #                   a reading came from even if labels change
    #   humidity      → nullable, reserved for future humidity sensor
    c.execute("""
        CREATE TABLE IF NOT EXISTS compost_readings (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp       TEXT    NOT NULL,
            probe_id        TEXT    NOT NULL,
            probe_address   TEXT    NOT NULL,
            probe_location  TEXT    NOT NULL,
            temperature_c   REAL    NOT NULL,
            temperature_f   REAL    NOT NULL,
            humidity        REAL,
            notes           TEXT
        )
    """)
    c.execute("CREATE INDEX IF NOT EXISTS idx_compost_ts     ON compost_readings(timestamp DESC)")
    c.execute("CREATE INDEX IF NOT EXISTS idx_compost_probe  ON compost_readings(probe_id)")
    c.execute("CREATE INDEX IF NOT EXISTS idx_compost_addr   ON compost_readings(probe_address)")

    # ---- Weather station readings ---------------------------
    # Populated by weather_station.py polling the GW1100 local API.
    # All columns nullable — the gateway has built-in indoor sensors
    # even before the WS69 outdoor array arrives.
    c.execute("""
        CREATE TABLE IF NOT EXISTS weather_readings (
            id                  INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp           TEXT    NOT NULL,

            outdoor_temp_f      REAL,
            outdoor_temp_c      REAL,
            outdoor_humidity    REAL,

            wind_speed_mph      REAL,
            wind_gust_mph       REAL,
            wind_direction_deg  REAL,

            rain_rate_in_hr     REAL,
            rain_daily_in       REAL,
            rain_event_in       REAL,

            indoor_temp_f       REAL,
            indoor_humidity     REAL
        )
    """)
    c.execute("CREATE INDEX IF NOT EXISTS idx_weather_ts ON weather_readings(timestamp DESC)")

    # ---- Alerts ---------------------------------------------
    c.execute("""
        CREATE TABLE IF NOT EXISTS alerts (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp       TEXT    NOT NULL,
            probe_id        TEXT    NOT NULL,
            alert_type      TEXT    NOT NULL,
            message         TEXT    NOT NULL,
            value           REAL    NOT NULL,
            threshold       REAL    NOT NULL,
            acknowledged    INTEGER DEFAULT 0,
            acknowledged_at TEXT
        )
    """)
    c.execute("CREATE INDEX IF NOT EXISTS idx_alerts_ts ON alerts(timestamp DESC)")

    # ---- System status --------------------------------------
    c.execute("""
        CREATE TABLE IF NOT EXISTS system_status (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp   TEXT NOT NULL,
            status_type TEXT NOT NULL,
            message     TEXT,
            details     TEXT
        )
    """)

    # ---- Google Sheets sync log -----------------------------
    c.execute("""
        CREATE TABLE IF NOT EXISTS sync_log (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp       TEXT NOT NULL,
            sync_type       TEXT NOT NULL,
            records_synced  INTEGER,
            status          TEXT NOT NULL,
            error_message   TEXT
        )
    """)

    # Record this setup run
    c.execute("""
        INSERT INTO system_status (timestamp, status_type, message)
        VALUES (?, 'database_init', 'Database created — two DS18B20 probes + GW1100 weather')
    """, (datetime.now().isoformat(),))

    conn.commit()
    conn.close()

    print(f"✅ Database created: {DATABASE_PATH}")
    print()
    print("Tables:")
    print("  compost_readings  — DS18B20 temps (shallow + deep probes)")
    print("  weather_readings  — GW1100 + WS69 weather station")
    print("  alerts            — threshold violations")
    print("  system_status     — system events")
    print("  sync_log          — Google Sheets sync history")


# ============================================================
# VERIFY
# ============================================================

def verify_database():
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()

    c.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = [r[0] for r in c.fetchall()]

    print()
    print(f"📊 Database: {DATABASE_PATH}")
    for table in tables:
        count = c.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        print(f"   {table:<22} {count} rows")

    conn.close()


# ============================================================
# TEST DATA
# ============================================================

def add_test_data():
    """Insert realistic sample data so the dashboard has something to show."""
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()

    now = datetime.now()

    # Two probes — shallow and deep
    probes = [
        ("shallow", "28-000000000001", "Bin 1 - Shallow (6 inch)",  52.0),
        ("deep",    "28-000000000002", "Bin 1 - Deep (24 inch)",    61.0),
    ]

    for probe_id, probe_addr, location, base_temp in probes:
        for i in range(24):   # 24 readings, one per hour
            ts   = (now - timedelta(hours=i)).isoformat()
            tc   = round(base_temp + (i % 5) * 0.4, 2)
            tf   = round(tc * 9/5 + 32, 2)
            c.execute("""
                INSERT INTO compost_readings
                    (timestamp, probe_id, probe_address, probe_location,
                     temperature_c, temperature_f, humidity, notes)
                VALUES (?, ?, ?, ?, ?, ?, NULL, 'test data')
            """, (ts, probe_id, probe_addr, location, tc, tf))

    # Weather samples
    for i in range(24):
        ts = (now - timedelta(hours=i)).isoformat()
        c.execute("""
            INSERT INTO weather_readings
                (timestamp,
                 outdoor_temp_f, outdoor_temp_c, outdoor_humidity,
                 wind_speed_mph, wind_gust_mph, wind_direction_deg,
                 rain_rate_in_hr, rain_daily_in, rain_event_in,
                 indoor_temp_f, indoor_humidity)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (ts,
              round(58 + i * 0.3, 1), round(14 + i * 0.15, 1), round(45 + i % 10, 1),
              round(5 + i % 8, 1),    round(9 + i % 12, 1),    round((180 + i * 15) % 360, 0),
              0.0, round(0.12 + i * 0.01, 2), 0.05,
              round(65 + i % 5, 1),   round(38 + i % 8, 1)))

    conn.commit()
    conn.close()
    print("✅ Test data added: 48 compost readings (2 probes × 24h) + 24 weather readings")


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    print("=" * 60)
    print("Milk & Honey Farm — Database Setup")
    print("=" * 60)

    if os.path.exists(DATABASE_PATH):
        resp = input(f"\n⚠️  Database already exists at:\n   {DATABASE_PATH}\nRecreate from scratch? (y/N): ")
        if resp.lower() != "y":
            print("Exiting — no changes made.")
            raise SystemExit
        os.remove(DATABASE_PATH)
        print("Old database removed.")

    create_database()
    verify_database()

    resp = input("\nAdd test data so the dashboard has something to show? (y/N): ")
    if resp.lower() == "y":
        add_test_data()
        verify_database()

    print()
    print("✅ Setup complete — run data_collector.py to start collecting data.")

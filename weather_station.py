#!/usr/bin/env python3
"""
Ecowitt GW1100 Weather Station Integration
Polls the GW1100 local API and saves data to the existing SQLite database.

The GW1100 exposes a local HTTP endpoint at:
  http://<gateway-ip>/get_livedata_info

No internet required — all data stays on your local network.
"""

import requests
import sqlite3
import logging
from datetime import datetime

try:
    from config_local import *
except ImportError:
    from config import *

logger = logging.getLogger(__name__)


# ============================================================
# FETCH FROM GW1100
# ============================================================

def fetch_weather_data():
    """
    Query the GW1100 local API and return a flat dict of readings.
    Returns None if the gateway is unreachable or returns bad data.
    """
    url = f"http://{WEATHER_STATION_IP}/get_livedata_info"

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        raw = response.json()
    except requests.exceptions.ConnectionError:
        logger.warning(f"Cannot reach GW1100 at {WEATHER_STATION_IP} — is it on the network?")
        return None
    except requests.exceptions.Timeout:
        logger.warning("GW1100 request timed out")
        return None
    except Exception as e:
        logger.error(f"Unexpected error fetching weather data: {e}")
        return None

    return parse_weather_data(raw)


def parse_weather_data(raw):
    """
    Parse the GW1100 JSON response into a flat dict with consistent keys.
    The GW1100 returns nested dicts; we flatten only what we need.
    """
    try:
        outdoor = raw.get("outdoor", {})
        wind    = raw.get("wind", {})
        rain    = raw.get("rainfall", {})
        indoor  = raw.get("indoor", {})

        def val(section, key):
            """Safely extract a numeric value, return None if missing."""
            try:
                return float(section[key]["value"])
            except (KeyError, TypeError, ValueError):
                return None

        data = {
            # Outdoor temperature — GW1100 returns °F by default
            "outdoor_temp_f":     val(outdoor, "temperature"),
            "outdoor_humidity":   val(outdoor, "humidity"),

            # Wind
            "wind_speed_mph":     val(wind, "wind_speed"),
            "wind_gust_mph":      val(wind, "wind_gust"),
            "wind_direction_deg": val(wind, "wind_direction"),

            # Rainfall
            "rain_rate_in_hr":    val(rain, "rain_rate"),
            "rain_daily_in":      val(rain, "daily"),
            "rain_event_in":      val(rain, "event"),

            # Indoor (built into GW1100 unit itself)
            "indoor_temp_f":      val(indoor, "temperature"),
            "indoor_humidity":    val(indoor, "humidity"),

            "timestamp": datetime.now().isoformat(),
            "raw_response": str(raw),  # keep for debugging
        }

        # Convert outdoor temp to Celsius too
        if data["outdoor_temp_f"] is not None:
            data["outdoor_temp_c"] = round(
                (data["outdoor_temp_f"] - 32) * 5 / 9, 2
            )
        else:
            data["outdoor_temp_c"] = None

        return data

    except Exception as e:
        logger.error(f"Failed to parse weather data: {e}")
        logger.debug(f"Raw response was: {raw}")
        return None


# ============================================================
# SAVE TO DATABASE
# ============================================================

def save_weather_reading(data):
    """Save a parsed weather reading to the weather_readings table."""
    if data is None:
        logger.warning("No data to save — skipping")
        return False

    conn = sqlite3.connect(DATABASE_PATH)
    try:
        conn.execute("""
            INSERT INTO weather_readings (
                timestamp,
                outdoor_temp_f,
                outdoor_temp_c,
                outdoor_humidity,
                wind_speed_mph,
                wind_gust_mph,
                wind_direction_deg,
                rain_rate_in_hr,
                rain_daily_in,
                rain_event_in,
                indoor_temp_f,
                indoor_humidity
            ) VALUES (
                :timestamp,
                :outdoor_temp_f,
                :outdoor_temp_c,
                :outdoor_humidity,
                :wind_speed_mph,
                :wind_gust_mph,
                :wind_direction_deg,
                :rain_rate_in_hr,
                :rain_daily_in,
                :rain_event_in,
                :indoor_temp_f,
                :indoor_humidity
            )
        """, data)
        conn.commit()
        logger.info(
            f"Weather saved: "
            f"{data['outdoor_temp_f']}°F  "
            f"{data['outdoor_humidity']}% RH  "
            f"Wind {data['wind_speed_mph']} mph @ {data['wind_direction_deg']}°  "
            f"Rain {data['rain_daily_in']}\" today"
        )
        return True
    except Exception as e:
        logger.error(f"Failed to save weather reading: {e}")
        return False
    finally:
        conn.close()


# ============================================================
# CONVENIENCE: FETCH LATEST FROM DB (for dashboard)
# ============================================================

def get_latest_weather():
    """Return the most recent weather reading from the database as a dict."""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    try:
        row = conn.execute("""
            SELECT * FROM weather_readings
            ORDER BY timestamp DESC
            LIMIT 1
        """).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def get_weather_history(hours=24):
    """Return the last N hours of weather readings as a list of dicts."""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    try:
        rows = conn.execute("""
            SELECT * FROM weather_readings
            WHERE timestamp >= datetime('now', ?)
            ORDER BY timestamp ASC
        """, (f"-{hours} hours",)).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


# ============================================================
# WIND DIRECTION HELPER
# ============================================================

def degrees_to_compass(degrees):
    """Convert wind direction in degrees to a compass label (N, NE, etc.)."""
    if degrees is None:
        return "—"
    directions = [
        "N", "NNE", "NE", "ENE",
        "E", "ESE", "SE", "SSE",
        "S", "SSW", "SW", "WSW",
        "W", "WNW", "NW", "NNW"
    ]
    index = round(degrees / 22.5) % 16
    return directions[index]


# ============================================================
# QUICK TEST
# ============================================================

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print("Testing GW1100 connection...\n")

    data = fetch_weather_data()

    if data:
        print("✅  Live data from GW1100:")
        print(f"  Outdoor Temp:  {data['outdoor_temp_f']}°F  /  {data['outdoor_temp_c']}°C")
        print(f"  Humidity:      {data['outdoor_humidity']}%")
        print(f"  Wind:          {data['wind_speed_mph']} mph  {degrees_to_compass(data['wind_direction_deg'])}  (gust {data['wind_gust_mph']} mph)")
        print(f"  Rain today:    {data['rain_daily_in']}\"")
        print(f"  Rain rate:     {data['rain_rate_in_hr']}\"/hr")
        print(f"  Indoor:        {data['indoor_temp_f']}°F  {data['indoor_humidity']}% RH")
    else:
        print("❌  Could not reach GW1100.")
        print(f"   Make sure WEATHER_STATION_IP in config.py is correct.")
        print(f"   Current value: {WEATHER_STATION_IP}")
        print("   Find the IP in your router's device list or the Ecowitt app.")

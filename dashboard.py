#!/usr/bin/env python3
"""
Flask Dashboard — Milk & Honey Farm Compost Monitoring
"""

from flask import Flask, render_template, jsonify, request
import sqlite3
from datetime import datetime, timedelta
import config
from weather_station import get_latest_weather, get_weather_history, degrees_to_compass

app = Flask(__name__)
app.config['DEBUG'] = config.FLASK_DEBUG


# ============================================================
# DATABASE HELPERS
# ============================================================

def get_db():
    conn = sqlite3.connect(config.DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def get_latest_readings():
    """Most recent reading from each probe (shallow + deep)."""
    conn = get_db()
    rows = conn.execute("""
        SELECT cr.*
        FROM compost_readings cr
        INNER JOIN (
            SELECT probe_id, MAX(timestamp) AS latest
            FROM compost_readings
            GROUP BY probe_id
        ) latest ON cr.probe_id = latest.probe_id
                     AND cr.timestamp = latest.latest
        ORDER BY cr.probe_id
    """).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_recent_alerts(hours=24):
    """Unacknowledged alerts from the last N hours."""
    conn = get_db()
    since = (datetime.now() - timedelta(hours=hours)).isoformat()
    rows = conn.execute("""
        SELECT * FROM alerts
        WHERE timestamp > ? AND acknowledged = 0
        ORDER BY timestamp DESC
    """, (since,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_compost_history(probe_id, hours=24):
    """Historical compost readings for a single probe."""
    conn = get_db()
    since = (datetime.now() - timedelta(hours=hours)).isoformat()
    rows = conn.execute("""
        SELECT timestamp, temperature_c, temperature_f, humidity
        FROM compost_readings
        WHERE probe_id = ? AND timestamp > ?
        ORDER BY timestamp ASC
    """, (probe_id, since)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ============================================================
# ROUTES
# ============================================================

@app.route('/')
def index():
    readings = get_latest_readings()
    alerts   = get_recent_alerts(hours=24)

    # Weather
    weather      = get_latest_weather()
    wind_compass = degrees_to_compass(
        weather['wind_direction_deg'] if weather else None
    )

    # Last Google Sheets sync
    conn = get_db()
    last_sync_row = conn.execute("""
        SELECT timestamp FROM sync_log
        WHERE status = 'success'
        ORDER BY timestamp DESC LIMIT 1
    """).fetchone()
    last_sync = last_sync_row['timestamp'] if last_sync_row else None

    # Total reading count
    total_readings = conn.execute(
        "SELECT COUNT(*) FROM compost_readings"
    ).fetchone()[0]
    conn.close()

    return render_template('dashboard.html',
                           readings=readings,
                           alerts=alerts,
                           weather=weather,
                           wind_compass=wind_compass,
                           total_readings=total_readings,
                           last_sync=last_sync,
                           config=config)


@app.route('/api/latest')
def api_latest():
    """Latest compost + weather readings (used by auto-refresh)."""
    weather = get_latest_weather()
    return jsonify({
        'readings':     get_latest_readings(),
        'alerts':       get_recent_alerts(hours=1),
        'weather':      weather,
        'wind_compass': degrees_to_compass(
            weather['wind_direction_deg'] if weather else None
        ),
        'timestamp':    datetime.now().isoformat()
    })


@app.route('/api/historical/<probe_id>')
def api_historical(probe_id):
    """Historical compost data for a probe (shallow or deep)."""
    hours = request.args.get('hours', default=24, type=int)
    data  = get_compost_history(probe_id, hours)
    return jsonify({'probe_id': probe_id, 'hours': hours, 'data': data})


@app.route('/api/weather')
def api_weather():
    """Historical weather data for charts."""
    hours = request.args.get('hours', default=24, type=int)
    return jsonify(get_weather_history(hours=hours))


@app.route('/api/stats')
def api_stats():
    """System statistics."""
    conn = get_db()

    total   = conn.execute("SELECT COUNT(*) FROM compost_readings").fetchone()[0]
    n_alert = conn.execute(
        "SELECT COUNT(*) FROM alerts WHERE acknowledged = 0"
    ).fetchone()[0]

    row = conn.execute("""
        SELECT MIN(timestamp) AS first, MAX(timestamp) AS last
        FROM compost_readings
    """).fetchone()
    conn.close()

    uptime_days = 0
    if row['first'] and row['last']:
        uptime_days = (
            datetime.fromisoformat(row['last']) -
            datetime.fromisoformat(row['first'])
        ).days

    return jsonify({
        'total_readings': total,
        'active_alerts':  n_alert,
        'uptime_days':    uptime_days,
        'first_reading':  row['first'],
        'last_reading':   row['last']
    })


# ============================================================
# MAIN
# ============================================================

if __name__ == '__main__':
    print("=" * 60)
    print("Farm Monitoring Dashboard — Milk & Honey Farm")
    print("=" * 60)
    print(f"URL:      http://{config.FLASK_HOST}:{config.FLASK_PORT}")
    print(f"Database: {config.DATABASE_PATH}")
    print(f"Refresh:  every {config.DASHBOARD_REFRESH}s")
    print("=" * 60)
    print("Press Ctrl+C to stop\n")
    app.run(host=config.FLASK_HOST, port=config.FLASK_PORT)

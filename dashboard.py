#!/usr/bin/env python3
"""
Flask Dashboard for Farm Monitoring System
Web interface for viewing sensor data, alerts, and system status
"""

from flask import Flask, render_template, jsonify, request
import sqlite3
from datetime import datetime, timedelta
import json
import config


app = Flask(__name__)
app.config['DEBUG'] = config.FLASK_DEBUG

def get_db_connection():
    """Create database connection"""
    conn = sqlite3.connect(config.DATABASE_PATH)
    conn.row_factory = sqlite3.Row  # Return rows as dictionaries
    return conn

def get_latest_readings():
    """Get the most recent reading from each sensor"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    readings = []
    for sensor_config in config.DS18B20_LOCATIONS:
        if sensor_config['enabled']:
            cursor.execute('''
                SELECT * FROM sensor_readings 
                WHERE sensor_id = ?
                ORDER BY timestamp DESC 
                LIMIT 1
            ''', (sensor_config['id'],))
            
            row = cursor.fetchone()
            if row:
                readings.append(dict(row))
    
    conn.close()
    return readings

def get_recent_alerts(hours=24):
    """Get recent unacknowledged alerts"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    since = datetime.now() - timedelta(hours=hours)
    cursor.execute('''
        SELECT * FROM alerts 
        WHERE timestamp > ? AND acknowledged = 0
        ORDER BY timestamp DESC
    ''', (since,))
    
    alerts = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return alerts

def get_historical_data(sensor_id, hours=24):
    """Get historical sensor data for charting"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    since = datetime.now() - timedelta(hours=hours)
    cursor.execute('''
        SELECT timestamp, temperature_c, humidity
        FROM sensor_readings 
        WHERE sensor_id = ? AND timestamp > ?
        ORDER BY timestamp ASC
    ''', (sensor_id, since))
    
    data = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return data

@app.route('/')
def index():
    """Main dashboard page"""
    latest_readings = get_latest_readings()
    recent_alerts = get_recent_alerts(hours=24)
    
    # Get system status
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Count total readings
    cursor.execute('SELECT COUNT(*) as count FROM sensor_readings')
    total_readings = cursor.fetchone()['count']
    
    # Get last sync time (if Google Sheets enabled)
    cursor.execute('''
        SELECT timestamp FROM sync_log 
        WHERE status = 'success' 
        ORDER BY timestamp DESC 
        LIMIT 1
    ''')
    last_sync_row = cursor.fetchone()
    last_sync = last_sync_row['timestamp'] if last_sync_row else None
    
    conn.close()
    
    return render_template('dashboard.html',
                         readings=latest_readings,
                         alerts=recent_alerts,
                         total_readings=total_readings,
                         last_sync=last_sync,
                         config=config)

@app.route('/api/latest')
def api_latest():
    """API endpoint for latest sensor readings (for auto-refresh)"""
    readings = get_latest_readings()
    alerts = get_recent_alerts(hours=1)  # Last hour of alerts
    
    return jsonify({
        'readings': readings,
        'alerts': alerts,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/historical/<sensor_id>')
def api_historical(sensor_id):
    """API endpoint for historical data (for charts)"""
    hours = request.args.get('hours', default=24, type=int)
    data = get_historical_data(sensor_id, hours)
    
    return jsonify({
        'sensor_id': sensor_id,
        'hours': hours,
        'data': data
    })

@app.route('/api/stats')
def api_stats():
    """API endpoint for system statistics"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get various statistics
    cursor.execute('SELECT COUNT(*) as count FROM sensor_readings')
    total_readings = cursor.fetchone()['count']
    
    cursor.execute('SELECT COUNT(*) as count FROM alerts WHERE acknowledged = 0')
    active_alerts = cursor.fetchone()['count']
    
    cursor.execute('''
        SELECT MIN(timestamp) as first, MAX(timestamp) as last 
        FROM sensor_readings
    ''')
    row = cursor.fetchone()
    first_reading = row['first']
    last_reading = row['last']
    
    # Calculate uptime
    if first_reading and last_reading:
        first_dt = datetime.fromisoformat(first_reading)
        last_dt = datetime.fromisoformat(last_reading)
        uptime_days = (last_dt - first_dt).days
    else:
        uptime_days = 0
    
    conn.close()
    
    return jsonify({
        'total_readings': total_readings,
        'active_alerts': active_alerts,
        'uptime_days': uptime_days,
        'first_reading': first_reading,
        'last_reading': last_reading
    })

if __name__ == '__main__':
    print("=" * 60)
    print("Starting Farm Monitoring Dashboard")
    print("=" * 60)
    print(f"Dashboard URL: http://{config.FLASK_HOST}:{config.FLASK_PORT}")
    print(f"Database: {config.DATABASE_PATH}")
    print(f"Auto-refresh: {config.DASHBOARD_REFRESH} seconds")
    print("=" * 60)
    print("\nPress Ctrl+C to stop\n")
    
    app.run(host=config.FLASK_HOST, port=config.FLASK_PORT)

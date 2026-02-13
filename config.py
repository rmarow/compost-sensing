"""
Configuration file for Farm Monitoring System
Adjust these settings for your deployment
"""

# ============================================================================
# SENSOR CONFIGURATION
# ============================================================================

# DHT22 Sensor GPIO Pin (BCM numbering)
DHT22_GPIO_PIN = 4  # GPIO 4 = Physical Pin 7

# Sensor reading interval (seconds)
READING_INTERVAL = 300  # 5 minutes

# ============================================================================
# ALERT THRESHOLDS
# ============================================================================

# Temperature alerts (Celsius)
TEMP_HIGH_THRESHOLD = 71.1  # Alert if above 71.1°C (159.98°F)
TEMP_LOW_THRESHOLD = 54.5   # Alert if below 54.5°C (130.1°F)

# Humidity/Moisture alerts (percentage)
#TODO: ask becca and talia about this range
HUMIDITY_LOW_THRESHOLD = 40  # Alert if below 40%
HUMIDITY_HIGH_THRESHOLD = 70 # Alert if above 70%

# ============================================================================
# DATABASE CONFIGURATION
# ============================================================================

DATABASE_PATH = "/home/pi/farm-monitoring/compost_data.db"

# Data retention (days) - older data will be archived
DATA_RETENTION_DAYS = 365

# ============================================================================
# DASHBOARD CONFIGURATION
# ============================================================================

# Flask server settings
FLASK_HOST = "0.0.0.0"  # Listen on all network interfaces
FLASK_PORT = 5000
FLASK_DEBUG = False  # Set to True for development

# Dashboard refresh rate (seconds)
DASHBOARD_REFRESH = 30

# ============================================================================
# GOOGLE SHEETS INTEGRATION
# ============================================================================

# Enable/disable Google Sheets sync
GOOGLE_SHEETS_ENABLED = False  # Set to True when configured

# Google Sheets credentials file path
GOOGLE_CREDENTIALS_FILE = "/home/pi/farm-monitoring/credentials.json"

# Google Sheet name
GOOGLE_SHEET_NAME = "Milk and Honey Farm - Compost Data"

# Sync interval (seconds) - SOW specifies hourly
GOOGLE_SHEETS_SYNC_INTERVAL = 3600  # 1 hour

# ============================================================================
# ALERT NOTIFICATIONS
# ============================================================================

# Enable/disable email alerts
EMAIL_ALERTS_ENABLED = False  # Set to True when configured

# Email settings (for Gmail, you'll need an app-specific password)
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USERNAME = "your-email@gmail.com"
SMTP_PASSWORD = "your-app-specific-password"

# Alert recipients (list of email addresses)
ALERT_RECIPIENTS = [
    "farm-manager@example.com",
]

# Alert cooldown (seconds) - prevent spam
# Won't send duplicate alerts within this period
ALERT_COOLDOWN = 3600  # 1 hour

# ============================================================================
# COMPOST BIN CONFIGURATION
# ============================================================================

# Sensor locations (for  multi-bin expansion)
SENSOR_LOCATIONS = [
    {
        "id": "bin1_top",
        "name": "Bin 1 - Top",
        "gpio_pin": 4,
        "enabled": True
    },
    # Add more sensors as you expand
=

# ============================================================================
# LOGGING
# ============================================================================

LOG_FILE = "/home/pi/farm-monitoring/farm_monitor.log"
LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL

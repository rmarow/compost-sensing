"""
Configuration file for Farm Monitoring System
Updated for DS18B20 (waterproof temp) + DHT11 (ambient temp/humidity)
"""

# ============================================================================
# SENSOR CONFIGURATION
# ============================================================================

# Sensor reading interval (seconds)
READING_INTERVAL = 1800  # 30 minutes

# ============================================================================
# DS18B20 CONFIGURATION (Waterproof Temperature Probes)
# ============================================================================

DS18B20_ENABLED = True

# DS18B20 sensor locations (will auto-detect sensor IDs)
DS18B20_LOCATIONS = [
    {
        "id": "1ft_probe",
        "name": "Shorter probe",
        "device_id": "28-0000005fe1bf"
        "enabled": True,
    },
    {
        "id": "2ft_probe",
        "name": "Longer probe",
        "device_id": "28-0000005f6979"
        "enabled": True,
    },
]

# DS18B20 temperature thresholds (Celsius)
DS18B20_TEMP_HIGH_THRESHOLD = 65  # Alert if above 65°C
DS18B20_TEMP_LOW_THRESHOLD = 40   # Alert if below 40°C

# ============================================================================
# DHT11 CONFIGURATION (Ambient Temperature & Humidity)
# ============================================================================

DHT11_SENSORS = [
    {
        "id": "bin1_ambient",
        "name": "Bin 1 - Ambient",
        "gpio_pin": 17,  # GPIO 17 = Physical Pin 11
        "enabled": False 
    },
]

# DHT11 Temperature thresholds (Celsius)
DHT11_TEMP_HIGH_THRESHOLD = 40
DHT11_TEMP_LOW_THRESHOLD = 0

# DHT11 Humidity thresholds (percentage)
DHT11_HUMIDITY_LOW_THRESHOLD = 40
DHT11_HUMIDITY_HIGH_THRESHOLD = 70

# ============================================================================
# DATABASE CONFIGURATION
# ============================================================================

DATABASE_PATH = "/home/rmarowitz/compost-sensing/compost_data.db"
# TODO: figure out how long this should be
### NOTE: May want to change to daily or weekly averages and keep for more than a year
DATA_RETENTION_DAYS = 365

# ============================================================================
# DASHBOARD CONFIGURATION
# ============================================================================

FLASK_HOST = "0.0.0.0"
FLASK_PORT = 5000
FLASK_DEBUG = False
DASHBOARD_REFRESH = 30

# ============================================================================
# GOOGLE SHEETS INTEGRATION
# ============================================================================

GOOGLE_SHEETS_ENABLED = False
GOOGLE_CREDENTIALS_FILE = "/home/rmarowitz/compost-sensing/credentials.json"
GOOGLE_SHEET_NAME = "Milk and Honey Farm - Compost Data"
GOOGLE_SHEETS_SYNC_INTERVAL = 3600

# ============================================================================
# ALERT NOTIFICATIONS
# ============================================================================

# Enable/disable email alerts
EMAIL_ALERTS_ENABLED = True  # Set to True when configured

# Email settings (for Gmail, you'll need an app-specific password)
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
# TODO - May need to get a system email or something for milk and honey
SMTP_USERNAME = "marowitzrobyn14@gmail.com"
SMTP_PASSWORD = ""

# Alert recipients (list of email addresses)
ALERT_RECIPIENTS = [
    # "farmerbecca@boulderjcc.org",
    # "talia.edah@boulderjcc.org",
    "marowitzrobyn14@gmail.com"
]

# Alert cooldown (seconds) - prevent spam
# Won't send duplicate alerts within this period
ALERT_COOLDOWN = 3600  # 1 hour

# ============================================================================
# SMS ALERTS (Two Options)
# ============================================================================

# TODO: figure out if text is needed
#  Email-to-SMS Gateway (FREE!)
# Use your carrier's email-to-SMS gateway
# Each carrier has an email address that converts to SMS
# Format: phonenumber@carrier-gateway.com
# 
# Common carrier gateways:
# Verizon: phonenumber@vtext.com
# AT&T: phonenumber@txt.att.net  
# T-Mobile: phonenumber@tmomail.net
# Sprint: phonenumber@messaging.sprintpcs.com
# 
# Example: 3035551234@vtext.com

SMS_RECIPIENTS = [
    # Add phone numbers (Twilio) or email-to-SMS addresses (free)
    # "5551234567",  # For Twilio
    # "5551234567@vtext.com",  # For free email-to-SMS
]

# ============================================================================
# LOGGING
# ============================================================================

LOG_FILE = "/home/rmarowitz/compost-sensing/compost-sensing.log"
LOG_LEVEL = "INFO"

# ============================================================================
# ADVANCED SETTINGS
# ============================================================================

W1_DEVICE_DIR = "/sys/bus/w1/devices"
DS18B20_CONVERSION_TIME = 0.75
DHT11_MAX_RETRIES = 3
DHT11_RETRY_DELAY = 2

try:
    from config_local import *
except ImportError:
    pass


# --- Weather Station (Ecowitt GW1100) ---
 
# IP address of your GW1100 on the local network.
# Find it in your router's device list, or in the Ecowitt app
# under "Device List" after the gateway connects to WiFi.
WEATHER_STATION_IP = "192.168.1.XXX"   # <-- update this after setup
 
# How often to poll the GW1100 (seconds).
# 16 seconds matches the WS69 sensor reporting interval.
WEATHER_READING_INTERVAL = 60   # once per minute is plenty for a dashboard

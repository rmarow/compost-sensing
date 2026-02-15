# Farm Monitoring System - Quick Start Guide
## Milk and Honey Farm at Boulder JCC

This is a  guide to setting up and running the compost monitoring system.


### Core Files
- **`GETTING_STARTED.md`** - Hardware setup guide (wiring diagrams, initial config)
- **`wiring_guide.md`** - How to wire the sensors
- **`config.py`** - All configuration settings (thresholds, intervals, etc.)
- **`database_setup.py`** - Creates the SQLite database
- **`sensor_test.py`** - Tests your DHT22 sensor
- **`data_collector.py`** - Main monitoring script (runs continuously)
- **`dashboard.py`** - Flask web server for the dashboard
- **`templates/dashboard.html`** - Dashboard web interface

## 🚀 Quick Start (5 Steps)

### Step 1: Read the Wiring Guide

`/WIRING_GUIDE.md`

### Step 2: Copy Files to Your Raspberry Pi

```bash
# On your computer, copy all files to the Pi
scp -r /home/claude/* pi@raspberrypi.local:~/farm-monitoring/

# OR use a USB drive or Git
```

### Step 3: SSH into Your Pi

```bash
ssh pi@raspberrypi.local

sudo raspi-config

sudo reboot
```

### Step 4: Install Dependencies

```bash 
cd ~/farm-monitoring

python3 -m venv venv
source venv/bin/activate

# Install required packages
pip install -r requirements_updated.txt
```

### Step 5: Test Your Sensor

```bash
python sensor_test.py
```

### Step 6: Initialize Database and Start Monitoring

```bash
# Create database
python database_setup.py

# Start data collector (in one terminal)
python data_collector.py

# Start dashboard (in another terminal)
python dashboard.py
```

Now open your web browser and go to: **http://raspberrypi.local:5000**

🎉 You should see your dashboard!

## 🔧 Configuration

Edit `config.py` to change:

### Alert Thresholds

#### DS18B20 Settings (Compost Temperature)

```python
DS18B20_ENABLED = True

DS18B20_LOCATIONS = [
    {
        "id": "bin1_probe",
        "name": "Bin 1 - Compost Core",
        "enabled": True,
    },
]

# Alert thresholds for compost
DS18B20_TEMP_HIGH_THRESHOLD = 70  # Too hot!
DS18B20_TEMP_LOW_THRESHOLD = 35   # Not composting
```

#### DHT11 Settings (Ambient Conditions)

```python
DHT11_SENSORS = [
    {
        "id": "bin1_ambient",
        "name": "Bin 1 - Ambient",
        "gpio_pin": 17,  # GPIO 17
        "enabled": True
    },
]

# Ambient thresholds
DHT11_TEMP_HIGH_THRESHOLD = 40  # Ambient too hot
DHT11_HUMIDITY_LOW_THRESHOLD = 30  # Too dry
DHT11_HUMIDITY_HIGH_THRESHOLD = 85  # Too humid
### Reading Interval
```python
READING_INTERVAL = 300  # 5 minutes (recommended for compost)
```

### Dashboard Settings
```python
DASHBOARD_REFRESH = 30  # Dashboard auto-refresh every 30 seconds
```


## 🎯 System Architecture

```
┌─────────────────┐
│   DHT22 Sensor  │
│  (Temp/Humidity)│
└────────┬────────┘
         │
         v
┌─────────────────┐
│  Raspberry Pi   │
│  Data Collector │
│   (Python)      │
└────────┬────────┘
         │
         v
┌─────────────────┐
│ SQLite Database │
│  (Local Storage)│
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
    v         v
┌────────┐  ┌──────────────┐
│ Flask  │  │Google Sheets │
│Dashboard│ │   (Hourly)   │
└────────┘  └──────────────┘
```

---

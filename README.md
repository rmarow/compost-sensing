# Farm Monitoring System - Quick Start Guide
## Milk and Honey Farm at Boulder JCC

This is a  guide to setting up and running the compost monitoring system.


### Core Files
- **`GETTING_STARTED.md`** - Hardware setup guide (wiring diagrams, initial config)
- **`config.py`** - All configuration settings (thresholds, intervals, etc.)
- **`database_setup.py`** - Creates the SQLite database
- **`sensor_test.py`** - Tests your DHT22 sensor
- **`data_collector.py`** - Main monitoring script (runs continuously)
- **`dashboard.py`** - Flask web server for the dashboard
- **`templates/dashboard.html`** - Dashboard web interface

## 🚀 Quick Start (5 Steps)

### Step 1: Copy Files to Your Raspberry Pi

```bash
# On your computer, copy all files to the Pi
scp -r /home/claude/* pi@raspberrypi.local:~/farm-monitoring/

# OR use a USB drive or Git
```

### Step 2: SSH into Your Pi and Install Dependencies

```bash
ssh pi@raspberrypi.local
cd ~/farm-monitoring

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install required packages
pip install flask adafruit-circuitpython-dht gspread oauth2client plotly pandas RPi.GPIO
```

### Step 3: Wire Up Your DHT22 Sensor

Follow the wiring diagram in `GETTING_STARTED.md`:
- DHT22 VCC → Pi Pin 1 (3.3V)
- DHT22 Data → Pi Pin 7 (GPIO 4)
- DHT22 GND → Pi Pin 6 (Ground)

### Step 4: Test Your Sensor

```bash
python sensor_test.py
```

You should see temperature and humidity readings! If not, check `GETTING_STARTED.md` for troubleshooting.

### Step 5: Initialize Database and Start Monitoring

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
```python
TEMP_HIGH_THRESHOLD = 65  # Alert if above 65°C
TEMP_LOW_THRESHOLD = 40   # Alert if below 40°C
HUMIDITY_LOW_THRESHOLD = 40
HUMIDITY_HIGH_THRESHOLD = 70
```

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

You're ready to go! Start with sensor_test.py and work through the Quick Start steps. The system is designed to be simple and reliable.

# Farm Monitoring - Compost Sensing System - Complete Setup Guide
## Milk and Honey Farm at Boulder JCC

**Compost monitoring with waterproof temperature probes, ambient sensors, web dashboard, and email alerts.**

---

## 🎯 What This System Does

### Monitors Your Compost
- **DS18B20 Waterproof Probes**: Measure temperature INSIDE the compost pile
- **Automatic Alerts**: Get email when temps are too high/low
- **Web Dashboard**: View real-time data and 24-hour trends from any device
- **Data Logging**: Everything stored locally in SQLite database

### Your Alert Thresholds
- 🔥 **Compost too hot**: > 65°C (149°F)
- ❄️ **Compost too cold**: < 40°C (104°F)

---

## 📦 Requirements

### Hardware
- **Raspberry Pi 5** (with Raspberry Pi OS)
- **DS18B20 Waterproof Temperature Probes** (stainless steel, goes IN compost)
- **4.7kΩ Resistor** (required for DS18B20)
- **Screw terminal breakout board** and power supply

### Software Files

**Documentation:**
- `README.md` (this file) - Complete setup guide
- `WIRING_GUIDE.md` - Detailed sensor wiring diagrams
- `ALERT_SETUP_GUIDE.md` - Email setup instructions

**Configuration:**
- `config.py` - All settings (thresholds, GPIO pins, alerts)
- `config_local.py` - Local credentials (gitignored, not committed)
- `requirements.txt` - Python dependencies

**Core System:**
- `sensor_test.py` - Test sensors
- `database_setup.py` - Create SQLite database
- `data_collector.py` - Main monitoring script
- `dashboard.py` - Web dashboard server
- `notifications.py` - Email alert handler

**Web Interface:**
- `templates/dashboard.html` - Dashboard UI

---

## 🚀 Quick Start (7 Steps)

### Step 1: Wire Your Sensors

**Read WIRING_GUIDE.md for detailed diagrams!**

**DS18B20 (Waterproof - goes IN compost):**
Note: There are 2 of these, but they share the exact same wiring config. A screw terminal breakout board is how they are attached to the Pi.
```
RED wire    → Pin 1 (3.3V)
YELLOW wire → Pin 7 (GPIO 4)
BLACK wire  → Pin 9 (Ground)
+ 4.7kΩ resistor between RED and YELLOW
```

### Step 2: Clone Repo to Raspberry Pi

```bash
# SSH into your Pi, then:
cd ~
git clone https://github.com/rmarow/compost-sensing.git
cd compost-sensing
```

Note: Instructions for connecting a Raspberry Pi to a monitor, WiFi, keyboard, and mouse can be found in the official Raspberry Pi documentation.

### Step 3: SSH and Enable 1-Wire

```bash
ssh rmarowitz@raspberrypi.local

# Enable 1-Wire interface (required for DS18B20)
sudo raspi-config
# Navigate: Interface Options → 1-Wire → Enable

# Reboot
sudo reboot
```

### Step 4: Install Dependencies

```bash
ssh rmarowitz@raspberrypi.local
cd ~/compost-sensing

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install packages
pip install -r requirements.txt
```

### Step 5: Test Your Sensors

```bash
python sensor_test.py
```

**You should see:**
```
✅ Found 2 DS18B20 sensor(s):
  Sensor 1 (1ft deep):  28-0000005fe1bf - Reading: 55.2°C / 131.4°F
  Sensor 2 (2ft deep):  28-0000005f6979 - Reading: 57.8°C / 136.0°F
```

**If sensors fail**, check WIRING_GUIDE.md troubleshooting section.

### Step 6: Initialize Database

```bash
python database_setup.py
```

Creates database with tables for sensor readings, alerts, and system status.

### Step 7: Start Monitoring!

**Terminal 1 - Data Collector:**
```bash
cd ~/compost-sensing
source venv/bin/activate
python data_collector.py
```

**Terminal 2 - Dashboard:**
```bash
cd ~/compost-sensing
source venv/bin/activate
python dashboard.py
```

**Access Dashboard:**
Open browser and go to: **http://raspberrypi.local:5000**

🎉 **You should see your dashboard with live sensor data!**

---

## 🔧 Configuration

Edit `config.py` to customize your system:

### Temperature Thresholds (Compost)

```python
# DS18B20 waterproof probes inside compost
DS18B20_TEMP_HIGH_THRESHOLD = 65  # Alert if > 65°C (149°F)
DS18B20_TEMP_LOW_THRESHOLD = 40   # Alert if < 40°C (104°F)
```

**Understanding Compost Temps:**
- **< 40°C**: Not actively composting
- **40-55°C**: Active mesophilic phase
- **55-65°C**: Optimal thermophilic phase (BEST!)
- **> 65°C**: Too hot, may kill beneficial bacteria

### Humidity Thresholds (Ambient)

```python
# DHT11 ambient sensor outside bin (currently disabled)
DHT11_HUMIDITY_LOW_THRESHOLD = 40   # Alert if < 40%
DHT11_HUMIDITY_HIGH_THRESHOLD = 70  # Alert if > 70%
```

### Reading Interval

```python
READING_INTERVAL = 1800  # 30 minutes (changeable in config.py)
```

### Dashboard Settings

```python
DASHBOARD_REFRESH = 60  # Auto-refresh every 60 seconds
```

---

## 🔔 Email Alerts (Optional)

Get notified immediately when thresholds are violated.

### Quick Setup

**1. Enable Email Alerts (FREE):**
```python
# In config_local.py (never committed to git)
EMAIL_ALERTS_ENABLED = True
SMTP_USERNAME = "your-email@gmail.com"
SMTP_PASSWORD = "your-gmail-app-password"  # See ALERT_SETUP_GUIDE.md
ALERT_RECIPIENTS = ["farmerbecca@boulderjcc.org"]
```

**2. Test Notifications:**
```bash
python notifications.py
```

**For complete setup instructions, see ALERT_SETUP_GUIDE.md**

### What Alerts Look Like

**Email:**
```
Subject: 🚨 Compost Alert: Bin 1 - 2ft Deep

Alert: Temperature too high: 68.5°C
Threshold: 65°C
Time: 2026-02-15 2:30 PM

[View Dashboard Button]
```

Won't spam you - 1 hour cooldown between duplicate alerts.

---

## 🤖 Run Automatically on Boot

Make the system start when your Raspberry Pi boots.

### Create systemd Services

**1. Data Collector Service:**
```bash
sudo nano /etc/systemd/system/compost-collector.service
```

Paste:
```ini
[Unit]
Description=Compost Sensing Data Collector
After=network.target

[Service]
Type=simple
User=rmarowitz
WorkingDirectory=/home/rmarowitz/compost-sensing
ExecStart=/home/rmarowitz/compost-sensing/venv/bin/python /home/rmarowitz/compost-sensing/data_collector.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**2. Dashboard Service:**
```bash
sudo nano /etc/systemd/system/compost-dashboard.service
```

Paste:
```ini
[Unit]
Description=Compost Sensing Dashboard
After=network.target compost-collector.service

[Service]
Type=simple
User=rmarowitz
WorkingDirectory=/home/rmarowitz/compost-sensing
ExecStart=/home/rmarowitz/compost-sensing/venv/bin/python /home/rmarowitz/compost-sensing/dashboard.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**3. Enable and Start:**
```bash
sudo systemctl daemon-reload
sudo systemctl enable compost-collector.service
sudo systemctl enable compost-dashboard.service
sudo systemctl start compost-collector.service
sudo systemctl start compost-dashboard.service
```

**4. Check Status:**
```bash
sudo systemctl status compost-collector.service
sudo systemctl status compost-dashboard.service
```

**Now it runs automatically on boot!** ✅

---

## 📊 Using the Dashboard

### What You'll See

**Main Stats Cards:**
- Active alerts (color-coded)
- Number of active sensors
- Last Google Sheets sync (if enabled)

**For Each Sensor:**
- Current temperature in °F (color-coded: green=good, red=alert)
- Temperature in °C (secondary)
- Last reading timestamp

**Combined Temperature Chart:**
- 24-hour trend for both probes on one chart
- 1ft probe in red, 2ft probe in green

**Active Alerts Section:**
- Lists all unacknowledged alerts
- Shows when alert occurred and what threshold was violated

### Accessing Dashboard

**On farm WiFi:**
```
http://raspberrypi.local:5000
```

**By IP address:**
```bash
# Find your Pi's IP
hostname -I
# Then visit: http://192.168.1.XX:5000
```

Works on any device on the same WiFi network!

---

## 🚀 Expanding Your System

### Add More DS18B20 Probes (Easy!)

Monitor multiple depths in the same bin — ALL on the same GPIO 4 pin!

```python
# In config.py
DS18B20_LOCATIONS = [
    {"id": "probe_1ft", "name": "Bin 1 - 1ft Deep", "device_id": "28-0000005fe1bf", "enabled": True},
    {"id": "probe_2ft", "name": "Bin 1 - 2ft Deep", "device_id": "28-0000005f6979", "enabled": True},
]
```

Wire them all the same way — the system auto-detects them by unique ID!

### Add DHT11 for Ambient Humidity

Each DHT11 needs its own GPIO pin:

```python
# In config.py
DHT11_SENSORS = [
    {"id": "bin1_ambient", "name": "Bin 1", "gpio_pin": 17, "enabled": True},
    {"id": "bin2_ambient", "name": "Bin 2", "gpio_pin": 27, "enabled": True},
]
```

Available GPIO pins: 17, 27, 22, 23, 24, 25

---

## 🔍 Troubleshooting

### DS18B20 Not Detected

```bash
# Check if 1-Wire is enabled
ls /sys/bus/w1/devices/
# Should see entries like: 28-0000005fe1bf

# If not found:
sudo raspi-config  # Interface Options → 1-Wire → Enable
sudo reboot

# Load modules manually
sudo modprobe w1-gpio
sudo modprobe w1-therm
```

**Check wiring:**
- RED → 3.3V (Pin 1)
- YELLOW → GPIO 4 (Pin 7)
- BLACK → Ground (Pin 9)
- **4.7kΩ resistor between RED and YELLOW**

### DHT11 Errors

DHT11 is currently disabled in config. When re-enabled, note it has a ~20-30% failure rate (normal) — the code handles this with retries.

**If all reads fail:**
```bash
# Check wiring:
# + → 5V (Pin 2)
# OUT → GPIO 17 (Pin 11)
# - → Ground (Pin 14)
# Make sure using 5V, not 3.3V!
```

### Dashboard Not Loading

```bash
# Check if running
ps aux | grep dashboard

# Restart dashboard service
sudo systemctl restart compost-dashboard.service

# Check logs
tail -f ~/compost-sensing/compost-sensing.log
```

### No Data Saving

```bash
# Check database exists
ls -lh ~/compost-sensing/compost_data.db

# Recreate if needed
python database_setup.py

# Check collector is running
sudo systemctl status compost-collector.service
```

### Alerts Not Sending

```bash
# Test notifications
python notifications.py

# Check config_local.py:
# EMAIL_ALERTS_ENABLED = True?
# SMTP credentials correct?

# See ALERT_SETUP_GUIDE.md for detailed troubleshooting
```

---

## 📁 Where Data Lives

### Database
```
/home/rmarowitz/compost-sensing/compost_data.db
```

### Logs
```
/home/rmarowitz/compost-sensing/compost-sensing.log
```

### Query Database Directly
```bash
sqlite3 ~/compost-sensing/compost_data.db

# Recent readings
SELECT * FROM sensor_readings ORDER BY timestamp DESC LIMIT 10;

# Active alerts
SELECT * FROM alerts WHERE acknowledged = 0;

# Exit
.quit
```

---

## 🎓 System Architecture

```
Physical Layer:          Data Layer:             Interface Layer:

┌──────────┐            ┌──────────┐            ┌──────────┐
│  DS18B20 │──GPIO4───→ │  SQLite  │──Query───→ │  Flask   │
│  1ft     │            │ Database │            │Dashboard │
│  Probe   │            └────┬─────┘            └────┬─────┘
├──────────┤                 │                       │
│  DS18B20 │──GPIO4───→  Local Storage          Web Browser
│  2ft     │                 │                  Any Device
│  Probe   │                 │                       │
└──────────┘            ┌────┴─────┐           ┌────┴─────┐
                        │  Alerts  │           │ Google   │
┌──────────┐            │  Check   │           │ Sheets   │
│  DHT11   │──GPIO17──→ └────┬─────┘           │(Optional)│
│ Ambient  │                 │                 └──────────┘
│(disabled)│            ┌────┴─────┐
└──────────┘            │   📧     │
                        │  Email   │
                        └──────────┘
```

---

## ✅ Success Checklist

### Hardware Setup:
- [ ] DS18B20 probes wired: RED→3.3V, YELLOW→GPIO4, BLACK→GND
- [ ] 4.7kΩ resistor between DS18B20 VCC and DATA
- [ ] Both probes connected via screw terminal breakout board
- [ ] All connections secure, no loose wires
- [ ] Raspberry Pi powered on and connected to WiFi

### Software Setup:
- [ ] 1-Wire enabled via raspi-config
- [ ] Virtual environment created
- [ ] Dependencies installed from requirements.txt
- [ ] sensor_test.py shows both sensors working
- [ ] Database created with database_setup.py
- [ ] Probe IDs and thresholds configured in config.py

### System Running:
- [ ] data_collector.py running (or as systemd service)
- [ ] dashboard.py running (or as systemd service)
- [ ] Dashboard accessible at http://raspberrypi.local:5000
- [ ] Both probes showing live data
- [ ] 24-hour combined chart displaying

### Alerts (Optional):
- [ ] Email alerts configured in config_local.py and tested
- [ ] Test alert received via notifications.py
- [ ] Cooldown period set appropriately

### Deployment:
- [ ] Probes inserted at correct depths (1ft and 2ft)
- [ ] Cables protected and secured
- [ ] System running reliably for 24+ hours
- [ ] Auto-start on boot configured

---

## 📝 Next Steps

### Phase 1b: Current Enhancements
- [ ] **Deploy to compost bin** (weatherproof enclosures)
- [ ] **Enable email alerts** (ALERT_SETUP_GUIDE.md)
- [ ] **Google Sheets integration** (hourly data sync)
- [ ] **Run 7-day reliability test**

### Phase 2: Weather Station (Coming Soon)
- Add weather sensors (temp, humidity, rainfall, wind)
- Integrate into same dashboard
- Correlate weather with compost temps

### Phase 3: Harvest Tracking (If Time Permits)
- Digital scale with Arduino
- Touchscreen UI
- Automatic tare function
- Yield tracking and reporting

---

## 🌱 Why This Setup Works

### For the Practicum:
✅ **Technical depth**: Two sensor protocols, IoT, web dev, database design
✅ **Real impact**: Actual farm problem solved with engineering
✅ **Scalable**: Easy to expand to multiple bins and sensors
✅ **Professional**: Production-ready code, proper architecture
✅ **Documented**: Clear guides for maintenance and expansion

### For the Farm:
✅ **Waterproof probes**: Measure inside the compost pile at multiple depths
✅ **Accurate data**: ±0.5°C precision for DS18B20
✅ **Remote monitoring**: Check from anywhere on farm WiFi
✅ **Alerts**: Know immediately when action needed
✅ **No ongoing costs**: Local storage + free email alerts
✅ **Expandable**: Add more bins as farm grows

### For Science:
✅ **Data-driven**: Track what actually works
✅ **Historical trends**: See seasonal patterns
✅ **Correlations**: Weather vs compost activity
✅ **Grant reporting**: Professional data visualization

---

## 🆘 Getting Help

### Check Documentation:
1. **WIRING_GUIDE.md** - Sensor connections and diagrams
2. **ALERT_SETUP_GUIDE.md** - Email setup
3. **This README** - Complete system overview

### Check Logs:
```bash
# System logs
tail -f ~/compost-sensing/compost-sensing.log

# Service logs
journalctl -u compost-collector.service -f
journalctl -u compost-dashboard.service -f
```

### Test Components:
```bash
# Test sensors
python sensor_test.py

# Test notifications
python notifications.py

# Check database
sqlite3 ~/compost-sensing/compost_data.db "SELECT COUNT(*) FROM sensor_readings;"
```

---

## 🎯 Quick Reference

### Start/Stop Services
```bash
# Start
sudo systemctl start compost-collector.service
sudo systemctl start compost-dashboard.service

# Stop
sudo systemctl stop compost-collector.service
sudo systemctl stop compost-dashboard.service

# Restart
sudo systemctl restart compost-collector.service
sudo systemctl restart compost-dashboard.service

# Status
sudo systemctl status compost-collector.service
sudo systemctl status compost-dashboard.service
```

### Manual Operation
```bash
# Terminal 1 - Data Collector
cd ~/compost-sensing
source venv/bin/activate
python data_collector.py

# Terminal 2 - Dashboard
cd ~/compost-sensing
source venv/bin/activate
python dashboard.py
```

### Important Files
```
config.py            - All settings
config_local.py      - Local credentials (gitignored)
data_collector.py    - Main monitoring loop
dashboard.py         - Web interface
notifications.py     - Alert handler
compost_data.db      - Database
compost-sensing.log  - System logs
```

---

**You're all set!** 🚀

Start with sensor wiring (WIRING_GUIDE.md), then follow the Quick Start steps above.

**Happy composting!** 🌱♻️

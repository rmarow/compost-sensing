# Farm Monitoring System - Complete Setup Guide
## Milk and Honey Farm at Boulder JCC

**Compost monitoring with waterproof temperature probes, ambient sensors, web dashboard, and email/SMS alerts.**

---

## 🎯 What This System Does

### Monitors Your Compost
- **DS18B20 Waterproof Probes**: Measure temperature INSIDE the compost pile
- **Automatic Alerts**: Get email and text when temps are too high/low
- **Web Dashboard**: View real-time data and 24-hour trends from any device
- **Data Logging**: Everything stored locally in SQLite database

### Your Alert Thresholds
- 🔥 **Compost too hot**: > 65°C (149°F)
- ❄️ **Compost too cold**: < 40°C (104°F)

---

## 📦 

### Hardware
- **Raspberry Pi 5** (with Raspberry Pi OS)
- **DS18B20 Waterproof Temperature Probes** (stainless steel, goes IN compost)
- **4.7kΩ Resistor** (required for DS18B20)
- **Jumper wires** and power supply

### Software Files

**Documentation:**
- `README.md` (this file) - Complete setup guide
- `WIRING_GUIDE.md` - Detailed sensor wiring diagrams
- `ALERT_SETUP_GUIDE.md` - Email and SMS setup instructions

**Configuration:**
- `config.py` - All settings (thresholds, GPIO pins, alerts)
- `requirements.txt` - Python dependencies

**Core System:**
- `sensor_test.py` - Test both sensors
- `database_setup.py` - Create SQLite database
- `data_collector.py` - Main monitoring script
- `dashboard.py` - Web dashboard server
- `notifications.py` - Email/SMS alert handler

**Web Interface:**
- `templates/dashboard.html` - Dashboard UI

---

## 🚀 Quick Start (7 Steps)

### Step 1: Wire Your Sensors

**Read WIRING_GUIDE.md for detailed diagrams!**

**DS18B20 (Waterproof - goes IN compost):**
Note: there are 2 of these, but they share the exact same wiring config. A screw top breakout board is how they are attached to the Pi.
```
RED wire    → Pin 1 (3.3V)
YELLOW wire → Pin 7 (GPIO 4)
BLACK wire  → Pin 9 (Ground)
+ 4.7kΩ resistor between RED and YELLOW
```

### Step 2: Copy Files to Raspberry Pi

```bash
# From your computer
scp -r * pi@raspberrypi.local:~/compost-sensing/

# Or use USB drive or Git
```
Note: I used git...this repo to be specific. Instructions can be found online of how to connect Raspberry Pi to a monitor, wifi, keyboard, and mouse to code and test directly on the device. 

### Step 3: SSH and Enable 1-Wire

```bash
ssh pi@raspberrypi.local

# Enable 1-Wire interface (required for DS18B20)
sudo raspi-config
# Navigate: Interface Options → 1-Wire → Enable

# Reboot
sudo reboot
```

### Step 4: Install Dependencies

```bash
ssh pi@raspberrypi.local
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
✅ Found 1 DS18B20 sensor(s):
  Sensor 1: 28-xxxxxxxxxxxx
    Reading 1: 55.2°C / 131.4°F
```
TODO: update for second sensor.

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
# DS18B20 waterproof probe inside compost
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
# DHT11 ambient sensor outside bin
DHT11_HUMIDITY_LOW_THRESHOLD = 40   # Alert if < 40%
DHT11_HUMIDITY_HIGH_THRESHOLD = 70  # Alert if > 70%
```

### Reading Interval

```python
READING_INTERVAL = 1800  # 30 minutes 
```
This is changeable in the config.py

### Dashboard Settings

```python
DASHBOARD_REFRESH = 60  # Auto-refresh every 60 seconds
```

---

## 🔔 Email & SMS Alerts (Optional)

Get notified immediately when thresholds are violated.

### Quick Setup

**1. Enable Email Alerts (FREE):**
```python
# In config_updated.py
EMAIL_ALERTS_ENABLED = True
SMTP_USERNAME = "your-email@gmail.com"
SMTP_PASSWORD = "your-gmail-app-password"  # See ALERT_SETUP_GUIDE.md
ALERT_RECIPIENTS = ["becca@milkandhoneyfarm.org"]
```

**2. Enable SMS Alerts (FREE with email-to-SMS):**
```python
# In config_updated.py
SMS_ALERTS_ENABLED = True
SMS_RECIPIENTS = [
    "3035551234@vtext.com",  # Verizon
    # "3035551234@txt.att.net",  # AT&T
    # "3035551234@tmomail.net",  # T-Mobile
]
```

**3. Test Notifications:**
```bash
python notifications.py
```

**For complete setup instructions, see ALERT_SETUP_GUIDE.md**

### What Alerts Look Like

**Email:**
```
Subject: 🚨 Farm Alert: Shorter Probe (or Longer Probe) - Compost Core

Alert: Temperature too high: 68.5°C
Threshold: 65°C
Time: 2026-02-15 2:30 PM

[View Dashboard Button]
```

**SMS:**
```
Farm Alert: (Shotrter/Longer) Probe - Compost Core
Temperature too high: 68.5°C
```

Won't spam you - 1 hour between duplicate alerts
TODO: Finalize this

---

## 🤖 Run Automatically on Boot

Make the system start when your Raspberry Pi boots.

### Create systemd Services

**1. Data Collector Service:**
```bash
sudo nano /etc/systemd/system/compost-sensing.service
```

Paste:
```ini
[Unit]
Description=Farm Monitoring Data Collector
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/compost-sensing
ExecStart=/home/pi/farm-monitoring/venv/bin/python /home/pi/compost-sensing/data_collector_updated.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**2. Dashboard Service:**
```bash
sudo nano /etc/systemd/system/compost-sensor.service
```

Paste:
```ini
[Unit]
Description=Farm Monitoring Dashboard
After=network.target compost-sensor.service

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/compsost-sensor
ExecStart=/home/pi/farm-monitoring/venv/bin/python /home/pi/compost-sensing/dashboard.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**3. Enable and Start:**
```bash
sudo systemctl daemon-reload
sudo systemctl enable compost-sensor.service
sudo systemctl enable farm-dashboard.service
sudo systemctl start compost-sensor.service
sudo systemctl start farm-dashboard.service
```

**4. Check Status:**
```bash
sudo systemctl status compost-sensor.service
sudo systemctl status farm-dashboard.service
```

**Now it runs automatically on boot!** ✅

---

## 📊 Using the Dashboard

### What You'll See

**Main Stats Cards:**
- Total sensor readings collected
- Active alerts (color-coded)
- Number of active sensors
- Last Google Sheets sync (if enabled)

**For Each Sensor:**
- Current temperature (color-coded: green=good, red=alert)
- Current humidity (DHT11 only)
- Last reading timestamp
- 24-hour trend chart

**Active Alerts Section:**
- Lists all unacknowledged alerts
- Shows when alert occurred
- What threshold was violated

### Accessing Dashboard

**On farm WiFi:**
- http://raspberrypi.local:5000

**By IP address:**
```bash
# Find your Pi's IP
hostname -I
# Use that IP: http://192.168.1.XX:5000
```

**From phone/tablet:**
Works on any device on the same WiFi network!

---

## 🚀 Expanding Your System

### Add More DS18B20 Probes (Easy!)

Monitor multiple depths in the same bin - ALL on the same GPIO 4 pin!

```python
# In config_updated.py
DS18B20_LOCATIONS = [
    {"id": "bin1_top", "name": "Bin 1 - Top (6 inches)", "enabled": True},
    {"id": "bin1_mid", "name": "Bin 1 - Middle (12 inches)", "enabled": True},
    {"id": "bin1_bot", "name": "Bin 1 - Bottom (24 inches)", "enabled": True},
]
```

Wire them all the same way - the system auto-detects them!

### Add DHT11 for More Bins

Each DHT11 needs its own GPIO pin:

```python
# In config_updated.py
DHT11_SENSORS = [
    {"id": "bin1_ambient", "name": "Bin 1", "gpio_pin": 17, "enabled": True},
    {"id": "bin2_ambient", "name": "Bin 2", "gpio_pin": 27, "enabled": True},
    {"id": "bin3_ambient", "name": "Bin 3", "gpio_pin": 22, "enabled": True},
]
```

Available GPIO pins: 17, 27, 22, 23, 24, 25

---

## 🔍 Troubleshooting

### DS18B20 Not Detected

```bash
# Check if 1-Wire is enabled
ls /sys/bus/w1/devices/
# Should see: 28-xxxxxxxxxxxx

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

DHT11 has ~20-30% failure rate (normal). Code handles this with retries.

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

# Restart dashboard
sudo systemctl restart farm-dashboard.service

# Check logs
tail -f ~/farm-monitoring/compost-sensing.log
```

### No Data Saving

```bash
# Check database exists
ls -lh ~/farm-monitoring/compost_data.db

# Recreate if needed
python database_setup_updated.py

# Check collector is running
sudo systemctl status compost-sensor.service
```

### Alerts Not Sending

```bash
# Test notifications
python notifications.py

# Check config
# EMAIL_ALERTS_ENABLED = True?
# SMTP credentials correct?
# SMS_RECIPIENTS have correct format?

# See ALERT_SETUP_GUIDE.md for detailed troubleshooting
```

---

## 📁 Where Data Lives

### Database
```
/home/pi/farm-monitoring/compost_data.db
```

All sensor readings, alerts, and system events.

### Logs
```
/home/pi/farm-monitoring/farm_monitor.log
```

Debug info, errors, sensor readings.

### Query Database Directly
```bash
sqlite3 /home/pi/farm-monitoring/compost_data.db

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
│Waterproof│            │ Database │            │Dashboard │
│  Probe   │            └────┬─────┘            └────┬─────┘
└──────────┘                 │                       │
                             │                  Web Browser
┌──────────┐                 │                  Any Device
│  DHT11   │──GPIO17──→  Local Storage              │
│ Ambient  │                 │                       │
└──────────┘                 │                       │
                        ┌────┴─────┐           ┌────┴─────┐
                        │  Alerts  │           │ Google   │
                        │  Check   │           │ Sheets   │
                        └────┬─────┘           │(Optional)│
                             │                 └──────────┘
                        ┌────┴─────┐
                        │   📧📱   │
                        │Email/SMS │
                        └──────────┘
```

---

## ✅ Success Checklist

### Hardware Setup:
- [ ] DS18B20 wired: RED→3.3V, YELLOW→GPIO4, BLACK→GND
- [ ] 4.7kΩ resistor between DS18B20 VCC and DATA
- [ ] DHT11 wired: +→5V, OUT→GPIO17, -→GND
- [ ] All connections secure, no loose wires
- [ ] Raspberry Pi powered on and connected to WiFi

### Software Setup:
- [ ] 1-Wire enabled via raspi-config
- [ ] Virtual environment created
- [ ] Dependencies installed from requirements.txt
- [ ] sensor_test.py shows both sensors working
- [ ] Database created with database_setup.py
- [ ] Thresholds configured in config.py

### System Running:
- [ ] data_collector.py running (or as systemd service)
- [ ] dashboard.py running (or as systemd service)
- [ ] Dashboard accessible at http://raspberrypi.local:5000
- [ ] Both sensor types showing live data
- [ ] 24-hour charts displaying

### Alerts (Optional):
- [ ] Email alerts configured and tested
- [ ] SMS alerts configured and tested
- [ ] Test alert received via notifications.py
- [ ] Cooldown period set appropriately

### Deployment:
- [ ] DS18B20 probe inserted 12-18" into compost
- [ ] Cables protected and secured
- [ ] System running reliably for 24+ hours
- [ ] Auto-start on boot configured

---

## 📝 Next Steps

### Phase 1b: Current Enhancements
- [ ] **Deploy to compost bin** (weatherproof enclosures)
- [ ] **Enable email/SMS alerts** (ALERT_SETUP_GUIDE.md)
- [ ] **Add more DS18B20s** (multiple depths)
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

## 🌱 Why This Setup is Perfect

### For Your Practicum:
✅ **Technical depth**: Two sensor protocols, IoT, web dev, database design
✅ **Real impact**: Actual farm problem solved with engineering
✅ **Scalable**: Easy to expand to multiple bins and sensors
✅ **Professional**: Production-ready code, proper architecture
✅ **Documented**: Clear guides for maintenance and expansion

### For the Farm:
✅ **Waterproof probes**: Can measure inside compost pile
✅ **Accurate data**: ±0.5°C precision for DS18B20
✅ **Remote monitoring**: Check from anywhere on farm WiFi
✅ **Alerts**: Know immediately when action needed
✅ **No ongoing costs**: Local storage + free email/SMS
✅ **Expandable**: Add more bins as farm grows

### For Science:
✅ **Data-driven**: Track what actually works
✅ **Historical trends**: See seasonal patterns
✅ **Correlations**: Weather vs compost activity
✅ **Grant reporting**: Professional data visualization

---

## 🆘 Getting Help

### Check Documentation:
1. **WIRING_GUIDE_UPDATED.md** - Sensor connections and diagrams
2. **ALERT_SETUP_GUIDE.md** - Email and SMS setup
3. **This README** - Complete system overview

### Check Logs:
```bash
# System logs
tail -f ~/farm-monitoring/farm_monitor.log

# Service logs
journalctl -u compost-sensor.service -f
journalctl -u farm-dashboard.service -f
```

### Test Components:
```bash
# Test sensors
python sensor_test_updated.py

# Test notifications
python notifications.py

# Check database
sqlite3 compost_data.db "SELECT COUNT(*) FROM sensor_readings;"
```

---

## 🎯 Quick Reference

### Start/Stop Services
```bash
# Start
sudo systemctl start compost-sensor.service
sudo systemctl start farm-dashboard.service

# Stop
sudo systemctl stop compost-sensor.service
sudo systemctl stop farm-dashboard.service

# Restart
sudo systemctl restart compost-sensor.service
sudo systemctl restart farm-dashboard.service

# Status
sudo systemctl status compost-sensor.service
```

### Manual Operation
```bash
# Terminal 1
cd ~/farm-monitoring
source venv/bin/activate
python data_collector_updated.py

# Terminal 2  
cd ~/farm-monitoring
source venv/bin/activate
python dashboard.py
```

### Important Files
```
config_updated.py          - All settings
data_collector_updated.py  - Main monitoring loop
dashboard.py               - Web interface
notifications.py           - Alert handler
compost_data.db            - Database
farm_monitor.log           - System logs
```

---

**You're all set!** 🚀

Start with sensor wiring (WIRING_GUIDE_UPDATED.md), then follow the Quick Start steps above. Your compost monitoring system will be running in under an hour!

For questions during setup, check the troubleshooting section or the detailed guides. The system is designed to be reliable and handle sensor errors gracefully.

**Happy composting!** 🌱♻️

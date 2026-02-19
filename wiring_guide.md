# Updated Wiring Guide: DS18B20 + DHT11 Sensors
## Compost Monitoring System - Milk and Honey Farm

## 🌡️ Your New Sensor Setup

You have TWO types of sensors - perfect combination for compost monitoring!

### DS18B20 - Waterproof Temperature Probe
- **Best for**: Direct compost temperature (can go INTO the pile)
- **Measures**: Temperature only (high accuracy ±0.5°C)
- **Waterproof**: Stainless steel probe
- **Protocol**: 1-Wire (multiple sensors on one GPIO pin!)

### DHT11 - Ambient Temperature & Humidity
- **Best for**: Air temperature and humidity around the bins
- **Measures**: Temperature (±2°C) and Humidity (±5%)
- **Not waterproof**: For ambient air only
- **Protocol**: Same as DHT22 (one sensor per GPIO pin)

## 🎯 Ideal Setup

```
Compost Bin Setup:
┌─────────────────────────────┐
│    Compost Bin 1            │
│  ┌──────────────┐           │
│  │   DS18B20    │ ← Inside compost
│  │  Probe #1    │    (temperature)
│  └──────┬───────┘           │
│         │                   │
│    ┌────┴────┐              │
│    │ DHT11   │ ← Outside bin
│    │ #1      │    (air temp/humidity)
│    └─────────┘              │
└─────────────────────────────┘
```

---

## 📍 DS18B20 Waterproof Sensor Wiring

### DS18B20 Cable Colors
Most DS18B20 probes have 3 wires:
```
┌─────────────────┐
│ Stainless Steel │
│     Probe       │
└────────┬────────┘
         │ (3 wires)
    ┌────┴────┬────────┐
    │         │        │
   RED     YELLOW    BLACK
    │         │        │
   VCC      DATA      GND
  (3.3V)  (GPIO 4)  (Ground)
```

### DS18B20 to Raspberry Pi Connection
```
DS18B20                      Raspberry Pi
┌─────────┐                 ┌──────────┐
│  RED    │────────────────→│ Pin 1    │ 3.3V Power
│ YELLOW  │────────────────→│ Pin 7    │ GPIO 4 (Data)
│ BLACK   │────────────────→│ Pin 9    │ Ground
└─────────┘                 └──────────┘
```

### IMPORTANT: Pull-up Resistor Required!
DS18B20 **REQUIRES** a 4.7kΩ resistor between VCC and DATA:

```
                 ┌── 4.7kΩ Resistor ──┐
                 │                     │
DS18B20          │                     │
┌─────────┐      │                     │
│  RED    │──────┴─────────────────────┴──→ 3.3V (Pin 1)
│ YELLOW  │────────────────────────────────→ GPIO 4 (Pin 7)
│ BLACK   │────────────────────────────────→ Ground (Pin 9)
└─────────┘
```

**Note**: Some modules come with the resistor built-in. If your readings don't work, add the resistor!

---

## 📍 DHT11 Module Wiring

### DHT11 Module Pinout
Your DHT11 modules have 3 pins (module version with built-in resistor):

```
┌─────────────┐
│   DHT11     │
│   Module    │
├─────────────┤
│  -  OUT  +  │
└──┬───┬───┬──┘
   │   │   │
  GND DATA VCC
```

### DHT11 to Raspberry Pi Connection
```
DHT11 Module                 Raspberry Pi
┌─────────┐                 ┌──────────┐
│  + (VCC)│────────────────→│ Pin 2    │ 5V Power
│OUT(DATA)│────────────────→│ Pin 11   │ GPIO 17 (Data)
│  - (GND)│────────────────→│ Pin 14   │ Ground
└─────────┘                 └──────────┘
```

---

## 🔌 Complete Wiring Setup

### Pin Assignment Summary
| Sensor | Wire/Pin | Raspberry Pi Pin | GPIO # |
|--------|----------|------------------|--------|
| DS18B20 | RED (VCC) | Pin 1 | 3.3V |
| DS18B20 | YELLOW (DATA) | Pin 7 | GPIO 4 |
| DS18B20 | BLACK (GND) | Pin 9 | Ground |
| DHT11 | + (VCC) | Pin 2 | 5V |
| DHT11 | OUT (DATA) | Pin 11 | GPIO 17 |
| DHT11 | - (GND) | Pin 14 | Ground |

---

## 🛠️ Step-by-Step Setup

### 1. Wire the Sensors
Follow the diagrams above

### 2. Enable 1-Wire for DS18B20
```bash
# SSH into your Pi
ssh pi@raspberrypi.local

# Enable 1-Wire interface
sudo raspi-config
# Navigate to: Interface Options > 1-Wire > Enable

# Reboot
sudo reboot

# After reboot, verify DS18B20 is detected
ls /sys/bus/w1/devices/
# Should see: 28-xxxxxxxxxxxx (your sensor ID)
```

### 3. Test DS18B20
```bash
# Read temperature directly
cat /sys/bus/w1/devices/28-*/w1_slave

# Output shows temperature in millidegrees:
# t=23187 means 23.187°C
```

### 4. Test DHT11
```bash
cd ~/farm-monitoring
source venv/bin/activate
python sensor_test.py
```

---

## 🔍 Troubleshooting

### DS18B20 Not Detected
- Check 4.7kΩ resistor is connected
- Verify wiring (RED=3.3V, YELLOW=GPIO4, BLACK=GND)
- Run `sudo modprobe w1-gpio && sudo modprobe w1-therm`

### DHT11 Checksum Errors
- Normal! DHT11 is less reliable than DHT22
- Check wiring is secure
- Make sure using 5V power (not 3.3V)

---

This sensor combo gives you:
- **Accurate compost temp** with waterproof DS18B20
- **Ambient conditions** with DHT11
- **Better reliability** - DS18B20 rarely fails
- **Scalability** - add more DS18B20s on same GPIO pin!

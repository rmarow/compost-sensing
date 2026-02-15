#!/usr/bin/env python3
"""
Data Collector Script - Updated for DS18B20 + DHT11
Reads from waterproof temperature probes and ambient sensors
Stores data in SQLite database and handles alerts
"""

import time
import sqlite3
import glob
import os
import board
import adafruit_dht
from datetime import datetime
import logging
import sys
import config_updated as config
from notifications import AlertNotifier

# Setup logging
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(config.LOG_FILE),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class DS18B20Reader:
    """Handles DS18B20 waterproof temperature sensor reading"""
    
    def __init__(self, sensor_config):
        self.sensor_id = sensor_config['id']
        self.sensor_name = sensor_config['name']
        self.device_file = None
        self.hw_sensor_id = sensor_config.get('sensor_id', None)
        
        # Find sensor device file
        if self.hw_sensor_id:
            # Use specified sensor ID
            device_path = f"{config.W1_DEVICE_DIR}/{self.hw_sensor_id}"
            if os.path.exists(device_path):
                self.device_file = device_path + '/w1_slave'
        else:
            # Auto-detect first available sensor
            devices = glob.glob(config.W1_DEVICE_DIR + '/28-*')
            if devices:
                self.device_file = devices[0] + '/w1_slave'
                self.hw_sensor_id = os.path.basename(devices[0])
        
        if self.device_file:
            logger.info(f"Initialized DS18B20: {self.sensor_name} ({self.hw_sensor_id})")
        else:
            logger.error(f"Could not find DS18B20 sensor: {self.sensor_name}")
        
        self.last_temp_high_alert = None
        self.last_temp_low_alert = None
    
    def read_sensor(self):
        """Read temperature from DS18B20"""
        if not self.device_file:
            return {
                'temperature_c': None,
                'temperature_f': None,
                'success': False,
                'error': 'Sensor not found'
            }
        
        try:
            with open(self.device_file, 'r') as f:
                lines = f.readlines()
            
            # Check CRC
            if lines[0].strip()[-3:] != 'YES':
                raise RuntimeError("CRC check failed")
            
            # Extract temperature
            equals_pos = lines[1].find('t=')
            if equals_pos != -1:
                temp_string = lines[1][equals_pos+2:]
                temp_c = float(temp_string) / 1000.0
                temp_f = temp_c * 9.0 / 5.0 + 32.0
                
                return {
                    'temperature_c': round(temp_c, 1),
                    'temperature_f': round(temp_f, 1),
                    'success': True,
                    'error': None
                }
            else:
                raise RuntimeError("Could not parse temperature")
                
        except Exception as error:
            logger.warning(f"DS18B20 read failed ({self.sensor_name}): {error}")
            return {
                'temperature_c': None,
                'temperature_f': None,
                'success': False,
                'error': str(error)
            }
    
    def save_reading(self, reading):
        """Save DS18B20 reading to database"""
        if not reading['success']:
            return False
        
        try:
            conn = sqlite3.connect(config.DATABASE_PATH)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO sensor_readings 
                (timestamp, sensor_id, sensor_location, sensor_type,
                 temperature_c, temperature_f, humidity)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                datetime.now(),
                self.sensor_id,
                self.sensor_name,
                'DS18B20',
                reading['temperature_c'],
                reading['temperature_f'],
                None  # DS18B20 doesn't measure humidity
            ))
            
            conn.commit()
            conn.close()
            
            logger.info(f"{self.sensor_name}: {reading['temperature_c']}°C")
            return True
            
        except Exception as error:
            logger.error(f"Error saving DS18B20 data: {error}")
            return False
    
    def check_alerts(self, reading):
        """Check DS18B20 temperature thresholds"""
        if not reading['success']:
            return
        
        now = datetime.now()
        alerts = []
        
        if reading['temperature_c'] > config.DS18B20_TEMP_HIGH_THRESHOLD:
            if self._can_send_alert(self.last_temp_high_alert):
                alerts.append({
                    'type': 'temp_high',
                    'message': f"{self.sensor_name}: Temperature too high: {reading['temperature_c']}°C",
                    'value': reading['temperature_c'],
                    'threshold': config.DS18B20_TEMP_HIGH_THRESHOLD
                })
                self.last_temp_high_alert = now
        
        if reading['temperature_c'] < config.DS18B20_TEMP_LOW_THRESHOLD:
            if self._can_send_alert(self.last_temp_low_alert):
                alerts.append({
                    'type': 'temp_low',
                    'message': f"{self.sensor_name}: Temperature too low: {reading['temperature_c']}°C",
                    'value': reading['temperature_c'],
                    'threshold': config.DS18B20_TEMP_LOW_THRESHOLD
                })
                self.last_temp_low_alert = now
        
        for alert in alerts:
            self._save_alert(alert)
            logger.warning(f"ALERT: {alert['message']}")
    
    def _can_send_alert(self, last_alert_time):
        if last_alert_time is None:
            return True
        time_since = (datetime.now() - last_alert_time).total_seconds()
        return time_since >= config.ALERT_COOLDOWN
    
    def _save_alert(self, alert):
        try:
            conn = sqlite3.connect(config.DATABASE_PATH)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO alerts 
                (timestamp, sensor_id, alert_type, message, value, threshold)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                datetime.now(),
                self.sensor_id,
                alert['type'],
                alert['message'],
                alert['value'],
                alert['threshold']
            ))
            
            conn.commit()
            conn.close()
            
            # Send notification if enabled
            if hasattr(self, 'notifier') and self.notifier:
                alert_data = {
                    'sensor_name': self.sensor_name,
                    'alert_type': alert['type'],
                    'message': alert['message'],
                    'value': alert['value'],
                    'threshold': alert['threshold'],
                    'timestamp': datetime.now()
                }
                self.notifier.send_alert(alert_data)
                
        except Exception as error:
            logger.error(f"Error saving alert: {error}")

class DHT11Reader:
    """Handles DHT11 ambient temperature and humidity sensor"""
    
    def __init__(self, sensor_config):
        self.sensor_id = sensor_config['id']
        self.sensor_name = sensor_config['name']
        self.gpio_pin = sensor_config['gpio_pin']
        
        pin = getattr(board, f'D{self.gpio_pin}')
        self.dht_device = adafruit_dht.DHT11(pin, use_pulseio=False)
        
        self.last_temp_high_alert = None
        self.last_temp_low_alert = None
        self.last_humidity_low_alert = None
        self.last_humidity_high_alert = None
        
        logger.info(f"Initialized DHT11: {self.sensor_name} on GPIO{self.gpio_pin}")
    
    def read_sensor(self):
        """Read temperature and humidity from DHT11 with retries"""
        for attempt in range(config.DHT11_MAX_RETRIES):
            try:
                temperature_c = self.dht_device.temperature
                humidity = self.dht_device.humidity
                
                if temperature_c is None or humidity is None:
                    if attempt < config.DHT11_MAX_RETRIES - 1:
                        time.sleep(config.DHT11_RETRY_DELAY)
                        continue
                    raise RuntimeError("Sensor returned None values")
                
                temperature_f = temperature_c * (9 / 5) + 32
                
                return {
                    'temperature_c': round(temperature_c, 1),
                    'temperature_f': round(temperature_f, 1),
                    'humidity': round(humidity, 1),
                    'success': True,
                    'error': None
                }
                
            except RuntimeError as error:
                if attempt < config.DHT11_MAX_RETRIES - 1:
                    time.sleep(config.DHT11_RETRY_DELAY)
                    continue
                logger.warning(f"DHT11 read failed ({self.sensor_name}): {error.args[0]}")
                return {
                    'temperature_c': None,
                    'temperature_f': None,
                    'humidity': None,
                    'success': False,
                    'error': str(error)
                }
        
        return {
            'temperature_c': None,
            'temperature_f': None,
            'humidity': None,
            'success': False,
            'error': 'Max retries exceeded'
        }
    
    def save_reading(self, reading):
        """Save DHT11 reading to database"""
        if not reading['success']:
            return False
        
        try:
            conn = sqlite3.connect(config.DATABASE_PATH)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO sensor_readings 
                (timestamp, sensor_id, sensor_location, sensor_type,
                 temperature_c, temperature_f, humidity)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                datetime.now(),
                self.sensor_id,
                self.sensor_name,
                'DHT11',
                reading['temperature_c'],
                reading['temperature_f'],
                reading['humidity']
            ))
            
            conn.commit()
            conn.close()
            
            logger.info(f"{self.sensor_name}: {reading['temperature_c']}°C, {reading['humidity']}%")
            return True
            
        except Exception as error:
            logger.error(f"Error saving DHT11 data: {error}")
            return False
    
    def check_alerts(self, reading):
        """Check DHT11 thresholds"""
        if not reading['success']:
            return
        
        now = datetime.now()
        alerts = []
        
        # Temperature alerts
        if reading['temperature_c'] > config.DHT11_TEMP_HIGH_THRESHOLD:
            if self._can_send_alert(self.last_temp_high_alert):
                alerts.append({
                    'type': 'temp_high',
                    'message': f"{self.sensor_name}: Ambient temp too high: {reading['temperature_c']}°C",
                    'value': reading['temperature_c'],
                    'threshold': config.DHT11_TEMP_HIGH_THRESHOLD
                })
                self.last_temp_high_alert = now
        
        if reading['temperature_c'] < config.DHT11_TEMP_LOW_THRESHOLD:
            if self._can_send_alert(self.last_temp_low_alert):
                alerts.append({
                    'type': 'temp_low',
                    'message': f"{self.sensor_name}: Ambient temp too low: {reading['temperature_c']}°C",
                    'value': reading['temperature_c'],
                    'threshold': config.DHT11_TEMP_LOW_THRESHOLD
                })
                self.last_temp_low_alert = now
        
        # Humidity alerts
        if reading['humidity'] < config.DHT11_HUMIDITY_LOW_THRESHOLD:
            if self._can_send_alert(self.last_humidity_low_alert):
                alerts.append({
                    'type': 'humidity_low',
                    'message': f"{self.sensor_name}: Humidity too low: {reading['humidity']}%",
                    'value': reading['humidity'],
                    'threshold': config.DHT11_HUMIDITY_LOW_THRESHOLD
                })
                self.last_humidity_low_alert = now
        
        if reading['humidity'] > config.DHT11_HUMIDITY_HIGH_THRESHOLD:
            if self._can_send_alert(self.last_humidity_high_alert):
                alerts.append({
                    'type': 'humidity_high',
                    'message': f"{self.sensor_name}: Humidity too high: {reading['humidity']}%",
                    'value': reading['humidity'],
                    'threshold': config.DHT11_HUMIDITY_HIGH_THRESHOLD
                })
                self.last_humidity_high_alert = now
        
        for alert in alerts:
            self._save_alert(alert)
            logger.warning(f"ALERT: {alert['message']}")
    
    def _can_send_alert(self, last_alert_time):
        if last_alert_time is None:
            return True
        time_since = (datetime.now() - last_alert_time).total_seconds()
        return time_since >= config.ALERT_COOLDOWN
    
    def _save_alert(self, alert):
        try:
            conn = sqlite3.connect(config.DATABASE_PATH)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO alerts 
                (timestamp, sensor_id, alert_type, message, value, threshold)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                datetime.now(),
                self.sensor_id,
                alert['type'],
                alert['message'],
                alert['value'],
                alert['threshold']
            ))
            
            conn.commit()
            conn.close()
            
            # Send notification if enabled
            if hasattr(self, 'notifier') and self.notifier:
                alert_data = {
                    'sensor_name': self.sensor_name,
                    'alert_type': alert['type'],
                    'message': alert['message'],
                    'value': alert['value'],
                    'threshold': alert['threshold'],
                    'timestamp': datetime.now()
                }
                self.notifier.send_alert(alert_data)
                
        except Exception as error:
            logger.error(f"Error saving alert: {error}")
    
    def cleanup(self):
        try:
            self.dht_device.exit()
        except:
            pass

def main():
    """Main monitoring loop"""
    logger.info("=" * 60)
    logger.info("Starting Farm Monitoring System")
    logger.info("Updated for DS18B20 + DHT11 sensors")
    logger.info("=" * 60)
    
    # Initialize DS18B20 sensors
    ds18b20_sensors = []
    if config.DS18B20_ENABLED:
        for sensor_config in config.DS18B20_LOCATIONS:
            if sensor_config['enabled']:
                try:
                    sensor = DS18B20Reader(sensor_config)
                    if sensor.device_file:
                        ds18b20_sensors.append(sensor)
                except Exception as error:
                    logger.error(f"Failed to init DS18B20 {sensor_config['name']}: {error}")
    
    # Initialize DHT11 sensors
    dht11_sensors = []
    for sensor_config in config.DHT11_SENSORS:
        if sensor_config['enabled']:
            try:
                sensor = DHT11Reader(sensor_config)
                dht11_sensors.append(sensor)
            except Exception as error:
                logger.error(f"Failed to init DHT11 {sensor_config['name']}: {error}")
    
    total_sensors = len(ds18b20_sensors) + len(dht11_sensors)
    if total_sensors == 0:
        logger.error("No sensors initialized. Exiting.")
        sys.exit(1)
    
    logger.info(f"Initialized {len(ds18b20_sensors)} DS18B20 + {len(dht11_sensors)} DHT11 sensor(s)")
    logger.info(f"Reading interval: {config.READING_INTERVAL} seconds")
    logger.info(f"Database: {config.DATABASE_PATH}")
    
    # Initialize alert notifier
    notifier = None
    if config.EMAIL_ALERTS_ENABLED:
        notifier = AlertNotifier(config)
        logger.info("Alert notifications enabled:")
        if config.EMAIL_ALERTS_ENABLED:
            logger.info(f"  Email: {', '.join(config.ALERT_RECIPIENTS)}")

    
    # Attach notifier to all sensors
    for sensor in ds18b20_sensors + dht11_sensors:
        sensor.notifier = notifier
    
    # Main monitoring loop
    try:
        while True:
            logger.debug("Starting sensor read cycle")
            
            # Read DS18B20 sensors
            for sensor in ds18b20_sensors:
                reading = sensor.read_sensor()
                if reading['success']:
                    sensor.save_reading(reading)
                    sensor.check_alerts(reading)
            
            # Read DHT11 sensors
            for sensor in dht11_sensors:
                reading = sensor.read_sensor()
                if reading['success']:
                    sensor.save_reading(reading)
                    sensor.check_alerts(reading)
            
            # Wait for next reading
            logger.debug(f"Waiting {config.READING_INTERVAL} seconds")
            time.sleep(config.READING_INTERVAL)
            
    except KeyboardInterrupt:
        logger.info("\n\nShutdown requested by user")
    except Exception as error:
        logger.critical(f"Unexpected error: {error}", exc_info=True)
    finally:
        logger.info("Cleaning up sensors...")
        for sensor in dht11_sensors:
            sensor.cleanup()
        logger.info("Shutdown complete")

if __name__ == "__main__":
    main()

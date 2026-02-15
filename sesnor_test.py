#!/usr/bin/env python3
"""
Sensor Test Script - Updated for DS18B20 + DHT11
Tests both waterproof temperature probes and ambient sensors
"""

import time
import glob
import os
import board
import adafruit_dht
import config_updated as config

def test_ds18b20():
    """Test DS18B20 waterproof temperature sensor(s)"""
    print("\n" + "=" * 60)
    print("DS18B20 Waterproof Temperature Sensor Test")
    print("=" * 60)
    
    # Find all DS18B20 sensors
    device_folder = glob.glob(config.W1_DEVICE_DIR + '/28-*')
    
    if not device_folder:
        print("❌ NO DS18B20 SENSORS DETECTED!")
        print("\nTroubleshooting:")
        print("1. Check wiring: RED→3.3V, YELLOW→GPIO4, BLACK→GND")
        print("2. Verify 4.7kΩ resistor between VCC and DATA")
        print("3. Enable 1-Wire: sudo raspi-config → Interface Options → 1-Wire")
        print("4. Load modules: sudo modprobe w1-gpio && sudo modprobe w1-therm")
        print("5. Check devices: ls /sys/bus/w1/devices/")
        return False
    
    print(f"✅ Found {len(device_folder)} DS18B20 sensor(s):\n")
    
    all_success = True
    
    for i, device in enumerate(device_folder):
        device_file = device + '/w1_slave'
        sensor_id = os.path.basename(device)
        
        print(f"Sensor {i+1}: {sensor_id}")
        print(f"  Device file: {device_file}")
        
        # Take 5 readings
        readings = []
        for j in range(5):
            try:
                with open(device_file, 'r') as f:
                    lines = f.readlines()
                
                # Check CRC
                if lines[0].strip()[-3:] != 'YES':
                    print(f"  Reading {j+1}: CRC check failed")
                    continue
                
                # Extract temperature
                equals_pos = lines[1].find('t=')
                if equals_pos != -1:
                    temp_string = lines[1][equals_pos+2:]
                    temp_c = float(temp_string) / 1000.0
                    temp_f = temp_c * 9.0 / 5.0 + 32.0
                    readings.append(temp_c)
                    print(f"  Reading {j+1}: {temp_c:.1f}°C / {temp_f:.1f}°F")
                
                time.sleep(1)
                
            except Exception as e:
                print(f"  Reading {j+1}: Error - {e}")
                all_success = False
        
        if readings:
            avg_temp = sum(readings) / len(readings)
            print(f"  Average: {avg_temp:.1f}°C")
            print(f"  Success rate: {len(readings)}/5")
        else:
            print(f"  ❌ No successful readings!")
            all_success = False
        
        print()
    
    return all_success

def test_dht11():
    """Test DHT11 temperature and humidity sensors"""
    print("\n" + "=" * 60)
    print("DHT11 Ambient Temperature & Humidity Sensor Test")
    print("=" * 60)
    
    all_success = True
    
    for sensor_config in config.DHT11_SENSORS:
        if not sensor_config['enabled']:
            continue
        
        print(f"\nTesting: {sensor_config['name']}")
        print(f"  GPIO Pin: {sensor_config['gpio_pin']}")
        
        try:
            # Initialize DHT11 sensor
            pin = getattr(board, f"D{sensor_config['gpio_pin']}")
            dht_device = adafruit_dht.DHT11(pin, use_pulseio=False)
            
            # Take multiple readings
            successful_reads = 0
            
            for i in range(10):
                try:
                    temperature_c = dht_device.temperature
                    humidity = dht_device.humidity
                    
                    if temperature_c is not None and humidity is not None:
                        temperature_f = temperature_c * (9 / 5) + 32
                        
                        print(f"  Reading {i+1}:")
                        print(f"    Temperature: {temperature_c:.1f}°C / {temperature_f:.1f}°F")
                        print(f"    Humidity: {humidity:.1f}%")
                        
                        successful_reads += 1
                    else:
                        print(f"  Reading {i+1}: Sensor returned None")
                    
                except RuntimeError as error:
                    print(f"  Reading {i+1}: {error.args[0]}")
                
                time.sleep(2)  # DHT11 needs 1-2 seconds between reads
            
            dht_device.exit()
            
            print(f"\n  Success rate: {successful_reads}/10")
            
            if successful_reads == 0:
                print("  ❌ NO SUCCESSFUL READS!")
                print("\n  Troubleshooting:")
                print("  1. Check wiring: + → 5V, OUT → GPIO17, - → GND")
                print("  2. Make sure using 5V power (not 3.3V)")
                print("  3. Verify connections are secure")
                print("  4. DHT11 has ~20-30% failure rate (normal)")
                all_success = False
            elif successful_reads < 7:
                print("  ⚠️  Some reads failed - check connections")
            else:
                print("  ✅ Sensor working well!")
        
        except Exception as error:
            print(f"  ❌ Failed to initialize sensor: {error}")
            all_success = False
    
    return all_success

def main():
    """Run all sensor tests"""
    print("\n" + "=" * 60)
    print("FARM MONITORING SYSTEM - SENSOR TEST")
    print("Milk and Honey Farm")
    print("=" * 60)
    
    # Test DS18B20
    ds18b20_ok = False
    if config.DS18B20_ENABLED:
        ds18b20_ok = test_ds18b20()
    else:
        print("\nDS18B20 sensors disabled in config")
    
    # Test DHT11
    dht11_ok = test_dht11()
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    if config.DS18B20_ENABLED:
        print(f"DS18B20 (Compost Temp): {'✅ PASS' if ds18b20_ok else '❌ FAIL'}")
    
    print(f"DHT11 (Ambient):        {'✅ PASS' if dht11_ok else '❌ FAIL'}")
    
    if (ds18b20_ok or not config.DS18B20_ENABLED) and dht11_ok:
        print("\n🎉 All enabled sensors working!")
        print("\nNext steps:")
        print("1. Run: python database_setup.py")
        print("2. Run: python data_collector.py")
        print("3. Run: python dashboard.py")
    else:
        print("\n⚠️  Some sensors failed - check wiring and troubleshooting steps above")
    
    print("=" * 60)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")

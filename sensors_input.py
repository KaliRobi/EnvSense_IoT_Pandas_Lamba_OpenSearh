import os
import time
import logging
import csv
import glob
import Adafruit_DHT
import RPi.GPIO as GPIO
import boto3
import smbus  # I2C communication for PCF8591
from datetime import datetime

# Configure logging
logging.basicConfig(filename='sensor.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# AWS S3 Configuration
S3_BUCKET = "s3-bucket-name"
S3_KEY = "sensor-data/{}.csv"
s3 = boto3.client("s3")

# Sensor Configuration
DHT_PIN = 17  # GPIO pin for DHT11
DS18B20_BASE_PATH = "/sys/bus/w1/devices/"
PCF8591_ADDRESS = 0x48  # I2C Address of PCF8591
PCF8591_CHANNEL_GAS = 0  # MiCS-5524 CO Sensor
PCF8591_CHANNEL_SOIL = 1  # Soil Moisture Sensor

# Initialize I2C bus
bus = smbus.SMBus(1)


def read_dht11():
    """temperature and humidity from DHT11."""
    try:
        humidity, temperature = Adafruit_DHT.read_retry(Adafruit_DHT.DHT11, DHT_PIN)
        return round(temperature, 1), round(humidity, 1)
    except Exception as e:
        logging.error(f"Error reading DHT11: {e}")
        return None, None


def read_ds18b20():
    """temperature from DS18B20."""
    try:
        device_folders = glob.glob(DS18B20_BASE_PATH + "28-*")
        if not device_folders:
            logging.warning("No DS18B20 sensor found.")
            return None
        
        device_file = os.path.join(device_folders[0], "w1_slave")
        with open(device_file, "r") as f:
            lines = f.readlines()
            if lines[0].strip()[-3:] == "YES":
                temp_line = lines[1].find("t=")
                if temp_line != -1:
                    temp = float(lines[1][temp_line + 2:]) / 1000.0
                    return round(temp, 2)
    except Exception as e:
        logging.error(f"Error reading DS18B20: {e}")
    return None


def read_pcf8591(channel):
    """data from PCF8591 ADC (I2C interface)."""
    if channel < 0 or channel > 3:
        raise ValueError("Channel must be between 0 and 3")
    
    bus.write_byte(PCF8591_ADDRESS, 0x40 | channel)  # select channel
    bus.read_byte(PCF8591_ADDRESS)  # dummy 
    value = bus.read_byte(PCF8591_ADDRESS)  # actual value (0-255)
    return value


def read_gas_sensor():
    """CO levels from MiCS-5524 in ppm."""
    raw_value = read_pcf8591(PCF8591_CHANNEL_GAS)
    co_ppm = (raw_value / 255.0) * 1000  # scale to 0 - 1000 ppm range
    return round(co_ppm, 2)


def read_soil_moisture():
    """soil moisture level as percentage (0% = dry, 100% = wet)."""
    raw_value = read_pcf8591(PCF8591_CHANNEL_SOIL)
    moisture_percentage = (255 - raw_value) / 255 * 100  # invert scale
    return round(moisture_percentage, 2)


def collect_sensor_data():
    """get data from all sensors."""
    timestamp = datetime.now().isoformat()
    temp_dht11, humidity = read_dht11()
    temp_ds18b20 = read_ds18b20()
    co_ppm = read_gas_sensor()
    soil_moisture = read_soil_moisture()

    return [timestamp, temp_dht11, temp_ds18b20, humidity, co_ppm, soil_moisture]


def validate_sensor_data(data):
    """check sensor data before writing to CSV."""
    timestamp, temp_dht11, temp_ds18b20, humidity, co_ppm, soil_moisture = data
    
    if temp_dht11 is not None and (temp_dht11 < -20 or temp_dht11 > 50):
        logging.warning(f"Invalid DHT11 temperature: {temp_dht11}")
        return False
    
    if humidity is not None and (humidity < 0 or humidity > 100):
        logging.warning(f"Invalid DHT11 humidity: {humidity}")
        return False
    
    if co_ppm is not None and (co_ppm < 0 or co_ppm > 1000):
        logging.warning(f"Invalid CO ppm: {co_ppm}")
        return False
    
    if soil_moisture is not None and (soil_moisture < 0 or soil_moisture > 100):
        logging.warning(f"Invalid soil moisture: {soil_moisture}")
        return False
    
    return True


def create_csv_file():
    """new CSV file with a unique name."""
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    csv_file = f"sensor_data_{timestamp}.csv"
    with open(csv_file, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["timestamp", "temperature_dht11_C", "temperature_ds18b20_C", "humidity_%", "co_ppm", "soil_moisture_%"])
    return csv_file


def upload_to_s3(file_path):
    """Upload CSV file to S3."""
    try:
        file_name = S3_KEY.format(datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))
        s3.upload_file(file_path, S3_BUCKET, file_name)
        logging.info(f"Uploaded {file_path} to S3 as {file_name}")
    except Exception as e:
        logging.error(f"Error uploading to S3: {e}")


def main():
    """loop to collect sensor data and upload it every 60 seconds."""
    buffer = []
    csv_file = create_csv_file()
    
    try:
        while True:
            data = collect_sensor_data()
            if validate_sensor_data(data):
                buffer.append(data)
                
                # Upload data every 10 minutes (or adjust as needed)
                if len(buffer) >= 10:
                    with open(csv_file, "a", newline="") as f:
                        writer = csv.writer(f)
                        writer.writerows(buffer)
                    upload_to_s3(csv_file)
                    buffer = []  # Clear buffer after upload
                    csv_file = create_csv_file()  # a new CSV file

            time.sleep(30)  # Wait half minute before next reading

    except KeyboardInterrupt:
        logging.info("Sensor data collection stopped.")
    finally:
        GPIO.cleanup()
        


if __name__ == "__main__":
    main()

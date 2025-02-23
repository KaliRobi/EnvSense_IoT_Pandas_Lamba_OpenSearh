# **EnvSense_IoT_Pandas_Lambda_OpenSearch**

## **End-to-End Data Pipeline for Monitoring a Plant in a Room**

### **Overview**
This project sets up an IoT-based data pipeline that collects environmental sensor data, processes it using AWS services, and visualizes it in Kibana.

### **Sensors Used**
- **Gravity KIT0021** – DS18B20 temperature sensor (connected via **PCF8591** A/D and D/A converter, 8-bit I2C)
- **Fermion MiCS-5524** – MEMS gas sensor (**CO, alcohol, VOC detection**)
- **DFRobot Gravity SEN0193** – **Analog soil moisture sensor** (corrosion-resistant)
- **Okystar DHT11** – **Temperature and humidity sensor**

### **Pipeline Workflow**
1. **Data Collection**
   - The sensors are connected to a **Raspberry Pi 4B**.
   - The Raspberry Pi collects sensor readings at regular intervals.
   
2. **Data Storage**
   - Sensor data is stored as a **CSV file**.
   - The CSV file is uploaded to **AWS S3**.
   
3. **Data Processing**
   - Data transformation is handled using **AWS Step Functions and Pandas**.
   - The processed data is prepared for indexing in OpenSearch.
   
4. **Data Ingestion**
   - The transformed data is ingested into **AWS OpenSearch** for querying and analysis.
   
5. **Data Visualization**
   - Data is visualized in **Kibana** to monitor environmental conditions in real-time.

### **Technologies Used**
- **Raspberry Pi 4B** (data collection)
- **Python, Pandas** (data processing)
- **AWS S3** (data storage)
- **AWS Step Functions & Lambda** (data transformation)
- **AWS OpenSearch** (data indexing & querying)
- **Kibana** (data visualization)

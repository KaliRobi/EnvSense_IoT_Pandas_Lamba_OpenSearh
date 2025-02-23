#EnvSense_IoT_Pandas_Lambda_OpenSearch

End-to-End Data Pipeline for Monitoring a Plant in a Room

Sensors Used:
Gravity KIT0021 – DS18B20 temperature sensor (connected via PCF8591 A/D and D/A converter, 8-bit I2C)
Fermion MiCS-5524 – MEMS gas sensor (CO, alcohol, VOC detection)
DFRobot Gravity SEN0193 – Analog soil moisture sensor (corrosion-resistant)
Okystar DHT11 – Temperature and humidity sensor
Pipeline Overview:
The sensors are connected to a Raspberry Pi 4B, which collects and stores data.
The collected data is saved as a CSV file and uploaded to AWS S3.
Data transformation is performed using AWS Step Functions and Pandas.
The processed data is ingested into OpenSearch for indexing and querying.
Finally, the data is visualized in Kibana for analysis and monitoring.
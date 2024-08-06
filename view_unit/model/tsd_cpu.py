"""
This module provides a class for interacting with an InfluxDB database, specifically for storing and querying CPU utilization data. 
The TimeSeriesDatabase_Cpu class includes methods for writing CPU data to the database, formatting data for storage, reading data, and deleting data from specified buckets.

Dependencies:
    - influxdb_client
    - datetime


Class: TimeSeriesDatabase_Cpu

Initialization
    - TimeSeriesDatabase_Cpu(ipAdresse, org, url, token)

        Parameters:
        
            ipAdresse (str): The IP address of the server.
            org (str): The organization name in InfluxDB.
            url (str): The URL of the InfluxDB instance.
            token (str): The authentication token for InfluxDB.
        
Methods
    - getTimeZone
            @classmethod
            def getTimeZone()

        Returns the current time zone of the system.

    - writeData
            def writeData(self, bucket, measurement, tags, fields, dateTime)
        Writes data to InfluxDB.
        Parameters:
            bucket (str): The bucket name where data will be stored.
            measurement (str): The measurement name.
            tags (dict): A dictionary of tags (key-value pairs).
            fields (dict): A dictionary of fields (key-value pairs).
            dateTime (datetime): The timestamp of the data point.

        Returns:
            bool: True if data is written successfully, otherwise False.

    - formateCpuData
            def formateCpuData(self, cpu_percentages, domain, ip_address, dateTime, interval=10)

        Formats and writes CPU utilization data to InfluxDB.
        Parameters:
            cpu_percentages (list): List of CPU utilization percentages.
            domain (str): The domain name.
            ip_address (str): The IP address of the virtual machine.
            dateTime (datetime): The timestamp of the first data point.
            interval (int, optional): The interval between data points in minutes (default is 10).
        
        Returns:
            bool: True if data is written successfully, otherwise False.

    - writeCpuData
            def writeCpuData(self, cpu_percentages, ip_addresses, dateTime, interval)

        Writes multiple CPU utilization data points to InfluxDB.
        Parameters:
            cpu_percentages (dict): Dictionary where keys are domain names and values are lists of CPU utilization percentages.
            ip_addresses (dict): Dictionary where keys are domain names and values are IP addresses.
            dateTime (datetime): The timestamp of the first data point.
            interval (int): The interval between data points in minutes.
        
        Returns:
            bool: True if data is written successfully, otherwise False.


    - readCpuData
            def readCpuData(self, start_time, end_time, bucket)

        Reads CPU utilization data from InfluxDB.
        Parameters:
            start_time (str): The start time for the query in RFC 3339 format (YYYY-MM-DDTHH:MM:SSZ).
            end_time (str): The end time for the query in RFC 3339 format (YYYY-MM-DDTHH:MM:SSZ).
            bucket (str): The bucket name from which data will be read.

        Returns:
            list: A list of tables containing the query results.

    - getCpuData
            def getCpuData(self, start_time, end_time)

        Gets CPU utilization data from a specified time range.
        Parameters:
            start_time (str): The start time for the query in RFC 3339 format (YYYY-MM-DDTHH:MM:SSZ).
            end_time (str): The end time for the query in RFC 3339 format (YYYY-MM-DDTHH:MM:SSZ).

        Returns:
            list: A list of dictionaries containing CPU utilization data.

            The method returns a list of dictionaries, where each dictionary represents a record of CPU utilization data within the specified time range. 
            Each dictionary contains the following keys and values:
                server_ip (str): The IP address of the server where the data was recorded.
                vm_ip (str): The IP address of the virtual machine (VM) for which the CPU utilization was recorded.
                vm_name (str): The name of the virtual machine.
                cpu_percent (float): The percentage of CPU utilization, which is the most important value as it represents the CPU usage for the VM with the specified IP address, 
                                located on the physical server with the specified IP address, measured between dateI and dateF.
                dateI (str): The start time of the measurement period in RFC 3339 format.
                dateF (str): The end time of the measurement period in RFC 3339 format.
    
    - readAllData
            def readAllData(self, bucket)

        Reads all data from a specified bucket in InfluxDB.
        Parameters:
            bucket (str): The bucket name from which data will be read.

        Returns:
            list: A list of tables containing the query results.

    - delete
            def delete(self, bucket)

        Deletes all data from a specified bucket in InfluxDB.
        Parameters:
            bucket (str): The bucket name from which data will be deleted.

"""

import influxdb_client
from influxdb_client import Point
from influxdb_client.client.write_api import SYNCHRONOUS
from datetime import datetime, timezone, timedelta


class TimeSeriesDatabase_Cpu:
    def __init__(self, ipAdresse, org, url, token):
        self.ipAdresse = ipAdresse
        self.org = org
        self.url = url 
        self.token = token
    
    @classmethod
    def getTimeZone():
        offset = datetime.now() - datetime.utcnow()
        offset = round(offset.total_seconds()/3600)

        offset = timedelta(hours=offset)
        time_zone = timezone(offset=offset)

        return time_zone
    

    def writeData(self, bucket, measurement, tags, fields, dateTime):
        try:
            bucket = bucket 
            point = Point(measurement)
            for tag_id, tag_value in tags.items():
                point = point.tag(tag_id, tag_value)
            for field_id, field_value in fields.items():
                point = point.field(field_id, field_value)
            point = point.time(dateTime)
            print(self.url)
            client = influxdb_client.InfluxDBClient(url=self.url, token=self.token, org=self.org)
            
            write_api = client.write_api(write_options=SYNCHRONOUS)
            # Write the point to InfluxDB
            write_api.write(bucket=bucket, org=self.org, record=point)

            client.close()
            return True
        
        except Exception as e:
            print("Error in writeData")
            print("Info: ", e)
            return False

    def formateCpuData(self, cpu_percentages, domain, ip_address, dateTime, interval=10):
        bucket = "cpu_percentages"

        if(interval < 0 or interval > 60):
            print("Error")
            interval = 10

        measurement = f"{interval}_measure"
        tags = dict()
        tags["server_ip"] = self.ipAdresse
        tags["vm_ip"] = ip_address
        tags["vm_name"] = domain
        dateTime_measure = dateTime
        
        for percent in cpu_percentages:
            fields = dict()
            fields["cpu_utilisation"] = percent
            response = self.writeData(bucket, measurement, tags, fields, dateTime_measure)
            dateTime_measure += timedelta(minutes=interval)
            print(dateTime_measure)

        if(response):
            print("Success")
            return True
        else:
            print("Error")
            return False

    
    def writeCpuData(self, cpu_percentages, ip_addresses, dateTime, interval):
        try:
            for domain in cpu_percentages:
                self.formateCpuData(cpu_percentages[domain], domain, ip_addresses[domain], dateTime, interval)
    
            return True
        except Exception as e:
            print("Error in formateCpuData")
            print("Info ", e)
            return False
    
    def readCpuData(self, start_time, end_time, bucket):
        bucket = bucket

        field = "_value"
        query = f'from(bucket: "{bucket}") \
            |> range(start: {start_time}, stop: {end_time}) \
            |> group(columns: ["_measurement","server_ip", "vm_ip", "vm_name"]) \
            |> sum(column: "{field}")'

        client = influxdb_client.InfluxDBClient(url=self.url, token=self.token, org=self.org)
        result = client.query_api().query(query=query)
        client.close()
        # Affichage des résultats
        return result
    
    def getCpuData(self, start_time, end_time):
        bucket = "cpu_percentages"
        result = self.readCpuData(start_time, end_time, bucket)
        
        cpu_consumptions = []
        
        for table in result:
            for record in table.records:
                element = {
                    "server_ip" : record["server_ip"],
                    "vm_ip": record["vm_ip"],
                    "vm_name": record["vm_name"],
                    "cpu_percent" : record["_value"],
                    "dateI": record["_start"],
                    "dateF": record["_stop"],
                }
                cpu_consumptions.append(element)

        return cpu_consumptions

    def readAllData(self, bucket):
        """
        Read all data from InfluxDB for a specified bucket.

        Parameters:
            bucket (str): The bucket to read data from.

        Returns:
            list: The result of the query as a list of tables.
        """
        query = f'from(bucket: "{bucket}") |> range(start: -inf)'
        
        client = influxdb_client.InfluxDBClient(url=self.url, token=self.token, org=self.org)
        result = client.query_api().query(query=query)
        client.close()
        return result  

    def delete(self, bucket):
        bucket = bucket
        client = influxdb_client.InfluxDBClient(url=self.url, token=self.token, org=self.org)
        delete_api = client.delete_api()

         # Définir une plage de temps couvrant toute l'existence des données
        start = datetime(1970, 1, 1, 0, 0, )  # Début du temps UNIX
        # Obtenir la date et l'heure actuelles
        now = datetime.now()
        
        # Formater la date et l'heure actuelles en RFC 3339
        start = start.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        stop = now.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        print(start)
        print(stop)
        # Définir le prédicat de suppression pour supprimer toutes les séries dans le bucket spécifié
        predicate = '_measurement="10_measure"'

        # Exécuter la suppression
        delete_api.delete(bucket=bucket, start=start, stop=stop, predicate=predicate)
        client.close()
        print(f"Toutes les données dans le bucket '{bucket}' ont été supprimées.")


def test_creatData():
    cpu_percentages = dict()
    vms_ip_addresses = dict()


    cpu_percentages["VM110"] = [10]
    vms_ip_addresses["VM110"] = "10.10.10.110"

    cpu_percentages["VM111"] = [10]
    vms_ip_addresses["VM111"] = "10.10.10.111"

    cpu_percentages["VM121"] = [40]
    vms_ip_addresses["VM121"] = "10.10.10.121"

    cpu_percentages["VM133"] = [20]
    vms_ip_addresses["VM133"] = "10.10.10.133"


    return cpu_percentages, vms_ip_addresses

def testFunction():
    token = "btmlphqXfMo7R43O4R9J5Xsdnfx570GdHoXCVcA8vZywrm_2UtHT1BADvN30_tfHCumgeZVQd5F3msgo3UKN9w=="
    org = "masnssen"
    url = "http://localhost:8086"
    ipAdresse = "10.10.10.0"
    tsd = TimeSeriesDatabase_Cpu(ipAdresse, org, url, token)


    cpu_percentages, vms_ip_addresses = test_creatData()
    dt = datetime(2024, 7, 22, 12, 0)
    tsd.writeCpuData(cpu_percentages, vms_ip_addresses, dt, 60)

    
    st = datetime(2024, 7, 22, 12, 0).isoformat() + "Z"
    et = datetime(2024, 7, 22, 13, 0).isoformat() + "Z"
    
    results = tsd.getCpuData(st, et)
    print(results)




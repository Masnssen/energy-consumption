"""
This module provides functionalities to interact with an InfluxDB database to write and read energy consumption data. 
The TimeSeriesDatabase_Consumption class allows for writing data points with specified measurements, tags, and fields, as well as querying and managing consumption data.

Class: TimeSeriesDatabase_Consumption
    TimeSeriesDatabase_Consumption(ipAdresse, org, url, token)

    Initializes a new instance of the TimeSeriesDatabase_Consumption class.

    Parameters:
        ipAdresse (str): The IP address of the server.
        org (str): The organization name.
        url (str): The URL of the InfluxDB instance.
        token (str): The authentication token.

    - getTimeZone()
        Get the current time zone.

        Returns:
            timezone: The current time zone.

    - writeData
            writeData(self, bucket, measurement, tags, fields, dateTime)

        Writes a data point to the specified bucket in InfluxDB.

            Parameters:
                bucket (str): The bucket to write data to.
                measurement (str): The measurement name.
                tags (dict): A dictionary of tags.
                fields (dict): A dictionary of fields.
                dateTime (datetime): The timestamp for the data point.

            Returns:
                bool: True if the write operation is successful, False otherwise.

    - writeConsumptionData
            writeConsumptionData(self, consumption, dateTime, interval)
        Writes energy consumption data to InfluxDB.

            Parameters:
                consumption (float): The consumption value.
                dateTime (datetime): The timestamp for the data point.
                interval (int): The interval in minutes. Must be between 0 and 60.

    - readData
            readData(self, start_time, end_time, bucket)
        This function will return the amount of energy consumed by any device at a given IP address between two date-time values.

        Parameters:
            start_time (str): The start time for the query in RFC 3339 format (YYYY-MM-DDTHH:MM).
            end_time (str): The end time for the query in RFC 3339 format (YYYY-MM-DDTHH:MM).
            bucket (str): The bucket to read data from.
    
        Returns:
            list: The result of the query as a list of tables.

    - readAllData
            readAllData(self, bucket)
        Reads all data from InfluxDB for a specified bucket.

        Parameters:
            bucket (str): The bucket to read data from.
    
        Returns:
            list: The result of the query as a list of tables.

    - manageConsumptionData
            manageConsumptionData(self, start_time, end_time)
        Manages and retrieves the maximum consumption data within a specified time range.

        Parameters:
            start_time (str): The start time for the query in RFC 3339 format (YYYY-MM-DDTHH:MM).
            end_time (str): The end time for the query in RFC 3339 format (YYYY-MM-DDTHH:MM).

        Returns:
            dict: A dictionary with IP addresses as keys and consumption values as values.

    - readAllData
            def readAllData(self, bucket)

        Reads all data from a specified bucket in InfluxDB.
        Parameters:
            bucket (str): The bucket name from which data will be read.

        Returns:
            list: A list of tables containing the query results.
            
    - delete    
            delete(self, bucket)
        Deletes all data from a specified bucket in InfluxDB.

        Parameters:
            bucket (str): The bucket to delete data from.

"""

import influxdb_client, os, time
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
from datetime import datetime, timezone, timedelta

class TimeSeriesDatabase_Consumption:
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
        
        except:
            print("Error in writeData")
            return False

    def writeConsumptionData(self,consumption, dateTime, interval):
        bucket = "energy_consumptions"
        if(interval < 0 or interval > 60):
            print("Error")
            interval = 0

        measurement = f"{interval}_measure"
        tags = dict()
        tags["ip"] = self.ipAdresse
        fields = dict()
        fields["consumption"] = consumption
        response = self.writeData(bucket, measurement, tags, fields, dateTime)

        if(response):
            print("Success")
        else:
            print("Error")

    def readData(self, start_time, end_time, bucket):
        bucket = bucket

        field = "_value"
        query = f'from(bucket: "{bucket}") \
            |> range(start: {start_time}, stop: {end_time}) \
            |> group(columns: ["_measurement", "ip"]) \
            |> sum(column: "{field}")'

        client = influxdb_client.InfluxDBClient(url=self.url, token=self.token, org=self.org)
        result = client.query_api().query(query=query)
        client.close()
        # Affichage des résultats
        return result

    def readAllData(self, bucket):
       
        query = f'from(bucket: "{bucket}") |> range(start: -inf)'
        
        client = influxdb_client.InfluxDBClient(url=self.url, token=self.token, org=self.org)
        result = client.query_api().query(query=query)
        client.close()
        return result
            
    def manageConsumptionData(self, start_time, end_time):
        bucket = "energy_consumptions"
        result = self.readData(start_time, end_time, bucket)
        consumptions = dict()
    
        for table in result:
            for record in table.records:
                ip = record["ip"]
                cons = record["_value"]
                if(ip in consumptions):
                    consumptions[ip] += cons
                else:
                    consumptions[ip] = cons
        return consumptions

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



def testFunction():
    token = "btmlphqXfMo7R43O4R9J5Xsdnfx570GdHoXCVcA8vZywrm_2UtHT1BADvN30_tfHCumgeZVQd5F3msgo3UKN9w=="
    org = "masnssen"
    url = "http://localhost:8086"
    ipAdresse = "10.10.10.0"
    tsd = TimeSeriesDatabase_Consumption(ipAdresse, org, url, token)
    
    st = datetime(2024, 7, 22, 12, 0).isoformat() + "Z"
    et = datetime(2024, 7, 22, 13, 0).isoformat() + "Z"
    dt = datetime(2024, 7, 22, 12, 0)
    tsd.writeConsumptionData(200000, dt, 60)

    consumption = tsd.manageConsumptionData(st, et)
    print(consumption)
    #results = tsd.readAllData("energy_consumptions")


#testFunction()
# writeData(client)
# readData(client)
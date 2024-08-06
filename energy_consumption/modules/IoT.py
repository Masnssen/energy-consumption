"""
This module provides all the necessary functions to measure the energy consumption of a Tapo P110 IoT plug. Here is a detailed description of each function:

Functions:

    plug_connect(plug_username, plug_password, plug_ip)
        Description: Connects to the Tapo P110 IoT plug.
        Parameters:
            plug_username: The email address used to create the Tapo account.
            plug_password: The password associated with the Tapo account.
            plug_ip: The IP address of the plug.
        Returns: A device object that provides various functions for interacting with the plug (such as retrieving measurements, turning the plug on or off, etc.).

    plug_getMeasure(device)
        Description: Retrieves the current power consumption of the plug.
        Parameter:
            device: The device object returned by plug_connect.
        Returns: The current power consumption of the plug in watts (W).

    plug_getConso(device, duration, nbMeasure)
        Description: Calculates the plug's power consumption over a specified duration, with a given number of measurements per minute.
        Parameters:
            device: The device object identifying the plug.
            duration: The total duration over which to calculate consumption, in minutes.
            nbMeasure: The number of measurements to take per minute (cannot exceed 60).
        Returns: The average energy consumption over the specified duration, in watt-hours (Wh).

    plug_calculate_power_consumption(device, duration, numberPeriods, nbMeasure)
        Description: Calculates the power consumption over a long duration, divided into multiple periods. Returns an array where each value represents the consumption for a specific period.
        Parameters:
            device: The device object representing the plug.
            duration: The total duration over which to calculate consumption, in minutes.
            numberPeriods: The number of periods into which the total duration is divided.
            nbMeasure: The number of measurements to take per minute (cannot exceed 60).
        Returns:
            An array where each element represents the energy consumption for each specific period, in watt-hours (Wh).
            The total energy consumption over the entire specified duration, in watt-hours (Wh).

    plug_hour_calculate_power_consumption(device, dateI, dateF, numberPeriods, nbMeasure):
        Description:
            calculate the power consumption over a specified duration, divided into multiple periods.
            
            The function supports calculating the consumption between any two datetime values and can divide the 
            total duration into segments ranging from 1 minute to a maximum of 60 minutes per period.
            
            Returns an array where each value represents the consumption for a specific period in watt-hours (Wh).
            
            If the provided `dateI` or `dateF` is invalid or not in the required format, the function defaults to using the 
            start of the next full hour from the current time for `dateI`, and the start of the hour after that for `dateF`.
            This ensures that the function always has a valid starting and ending point for the calculation.

        Parameters:
            device: The device object representing the plug. This object should have methods to retrieve power usage.
            dateI: The start datetime for the period over which to calculate consumption.
               Must be in the format 'yyyy-mm-dd hh:mm', where:
               - yyyy: Year as a four-digit number (e.g., 2024)
               - mm: Month as a one or two-digit number (e.g., 1 for January, 10 for October)
               - dd: Day as a one or two-digit number (e.g., 5, 15, 25)
               - hh: Hour in 24-hour format (e.g., 0 for midnight, 14 for 2 PM)
               - mm: Minute as a two-digit number (e.g., 00, 30, 59)
            dateF: The end datetime for the period over which to calculate consumption.
                Must be in the same format as dateI: 'yyyy-mm-dd hh:mm'.
            period: The length of each period in minutes. Must be an integer between 1 and 60 minutes.
                This defines how the total duration between dateI and dateF is divided. For example, if period is 10, 
                the function will calculate and return the consumption for every 10-minutes interval between dateI and dateF.
            nbMeasure: The number of measurements to take per minute (cannot exceed 60).

        Returns:
            An array where each element represents the energy consumption for each specific period, in watt-hours (Wh).
            The total energy consumption over the entire specified duration, in watt-hours (Wh).

Notes:

    Instantaneous Consumption: The plug_getMeasure function provides a real-time reading of the plug's power consumption, useful for immediate monitoring.
    Duration and Segmentation: For longer-term evaluations, the plug_getConso and plug_calculate_power_consumption functions allow for energy consumption measurement over extended and segmented periods, offering a detailed view of energy usage.

These functions provide a comprehensive solution for monitoring and analyzing the energy consumption of your Tapo P110 IoT plug.
"""


import asyncio
from tapo import ApiClient
from time import *
from datetime import datetime, timedelta
import json

async def plug_connect(plug_username="tmasnssen@gmail.com", plug_password="Massi@1408", plug_ip="192.168.0.3"):
    try:
        client = ApiClient(plug_username, plug_password)
        device = await client.p110(plug_ip)
        print("Login success")
        return device
    except:
        print("Not connected")
        return False

async def plug_getMeasure(device):
    try:
        current_power = await device.get_current_power()
        return current_power.to_dict()['current_power']
    except:
        print("Error in plug_getMeasure")
        return False

async def plug_getConso(device, duration, nbMeasure):
    if nbMeasure > 60:
        nbMeasure = 60
    sleepTime = 60/nbMeasure - 0.01
    d = 0
    consumption = 0
    while d < duration:
        i = 0
        measure = 0
        while(i < nbMeasure):
            measure += await plug_getMeasure(device)
            sleep(sleepTime)
            i += 1
        consu = measure/nbMeasure*60
        consumption += consu
       
        d+=1

    
    return consumption

async def plug_calculate_power_consumption(device, duration, numberPeriods, nbMeasure):
    period = duration/numberPeriods
    overflow = period*(numberPeriods%int(numberPeriods))
    p = 0
    consumption = 0
    tabconsumtion = []
    while p < int(numberPeriods):
        consu = await plug_getConso(device, period, nbMeasure)
        tabconsumtion.append(consu)
        consumption += consu

        p += 1
    
    consu = await plug_getConso(device, overflow, nbMeasure)
    tabconsumtion.append(consu)
    consumption += consu
    
    return tabconsumtion, consumption

async def plug_hour_calculate_power_consumption(device, dateI="2024-07-23 14:10", dateF="2024-07-23 15:15", period=10, nbMeasure=6):
    actuel_dateTime = datetime.now()
    try:
        initial_dateTime = datetime.strptime(dateI, '%Y-%m-%d %H:%M')   
        final_dateTime = datetime.strptime(dateF, '%Y-%m-%d %H:%M')
       
        if(initial_dateTime < (actuel_dateTime-timedelta(minutes=2)) or initial_dateTime > final_dateTime):
            raise Exception("dateI > dateF")
    except:
        print("Error. By default, the initial datetime (dateI) is the start of the next hour.")
        initial_dateTime = (datetime.now() + timedelta(hours=1)).replace(minute=0, second=0, microsecond=0)
        final_dateTime = (datetime.now() + timedelta(hours=2)).replace(minute=0, second=0, microsecond=0)

    
    while(datetime.now() < initial_dateTime):
        print("***** Waiting *****")
        sleep((initial_dateTime-datetime.now()).total_seconds())


    duration = int((final_dateTime-datetime.now()).total_seconds()/60)
    if(duration == 0):
        duration = 1

    if(period > duration):
        print("Error: period > duration")
        period = int(duration/2)
        if(period == 0):
            period = 1

    tabconsumption = []
    consumption = 0 
    print("Start")
    nbPeriod = duration/period
    tabconsumption, consumption = await plug_calculate_power_consumption(device, duration, nbPeriod, nbMeasure)
    
    """
        Here we create a dictionary where each key is a datetime object, and each value is a tuple (x, y), where:

        x represents the energy consumption.
        y represents the duration in minutes over which this consumption is measured.

        For example, if y = 10, it means that x is the consumption from the time specified by the key up to the key time plus 10 minutes.
    """
    consumptionMeasur = dict()
    dateTime = initial_dateTime
    
    for elm in tabconsumption:
        consumptionMeasur[dateTime.strftime("%Y-%m-%d %H:%M")] = (elm/(60*60*1000), period) 
        dateTime += timedelta(minutes=period)
    
    return consumptionMeasur, consumption/(60*60*1000)


def storeDataFile(fileName, dictionary):
    with open(fileName, "w") as file:
        json.dump(dictionary, file)

from tapo.requests import EnergyDataInterval
async def test(device):
    today = datetime.now() - timedelta(days=1)
    print(today)
    result = await device.get_energy_data(EnergyDataInterval.Hourly, today)
    print(f"Device usage: {result.to_dict()}")

# if __name__ == "__main__":
#     device = asyncio.run(plug_connect())
# #     asyncio.run(test(device))
    
#     consumption = asyncio.run(plug_getMeasure(device))
#     print(consumption)
# #     # tabConsumption, consumption = asyncio.run(plug_hour_calculate_power_consumption(device))
# #     # print(tabConsumption, consumption)
# #     # storeDataFile("Consumption_test1.json", tabConsumption)



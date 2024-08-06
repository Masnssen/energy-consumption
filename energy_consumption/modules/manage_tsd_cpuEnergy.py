import sys, os
from datetime import datetime
import asyncio
from datetime import datetime, timedelta

import modules.tsd_consumption as enery_consumption
import modules.IoT as IoT
import modules.cpu_usage as cpu_usage
import modules.tsd_cpu as tsd_cpu


def writeConsumption_tsd(consumptions):
    token = "btmlphqXfMo7R43O4R9J5Xsdnfx570GdHoXCVcA8vZywrm_2UtHT1BADvN30_tfHCumgeZVQd5F3msgo3UKN9w=="
    org = "masnssen"
    url = "http://localhost:8086"
    ipAdresse = "10.10.10.0"

    tsd = enery_consumption.TimeSeriesDatabase_Consumption(ipAdresse, org, url, token)
    
    offset_date = datetime.utcnow() - datetime.now() 
    offset_date = round(offset_date.total_seconds()/3600)

    for elm in consumptions:
        dateT = datetime.strptime(elm, '%Y-%m-%d %H:%M') + timedelta(hours=offset_date)
        consumption, interval = consumptions[elm]
        tsd.writeConsumptionData(consumption, dateT, interval)
        print(dateT, ", interval :", consumption)

    st = (datetime.now() - timedelta(hours=2)).isoformat() + "Z"
    et = datetime.now().isoformat() + "Z"

    consumption = tsd.manageConsumptionData(st, et)
    print(consumption)
    #results = tsd.readAllData("energy_consumptions")


def readtest():
    token = "btmlphqXfMo7R43O4R9J5Xsdnfx570GdHoXCVcA8vZywrm_2UtHT1BADvN30_tfHCumgeZVQd5F3msgo3UKN9w=="
    org = "masnssen"
    url = "http://localhost:8086"
    ipAdresse = "10.10.10.0"

    tsd = enery_consumption.TimeSeriesDatabase_Consumption(ipAdresse, org, url, token)
    st = (datetime.now() - timedelta(hours=3)).isoformat() + "Z"
    et = datetime.now().isoformat() + "Z"

    consumption = tsd.manageConsumptionData(st, et)
    print(consumption)

    tsd = enery_consumption.TimeSeriesDatabase_Consumption(ipAdresse, org, url, token)

def iot(plug_username, plug_password, plug_ip):
    offset_date = datetime.utcnow() - datetime.now() 
    offset_date = round(offset_date.total_seconds()/3600)

    device = asyncio.run(IoT.plug_connect(plug_username, plug_password, plug_ip))
    if(device == False):
        print("Not connected to the IoT plug")
        return False
    print("Start IoT")
    dateDeb = (datetime.now()+timedelta(minutes=1)).strftime('%Y-%m-%d %H:%M') 
    dateFin = datetime.now() + timedelta(minutes=20)
    dateFin = (dateFin + timedelta(hours=1)).replace(minute=0, second=0, microsecond=0).strftime('%Y-%m-%d %H:%M') 
    
    i = 12
    periodDuration = 10
    while i > 0:
        tabConsumption, consumption = asyncio.run(IoT.plug_hour_calculate_power_consumption(device, dateDeb, dateFin, periodDuration))
        writeConsumption_tsd(tabConsumption)
        print("Consumption between: ", dateDeb, " and ", dateFin, " is ", consumption)
        dateDeb = datetime.now().strftime('%Y-%m-%d %H:%M') 
        if dateDeb < dateFin:
            dateDeb = dateFin
        dateFin = datetime.now() + timedelta(minutes=20)
        dateFin = (dateFin + timedelta(hours=1)).replace(minute=0, second=0, microsecond=0).strftime('%Y-%m-%d %H:%M') 

        i -= 1

def writeCpu_tsd(cpu_percentages, vms_ip_addresses, dt, interval, params):
    
    token = params["token"]
    org = params["org"]
    url = params["url"]
    ipAdresse = params["ip"]

    tsd = tsd_cpu.TimeSeriesDatabase_Cpu(ipAdresse, org, url, token)

    offset_date = datetime.utcnow() - datetime.now() 
    offset_date = round(offset_date.total_seconds()/3600)

    dateT = datetime.strptime(dt, '%Y-%m-%d %H:%M') + timedelta(hours=offset_date)

    tsd.writeCpuData(cpu_percentages, vms_ip_addresses, dateT, interval)




def cpu_tsd(params):
    dateDeb = datetime.now().strftime('%Y-%m-%d %H:%M')
    dateFin = datetime.now() + timedelta(minutes=20)
    dateFin = (dateFin + timedelta(hours=1)).replace(minute=0, second=0, microsecond=0)
    
    i = 10
    interval = 10
    while i > 0:
        vms_ip_addresses = cpu_usage.get_all_vms_ip_addresses()
        cpu_percentages = cpu_usage.manage_cpu_percentage(dateDeb, dateFin, interval)
        
        writeCpu_tsd(cpu_percentages, vms_ip_addresses, dateDeb, interval, params)

        dateDeb = datetime.now().strftime('%Y-%m-%d %H:%M') 
        if dateDeb < dateFin:
            dateDeb = dateFin

        dateFin = datetime.now() + timedelta(minutes=20)
        dateFin = (dateFin + timedelta(hours=1)).replace(minute=0, second=0, microsecond=0)

        i -= 1



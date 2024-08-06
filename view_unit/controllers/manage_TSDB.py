"""
This module provides functions to retrieve and process CPU and energy consumption data for servers and virtual machines (VMs). The functions use temporal database queries to obtain necessary data and compute the total consumption based on the retrieved information.

Functions:

    - getServerCpu(serverIp, dateS, dateF)

        Retrieves CPU usage data for a specific server between two dates.

        Parameters:
        - serverIp (str): The IP address of the server for which data is to be retrieved.
        - dateS (str): The start date and time in ISO 8601 format (e.g., "2024-07-10T08:00:00Z").
        - dateF (str): The end date and time in ISO 8601 format (e.g., "2024-07-10T10:00:00Z").

        Returns:
        - dict: A dictionary where each key is a server IP address, and the value is a list of lists. Each inner list contains the VM IP and the percentage of CPU used.
        - Example: {'20.20.20.20': [['10.10.10.10', 85], ['22.22.22.20', 90]]}

        Exceptions:
        - Exception: Raised if there is an error while retrieving or processing the data.


    - getServer_consumption(serverIp, dateS, dateF)

        Retrieves energy consumption data for a specific server between two dates.

        Parameters:
        - serverIp (str): The IP address of the server for which data is to be retrieved.
        - dateS (str): The start date and time in ISO 8601 format (e.g., "2024-07-10T08:00:00Z").
        - dateF (str): The end date and time in ISO 8601 format (e.g., "2024-07-10T10:00:00Z").

        Returns:
        - The energy consumption data for the server, with the server IP address as the key and the total consumption as the value.
        - Example: 12345

        Exceptions:
        - Exception: Raised if there is an error while retrieving or processing the data.

    

    - getVms_consumption(server_consumption, vms_cpu, vms)

        Calculates the consumption data for specific VMs based on the server's CPU data and energy consumption.

        Parameters:
        - server_consumption (float): The total energy consumption of the server for the specified period.
        - vms_cpu (dict): A dictionary where each key is a server IP and the value is a list of lists containing the VM IP and the percentage of CPU used.
            - Example: {'20.20.20.20': [['10.10.10.10', 85], ['22.22.22.20', 90]]}
        - vms (list): A list of VMs with their names and IPs.
            - Example: [['vm1', '10.10.10.10'], ['vm2', '22.22.22.20']]

        Returns:
        - float: The total consumption for the specified VMs, calculated by multiplying the server consumption by the CPU percentage for each VM.

        Exceptions:
        - ValueError: Raised if the server IP is not found in vms_cpu or if vms is not in the correct format.

    
    - manageCpu_consumption(serverIp, vms, dateS, dateF)

        Manages the retrieval and calculation of VM consumption using CPU data and server consumption data.

        Parameters:
        - serverIp (str): The IP address of the server.
        - vms (list): A list of VMs with their names and IPs.
            - Example: [['vm1', '10.10.10.10'], ['vm2', '22.22.22.20']]
        - dateS (str): The start date and time in ISO 8601 format.
        - dateF (str): The end date and time in ISO 8601 format.

        Returns:
        - float: The total consumption of the specified VMs for the given server.

        
    - manageEnergyConsumption(resources, dateS, dateF)

        Calculates the total energy consumption for all specified servers and VMs.

        Parameters:
        - resources (dict): A dictionary where each key represents a server and each value is a list of VMs for that server.
            - Example: {'server_20.20.20.20': [['vm1', '10.10.10.10'], ['vm2', '22.22.22.20']], 'server_30.30.30.30': [['vm3', '30.30.30.30']]}
        - dateS (str): The start date and time in ISO 8601 format.
        - dateF (str): The end date and time in ISO 8601 format.

        Returns:
        - float: The total energy consumption for all specified servers and VMs.
"""

import sys, os
from datetime import datetime
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'model')))
import tsd_cpu, tsd_consumption
import re



ISO_8601_REGEX = (
    r'^(\d{4}-\d{2}-\d{2})'  # Date : YYYY-MM-DD
    r'(T(\d{2}:\d{2}:\d{2})(\.\d{3}?))'  # Heure : THH:MM:SS:UUU
    r'(Z)$'  # Optionnel : Z pour UTC
)

def is_iso_8601(date_string):
    return re.match(ISO_8601_REGEX, date_string) is not None

def validate_dates(start_date, end_date):
    
    if not is_iso_8601(start_date):
        print("Hello erro")
        return False
        
    if not is_iso_8601(end_date):
        return False

    return True

def getServerCpu(serverIp, dateS, dateF):
    token = "btmlphqXfMo7R43O4R9J5Xsdnfx570GdHoXCVcA8vZywrm_2UtHT1BADvN30_tfHCumgeZVQd5F3msgo3UKN9w=="
    org = "masnssen"
    url = "http://localhost:8086"
    ipAdresse = "10.10.10.0"

    try:
        module_tsd_cpu = tsd_cpu.TimeSeriesDatabase_Cpu(serverIp, org, url, token)
        results = module_tsd_cpu.getCpuData(dateS, dateF)
        formated_result = dict()
        for server in results:
            server_ip = server["server_ip"]
            vm_ip = server["vm_ip"]
            cpu = server["cpu_percent"]
            if(server_ip in formated_result):
                formated_result[server_ip].append([vm_ip, cpu])
            else:
                formated_result[server_ip] = [[vm_ip, cpu]]
        
        #print(formated_result)
        return formated_result
    except Exception as e:
        print("Error : ", e)
        return False

def getServer_consumption(serverIp, dateS, dateF):
    token = "btmlphqXfMo7R43O4R9J5Xsdnfx570GdHoXCVcA8vZywrm_2UtHT1BADvN30_tfHCumgeZVQd5F3msgo3UKN9w=="
    org = "masnssen"
    url = "http://localhost:8086"
    ipAdresse = "20.20.20.20"

    try:
        print(serverIp)
        module_tsd_consumption = tsd_consumption.TimeSeriesDatabase_Consumption(serverIp, org, url, token)

        consumption = module_tsd_consumption.manageConsumptionData(dateS, dateF)
        print(consumption)
        if(serverIp in consumption):
            return consumption[serverIp] 
        
        return False
               
    except Exception as e:
        print("Error: ", e)
        return False

def getVms_consumption(server_consumption, vms_cpu, vms):
    vms_consumption = 0
    for elm in vms_cpu:
        for vm in vms:
            if elm[0] == vm[1]:
                vms_consumption += (server_consumption*elm[1]/100)
                break
    
    print("vms_consumption: ", vms_consumption)
    return vms_consumption

def manageCpu_consumption(serverIp, vms, dateS, dateF):
    vms_cpu = getServerCpu(serverIp, dateS, dateF)
    if(vms_cpu != False):
        server_consumption = getServer_consumption(serverIp, dateS, dateF)
        
        if(server_consumption == False):
            return False
        
        if(serverIp in vms_cpu):
            print("vms_cpu: ", vms_cpu[serverIp])
            print("Server_consumption", server_consumption)
            print("vms: ", vms)
            consumption = getVms_consumption(server_consumption, vms_cpu[serverIp], vms)
        else:
            consumption = server_consumption
            
    else:
        consumption = getServer_consumption(serverIp, dateS, dateF)
        if(consumption == False):
            return False

    return consumption


def manageEnergyConsumption(resources, dateS, dateF):

    if(validate_dates(dateS, dateF) == False):
        dateS = datetime.fromisoformat(dateS).isoformat()+"Z"  
        dateF = datetime.fromisoformat(dateF).isoformat()+"Z"  

        if(validate_dates(dateS, dateF) == False):
            return 0
        
    total_consumption = 0
    for server in resources:
        serverIp = server.split('_')[1]
        vms = resources[server]
        print(len(vms), vms)
        if(len(vms) == 0):
            consumption = getServer_consumption(serverIp, dateS, dateF)
        else:
            consumption = manageCpu_consumption(serverIp, vms, dateS, dateF)
            if(consumption == False):
                consumption = 0 
        print("Consumption: ", consumption)
        total_consumption += consumption
    print(total_consumption)
    return round(total_consumption, 3)


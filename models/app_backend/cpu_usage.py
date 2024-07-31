"""
***********Module for Managing VMs CPU Usage and IP Addresses******************

This module provides all the necessary functions to retrieve VM names, their IP addresses, and to measure the CPU usage percentage of VMs over a specified interval using virsh commands.
Functions:
    
    get_vms_list()
        Description: Retrieves the list of all running VMs.
        Parameters: None
        Returns:
            - A list of VM names.
            - Returns an empty list if there is an error executing the command.

    get_vm_ip_address(vm_name)
        Description: Retrieves the IP address of a specified VM.
        Parameters:
            vm_name (str): The name of the VM.
        Returns:
            The IP address of the VM as a string.
            None if the IP address is not found or if there is an error executing the command.

    get_all_vms_ip_addresses()
        Description: Retrieves the IP addresses for all running VMs.
        Parameters: None
        Returns:
            A dictionary where the keys are VM names and the values are their IP addresses or a message indicating no IP found.

    get_all_vms_cpu_usage()
        Description: Retrieves the CPU usage statistics for all running VMs.
        Parameters: None
        Returns:
            A dictionary where the keys are VM names and the values are CPU usage.
            Returns False if there is an error executing the command.

    calcul_cpu_percentage(initail_time, final_time, interval)
        Description: Calculates the CPU usage percentage of each VM between two time points.
        Parameters:
            initail_time (dict): Initial CPU usage statistics.
            final_time (dict): Final CPU usage statistics.
            interval (int): Time interval in seconds.
        Returns:
            A dictionary where the keys are VM names and the values are the CPU usage percentages.

    manage_cpu_percentage(dateI, dateF, interval)
        Description: Manages the CPU usage measurement process, calculating CPU usage percentages for VMs at specified intervals between two dates.
        Parameters:
            dateI (str): Initial datetime in the format 'YYYY-MM-DD HH:MM'.
            dateF (str): Final datetime in the format 'YYYY-MM-DD HH:MM'.
            interval (int): Time interval in seconds for calculating CPU usage.
        Returns:
            A dictionary where the keys are VM names and the values are lists of CPU usage percentages over the intervals.
        
        Additional Behavior:
            The function waits until the specified start time (dateI), then measures CPU usage at the given interval until the specified end time (dateF).
            If dateI is invalid or in the past, it defaults to the start of the next hour.
            Adjusts the interval if it is greater than the duration between dateI and dateF.

"""

import subprocess
import re
from datetime import datetime, timedelta
from time import sleep

def get_vms_list():
    try:
        result = subprocess.run(['virsh', 'list', '--name'], capture_output=True, text=True)
        if result.returncode != 0:
            print(f"Error executing virsh list: {result.stderr}")
            return []
        
        
        vms = result.stdout.strip().split('\n')
        return [vm for vm in vms if vm]  # Remove any empty strings
    except Exception as e:
        print(f"An error occurred: {e}")
        return []

def get_vm_ip_address(vm_name):
    try:
        result = subprocess.run(['virsh', 'domifaddr', vm_name], capture_output=True, text=True)
        if result.returncode != 0:
            print(f"Error executing virsh domifaddr for {vm_name}: {result.stderr}")
            return None

        # Parse the output for IP address
        ip_match = re.search(r'ipv4\s+(\S+)', result.stdout)
        if ip_match:
            return ip_match.group(1)
        else:
            return None
    except Exception as e:
        print(f"An error occurred while getting IP for {vm_name}: {e}")
        return None

def get_all_vms_ip_addresses():
    vms_ip = {}
    vms_list = get_vms_list()
    for vm in vms_list:
        ip_address = get_vm_ip_address(vm)
        if ip_address:
            vms_ip[vm] = ip_address
        else:
            vms_ip[vm] = 'No IP found'
    return vms_ip

def get_all_vms_cpu_usage():
    try:
        cpu_usage = dict()
        # Execute the virsh domstats command with --cpu-total option
        result = subprocess.run(['virsh', 'domstats', '--cpu-total'], capture_output=True, text=True)
        
        # Check if the command was successful
        if result.returncode != 0:
            print(f"Error executing virsh domstats: {result.stderr}")
            return

        # Parse the output
        vms_stats = result.stdout.split('\n\n')  # Each VM's stats are separated by a blank line
        for vm_stats in vms_stats:
            if(vm_stats == ""):
                continue
            vm_info = vm_stats.split("\n")
            if(len(vm_info) > 0):
                domain = vm_info[0].split()[1].strip("'")
                vm_info.pop(0)
                cpu = dict()
                for info in vm_info:
                    info_split = info.split("=") 
                    cpu[info_split[0].strip()] = info_split[1]

                if("cpu.time" not in cpu):
                    cpu["cpu.time"] = 0

                cpu_usage[domain] = cpu
        return cpu_usage
    except Exception as e:
        print(f"An error occurred: {e}")
        return False


def calcul_cpu_percentage(initail_time, final_time, interval):
    cpu_percentage = dict()
    interaval_ns = interval*1e9
    
    for domain in initail_time: 
        if domain in final_time:
            initial_cpu_time = int(initail_time[domain]['cpu.time'])
            final_cpu_time = int(final_time[domain]['cpu.time'])
            cpu_time_diff = final_cpu_time - initial_cpu_time
            cpu_percentage[domain] = (cpu_time_diff / interaval_ns) * 100

    return cpu_percentage

def manage_cpu_percentage(dateI, dateF, interval=10):
    actuel_dateTime = datetime.now()
    try:
        initial_dateTime = datetime.strptime(dateI, '%Y-%m-%d %H:%M')   
        final_dateTime = datetime.strptime(dateF, '%Y-%m-%d %H:%M')
        
        if(initial_dateTime < actuel_dateTime or initial_dateTime > final_dateTime):
            raise Exception("dateI > dateF")
    except:
        print("Error. By default, the initial datetime (dateI) is the start of the next hour.")
        initial_dateTime = (datetime.now() + timedelta(hours=1)).replace(minute=0, second=0, microsecond=0)
        final_dateTime = (datetime.now() + timedelta(hours=2)).replace(minute=0, second=0, microsecond=0)

    duration = int((final_dateTime-initial_dateTime).total_seconds())
    if(interval > duration):
        print("Error: interval > duration")
        interval = 10

    while(datetime.now() < initial_dateTime):
        print("***** Waiting *****")
        sleep((initial_dateTime-datetime.now()).total_seconds())

    print("Start")
    d = 0
    
    cpu_percentage = dict()
    cpu_usage_1 = get_all_vms_cpu_usage()
    
    while d < duration:
        sleep(interval*60)
        cpu_usage_2 = get_all_vms_cpu_usage()
        cpu_per = calcul_cpu_percentage(cpu_usage_1, cpu_usage_2, interval)
        
        for domain in cpu_per:
            if(domain in cpu_percentage):
                cpu_percentage[domain].append(cpu_per[domain])
            else:
                cpu_percentage[domain] = [cpu_per[domain]]
        cpu_usage_1 = cpu_usage_2
        d += interval*60

    return cpu_percentage
    
# Run the function
# manage_cpu_percentage("2024-07-15 14:31", "2024-07-15 14:33", 60)

# #Run the function and print the result
# vms_ip_addresses = get_all_vms_ip_addresses()
# vms_cpu = get_all_vms_cpu_usage()
# for domain in vms_cpu:
#     if(domain in vms_ip_addresses):
#         print(vms_ip_addresses[domain])
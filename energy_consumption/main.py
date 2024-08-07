import json
import threading
import modules.manage_tsd_cpuEnergy as manage

def readParams(fileName):
    try:
        with open(fileName, "r") as file:
            data = json.load(file)
            iot_unit = data["iot_unit"]

            plug_ip  = iot_unit["ip"]
            plug_username = iot_unit["plug_username"]
            plug_password = iot_unit["plug_password"]

            tsdb = data["tsdb"]
            url = tsdb["url"]
            org = tsdb["org"]
            tsdb_ip = tsdb["ip"]
            token = tsdb["token"]

            cpu_usage = data["cpu_usage"]["vms"]
        return plug_ip, plug_username, plug_password, cpu_usage, tsdb
    except Exception as e:
        print("Error reading configuration file.")
        print("Check the config file format")
        print(e)
        return False, False, False, False, False

def main():
    plug_ip, plug_username, plug_password, cpu_usage, tsdb = readParams("./configuration/config.json")
    if plug_ip != False:
        if(cpu_usage):
            iot_thread = threading.Thread(target=manage.iot, args=(plug_username, plug_password, plug_ip, tsdb))
            cpu_thread = threading.Thread(target=manage.cpu_tsd, args=(tsdb))

            iot_thread.start()
            cpu_thread.start()

            iot_thread.join()
            cpu_thread.join()
        else:
            manage.iot(plug_username, plug_password, plug_ip, tsdb)
    else:
        print("Exit")

main()
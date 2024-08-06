from flask import Flask, request, jsonify
from flask_cors import CORS
import sys, os
from datetime import datetime
from manage_TSDB import manageEnergyConsumption
# Ajoutez le répertoire parent au chemin
import read_data


app = Flask(__name__)
CORS(app) 
machines_files = '../configuration/server_vms.params'

# Endpoint pour obtenir la liste des serveurs
@app.route('/servers', methods=['GET'])
def get_servers():
    machines = read_data.parse_data(machines_files)
    servers = list(machines.keys())
    results = []
    i = 0
    for server in servers:
        info = server.split('_')
        elm = {
            "id": i,
            "name": info[0],
            "ip": info[1]
        }
        i+=1
        results.append(elm)
    return jsonify(results)

# Endpoint pour obtenir la liste des VMs de plusieurs serveurs spécifiques
@app.route('/vms', methods=['GET'])
def get_vms():
    server_names = request.args.getlist('server')  # Récupérer une liste de noms de serveur
    server_ips = request.args.getlist('ip')  # Récupérer une liste d'adresses IP de serveur
    
    if len(server_names) != len(server_ips):
        return jsonify({'error': 'Mismatch between number of server names and IPs'}), 400
    
    machines = read_data.parse_data(machines_files)
    result = {}

    for server_name, server_ip in zip(server_names, server_ips):
        server_key = f"{server_name}_{server_ip}"
        if server_key in machines:
            result[server_key] = machines[server_key]
        else:
            result[server_key] = {'error': 'Server name and IP not found'}

    return jsonify(result)


# Endpoint pour obtenir la consommation d'énergie journalière
@app.route('/energy', methods=['POST'])
def get_daily_energy():
    print("Hello")
    try:
        request_data = request.json

        dateS = request_data["dateRange"]["start"]
        dateF = request_data["dateRange"]["end"]
        resources = request_data["vms"]
        energy_consumption = manageEnergyConsumption(resources, dateS, dateF)
        print("Energy:", energy_consumption)
    except Exception as e:
        print("Error : ", e)
        energy_consumption = "Error"
    return jsonify(energy_consumption)

if __name__ == '__main__':
    app.run(debug=True)

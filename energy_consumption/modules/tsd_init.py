#Ici c'est la documentation des Time serie data
#y'aura l'installation sur debian, la configuration et l'utilisation, 
#ainsi que toutes les fonctions qui permette d'inserer des donners, de récupèrer des donnée. 
"""
Installation:

wget -q https://repos.influxdata.com/influxdata-archive_compat.key
echo '393e8779c89ac8958f81f942f9ad7fb82a25e133faddaf92e15b16e6ac9ce4c influxdata-archive_compat.key' | sha256sum -c && cat influxdata-archive_compat.key | gpg --dearmor | sudo tee /etc/apt/trusted.gpg.d/influxdata-archive_compat.gpg > /dev/null
echo 'deb [signed-by=/etc/apt/trusted.gpg.d/influxdata-archive_compat.gpg] https://repos.influxdata.com/debian stable main' | sudo tee /etc/apt/sources.list.d/influxdata.list

sudo apt-get update && sudo apt-get install influxdb2
sudo systemctl unmask influxdb.service
sudo systemctl start influxdb


token= btmlphqXfMo7R43O4R9J5Xsdnfx570GdHoXCVcA8vZywrm_2UtHT1BADvN30_tfHCumgeZVQd5F3msgo3UKN9w==


Install Dependencies

First, you need to install the influxdb-client module. Run the command below in your terminal.

    pip3 install influxdb-client


"""
import influxdb_client
import requests
import json

def createBucket(bucketName, url, token, org, saving_time):
    # Créer une instance du client InfluxDB
    client = influxdb_client.InfluxDBClient(url=url, token=token, org=org)
    # Définir les règles de rétention (Conserver les données pendant 1 année)
    retention_rules = influxdb_client.BucketRetentionRules(type="expire", every_seconds=saving_time*24*60*60)  # 30 jours en secondes
    # Nom du bucket à créer
    bucket_name = bucketName
    # Créer le bucket
    buckets_api = client.buckets_api()
    bucket = buckets_api.create_bucket(bucket_name=bucket_name, org=org, retention_rules=retention_rules)
    print(f"Bucket créé : {bucket.name}")


def init_fluxDb(url, org, bucket, password, username):
    # URL de l'API de configuration d'InfluxDB
    url = "http://localhost:8086/api/v2/setup"
    org = "masnssen"
    bucket = "test_bucket"
    password = "massi1482000"
    username = "massi"

    # Données de la requête
    payload = {
        "username": username,
        "password": password,
        "bucket": bucket,
        "org": org
    }

    # Envoyer la requête POST
    response = requests.post(url, json=payload)

    # Vérifier le statut de la réponse
    if response.status_code == 201:
        print("InfluxDB setup completed successfully.")
        print("Response:", response.json())
        token = response.json().get('auth', {}).get('token')
        print(token)
        url = "http://localhost:8086"
        return token
        
    else:
        print(f"Failed to set up InfluxDB: {response.status_code}")
        print("Response:", response.text)
        return False

def readParams(fileName):
    try:
        with open(fileName, "r") as file:
            data = json.load(file)
            tsdb = data["tsdb"]
            url = tsdb["url"]
            org = tsdb["org"]
            bucket = tsdb["bucket"]
            password = tsdb["password"]
            username = tsdb["username"]

            cpu_usage = data["cpu_usage"]["vms"]
        return tsdb, cpu_usage
    except Exception as e:
        print("Error reading configuration file.")
        print("Check the config file format")
        return False

def saveToken(fileName):
    with open(fileName, "r") as file:
        data = json.load(file)

    data["tsdb"]["token"] = "Le token"
    with open(fileName, "w") as file:
        json.dump(data, file, indent=4)


saveToken("../configuration/config.json")

def main():
    tsdb, cpu_usage = readParams("../configuration/config.json")
    if tsdb != False:
        url = tsdb["url"]
        org = tsdb["org"]
        bucket = tsdb["bucket"]
        password = tsdb["password"]
        username = tsdb["username"]
        token = init_fluxDb(url, org, bucket, password, username)
        if(token != False):
            print("Init energy consumprions bucket")
            createBucket("energy_consumptions", url, token, org, 365)
            if(cpu_usage == True):
                print("Init cpu percentages bucket")
                createBucket("cpu_percentages", url, token, org, 365)

            #Save token
                

# main()
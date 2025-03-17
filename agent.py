import psutil
import requests
import time
import json

# configuration 
SERVER_URL = "https://34.139.153.229"
INTERVAL = 5

def get_system_metrics():
    metrics = {
        "cpu": psutil.cpu_percent(interval=1),
        "memory": psutil.virtual_memory().percent,
        "disk": psutil.disk_usage('/').percent,
        "network": psutil.net_io_counters().bytes_sent + psutil.net_io_counters().bytes_recv,
        "temperature": get_temperature()
    }
    return metrics

def get_temperature():
    try:
        temps = psutil.sensors_temperatures()
        if "coretemp" in temps:
            return temps["coretemp"][0].current
        return None
    except AttributeError:
        return None
    
def send_data():
    while True:
        data = get_system_metrics
        try:
            response = requests.post(SERVER_URL, json=data, timeout=5)
            response.raise_for_status()

        except requests.exceptions.RequestException as e:
            print(f'Error sending data: {e}')
        time.sleep(INTERVAL)

if __name__ == "__main__":
    send_data()

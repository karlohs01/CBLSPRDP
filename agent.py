import psutil
import requests
import time
import json

SERVER_URL = "http://34.148.209.117:5000/data"  # Update with your server IP
INTERVAL = 5  # Data collection interval in seconds

def get_system_metrics():
    """Collect system performance metrics."""
    try:
        temperature = get_temperature()
        metrics = {
            "cpu": psutil.cpu_percent(interval=1),
            "memory": psutil.virtual_memory().percent,
            "disk": psutil.disk_usage('/').percent,
            "network": psutil.net_io_counters().bytes_sent + psutil.net_io_counters().bytes_recv,
            "temperature": temperature if temperature is not None else 0.0
        }
        return metrics
    except Exception as e:
        print(f"Error collecting metrics: {e}")
        return {}

def get_temperature():
    """Fetch CPU temperature if available"""
    try:
        temps = psutil.sensors_temperatures()
        if "coretemp" in temps:
            return temps["coretemp"][0].current
    except AttributeError:
        pass
    return None

def send_data():
    """Send metrics to the server."""
    while True:
        data = get_system_metrics()
        if data:
            try:
                response = requests.post(SERVER_URL, json=data, timeout=5)
                response.raise_for_status()
                print(f"Data sent: {data}")
            except requests.exceptions.RequestException as e:
                print(f"Error sending data: {e}")
        time.sleep(INTERVAL)

if __name__ == "__main__":
    send_data()

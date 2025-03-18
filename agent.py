import psutil
import os
import json
import time
import requests

SERVER_URL = "http://35.227.126.36:5000/data"  # Dashboard URL
PIPE_PATH = "/tmp/perf_metrics"
INTERVAL = 5

def get_system_metrics():
    """Collect system performance metrics."""
    temperature = get_temperature()
    metrics = {
        "cpu": psutil.cpu_percent(interval=1),
        "memory": psutil.virtual_memory().percent,
        "disk": psutil.disk_usage('/').percent,
        "network": psutil.net_io_counters().bytes_sent + psutil.net_io_counters().bytes_recv,
        "temperature": temperature if temperature is not None else 0.0
    }
    return metrics

def get_temperature():
    """Fetch CPU temperature if available."""
    try:
        temps = psutil.sensors_temperatures()
        if "coretemp" in temps:
            return temps["coretemp"][0].current
        return None
    except AttributeError:
        return None

def setup_named_pipe():
    """Create a named pipe (FIFO) if it doesn't exist."""
    if not os.path.exists(PIPE_PATH):
        os.mkfifo(PIPE_PATH)

def write_to_pipe(data):
    """Write system metrics to the named pipe."""
    with open(PIPE_PATH, "w") as pipe:
        pipe.write(json.dumps(data) + "\n")

def send_data(data):
    """Send system metrics to the dashboard via HTTP."""
    try:
        response = requests.post(SERVER_URL, json=data, timeout=5)
        response.raise_for_status()
        print(f"Data sent: {data}")
    except requests.exceptions.RequestException as e:
        print(f"Error sending data: {e}")

def main():
    setup_named_pipe()
    while True:
        metrics = get_system_metrics()
        write_to_pipe(metrics)  # Write to pipe (for local debugging)
        send_data(metrics)  # Send data to dashboard
        time.sleep(INTERVAL)

if __name__ == "__main__":
    main()

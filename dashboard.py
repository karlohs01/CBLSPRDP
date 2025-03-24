import tkinter as tk
from tkinter import messagebox
import requests
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import threading
import time

SERVER_URL = "http://104.196.136.236:5000/metrics"
REFRESH_INTERVAL = 5  # Refresh rate in seconds

# Default threshold values
thresholds = {
    "cpu": 80,
    "memory": 80,
    "disk": 90,
    "network": 50000000,  # 50MB threshold
    "temperature": 80
}

# Store historical data for plotting
history = {
    "cpu": [],
    "memory": [],
    "disk": [],
    "network": [],
    "temperature": []
}

def fetch_data():
    """Fetch system metrics from the server."""
    try:
        response = requests.get(SERVER_URL)
        response.raise_for_status()
        data = response.json()

        # Validate that data is not empty
        if not data:
            print("No data received from the server.")
            return {}

        # Ensure data contains at least one valid entry
        if not isinstance(data, list) or len(data) == 0:
            print("Invalid or empty data format.")
            return {}

        # Extract the latest metrics and convert to dictionary
        result = {key: data[-1][key] for key in data[0]}
        return result

    except requests.RequestException as e:
        print(f"Error fetching data: {e}")
        return {}
    except (IndexError, KeyError) as e:
        print(f"Data processing error: {e}")
        return {}



def update_graphs(data):
    """Update the graphs with new data."""
    if not data:
        return

    # Check if data is a dictionary
    if isinstance(data, dict):
        for key in history:
            if key in data:
                history[key].append(data[key])
                if len(history[key]) > 20:  # Limit history to 20 points
                    history[key].pop(0)
            else:
                print(f"Warning: Key '{key}' not found in data")
    else:
        print(f"Unexpected data format: {type(data)} - {data}")
        return

    # Update the graphs
    for key, ax in graph_axes.items():
        ax.clear()
        ax.plot(history[key], label=key.capitalize(), color="blue")
        ax.axhline(y=thresholds.get(key, 0), color="red", linestyle="--", label="Threshold")
        ax.legend()

    canvas.draw()

def check_thresholds(data):
    """Check if any metric exceeds the threshold and trigger alerts."""
    for metric, value in data.items():
        if isinstance(data, dict) and data:  # Ensure it's a dictionary and not empty
            if value > thresholds.get(metric, float('inf')):
                messagebox.showwarning(
                    "Threshold Exceeded",
                    f"{metric.capitalize()} is at {value}% (Threshold: {thresholds[metric]}%)"
                )

def update_dashboard():
    """Continuously fetch data, update graphs, and check thresholds."""
    while True:
        data = fetch_data()
        if data:
            update_graphs(data)
            check_thresholds(data)
        time.sleep(REFRESH_INTERVAL)

def set_thresholds():
    """Update threshold values based on user input."""
    for metric, entry in threshold_entries.items():
        try:
            new_value = float(entry.get())
            if new_value <= 0:
                raise ValueError
            thresholds[metric] = new_value
        except ValueError:
            messagebox.showerror("Invalid Input", f"Please enter a valid number for {metric.capitalize()} threshold.")
    update_graphs()


# GUI Setup
root = tk.Tk()
root.title("Performance Monitoring Dashboard")
root.geometry("900x500")  # Adjusted size for side panel

# Create main layout frames
main_frame = tk.Frame(root)
main_frame.pack(fill="both", expand=True, padx=10, pady=10)

graph_frame = tk.Frame(main_frame)
graph_frame.pack(side="left", fill="both", expand=True)

panel_frame = tk.Frame(main_frame, width=200, padx=10, pady=10, relief=tk.RIDGE, borderwidth=2)
panel_frame.pack(side="right", fill="y")

# Matplotlib figure for graphs
fig, axes = plt.subplots(nrows=5, ncols=1, figsize=(6, 8))
graph_axes = {metric: ax for metric, ax in zip(thresholds.keys(), axes)}

canvas = FigureCanvasTkAgg(fig, master=graph_frame)
canvas.get_tk_widget().pack()

# Panel for threshold adjustment controls
threshold_entries = {}
tk.Label(panel_frame, text="Adjust Thresholds", font=("Arial", 12, "bold")).pack(pady=5)

for metric, default_value in thresholds.items():
    tk.Label(panel_frame, text=f"{metric.capitalize()} Threshold:").pack()
    entry = tk.Entry(panel_frame, width=10)
    entry.insert(0, str(default_value))
    entry.pack(pady=5)
    threshold_entries[metric] = entry

set_button = tk.Button(panel_frame, text="Set Thresholds", command=set_thresholds)
set_button.pack(pady=10)

# Start data fetch thread
thread = threading.Thread(target=update_dashboard, daemon=True)
thread.start()

root.mainloop()

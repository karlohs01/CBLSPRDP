import tkinter as tk
from tkinter import messagebox
import requests
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import threading
import time

SERVER_URL = "http://35.227.126.36:5000/data"
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
    """Fetch performance data from the agent."""
    try:
        response = requests.get(SERVER_URL, timeout=5)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        return None

def update_graphs(data):
    """Update the graphs with new data."""
    if not data:
        return

    for key in history:
        history[key].append(data[key])
        if len(history[key]) > 20:  # Limit history to 20 points
            history[key].pop(0)

    for key, ax in graph_axes.items():
        ax.clear()
        ax.plot(history[key], label=key.capitalize(), color="blue")
        ax.axhline(y=thresholds[key], color="red", linestyle="--", label="Threshold")
        ax.legend()

    canvas.draw()

def check_thresholds(data):
    """Check if any metric exceeds the threshold and trigger alerts."""
    for metric, value in data.items():
        if value > thresholds[metric]:
            messagebox.showwarning("Threshold Exceeded", f"{metric.capitalize()} is at {value}% (Threshold: {thresholds[metric]}%)")

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
            thresholds[metric] = float(entry.get())
        except ValueError:
            messagebox.showerror("Invalid Input", f"Please enter a valid number for {metric.capitalize()} threshold.")

class ScrollableFrame(tk.Frame):
    def __init__(self, container, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        canvas = tk.Canvas(self)
        scrollbar = tk.Scrollbar(self, orient="vertical", command=canvas.yview)
        self.scrollable_frame = tk.Frame(canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

# GUI setup
root = tk.Tk()
root.title("Performance Monitoring Dashboard")
root.geometry("700x400")

# creating mpl figure for the graphs
fig, axes = plt.subplots(nrows=5, ncols=1, figsize=(6, 8))
graph_axes = {
    "cpu": axes[0],
    "memory": axes[1],
    "disk": axes[2],
    "network": axes[3],
    "temperature": axes[4],
}

canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().pack()

# creating scrollable frame for threshold adjustment and other controls
scroll_frame = ScrollableFrame(root)
scroll_frame.pack(fill="both", expand=True)

threshold_entries = {}
for metric, default_value in thresholds.items():
    lbl = tk.Label(scroll_frame.scrollable_frame, text=f"{metric.capitalize()} Threshold:")
    lbl.pack(pady=(10, 0))
    entry = tk.Entry(scroll_frame.scrollable_frame)
    entry.insert(0, str(default_value))
    entry.pack(pady=(0, 10))
    threshold_entries[metric] = entry

set_button = tk.Button(scroll_frame.scrollable_frame, text="Set Thresholds", command=set_thresholds)
set_button.pack(pady=10)

# starting data fetch thread
thread = threading.Thread(target=update_dashboard, daemon=True)
thread.start()

root.mainloop()

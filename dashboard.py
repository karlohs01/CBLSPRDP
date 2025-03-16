import tkinter as tk
from tkinter import messagebox
import requests
import threading
import json
import time
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


# configuration
PORT = 5000
THRESHOLDS = {"cpu": 80, "memory": 80, "disk": 90, "temperature": 75}

# data log to store received data
data_log = [] 

# function to start server
def start_server():
    from flask import Flask, request
    app = Flask(__name__)

    @app.route('/data', methods=['POST'])
    def receive_data():
        data = request.get_json()
        data_log.append(data)
        check_thresholds(data)
        return "received", 200
    
    app.run(host='0.0.0.0', port=PORT)
# checking thresholds and displaying warning message if thresholds are surpassed
def check_thresholds():
    for key, value in THRESHOLDS.items():
        if key in data and data[key] > value:
            messagebox.showwarning("Alert", f"{key.upper()} exceeded threshold! ({data[key]}%")

def update_graph():
    fig, ax = plt.subplots()
    ax.clear()
    metrics = ["cpu", "memory", "disk", "temperature"]
    for metric in metrics:
        values = [entry[metric] for entry in data_log[-50:]] # last 50 data points
        ax.plot(values, label=metric)
    ax.legend()
    canvas.draw()
    root.after(5000, update_graph)

# starting the flask server in a separate thread
server_thread = threading.Thread(target=start_server, daemon=True)
server_thread.start()

# GUI setup
root = tk.Tk()
root.title("Server Performance Monitor")
root.geometry("600x400")

canvas_frame = tk.Frame(root)
canvas_frame.pack()
fig, ax = plt.subplots()
canvas = FigureCanvasTkAgg(fig, master=canvas_frame)
canvas.get_tk_widget().pack()

update_graph()
root.mainloop()

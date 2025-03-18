from flask import Flask, request, render_template, jsonify
import plotly.graph_objs as go
from collections import deque

app = Flask(__name__)

# Store the last 20 data points for graphing
history = {
    "cpu": deque(maxlen=20),
    "memory": deque(maxlen=20),
    "disk": deque(maxlen=20),
    "network": deque(maxlen=20),
    "temperature": deque(maxlen=20)
}

# Default thresholds
thresholds = {
    "cpu": 80,
    "memory": 80,
    "disk": 90,
    "network": 50000000,
    "temperature": 80
}

@app.route('/')
def index():
    return render_template('dashboard.html', thresholds=thresholds)

@app.route('/data', methods=['POST'])
def receive_data():
    """Receive data from the agent and store it."""
    data = request.json
    for key in history:
        history[key].append(data[key])

    # Check if any metric exceeds the threshold
    exceeded = {k: v for k, v in data.items() if v > thresholds[k]}
    return jsonify({"status": "success", "exceeded": exceeded})

@app.route('/metrics')
def get_metrics():
    """Send historical data to update the dashboard."""
    return jsonify({k: list(v) for k, v in history.items()})

@app.route('/set_thresholds', methods=['POST'])
def set_thresholds():
    """Update threshold values based on user input."""
    global thresholds
    thresholds = request.json
    return jsonify({"status": "Thresholds updated!"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

from flask import Flask, request, jsonify

app = Flask(__name__)
metrics_data = []

@app.route('/data', methods=['POST'])
def receive_data():
    """Receive data from the agent."""
    data = request.json
    metrics_data.append(data)
    print(f"Received data: {data}")
    return jsonify({"message": "Data received"}), 200

@app.route('/metrics', methods=['GET'])
def get_metrics():
    """Retrieve all collected metrics."""
    return jsonify(metrics_data)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

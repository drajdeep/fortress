from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import json
import time

app = Flask(__name__)

UPLOAD_FOLDER = './uploads'  # Folder to save uploaded files
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Pointer to track which entries have been sent
data_pointer = 0

# Threshold for packet rate (PPS)
PACKET_RATE_THRESHOLD = 100  # Packets per second

# Function to calculate packet rate
def calculate_packet_rate():
    # This is a placeholder for the actual logic to calculate PPS
    # In your real application, this would come from the packet sniffing logic
    # For this example, we're just simulating a PPS value
    pps = 50 # Simulated PPS for demonstration
    return pps

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return "No file part", 400
    
    file = request.files['file']
    if file.filename == '':
        return "No selected file", 400
    
    # Save the file to the server
    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)

    # Get the packet rate (PPS) and check against the threshold
    pps = calculate_packet_rate()

    # Determine if the packet rate exceeds the threshold
    flag = False if pps > PACKET_RATE_THRESHOLD else True

    # Get the current timestamp
    timestamp = time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime())

    # Prepare the data to be logged
    data = {
        "timestamp": timestamp,
        "packet_rate": pps,
        "exceeds_limit": flag
    }

    # Save this data to the JSON file
    json_filename = os.path.join(UPLOAD_FOLDER, "packet_rate.json")

    # Load existing data from JSON if the file exists
    if os.path.exists(json_filename):
        with open(json_filename, 'r') as f:
            try:
                existing_data = json.load(f)
            except json.JSONDecodeError:
                existing_data = []
    else:
        existing_data = []

    # Append the new data to the existing data
    existing_data.append(data)

    # Save updated data back to the JSON file
    with open(json_filename, 'w') as f:
        json.dump(existing_data, f, indent=4)

    return f"File {file.filename} uploaded successfully with packet rate data", 200

@app.route('/fetch', methods=['GET'])
def fetch_data():
    global data_pointer
    
    # The JSON file is expected to be uploaded
    json_filename = os.path.join(UPLOAD_FOLDER, "packet_rate.json")
    
    if not os.path.exists(json_filename):
        return "No data file found", 404
    
    # Load the JSON data from the file
    with open(json_filename, 'r') as f:
        data = json.load(f)
    
    # Fetch the next 10 entries starting from the current pointer
    batch_data = data[data_pointer:data_pointer + 10]
    
    # Update the pointer to send the next 10 entries next time
    data_pointer += 10
    
    if len(batch_data) == 0:
        return "No more data available", 404

    return jsonify(batch_data), 200

if __name__ == "__main__":
    CORS(app)
    app.run(host="0.0.0.0", port=5000)  # Accessible on the local network

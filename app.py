from flask import Flask, jsonify, request
from flask_cors import CORS
import time
import threading

app = Flask(__name__)
CORS(app)

# Store traffic data
traffic_data = {
    "north": 0,
    "east": 0,
    "south": 0,
    "west": 0,
    "timestamp": time.time(),
    "ai_active": False,
    "simulation_active": False,
    "snapshot": None
}

# Simulation settings
SIMULATION_SETTINGS = {
    "vehicle_time": 3,  # 3 seconds per vehicle
    "green_time_base": 20,
    "green_time_per_vehicle": 2,
    "emergency_priority": True
}

@app.route("/")
def home():
    return """
    <h1>🚦 Smart Traffic Backend API</h1>
    <p>Real-time AI Traffic Management System</p>
    <p><b>Design Principle:</b></p>
    <ul>
        <li>AI continuously monitors traffic (3s/vehicle)</li>
        <li>Dashboard captures snapshots for simulation</li>
        <li>Simulation uses captured snapshot data</li>
        <li>AI continues independent data collection</li>
    </ul>
    """

@app.route("/traffic", methods=["GET"])
def get_traffic():
    """Get current traffic data"""
    return jsonify({
        **traffic_data,
        "settings": SIMULATION_SETTINGS,
        "simulation_ready": traffic_data["snapshot"] is not None
    })

@app.route("/update", methods=["POST"])
def update_traffic():
    """AI updates traffic data continuously"""
    try:
        data = request.json
        
        # Update traffic counts
        traffic_data["north"] = data.get("north", traffic_data["north"])
        traffic_data["east"] = data.get("east", traffic_data["east"])
        traffic_data["south"] = data.get("south", traffic_data["south"])
        traffic_data["west"] = data.get("west", traffic_data["west"])
        traffic_data["timestamp"] = time.time()
        traffic_data["ai_active"] = True
        traffic_data["simulation_active"] = data.get("simulation_active", False)
        
        print(f"📈 AI Update: N={traffic_data['north']}, E={traffic_data['east']}, S={traffic_data['south']}, W={traffic_data['west']}")
        return {"status": "success", "message": "Traffic data updated"}
    
    except Exception as e:
        return {"status": "error", "message": str(e)}, 400

@app.route("/snapshot", methods=["POST"])
def capture_snapshot():
    """Capture snapshot for simulation"""
    try:
        data = request.json
        
        snapshot = {
            "north": data.get("north", 0),
            "east": data.get("east", 0),
            "south": data.get("south", 0),
            "west": data.get("west", 0),
            "capture_time": data.get("capture_time", time.time()),
            "simulation_started": data.get("simulation_started", False)
        }
        
        traffic_data["snapshot"] = snapshot
        traffic_data["simulation_active"] = snapshot["simulation_started"]
        
        print("\n" + "="*50)
        print("📸 SIMULATION SNAPSHOT CAPTURED")
        print(f"North: {snapshot['north']} | East: {snapshot['east']}")
        print(f"South: {snapshot['south']} | West: {snapshot['west']}")
        print(f"Simulation Started: {snapshot['simulation_started']}")
        print("="*50)
        
        return {
            "status": "success",
            "message": "Snapshot captured for simulation",
            "snapshot": snapshot
        }
        
    except Exception as e:
        return {"status": "error", "message": str(e)}, 400

@app.route("/start_simulation", methods=["POST"])
def start_simulation():
    """Start simulation with current snapshot"""
    try:
        if not traffic_data["snapshot"]:
            return {"status": "error", "message": "No snapshot available"}, 400
        
        traffic_data["simulation_active"] = True
        
        # Calculate green times based on snapshot (3 seconds per vehicle)
        snapshot = traffic_data["snapshot"]
        
        # Green time = base + (vehicles * 3 seconds per vehicle)
        green_times = {
            "north": SIMULATION_SETTINGS["green_time_base"] + (snapshot["north"] * SIMULATION_SETTINGS["vehicle_time"]),
            "east": SIMULATION_SETTINGS["green_time_base"] + (snapshot["east"] * SIMULATION_SETTINGS["vehicle_time"]),
            "south": SIMULATION_SETTINGS["green_time_base"] + (snapshot["south"] * SIMULATION_SETTINGS["vehicle_time"]),
            "west": SIMULATION_SETTINGS["green_time_base"] + (snapshot["west"] * SIMULATION_SETTINGS["vehicle_time"])
        }
        
        print("\n" + "="*50)
        print("🚦 SIMULATION STARTED")
        print(f"Using snapshot from: {time.ctime(snapshot['capture_time'])}")
        print(f"Green Times: N={green_times['north']}s, E={green_times['east']}s")
        print(f"              S={green_times['south']}s, W={green_times['west']}s")
        print("="*50)
        
        return {
            "status": "success",
            "message": "Simulation started with snapshot data",
            "snapshot": snapshot,
            "green_times": green_times,
            "vehicle_rate": f"{SIMULATION_SETTINGS['vehicle_time']}s per vehicle"
        }
        
    except Exception as e:
        return {"status": "error", "message": str(e)}, 400

@app.route("/stop_simulation", methods=["POST"])
def stop_simulation():
    """Stop simulation"""
    traffic_data["simulation_active"] = False
    return {"status": "success", "message": "Simulation stopped"}

@app.route("/status", methods=["GET"])
def status():
    """Get system status"""
    return jsonify({
        "ai_active": traffic_data["ai_active"],
        "simulation_active": traffic_data["simulation_active"],
        "has_snapshot": traffic_data["snapshot"] is not None,
        "last_update": traffic_data["timestamp"],
        "vehicle_rate": f"{SIMULATION_SETTINGS['vehicle_time']}s per vehicle",
        "design": "AI collects continuously | Simulation uses snapshots"
    })

if __name__ == "__main__":
    print("="*60)
    print("🚀 SMART TRAFFIC BACKEND API")
    print("="*60)
    print("📡 API URL: http://localhost:5000")
    print("🤖 AI Updates: POST /update (continuous)")
    print("📸 Snapshots: POST /snapshot (for simulation)")
    print("🚦 Simulation: POST /start_simulation")
    print("")
    print("📊 System Design:")
    print("  • AI runs continuously (3s/vehicle rate)")
    print("  • Dashboard captures snapshots")
    print("  • Simulation uses captured snapshot data")
    print("  • AI continues independent data collection")
    print("="*60)
    
    app.run(debug=True, port=5000, use_reloader=False)
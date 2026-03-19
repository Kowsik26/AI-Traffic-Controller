from ultralytics import YOLO
import cv2
import time
import requests
import random

# ===============================
# CONFIGURATION
# ===============================
VIDEO_PATH = r"C:\Users\Hp\Desktop\Smart_Traffic_AI\data\traffic.mp4"
BACKEND_URL = "http://localhost:5000"
VEHICLE_TIME = 3  # Seconds per vehicle (3 seconds per vehicle)

# ===============================
# LOAD YOLO MODEL
# ===============================
model = YOLO("yolov8n.pt")
print("✅ YOLO Model Loaded")

# ===============================
# GLOBAL VARIABLES
# ===============================
vehicle_count = 0
simulation_snapshot = {"north": 0, "east": 0, "south": 0, "west": 0}
is_simulation_active = False
last_snapshot_time = 0

# ===============================
# BACKEND COMMUNICATION FUNCTIONS
# ===============================
def send_traffic_update():
    """Send current traffic data to backend"""
    try:
        # Get current counts
        north_count = vehicle_count
        east_count = random.randint(max(3, north_count-5), north_count+2)
        south_count = random.randint(max(2, north_count-6), north_count+1)
        west_count = random.randint(max(4, north_count-4), north_count+3)
        
        # Calculate time-based increment (3 seconds per vehicle)
        current_time = time.time()
        time_elapsed = current_time - last_snapshot_time if last_snapshot_time > 0 else 0
        
        # Simulate realistic traffic growth
        if time_elapsed > 1:  # Only update if significant time passed
            time_factor = int(time_elapsed / VEHICLE_TIME)  # How many vehicles per time
            north_count += time_factor
            east_count = int(north_count * 0.8)
            south_count = int(north_count * 0.6)
            west_count = int(north_count * 0.7)
        
        data = {
            "north": north_count,
            "east": east_count,
            "south": south_count,
            "west": west_count,
            "timestamp": current_time,
            "simulation_active": is_simulation_active
        }
        
        # Send to backend
        response = requests.post(
            f"{BACKEND_URL}/update",
            json=data,
            timeout=2
        )
        
        if response.status_code == 200:
            print(f"📊 Traffic Update: N={north_count}, E={east_count}, S={south_count}, W={west_count}")
            
        return data
        
    except Exception as e:
        print(f"⚠️  Backend Update Failed: {e}")
        return None

def capture_snapshot():
    """Capture current traffic snapshot for simulation"""
    global simulation_snapshot, last_snapshot_time, vehicle_count
    
    north_count = vehicle_count
    east_count = random.randint(max(3, north_count-5), north_count+2)
    south_count = random.randint(max(2, north_count-6), north_count+1)
    west_count = random.randint(max(4, north_count-4), north_count+3)
    
    simulation_snapshot = {
        "north": north_count,
        "east": east_count,
        "south": south_count,
        "west": west_count,
        "capture_time": time.time()
    }
    
    last_snapshot_time = time.time()
    
    print("\n" + "="*50)
    print("📸 SIMULATION SNAPSHOT CAPTURED")
    print("="*50)
    print(f"North Road: {north_count} vehicles")
    print(f"East Road:  {east_count} vehicles")
    print(f"South Road: {south_count} vehicles")
    print(f"West Road:  {west_count} vehicles")
    print("="*50)
    
    # Send snapshot to backend
    try:
        snapshot_data = {
            **simulation_snapshot,
            "is_snapshot": True,
            "simulation_started": True
        }
        requests.post(f"{BACKEND_URL}/snapshot", json=snapshot_data, timeout=2)
    except:
        pass
    
    return simulation_snapshot

# ===============================
# AI DETECTION MAIN FUNCTION
# ===============================
def run_ai_detection():
    """Main AI vehicle detection loop"""
    global vehicle_count, is_simulation_active
    
    # Local variables for tracking (FIXED THE ERROR HERE)
    counted_ids = set()
    previous_positions = {}      # track_id : previous center y
    recently_counted = {}        # track_id : last_seen_time
    COOLDOWN_TIME = 3            # seconds
    
    cap = cv2.VideoCapture(VIDEO_PATH)
    if not cap.isOpened():
        print("❌ Cannot open video file")
        return
    
    # Setup display window
    cv2.namedWindow("AI Traffic Detection", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("AI Traffic Detection", 540, 960)
    
    print("\n🚀 AI Detection Started")
    print("📹 Processing video...")
    print("📡 Sending data to backend every 5 seconds")
    print("📸 Press 'C' to capture simulation snapshot")
    print("⏹️  Press ESC to exit\n")
    
    last_update_time = time.time()
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        
        # Resize frame
        frame = cv2.resize(frame, (540, 960))
        height, width, _ = frame.shape
        
        # Draw counting zone
        zone_top = int(height * 0.65)
        zone_bottom = int(height * 0.85)
        cv2.rectangle(frame, (0, zone_top), (width, zone_bottom), (255, 0, 0), 2)
        
        # YOLO detection
        results = model.track(
            frame,
            persist=True,
            tracker="bytetrack.yaml",
            classes=[2, 3, 5, 7],
            conf=0.30,
            iou=0.5,
            verbose=False
        )
        
        current_time = time.time()
        
        # Clean old cooldown entries
        recently_counted = {
            k: v for k, v in recently_counted.items()
            if current_time - v < COOLDOWN_TIME
        }
        
        # Process detections
        if results and results[0].boxes.id is not None:
            boxes = results[0].boxes.xyxy
            ids = results[0].boxes.id
            
            for box, track_id in zip(boxes, ids):
                track_id = int(track_id)
                x1, y1, x2, y2 = map(int, box)
                cx = (x1 + x2) // 2
                cy = (y1 + y2) // 2
                
                # Filter noise
                box_area = (x2 - x1) * (y2 - y1)
                if box_area < 900:
                    continue
                
                # Draw detection
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.circle(frame, (cx, cy), 4, (0, 0, 255), -1)
                
                # Counting logic
                prev_cy = previous_positions.get(track_id, None)
                previous_positions[track_id] = cy
                
                if prev_cy is not None:
                    if prev_cy < zone_top and zone_top <= cy <= zone_bottom:
                        if track_id not in counted_ids and track_id not in recently_counted:
                            vehicle_count += 1
                            counted_ids.add(track_id)
                            recently_counted[track_id] = current_time
        
        # Send updates every 5 seconds
        if current_time - last_update_time > 5:
            send_traffic_update()
            last_update_time = current_time
        
        # Display info
        cv2.putText(frame, f"AI Detection: ACTIVE", (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
        cv2.putText(frame, f"Vehicles: {vehicle_count}", (20, 80),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
        cv2.putText(frame, f"Rate: ~{VEHICLE_TIME}s/vehicle", (20, 120),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
        cv2.putText(frame, f"Simulation: {'ACTIVE' if is_simulation_active else 'READY'}", (20, 160),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255) if is_simulation_active else (200, 200, 200), 2)
        cv2.putText(frame, "Press 'C' for snapshot | ESC to exit", (20, 200),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        cv2.imshow("AI Traffic Detection", frame)
        
        # Key controls
        key = cv2.waitKey(1) & 0xFF
        if key == 27:  # ESC
            break
        elif key == ord('c') or key == ord('C'):  # Capture snapshot
            capture_snapshot()
    
    cap.release()
    cv2.destroyAllWindows()
    
    print("\n" + "="*50)
    print("AI DETECTION STOPPED")
    print(f"Total Vehicles Detected: {vehicle_count}")
    print("="*50)

# ===============================
# MAIN EXECUTION
# ===============================
if __name__ == "__main__":
    print("="*50)
    print("🤖 SMART TRAFFIC AI DETECTION SYSTEM")
    print("="*50)
    print(f"Vehicle Rate: {VEHICLE_TIME} seconds per vehicle")
    print("AI runs continuously in background")
    print("Dashboard captures snapshots for simulation")
    print("="*50)
    
    run_ai_detection()
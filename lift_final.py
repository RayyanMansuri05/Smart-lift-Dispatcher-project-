import cv2
import requests
import base64
import pyttsx3
import time

# --- INITIALIZE ---
try:
    engine = pyttsx3.init()
    engine.setProperty('rate', 150)
except:
    engine = None

cap = cv2.VideoCapture(0)

# --- CONFIGURATION ---
API_KEY = "2z65F5xztTwfhUH6Ox2K"
MODEL_ID = "my-first-project-silig/6"
URL = f"https://detect.roboflow.com/{MODEL_ID}?api_key={API_KEY}&confidence=20"

FLOOR_MAP = {"fist hand": "G", "1st floor": "1", "two_fingers": "2", "3rd floor": "3", "changing postion": "4", "five_fingers": "5"}
FLOOR_Y = {"G": 400, "1": 340, "2": 280, "3": 220, "4": 160, "5": 100}

current_floor = "G"
target_y = FLOOR_Y["G"]
anim_y = FLOOR_Y["G"]
status_msg = "SYSTEM READY"

while True:
    ret, frame = cap.read()
    if not ret: break

    # OPTIMIZATION: Resize frame for Hotspot (saves 70% data)
    small_frame = cv2.resize(frame, (416, 416))
    _, buffer = cv2.imencode('.jpg', small_frame, [int(cv2.IMWRITE_JPEG_QUALITY), 70])
    img_base64 = base64.b64encode(buffer).decode('utf-8')
    
    try:
        # Increase timeout slightly for Hotspot stability
        response = requests.post(URL, data=img_base64, headers={'Content-Type': 'application/x-www-form-urlencoded'}, timeout=2.0)
        preds = response.json().get('predictions', [])
        
        if preds:
            status_msg = "AI TRACKING ACTIVE"
            for p in preds:
                label = p['class'].lower().strip()
                # Draw box for EVERYTHING (Red)
                x, y, w, h = int(p['x'] * (frame.shape[1]/416)), int(p['y'] * (frame.shape[0]/416)), int(p['width'] * (frame.shape[1]/416)), int(p['height'] * (frame.shape[0]/416))
                cv2.rectangle(frame, (x-w//2, y-h//2), (x+w//2, y+h//2), (0, 0, 255), 2)
                
                if label in FLOOR_MAP:
                    detected = FLOOR_MAP[label]
                    if detected != current_floor:
                        current_floor = detected
                        target_y = FLOOR_Y[current_floor]
                        if engine: engine.say(f"Going to {current_floor}"); engine.runAndWait()
        else:
            status_msg = "SCANNING FOR GESTURES..."
    except:
        status_msg = "HOTSPOT MODE: MANUAL ACTIVE"

    # KEYBOARD FAIL-SAFE
    key = cv2.waitKey(1) & 0xFF
    manual_keys = {ord('1'):'1', ord('2'):'2', ord('3'):'3', ord('4'):'4', ord('g'):'G'}
    if key in manual_keys:
        current_floor = manual_keys[key]
        target_y = FLOOR_Y[current_floor]
        status_msg = "MANUAL OVERRIDE"
        if engine: engine.say(f"Floor {current_floor}"); engine.runAndWait()

    # ANIMATION ENGINE
    if abs(anim_y - target_y) > 2:
        anim_y += 6 if anim_y < target_y else -6

    # --- DASHBOARD UI ---
    # Dark Side Panel
    overlay = frame.copy()
    cv2.rectangle(overlay, (0, 0), (240, 480), (25, 25, 25), -1)
    frame = cv2.addWeighted(overlay, 0.8, frame, 0.2, 0)
    
    # Lift Shaft & Markers
    cv2.line(frame, (120, 100), (120, 400), (80, 80, 80), 2)
    for f, y_p in FLOOR_Y.items():
        color = (0, 255, 0) if f == current_floor else (200, 200, 200)
        cv2.putText(frame, f, (80, y_p+5), 0, 0.6, color, 2 if f == current_floor else 1)
        cv2.circle(frame, (120, y_p), 5, color, -1)

    # Moving Green Lift Box
    cv2.rectangle(frame, (100, int(anim_y)-15), (140, int(anim_y)+15), (0, 255, 0), -1)
    
    # Text Dashboard
    cv2.putText(frame, status_msg, (10, 30), 0, 0.5, (0, 255, 255), 1)
    cv2.putText(frame, f"FLOOR: {current_floor}", (20, 450), 0, 1.2, (0, 255, 0), 2)

    cv2.imshow("SMART LIFT V6 - DEMO MODE", frame)
    if key == ord('q'): break

cap.release()
cv2.destroyAllWindows()
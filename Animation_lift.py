import cv2
import requests
import base64
import pyttsx3
import time

# --- 1. INITIALIZE ---
engine = pyttsx3.init()
engine.setProperty('rate', 150)
cap = cv2.VideoCapture(0)

API_KEY = "2z65F5xztTwfhUH6Ox2K"
MODEL_ID = "my-first-project-silig/6"
URL = f"https://detect.roboflow.com/{MODEL_ID}?api_key={API_KEY}&confidence=20"

FLOOR_MAP = {"fist hand": "G", "1st floor": "1", "two_fingers": "2", "3rd floor": "3", "changing postion": "4", "five_fingers": "5"}
# Vertical positions for the animation (G is at bottom, 5 is at top)
FLOOR_Y = {"G": 400, "1": 340, "2": 280, "3": 220, "4": 160, "5": 100}

current_floor = "G"
target_y = FLOOR_Y["G"]
anim_y = FLOOR_Y["G"] # Current position of the moving bar
last_voice_time = 0

while True:
    ret, frame = cap.read()
    if not ret: break

    # AI Detection Logic
    _, buffer = cv2.imencode('.jpg', frame)
    img_base64 = base64.b64encode(buffer).decode('utf-8')
    try:
        response = requests.post(URL, data=img_base64, headers={'Content-Type': 'application/x-www-form-urlencoded'}, timeout=0.5)
        predictions = response.json().get('predictions', [])
        gestures = [p for p in predictions if p['class'].lower() in FLOOR_MAP]
        if gestures:
            best = max(gestures, key=lambda x: x['confidence'])
            detected = FLOOR_MAP[best['class'].lower()]
            if detected != current_floor:
                current_floor = detected
                target_y = FLOOR_Y[current_floor]
                engine.say(f"Going to floor {current_floor}"); engine.runAndWait()
    except: pass

    # Keyboard Backup
    key = cv2.waitKey(1) & 0xFF
    manual_keys = {ord('1'):'1', ord('2'):'2', ord('3'):'3', ord('4'):'4', ord('g'):'G'}
    if key in manual_keys:
        current_floor = manual_keys[key]
        target_y = FLOOR_Y[current_floor]
        engine.say(f"Floor {current_floor} selected"); engine.runAndWait()

    # --- ANIMATION ENGINE ---
    # Smoothly move anim_y toward target_y
    if anim_y > target_y: anim_y -= 5  # Moving Up
    if anim_y < target_y: anim_y += 5  # Moving Down

    # --- ADVANCED DASHBOARD UI ---
    # 1. Background Sidebar
    cv2.rectangle(frame, (0, 0), (200, 480), (30, 30, 30), -1)
    
    # 2. Draw the "Lift Shaft" (Vertical Line)
    cv2.line(frame, (100, 100), (100, 400), (100, 100, 100), 2)
    
    # 3. Draw Floor Markers
    for f, y_pos in FLOOR_Y.items():
        cv2.putText(frame, f, (70, y_pos+5), 0, 0.5, (200, 200, 200), 1)
        cv2.circle(frame, (100, y_pos), 3, (150, 150, 150), -1)

    # 4. Draw the Moving "Lift Car" (Green Box)
    cv2.rectangle(frame, (85, int(anim_y)-15), (115, int(anim_y)+15), (0, 255, 0), -1)
    cv2.putText(frame, "LIFT", (110, int(anim_y)+5), 0, 0.4, (0, 255, 0), 1)

    # 5. Status Display
    cv2.putText(frame, "SMART LIFT V6", (20, 40), 0, 0.6, (255, 255, 255), 1)
    cv2.putText(frame, f"FLOOR: {current_floor}", (20, 450), cv2.FONT_HERSHEY_DUPLEX, 0.8, (0, 255, 0), 2)

    cv2.imshow("Smart Lift - Interactive Dashboard", frame)
    if key == ord('q'): break

cap.release()
cv2.destroyAllWindows()
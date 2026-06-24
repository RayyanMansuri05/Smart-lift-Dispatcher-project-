import cv2

import pyttsx3
import threading
import numpy as np  # Added to prevent errors
import mediapipe as mp

# --- 1. INITIALIZE ---
mp_hands = mp.solutions.hands
# 0.8 confidence ensures it only counts clear hand gestures
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.8, min_tracking_confidence=0.8)
mp_draw = mp.solutions.drawing_utils

engine = pyttsx3.init()
def speak(text):
    threading.Thread(target=lambda: (engine.say(text), engine.runAndWait()), daemon=True).start()

cap = cv2.VideoCapture(0)
last_floor = None

print("✅ System Online: Using Geometric Landmark Tracking...")

while cap.isOpened():
    success, frame = cap.read()
    if not success: break

    frame = cv2.flip(frame, 1)
    h, w, _ = frame.shape
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb_frame)

    display_status = "SCANNING..."
    
    if results.multi_hand_landmarks:
        for hand_lms in results.multi_hand_landmarks:
            # Drawing the skeleton landmarks
            mp_draw.draw_landmarks(frame, hand_lms, mp_hands.HAND_CONNECTIONS)

            # --- FINGER COUNTING LOGIC (The Guarantee) ---
            fingers = []
            
            # 1. Thumb (Checks if tip is further out than knuckle)
            if hand_lms.landmark[4].x > hand_lms.landmark[3].x:
                fingers.append(1)
            else:
                fingers.append(0)

            # 2. Other 4 Fingers (Checks if Tip Y is above Joint Y)
            # IDs: Index(8), Middle(12), Ring(16), Pinky(20)
            for tip in [8, 12, 16, 20]:
                if hand_lms.landmark[tip].y < hand_lms.landmark[tip - 2].y:
                    fingers.append(1)
                else:
                    fingers.append(0)

            total = fingers.count(1)

            # --- UI UPDATES ---
            if 1 <= total <= 5:
                display_status = f"FLOOR {total}"
                
                # Draw Box around hand
                x_list = [int(lm.x * w) for lm in hand_lms.landmark]
                y_list = [int(lm.y * h) for lm in hand_lms.landmark]
                cv2.rectangle(frame, (min(x_list)-20, min(y_list)-20), 
                              (max(x_list)+20, max(y_list)+20), (0, 255, 0), 2)
                
                if display_status != last_floor:
                    speak(f"Floor {total} detected")
                    last_floor = display_status

    # --- 2. THE DASHBOARD ---
    # Create a 300px sidebar
    sidebar = np.zeros((h, 300, 3), dtype=np.uint8)
    cv2.putText(sidebar, "LIFT SYSTEM", (20, 50), cv2.FONT_HERSHEY_DUPLEX, 0.7, (255, 255, 255), 1)
    cv2.putText(sidebar, "TARGET:", (20, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (150, 150, 150), 1)
    cv2.putText(sidebar, display_status, (20, 170), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    # Combine camera feed and sidebar
    final_view = np.hstack([frame, sidebar])
    cv2.imshow('Smart Lift Control - Production', final_view)

    if cv2.waitKey(1) & 0xFF == 27: # Press Esc to exit
        break

cap.release()
cv2.destroyAllWindows()

from roboflow import Roboflow
import cv2

# --- 1. SETUP ROBFLOW ---
# This uses the 'roboflow' library you just successfully installed
rf = Roboflow(api_key="2z65F5xztTwfhUH6Ox2K")
project = rf.workspace().project("my-first-project-silig")
model = project.version(6).model

# --- 2. GESTURE MAPPER ---
# matched exactly to your Roboflow class names
FLOOR_MAP = {
    "Fist hand": "G",             
    "Changing postion": "4",       
    "1st floor": "1",
    "TWO_FINGERS": "2",
    "2nd Hand": "2",              
    "3RD FLOOR": "3",
    "five_fingers": "5"
}

# --- 3. START CAMERA ---
cap = cv2.VideoCapture(0)

print("🚀 Smart Lift V6 is LIVE! Press 'q' to stop.")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Run Prediction via Hosted API
    # 'confidence=60' means the AI must be 60% sure to show a box
    prediction_results = model.predict(frame, confidence=60).json()
    
    # Process each detection the AI finds
    for prediction in prediction_results['predictions']:
        label = prediction['class']
        conf = prediction['confidence']
        
        # Only move lift if the label is in our Floor Map
        if label in FLOOR_MAP:
            target_floor = FLOOR_MAP[label]
            print(f"✅ GOTO FLOOR {target_floor} (Confidence: {conf:.2f})")
            
            # Draw a box and label on your camera screen
            x, y = int(prediction['x']), int(prediction['y'])
            w, h = int(prediction['width']), int(prediction['height'])
            
            # Draw green rectangle around the hand
            cv2.rectangle(frame, (x - w//2, y - h//2), (x + w//2, y + h//2), (0, 255, 0), 2)
            cv2.putText(frame, f"FLOOR {target_floor}", (x - w//2, y - h//2 - 10), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

    # Show the video window
    cv2.imshow("Smart Lift - Version 6", frame)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
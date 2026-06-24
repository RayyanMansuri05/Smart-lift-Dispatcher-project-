import cv2

# 1. Initialize the camera
cap = cv2.VideoCapture(0)

# Check if camera opened correctly
if not cap.isOpened():
    print("❌ Error: Could not open webcam.")
    exit()

print("🚀 Camera System Live!")
print("Look for a new window icon in your Taskbar.")
print("Press 'q' on your keyboard to close the window.")

while True:
    # 2. Capture frame-by-frame
    ret, frame = cap.read()
    
    if not ret:
        print("❌ Error: Can't receive frame.")
        break

    # 3. Add text to the screen (to show it's live)
    cv2.putText(frame, "SMART LIFT: LIVE FEED", (20, 50), 
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    # 4. Display the resulting frame
    cv2.imshow('Monday Demo Preview', frame)

    # 5. Bring window to front (Hack for Windows)
    cv2.setWindowProperty('Monday Demo Preview', cv2.WND_PROP_TOPMOST, 1)

    # 6. Wait for 'q' key to stop
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# 7. Clean up
cap.release()
cv2.destroyAllWindows()
print("System shut down cleanly.")
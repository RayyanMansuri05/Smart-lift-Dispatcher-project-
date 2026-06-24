import cv2
import pyttsx3
import speech_recognition as sr
import threading
from roboflow import Roboflow

# --- 1. CONFIGURATION ---
API_KEY = "2z65F5xztTwfhUH6Ox2K"
PROJECT_ID = "my-first-project-silig"
VERSION = 9

# --- 2. SETUP LIFT SYSTEM ---
# Initialize the Roboflow Model
try:
    rf = Roboflow(api_key=API_KEY)
    project = rf.workspace().project(PROJECT_ID)
    model = project.version(VERSION).model
    print("✅ Model Loaded Successfully")
except Exception as e:
    print(f"❌ Error loading model: {e}")
    exit()

# Initialize Voice Engine
engine = pyttsx3.init()
def speak(text):
    """Announces messages without freezing the video."""
    print(f"🔊 LIFT: {text}")
    try:
        # We run this in a quick separate way to avoid lag
        engine.say(text)
        engine.runAndWait()
    except:
        pass

# --- 3. VOICE LISTENER (Background Thread) ---
def listen_for_voice():
    recognizer = sr.Recognizer()
    mic = sr.Microphone()
    
    speak("System Ready. Listening for floor commands.")
    
    while True:
        try:
            with mic as source:
                recognizer.adjust_for_ambient_noise(source, duration=0.5)
                # Listen briefly
                audio = recognizer.listen(source, timeout=4, phrase_time_limit=3)
                command = recognizer.recognize_google(audio).lower()
                
                if "floor" in command:
                    speak(f"Voice confirmed. Going to {command}.")
                elif "stop" in command:
                    speak("Emergency Stop!")
                    
        except (sr.WaitTimeoutError, sr.UnknownValueError):
            pass # Ignore silence or noise
        except Exception as e:
            print(f"Mic Error: {e}")

# --- 4. MAIN VIDEO LOOP ---
def start_lift_system():
    # Start Voice Thread
    threading.Thread(target=listen_for_voice, daemon=True).start()

    # Start Camera
    video = cv2.VideoCapture(0)
    
    while True:
        ret, frame = video.read()
        if not ret:
            break

        # --- A. DETECT GESTURES ---
        # We send the frame to your local model (or cloud if local fails)
        # confidence=40 means it needs to be 40% sure to show a box
        predictions = model.predict(frame, confidence=40, overlap=30).json()

        # --- B. DRAW RESULTS ---
        for detection in predictions['predictions']:
            # Get coordinates
            x, y, w, h = detection['x'], detection['y'], detection['width'], detection['height']
            class_name = detection['class']
            
            # Calculate box corners for drawing
            x1 = int(x - w / 2)
            y1 = int(y - h / 2)
            x2 = int(x + w / 2)
            y2 = int(y + h / 2)

            # Draw Box (Green)
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            
            # Draw Label
            label = f"{class_name} ({detection['confidence']*100:.1f}%)"
            cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

            # Trigger Action (Limit spamming)
            print(f"👉 Gesture Detected: {class_name}")

        # Show the video
        cv2.imshow("Lift Dispatcher (Universal)", frame)

        # Press 'q' to quit
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    video.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    start_lift_system()
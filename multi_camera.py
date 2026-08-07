import cv2
import pickle
import sqlite3
import numpy as np
import threading
from datetime import datetime
from deepface import DeepFace
from scipy.spatial.distance import cosine

# ─── CONFIG ───────────────────────────────────────
THRESHOLD  = 0.4
MODEL_NAME = "Facenet"
DB_PATH    = "attendance.db"
CAMERAS    = [0]   # Add more: [0, 1, 2] for 3 cameras
# ──────────────────────────────────────────────────

with open("models/face_embeddings.pkl", "rb") as f:
    known_embeddings = pickle.load(f)

already_marked = set()

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c    = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS attendance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT, date TEXT, time TEXT,
        camera_id INTEGER, status TEXT DEFAULT "Present"
    )''')
    conn.commit()
    conn.close()

def mark_attendance(name, camera_id):
    today = datetime.now().strftime("%Y-%m-%d")
    key   = f"{name}_{today}"
    if key not in already_marked:
        conn = sqlite3.connect(DB_PATH)
        c    = conn.cursor()
        c.execute(
            "INSERT INTO attendance (name, date, time, camera_id) VALUES (?,?,?,?)",
            (name, today, datetime.now().strftime("%H:%M:%S"), camera_id)
        )
        conn.commit()
        conn.close()
        already_marked.add(key)
        print(f"[CAM {camera_id}] ✅ Marked: {name}")

def recognize(face_img):
    try:
        result    = DeepFace.represent(face_img, model_name=MODEL_NAME,
                                       enforce_detection=False)
        embedding = result[0]["embedding"]
        best, score = "Unknown", float("inf")
        for person, emb in known_embeddings.items():
            s = cosine(embedding, emb)
            if s < score:
                score, best = s, person
        return (best, score) if score < THRESHOLD else ("Unknown", score)
    except:
        return "Error", 1.0

def run_camera(camera_id):
    cap          = cv2.VideoCapture(camera_id)
    face_cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    )
    frame_count  = 0
    print(f"[INFO] Camera {camera_id} started!")

    while True:
        ret, frame = cap.read()
        if not ret:
            print(f"[ERROR] Camera {camera_id} disconnected!")
            break

        frame_count += 1
        if frame_count % 3 != 0:
            cv2.imshow(f"Camera {camera_id}", frame)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
            continue

        gray  = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)

        for (x, y, w, h) in faces:
            face_roi       = frame[y:y+h, x:x+w]
            name, score    = recognize(face_roi)
            confidence     = f"{(1-score)*100:.1f}%"
            color          = (0,255,0) if name not in ["Unknown","Error"] else (0,0,255)

            cv2.rectangle(frame, (x,y), (x+w,y+h), color, 2)
            cv2.putText(frame, f"{name} {confidence}",
                        (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)

            if name not in ["Unknown", "Error"]:
                mark_attendance(name, camera_id)

        # Show camera label
        cv2.putText(frame, f"Camera {camera_id}",
                    (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,0), 2)
        cv2.putText(frame, datetime.now().strftime("%H:%M:%S"),
                    (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,255), 2)

        cv2.imshow(f"Camera {camera_id}", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()

# Run all cameras in parallel threads
init_db()
threads = []
for cam_id in CAMERAS:
    t = threading.Thread(target=run_camera, args=(cam_id,))
    t.daemon = True
    t.start()
    threads.append(t)

for t in threads:
    t.join()

cv2.destroyAllWindows()
print("[INFO] All cameras stopped.")
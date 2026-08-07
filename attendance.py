import cv2
import pickle
import numpy as np
import sqlite3
from datetime import datetime
from deepface import DeepFace
from scipy.spatial.distance import cosine

# ─── CONFIG ───────────────────────────────────────────
MODEL_NAME    = "Facenet"
THRESHOLD     = 0.3       # Lower = stricter matching
EMBEDDINGS    = "models/face_embeddings.pkl"
DB_PATH       = "attendance.db"
# ──────────────────────────────────────────────────────

# ─── Load saved embeddings ────────────────────────────
with open(EMBEDDINGS, "rb") as f:
    known_embeddings = pickle.load(f)
print(f"[INFO] Loaded {len(known_embeddings)} person(s): {list(known_embeddings.keys())}")

# ─── Database setup ───────────────────────────────────
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS attendance (
        id      INTEGER PRIMARY KEY AUTOINCREMENT,
        name    TEXT    NOT NULL,
        date    TEXT    NOT NULL,
        time    TEXT    NOT NULL,
        status  TEXT    DEFAULT 'Present'
    )''')
    conn.commit()
    conn.close()

already_marked = set()

def mark_attendance(name):
    today = datetime.now().strftime("%Y-%m-%d")
    key   = f"{name}_{today}"
    if key not in already_marked:
        conn = sqlite3.connect(DB_PATH)
        c    = conn.cursor()
        c.execute(
            "INSERT INTO attendance (name, date, time) VALUES (?, ?, ?)",
            (name, today, datetime.now().strftime("%H:%M:%S"))
        )
        conn.commit()
        conn.close()
        already_marked.add(key)
        print(f"[ATTENDANCE] ✅ Marked: {name} at {datetime.now().strftime('%H:%M:%S')}")

# ─── Face recognition ─────────────────────────────────
def recognize_face(face_img):
    try:
        result    = DeepFace.represent(
            img_path          = face_img,
            model_name        = MODEL_NAME,
            enforce_detection = False
        )
        embedding = result[0]["embedding"]

        best_name  = "Unknown"
        best_score = float("inf")

        for person, known_emb in known_embeddings.items():
            score = cosine(embedding, known_emb)
            if score < best_score:
                best_score = score
                best_name  = person

        if best_score < THRESHOLD:
            return best_name, best_score
        return "Unknown", best_score

    except Exception as e:
        return "Error", 1.0

# ─── Main loop ────────────────────────────────────────
def run():
    init_db()
    cap          = cv2.VideoCapture(0)
    face_cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    )

    print("[INFO] Camera started. Press 'Q' to quit.")
    frame_skip = 0  # process every 3rd frame for speed

    while True:
        ret, frame = cap.read()
        if not ret:
            print("[ERROR] Cannot read camera!")
            break

        frame_skip += 1
        if frame_skip % 3 != 0:          # skip frames for speed
            cv2.imshow("Attendance System - Press Q to quit", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            continue

        gray  = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)

        for (x, y, w, h) in faces:
            face_roi = frame[y:y+h, x:x+w]
            name, score = recognize_face(face_roi)
            confidence  = f"{(1 - score) * 100:.1f}%"

            color = (0, 255, 0) if name not in ["Unknown", "Error"] else (0, 0, 255)
            cv2.rectangle(frame, (x, y), (x+w, y+h), color, 2)
            cv2.putText(frame, f"{name}  {confidence}",
                        (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)

            if name not in ["Unknown", "Error"]:
                mark_attendance(name)

        # Show date/time on screen
        now = datetime.now().strftime("%Y-%m-%d  %H:%M:%S")
        cv2.putText(frame, now, (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

        cv2.imshow("Attendance System - Press Q to quit", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    print("[INFO] System stopped.")

run()
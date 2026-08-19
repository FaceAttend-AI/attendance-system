import cv2
import os
import sqlite3
from datetime import datetime

DB_PATH = "attendance.db"

def get_conn():
    return sqlite3.connect(DB_PATH)

def get_registered_students():
    try:
        conn = get_conn()
        c    = conn.cursor()
        rows = c.execute(
            "SELECT reg_no, name, department, class FROM students ORDER BY id DESC"
        ).fetchall()
        conn.close()
        return rows
    except:
        return []

def update_student_status(name, img_count):
    try:
        conn = get_conn()
        c    = conn.cursor()
        c.execute(
            "UPDATE students SET img_count=?, status=? WHERE name=?",
            (img_count, "IMAGES_COLLECTED", name)
        )
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"[WARN] Could not update DB: {e}")

def collect_faces():
    print("\n" + "="*50)
    print("   FaceAttend — Face Collection")
    print("="*50)

    # ── Show registered students ──────────────────
    students = get_registered_students()
    if students:
        print("\n📋 Registered Students in Dashboard:")
        print("-"*50)
        for i, (reg, name, dept, cls) in enumerate(students, 1):
            # Check if dataset exists
            has_data = os.path.exists(f"dataset/{name}") and \
                       len(os.listdir(f"dataset/{name}")) > 0
            status = f"✅ {len(os.listdir(f'dataset/{name}'))} imgs" if has_data else "⚠️  No images yet"
            print(f"  [{i}] {name} | {reg} | {dept} | {status}")
        print("-"*50)
        print("  [N] Enter a new name manually")
        print()

        choice = input("Select student number or press N for new: ").strip()

        if choice.upper() == "N":
            person_name = input("Enter name: ").strip().replace(" ", "_")
            reg_no      = ""
        else:
            try:
                idx         = int(choice) - 1
                reg_no, person_name, dept, cls = students[idx]
                person_name = person_name.replace(" ", "_")
                print(f"\n[INFO] Selected: {person_name} ({reg_no})")
            except:
                print("[ERROR] Invalid selection!")
                return
    else:
        print("\n[INFO] No students in database yet.")
        person_name = input("Enter student name: ").strip().replace(" ", "_")
        reg_no      = ""

    if not person_name:
        print("[ERROR] Name cannot be empty!"); return

    try:
        num_samples = int(input(f"Number of photos (default 100): ") or "100")
    except:
        num_samples = 100

    save_path = f"dataset/{person_name}"
    os.makedirs(save_path, exist_ok=True)
    existing  = len(os.listdir(save_path))

    if existing > 0:
        print(f"[INFO] Already has {existing} images. Adding more...")

    # ── Open camera ───────────────────────────────
    face_cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    )
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("[ERROR] Camera not found!"); return

    count = 0
    print(f"\n[INFO] Camera opened!")
    print(f"[INFO] Collecting {num_samples} images for: {person_name}")
    print("[INFO] Move head slightly L/R/U/D for variety")
    print("[INFO] Press Q to stop early\n")

    while count < num_samples:
        ret, frame = cap.read()
        if not ret: break

        gray  = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)

        for (x, y, w, h) in faces:
            face_crop = frame[y:y+h, x:x+w]
            filename  = f"{save_path}/{existing + count}.jpg"
            cv2.imwrite(filename, face_crop)
            count += 1

            cv2.rectangle(frame, (x,y), (x+w,y+h), (123,110,246), 2)
            cv2.putText(frame, f"{person_name}: {count}/{num_samples}",
                        (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (123,110,246), 2)

            # Progress bar
            prog = int((count/num_samples) * frame.shape[1])
            cv2.rectangle(frame, (0, frame.shape[0]-8),
                          (prog, frame.shape[0]), (62,207,178), -1)

        cv2.imshow(f"FaceAttend — Collecting: {person_name} | Q to stop", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()

    total = existing + count
    print(f"\n[DONE] Saved {count} new images")
    print(f"[DONE] Total images for {person_name}: {total}")

    # ── Update database status ────────────────────
    update_student_status(
        person_name.replace("_", " "),
        total
    )
    update_student_status(person_name, total)
    print(f"[DB]   Status updated → IMAGES_COLLECTED")

    # ── Ask for another ───────────────────────────
    again = input("\nCollect for another student? (y/n): ").strip().lower()
    if again == "y":
        collect_faces()
    else:
        print("\n" + "="*50)
        print("[NEXT] Now run:")
        print('  python build_embeddings.py')
        print("[NEXT] Then run:")
        print('  python attendance.py')
        print("="*50)

collect_faces()
import os
import pickle
import sqlite3
import numpy as np
from deepface import DeepFace

DB_PATH = "attendance.db"

def update_trained(name):
    try:
        conn = sqlite3.connect(DB_PATH)
        c    = conn.cursor()
        # Try both with and without underscore
        c.execute("UPDATE students SET status='TRAINED' WHERE name=?", (name,))
        c.execute("UPDATE students SET status='TRAINED' WHERE name=?",
                  (name.replace("_"," "),))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"[WARN] DB update failed: {e}")

def build_embeddings(dataset_path="dataset", model_name="Facenet"):
    embeddings = {}
    if not os.path.exists(dataset_path):
        print("[ERROR] dataset/ folder not found!")
        return

    persons = [p for p in os.listdir(dataset_path)
               if os.path.isdir(os.path.join(dataset_path, p))]

    if not persons:
        print("[ERROR] No person folders found in dataset/")
        print("[TIP]   Run collect_faces.py first!")
        return

    print("\n" + "="*50)
    print("   FaceAttend — Building Embeddings")
    print("="*50)
    print(f"[INFO] Found {len(persons)} person(s): {persons}")
    print(f"[INFO] Model: {model_name}\n")

    for person in persons:
        person_path = os.path.join(dataset_path, person)
        images      = [f for f in os.listdir(person_path)
                       if f.lower().endswith((".jpg",".jpeg",".png"))]

        if not images:
            print(f"[SKIP] '{person}' — no images found!")
            continue

        print(f"[INFO] Processing '{person}' — {len(images)} images...")

        person_embeddings = []
        failed = 0

        for img_file in images:
            img_path = os.path.join(person_path, img_file)
            try:
                result    = DeepFace.represent(
                    img_path          = img_path,
                    model_name        = model_name,
                    enforce_detection = False
                )
                embedding = result[0]["embedding"]
                person_embeddings.append(embedding)
            except:
                failed += 1

        if person_embeddings:
            embeddings[person] = np.mean(person_embeddings, axis=0)
            print(f"[OK]   '{person}' — {len(person_embeddings)} success, {failed} failed")
            # Update DB status to TRAINED
            update_trained(person)
            print(f"[DB]   '{person}' → TRAINED ✅")
        else:
            print(f"[FAIL] '{person}' — no valid embeddings!")

    if embeddings:
        os.makedirs("models", exist_ok=True)
        with open("models/face_embeddings.pkl", "wb") as f:
            pickle.dump(embeddings, f)
        print(f"\n[DONE] Embeddings saved → models/face_embeddings.pkl")
        print(f"[DONE] Registered: {list(embeddings.keys())}")
        print("\n[NEXT] Run: python attendance.py")
    else:
        print("\n[ERROR] No embeddings built! Check your dataset/ folder.")

build_embeddings()
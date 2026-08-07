import os
import pickle
import numpy as np
from deepface import DeepFace

def build_embeddings(dataset_path="dataset", model_name="Facenet"):
    embeddings = {}
    persons = os.listdir(dataset_path)

    if len(persons) == 0:
        print("[ERROR] No persons found in dataset folder!")
        return

    print(f"[INFO] Found {len(persons)} person(s): {persons}")
    print(f"[INFO] Using model: {model_name}")

    for person in persons:
        person_path = os.path.join(dataset_path, person)
        if not os.path.isdir(person_path):
            continue

        images = os.listdir(person_path)
        print(f"\n[INFO] Processing '{person}' — {len(images)} images...")

        person_embeddings = []
        failed = 0

        for img_file in images:
            img_path = os.path.join(person_path, img_file)
            try:
                result = DeepFace.represent(
                    img_path=img_path,
                    model_name=model_name,
                    enforce_detection=False
                )
                embedding = result[0]["embedding"]
                person_embeddings.append(embedding)
            except Exception as e:
                failed += 1

        if person_embeddings:
            # Average all embeddings into one vector per person
            embeddings[person] = np.mean(person_embeddings, axis=0)
            print(f"[OK] '{person}' — {len(person_embeddings)} successful, {failed} failed")
        else:
            print(f"[SKIP] '{person}' — no valid embeddings found")

    # Save to file
    with open("models/face_embeddings.pkl", "wb") as f:
        pickle.dump(embeddings, f)

    print(f"\n[DONE] Embeddings saved to 'models/face_embeddings.pkl'")
    print(f"[DONE] Registered persons: {list(embeddings.keys())}")

build_embeddings()
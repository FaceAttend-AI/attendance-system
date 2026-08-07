import cv2
import os

print("="*45)
print("  FACE COLLECTION - Attendance System")
print("="*45)

person_name = input("Enter Student Name: ").strip().replace(" ", "_")

if not person_name:
    print("[ERROR] Name cannot be empty!")
    exit()

num_samples = 100
save_path = "dataset/" + person_name
os.makedirs(save_path, exist_ok=True)

existing = len(os.listdir(save_path))
print("[INFO] Collecting", num_samples, "images for:", person_name)
print("[INFO] Look at camera. Press Q to quit.")

face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)

cap = cv2.VideoCapture(0)
count = 0

while count < num_samples:
    ret, frame = cap.read()
    if not ret:
        print("[ERROR] Camera not found!")
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)

    for (x, y, w, h) in faces:
        face_crop = frame[y:y+h, x:x+w]
        filename = save_path + "/" + str(existing + count) + ".jpg"
        cv2.imwrite(filename, face_crop)
        count += 1
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
        cv2.putText(frame, person_name + ": " + str(count) + "/" + str(num_samples),
                    (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

    cv2.imshow("Collecting Faces - Press Q to quit", frame)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
print("[DONE] Saved", count, "images for:", person_name)
print("[NEXT] Now run build_embeddings.py")
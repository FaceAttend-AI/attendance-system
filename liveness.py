import cv2
import time

def check_liveness():
    face_cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    )
    eye_cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades + "haarcascade_eye.xml"
    )

    cap           = cv2.VideoCapture(0)
    blink_count   = 0
    BLINKS_NEEDED = 2
    TIME_LIMIT    = 15
    start_time    = time.time()
    eyes_open     = True
    is_live       = False

    print("\n" + "="*45)
    print("   LIVENESS DETECTION - Anti Spoofing")
    print("="*45)
    print(f"[INFO] Please BLINK {BLINKS_NEEDED} times in {TIME_LIMIT} seconds!")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        gray    = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces   = face_cascade.detectMultiScale(gray, 1.3, 5)
        elapsed = time.time() - start_time
        remaining = int(TIME_LIMIT - elapsed)

        eyes_detected = False

        for (x, y, w, h) in faces:
            face_gray  = gray[y:y+h, x:x+w]
            face_color = frame[y:y+h, x:x+w]
            eyes       = eye_cascade.detectMultiScale(face_gray, 1.1, 3)

            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)

            if len(eyes) >= 2:
                eyes_detected = True
                for (ex, ey, ew, eh) in eyes:
                    cv2.rectangle(face_color, (ex, ey),
                                  (ex+ew, ey+eh), (0, 255, 255), 2)

        # ── Blink logic ───────────────────────────
        if eyes_detected:
            if not eyes_open:          # eyes were closed, now open = 1 blink
                blink_count += 1
                print(f"[BLINK] Detected! {blink_count}/{BLINKS_NEEDED}")
            eyes_open = True
        else:
            eyes_open = False          # eyes closed / not visible

        # ── Display info ──────────────────────────
        color = (0,255,0) if blink_count >= BLINKS_NEEDED else (0,165,255)
        cv2.putText(frame, f"Blinks: {blink_count}/{BLINKS_NEEDED}",
                    (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
        cv2.putText(frame, f"Time left: {remaining}s",
                    (10, 65), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,255), 2)
        cv2.putText(frame, "Please BLINK to verify liveness!",
                    (10, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,255,0), 2)

        eye_status = "Eyes: OPEN" if eyes_open else "Eyes: CLOSED"
        cv2.putText(frame, eye_status,
                    (10, 130), cv2.FONT_HERSHEY_SIMPLEX, 0.6,
                    (0,255,0) if eyes_open else (0,0,255), 2)

        # ── Check pass ────────────────────────────
        if blink_count >= BLINKS_NEEDED:
            cv2.putText(frame, "LIVE PERSON CONFIRMED! ✓",
                        (30, 220), cv2.FONT_HERSHEY_SIMPLEX,
                        0.9, (0, 255, 0), 3)
            cv2.imshow("Liveness Detection", frame)
            cv2.waitKey(2000)
            is_live = True
            break

        # ── Check timeout ─────────────────────────
        if elapsed > TIME_LIMIT:
            cv2.putText(frame, "FAKE / TIMEOUT - BLOCKED!",
                        (30, 220), cv2.FONT_HERSHEY_SIMPLEX,
                        0.9, (0, 0, 255), 3)
            cv2.imshow("Liveness Detection", frame)
            cv2.waitKey(2000)
            break

        cv2.imshow("Liveness Detection - BLINK Please!", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()
    return is_live

if __name__ == "__main__":
    result = check_liveness()
    print()
    if result:
        print("[RESULT] ✅ LIVE PERSON — Attendance can be marked!")
    else:
        print("[RESULT] ❌ FAKE DETECTED — Attendance BLOCKED!")
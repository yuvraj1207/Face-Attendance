import cv2

def capture_face_from_webcam():
    # Try forcing DirectShow backend (Windows fix)
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

    if not cap.isOpened():
        print("❌ Error: Could not open webcam.")
        return None

    print("✅ Webcam started. Press SPACE to capture, ESC to exit.")

    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    captured_face = None

    while True:
        ret, frame = cap.read()
        if not ret:
            print("❌ Failed to grab frame.")
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)

        # Draw rectangle around detected faces
        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

        cv2.imshow("Press SPACE to Capture | ESC to Exit", frame)

        key = cv2.waitKey(1) & 0xFF
        if key == 27:  # ESC
            print("❌ Exit without capturing.")
            break
        elif key == 32:  # SPACE
            if len(faces) > 0:
                (x, y, w, h) = faces[0]  # Take first face
                captured_face = frame[y:y+h, x:x+w]
                cv2.imwrite("captured_face.jpg", captured_face)
                print("✅ Face captured and saved as captured_face.jpg")
                break
            else:
                print("⚠️ No face detected. Try again.")

    cap.release()
    cv2.destroyAllWindows()
    return captured_face

if __name__ == "__main__":
    capture_face_from_webcam()

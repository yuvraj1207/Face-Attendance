import cv2
import os
from datetime import datetime
import face_recognition

# Capture face with real-time detection
def capture_face(username):
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        raise Exception("Could not open camera")

    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

    saved_face_path = None

    while True:
        ret, frame = cap.read()
        if not ret:
            continue

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)

        for (x, y, w, h) in faces:
            # Draw rectangle around detected face
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

            # Crop the detected face
            face_img = frame[y:y+h, x:x+w]

            # Save when face is detected
            faces_dir = "faceapp/faces"
            os.makedirs(faces_dir, exist_ok=True)

            filename = f"{username}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            saved_face_path = os.path.join(faces_dir, filename)

            cv2.imwrite(saved_face_path, face_img)
            cap.release()
            cv2.destroyAllWindows()
            return saved_face_path

        # Show camera feed
        cv2.imshow("Face Capture - Press 'q' to Quit", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    return saved_face_path


# Extract encoding from saved face
def extract_encoding(image_path):
    image = face_recognition.load_image_file(image_path)
    encodings = face_recognition.face_encodings(image)

    if len(encodings) == 0:
        raise Exception("No face found in the image")

    return encodings[0]

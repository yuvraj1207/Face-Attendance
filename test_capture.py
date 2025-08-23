import cv2
import face_recognition

# Try both cameras manually
#cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)  # try 0 first
cap = cv2.VideoCapture(1, cv2.CAP_DSHOW)  # uncomment if 0 fails

if not cap.isOpened():
    print("❌ Could not access the camera")
    exit()

print("✅ Webcam started. Press SPACE to capture, ESC to exit.")

while True:
    ret, frame = cap.read()
    if not ret:
        print("❌ Failed to grab frame")
        break

    # Flip frame (sometimes webcam appears mirrored)
    frame = cv2.flip(frame, 1)

    # Detect faces
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    faces = face_recognition.face_locations(rgb_frame)

    # Draw rectangles
    for (top, right, bottom, left) in faces:
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)

    cv2.imshow("Signup - Capture Face", frame)

    key = cv2.waitKey(1) & 0xFF
    if key == 27:  # ESC
        print("❌ Exit without capturing.")
        break
    elif key == 32:  # SPACE
        if faces:
            print("✅ Face detected and captured!")
            (top, right, bottom, left) = faces[0]
            face_image = frame[top:bottom, left:right]
            cv2.imwrite("captured_face.jpg", face_image)
            print("💾 Saved cropped face as captured_face.jpg")
        else:
            print("⚠️ No face detected. Try again.")

cap.release()
cv2.destroyAllWindows()

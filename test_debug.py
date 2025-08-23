import cv2

for i in range(3):  # test first 3 indexes
    print(f"\n🔎 Trying camera index {i}...")
    cap = cv2.VideoCapture(i, cv2.CAP_DSHOW)  # try DirectShow
    if not cap.isOpened():
        print(f"❌ Camera {i} not available")
        continue

    ret, frame = cap.read()
    if ret:
        print(f"✅ Camera {i} is working! Frame size: {frame.shape}")
        cv2.imshow(f"Camera {i}", frame)
        cv2.waitKey(2000)  # show for 2 sec
        cv2.destroyAllWindows()
    else:
        print(f"⚠️ Camera {i} opened but no frame captured.")

    cap.release()

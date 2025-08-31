import cv2

cap = cv2.VideoCapture(0)  # 0 is usually the default system camera
if not cap.isOpened():
    print("Error: Could not access the camera.")
else:
    print("Camera is working.")
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Failed to capture image")
            break
        cv2.imshow("Camera Feed", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()

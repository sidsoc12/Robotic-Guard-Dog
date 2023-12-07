import cv2
import torch
import mediapipe as mp
import os


# Path to the YOLOv5 weights file
weights_path = "yolov5s.pt"  # Adjust if your weights file is in a different directory

# Load the pre-trained YOLOv5 model from the local weights file
model = torch.hub.load("yolov5", "custom", path=weights_path, source="local")


# Initialize MediaPipe solutions
mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose
pose = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)

# Define weapon classes
weapon_classes = [
    "cell phone",
]  # Add or modify based on YOLO model training


def main():
    cap = cv2.VideoCapture(0)  # Use 0 for webcam

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame from camera")
            break

        # Convert frame to RGB (YOLOv5 model expects RGB)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Perform inference with YOLOv5
        results = model(rgb_frame)

        # Check for weapons in the results
        weapon_detected = False
        for detection in results.xyxy[0].numpy():
            class_id = int(detection[-1])
            class_name = model.names[class_id]
            print(class_name)
            if class_name in weapon_classes:
                weapon_detected = True
                x1, y1, x2, y2 = map(int, detection[:4])
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
                cv2.putText(
                    frame,
                    f"Weapon: {class_name}",
                    (x1, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.9,
                    (0, 0, 255),
                    2,
                )
                threat_level = "medium"  # Example variable
                message = f"Harmful threat detected with {threat_level} risk, pupper now engaging in defensive pose after seeing {class_name}"
                os.system(f'say "{message}"')

        # Process the frame with MediaPipe Pose
        results_pose = pose.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        if results_pose.pose_landmarks:
            mp_drawing.draw_landmarks(
                frame, results_pose.pose_landmarks, mp_pose.POSE_CONNECTIONS
            )

        # Display the frame
        cv2.imshow("Frame", frame)

        # Break the loop when 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()

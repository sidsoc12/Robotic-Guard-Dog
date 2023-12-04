import cv2
import mediapipe as mp
import numpy as np
import pyttsx3

mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose
mp_hands = mp.solutions.hands

# # Initialize text-to-speech engine
# engine = pyttsx3.init()

# Initialize pose and hands models.
pose = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)
hands = mp_hands.Hands(min_detection_confidence=0.5, min_tracking_confidence=0.5)
# Prepare DrawingSpec for drawing the landmarks later.
drawing_spec = mp_drawing.DrawingSpec(thickness=2, circle_radius=1)


def calculate_angle(a, b, c):
    a = np.array(a)  # First
    b = np.array(b)  # Mid
    c = np.array(c)  # End

    radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(
        a[1] - b[1], a[0] - b[0]
    )
    angle = np.abs(radians * 180.0 / np.pi)

    if angle > 180.0:
        angle = 360 - angle

    return angle


def is_fist_clenched(hand_landmarks):
    # Check if the fist is clenched based on the angles of the finger joints
    clenched_fist_angle_threshold = 160  # Angle threshold, this might need tuning

    # Loop through each finger
    for finger in [
        mp_hands.HandLandmark.THUMB_MCP,
        mp_hands.HandLandmark.INDEX_FINGER_MCP,
        mp_hands.HandLandmark.MIDDLE_FINGER_MCP,
        mp_hands.HandLandmark.RING_FINGER_MCP,
        mp_hands.HandLandmark.PINKY_MCP,
    ]:
        # Calculate the angle for the finger base joint
        if finger != mp_hands.HandLandmark.THUMB_MCP:  # Skip the thumb MCP
            joint_base = hand_landmarks.landmark[finger]
            joint_mid = hand_landmarks.landmark[finger + 1]
            joint_tip = hand_landmarks.landmark[finger + 2]

            angle = calculate_angle(
                [joint_base.x, joint_base.y],
                [joint_mid.x, joint_mid.y],
                [joint_tip.x, joint_tip.y],
            )

            if angle > clenched_fist_angle_threshold:
                return False

    return True


# Function to check if arms are out or in
def check_arms_out(landmarks, width):
    # Coordinates of shoulders and wrists
    left_shoulder = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value]
    right_shoulder = landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value]
    left_wrist = landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value]
    right_wrist = landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value]

    # Check if wrists are outside the shoulders
    if left_wrist.x < left_shoulder.x and right_wrist.x > right_shoulder.x:
        return "Arms In"
    else:
        return "Arms Out"


# def speak_warning():
#     # Play a system beep sound
#     # For Windows:
#     # import winsound
#     # winsound.Beep(frequency, duration)
#     # For example: winsound.Beep(440, 500) # Beep at 440 Hz for 500 ms

#     # Speak a warning message
#     engine.say("Harmful threat detected, pupper now engaging in defensive pose")
#     engine.runAndWait()

import os
import depthai as dai


def create_pipeline():
    pipeline = dai.Pipeline()
    cam_rgb = pipeline.createColorCamera()
    cam_rgb.setBoardSocket(dai.CameraBoardSocket.RGB)
    cam_rgb.setResolution(dai.ColorCameraProperties.SensorResolution.THE_1080_P)

    xout_video = pipeline.createXLinkOut()
    xout_video.setStreamName("video")
    cam_rgb.video.link(xout_video.input)

    return pipeline


def main():
    pipeline = create_pipeline()

    # Start the pipeline
    with dai.Device(pipeline) as device:
        # Output queue will be used to get the rgb frames from the output defined above
        q_video = device.getOutputQueue(name="video", maxSize=4, blocking=False)
        arm_status = ""

        while True:
            in_video = (
                q_video.get()
            )  # blocking call, will wait until a new data has arrived
            frame = in_video.getCvFrame()

            # Flip the image horizontally for a later selfie-view display, and convert the BGR image to RGB.
            image = cv2.cvtColor(cv2.flip(frame, 1), cv2.COLOR_BGR2RGB)
            image.flags.writeable = False

            # Process the image and detect the pose and hands.
            results_pose = pose.process(image)
            results_hands = hands.process(image)

            image.flags.writeable = True
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

            # Draw the pose annotation on the image.
            if results_pose.pose_landmarks:
                mp_drawing.draw_landmarks(
                    image, results_pose.pose_landmarks, mp_pose.POSE_CONNECTIONS
                )
                arm_status = check_arms_out(
                    results_pose.pose_landmarks.landmark, image.shape[1]
                )

            # Check if hands are clenched.
            hands_clenched = False
            if results_hands.multi_hand_landmarks:
                for hand_landmarks in results_hands.multi_hand_landmarks:
                    if is_fist_clenched(hand_landmarks):
                        hands_clenched = True
                        break

            # Combine the checks for arms out and hands clenched for the final status.
            if hands_clenched:
                status_text = "Harmful threat detected"
                os.system(
                    'say "Harmful threat detected, pupper now engaging in defensive pose"'
                )
            else:
                status_text = "Pupper is Safe"
                if arm_status == "Arms Out":
                    status_text = "Harmful threat detected"

            final_status = f"Status: {status_text} | Arm Status: {arm_status} | Hands Clenched: {hands_clenched}"

            # Display the status on the image.
            cv2.putText(
                image,
                final_status,
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 255, 0),
                2,
                cv2.LINE_AA,
            )

            # Show the image.
            cv2.imshow("MediaPipe Pose and Hands", image)

            # Break the loop when 'q' is pressed.
            if cv2.waitKey(5) & 0xFF == ord("q"):
                break

        cv2.destroyAllWindows()


# Main function
# def main():
#     cap = cv2.VideoCapture(0)

#     while cap.isOpened():
#         ret, frame = cap.read()
#         if not ret:
#             print("Ignoring empty camera frame.")
#             continue

#         # Flip the image horizontally for a later selfie-view display, and convert the BGR image to RGB.
#         image = cv2.cvtColor(cv2.flip(frame, 1), cv2.COLOR_BGR2RGB)
#         image.flags.writeable = False

#         # Process the image and detect the pose.
#         results_pose = pose.process(image)
#         # Process the image and detect the hands.
#         results_hands = hands.process(image)

#         image.flags.writeable = True
#         image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

#         # Draw the pose annotation on the image.
#         if results_pose.pose_landmarks:
#             mp_drawing.draw_landmarks(
#                 image, results_pose.pose_landmarks, mp_pose.POSE_CONNECTIONS
#             )
#             arm_status = check_arms_out(
#                 results_pose.pose_landmarks.landmark, image.shape[1]
#             )

#         # Check if hands are clenched.
#         hands_clenched = False
#         if results_hands.multi_hand_landmarks:
#             for hand_landmarks in results_hands.multi_hand_landmarks:
#                 if is_fist_clenched(hand_landmarks):
#                     hands_clenched = True
#                     break

#         # Combine the checks for arms out and hands clenched for the final status.
#         if hands_clenched:
#             status_text = "Harmful threat detected"
#             os.system(
#                 'say "Harmful threat detected, pupper now engaging in defensive pose"'
#             )
#         else:
#             if arm_status == "Arms Out":
#                 status_text = "Harmful threat detected"
#             status_text = "Pupper is Safe"

#         final_status = f"Status: {status_text} | Arm Status: {arm_status} | Hands Clenched: {hands_clenched}"

#         # Display the status on the image.
#         cv2.putText(
#             image,
#             final_status,
#             (10, 30),
#             cv2.FONT_HERSHEY_SIMPLEX,
#             1,
#             (0, 255, 0),
#             2,
#             cv2.LINE_AA,
#         )

#         # Show the image.
#         cv2.imshow("MediaPipe Pose and Hands", image)

#         # Break the loop when 'q' is pressed.
#         if cv2.waitKey(5) & 0xFF == ord("q"):
#             break

#     cap.release()
#     cv2.destroyAllWindows()


if __name__ == "__main__":
    main()

import cv2
import mediapipe as mp
import numpy as np
from StanfordQuadruped import karelPupper
import time

import pyttsx3

mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose
mp_hands = mp.solutions.hands


# # Initialize text-to-speech engine
# engine = pyttsx3.init()

# Initialize pose and hands models.
pose = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.7)
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
    cam_rgb.setBoardSocket(dai.CameraBoardSocket.CAM_A)
    cam_rgb.setResolution(dai.ColorCameraProperties.SensorResolution.THE_1080_P)

    xout_video = pipeline.createXLinkOut()
    xout_video.setStreamName("video")
    cam_rgb.video.link(xout_video.input)

    return pipeline

def speak_statement(engine, statement):
    engine.say(statement) 
    engine.runAndWait()
    engine.stop() 

def main():
    pipeline = create_pipeline()
    myPup = karelPupper.Pupper()
    myPup.wakeup()
    time.sleep(0.2)
    print("started")
    myPup.slowStand()

    #initilaize text to speech engine
    engine = pyttsx3.init()
    engine.setProperty("rate", 150)
    engine.setProperty("volume", 0.9)
   
    # engine.say("Hello, I am your robotic guard dog, Tin") 
    
    # engine.runAndWait()
    # engine.stop() 

    speak_statement(engine, "Hello, I am your robotic guard dog, Tin")

    # Start the pipeline
    with dai.Device(pipeline) as device:
        # Output queue will be used to get the rgb frames from the output defined above
        q_video = device.getOutputQueue(name="video", maxSize=4, blocking=False)
        arm_status = ""

        # External Camera gets frames -> make it into cv frame -> covert that to image -> then run opencv models on image
        current_state = "stand"
        status_text = "Pupper is Safe"
        old_threats = []

        while True:
            threats = []
            print("looped")
            try:
                in_video = (
                    q_video.get()
                )  # blocking call, will wait until a new data has arrived
                frame = in_video.getCvFrame()
            except Exception as e:
                print(e)
                continue

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
                # mp_drawing.draw_landmarks(
                #     image, results_pose.pose_landmarks, mp_pose.POSE_CONNECTIONS
                # )
                arm_status = check_arms_out(
                    results_pose.pose_landmarks.landmark, image.shape[1]
                )
                #print("DRAWING POSE ANNOTATION")

            # Check if hands are clenched.
            hands_clenched = False
            if results_hands.multi_hand_landmarks:
                for hand_landmarks in results_hands.multi_hand_landmarks:
                    if is_fist_clenched(hand_landmarks):
                        hands_clenched = True
                        threats.append("hands_clenched")
                        break

            # Combine the checks for arms out and hands clenched for the final status.
            if hands_clenched:
                status_text = "Harmful threat detected"
                # os.system(
                #     'say "Harmful threat detected, pupper now engaging in defensive pose"'
                # )
            else:
                if arm_status == "Arms Out":
                    status_text = "Harmful threat detected"
                    threats.append("arms_out")
                else:
                    status_text = "Pupper is Safe"

            # final_status = f"Status: {status_text} | Arm Status: {arm_status} | Hands Clenched: {hands_clenched}"
            states = [status_text, arm_status, hands_clenched]
            print(states)
            print(current_state)
            if status_text == "Harmful threat detected":
                if current_state == "sit":
                    myPup.slowStand()
                    print("finished standing")
                current_state = "stand"
            else:
                if(current_state == "stand"):
                    myPup.nod()
                    myPup.nap()
                    print("finished sitting")
                    current_state = "sit"

            if old_threats == threats:
                continue
            elif threats == ["arms_out"]:
                speak_statement(engine, "Threat detected, arms are out")
            elif threats == ["hands_clenched"]:
                speak_statement(engine, "Threat detected, hands are clenched")
            elif len(threats) == 2:
                speak_statement(engine, "Threat detected, hands are clenched, arms are out")
            elif threats == []:
                speak_statement(engine, "Thank you for assuming a non-threatening position")

            # Display the status on the image.
            # Display the status on the image.
            # cv2.putText(
            #     image,
            #     final_status,
            #     (10, 30),  # Position of the text
            #     cv2.FONT_HERSHEY_SIMPLEX,  # Font style
            #     1.5,  # Font scale (1.5 is larger than the default 1)
            #     (0, 0, 255),  # Font color in BGR (red)
            #     3,  # Font thickness
            #     cv2.LINE_AA,
            # )

            # Show the image.
            # cv2.imshow("MediaPipe Pose and Hands", image)

            # Break the loop when 'q' is pressed.
            if cv2.waitKey(5) & 0xFF == ord("q"):
                break
            old_threats = threats

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

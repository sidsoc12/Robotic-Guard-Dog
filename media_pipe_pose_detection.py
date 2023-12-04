import cv2
import mediapipe as mp
import numpy as np

mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose
mp_hands = mp.solutions.hands

# Initialize pose and hands models.
pose = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)
hands = mp_hands.Hands(min_detection_confidence=0.5, min_tracking_confidence=0.5)
# Prepare DrawingSpec for drawing the landmarks later.
drawing_spec = mp_drawing.DrawingSpec(thickness=2, circle_radius=1)


def is_fist_clenched(hand_landmarks):
    # Assuming a simple heuristic where we check if the fingertips are close to the base of the index finger.
    # This will need refinement based on your specific requirements.
    clenched_threshold = (
        0.3  # Threshold for how close fingertips should be to the palm base.
    )

    # Get the base of the palm.
    wrist = np.array(
        [
            hand_landmarks.landmark[mp_hands.HandLandmark.WRIST].x,
            hand_landmarks.landmark[mp_hands.HandLandmark.WRIST].y,
        ]
    )

    # Check each fingertip's proximity to the wrist.
    for fingertip in [
        mp_hands.HandLandmark.INDEX_FINGER_TIP,
        mp_hands.HandLandmark.MIDDLE_FINGER_TIP,
        mp_hands.HandLandmark.RING_FINGER_TIP,
        mp_hands.HandLandmark.PINKY_TIP,
    ]:
        finger_tip = np.array(
            [hand_landmarks.landmark[fingertip].x, hand_landmarks.landmark[fingertip].y]
        )
        # Calculate distance from wrist to fingertip.
        distance = np.linalg.norm(finger_tip - wrist)

        # If the distance is greater than the threshold, the fist is likely not clenched.
        if distance > clenched_threshold:
            return False

    # If all fingertips are within the threshold distance, the fist is likely clenched.
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


# Main function
def main():
    cap = cv2.VideoCapture(0)

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            print("Ignoring empty camera frame.")
            continue

        # Flip the image horizontally for a later selfie-view display, and convert the BGR image to RGB.
        image = cv2.cvtColor(cv2.flip(frame, 1), cv2.COLOR_BGR2RGB)
        image.flags.writeable = False

        # Process the image and detect the pose.
        results_pose = pose.process(image)
        # Process the image and detect the hands.
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
        else:
            if arm_status == "Arms Out":
                status_text = "Harmful threat detected"
            status_text = "Pupper is Safe"

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

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()

import cv2
import mediapipe as mp
import numpy as np

mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_hands = mp.solutions.hands

# For webcam input:
cap = cv2.VideoCapture(0)
with mp_hands.Hands(
        model_complexity=0,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5) as hands:
    frames = 0
    while cap.isOpened():
        success, image = cap.read()
        if not success:
            print("Ignoring empty camera frame.")
            # If loading a video, use 'break' instead of 'continue'.
            continue
        if frames > 5:
            break
        # To improve performance, optionally mark the image as not writeable to
        # pass by reference.
        image.flags.writeable = False
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = hands.process(image)

        # Draw the hand annotations on the image.
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:     # 양손이면 2개, 한손이면 1개
                # print(type(hand_landmarks))   # NormalizedLandmarkList
                # print(dir(hand_landmarks))    # landmark로 접근
                mp_drawing.draw_landmarks(
                    image,
                    hand_landmarks,
                    mp_hands.HAND_CONNECTIONS,
                    mp_drawing_styles.get_default_hand_landmarks_style(),
                    mp_drawing_styles.get_default_hand_connections_style())


        # TODO : process hand landmark --> gesture recognition --> driving
        # TODO : (1) process hand landmarks
        for hand_landmarks, hand_cls in zip(results.multi_hand_landmarks, results.multi_handedness):
            hand_joints = np.zeros((21, 3))
            for i, landmark_ in enumerate(hand_landmarks.landmark):
                hand_joints[i, :] = landmark_.x, landmark_.y, landmark_.z
            cls = str(hand_cls.classification._values[0].label)

        # TODO : (2) gesture recognition ?


        # TODO : visualize above process


        # Flip the image horizontally for a selfie-view display.
        cv2.imshow('MediaPipe Hands', cv2.flip(image, 1))
        if cv2.waitKey(5) & 0xFF == 27:
            break
        frames += 1

cap.release()

# print(dir(results))
# print(results.multi_handedness)     # Left랑 Right랑 지금 반대임. 웹캠이 날 보는 입장에서는 내 오른손이 웹캠의 왼손 (그래서 visualize할 때 flip 시켜줌)
# print(results.multi_handedness[0])




import cv2
import mediapipe as mp
import numpy as np
import os

mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_hands = mp.solutions.hands

# For webcam input:
cap = cv2.VideoCapture(0)
# log_x = [[] for _ in range(21)]
# log_y = [[] for _ in range(21)]
# log_z = [[] for _ in range(21)]

log_xr = []
log_yr = []
log_zr = []
log_xl = []
log_yl = []
log_zl = []
log_zr_wrist = []
log_xr_wrist = []
log_yr_wrist = []

log_zl_wrist = []
log_xl_wrist = []
log_yl_wrist = []

log_z_root = []
log_z_fingers = []

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
        if frames > 300:
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
            for hand_landmarks in results.multi_hand_landmarks:  # 양손이면 2개, 한손이면 1개
                # print(type(hand_landmarks))   # NormalizedLandmarkList
                # print(dir(hand_landmarks))    # landmark로 접근
                mp_drawing.draw_landmarks(
                    image,
                    hand_landmarks,
                    mp_hands.HAND_CONNECTIONS,
                    mp_drawing_styles.get_default_hand_landmarks_style(),
                    mp_drawing_styles.get_default_hand_connections_style())
        cv2.imwrite(os.path.join('C:\\Users\\82106\\EE_app\\EE_app\\videos', str(frames) + '.jpg'), image)

        # TODO : process hand landmark --> gesture recognition --> driving
        # TODO : (1) process hand landmarks

        if results.multi_hand_landmarks:
            string_packet = ''
            for hand_landmarks, hand_cls in zip(results.multi_hand_landmarks, results.multi_handedness):
                hand_joints = np.zeros((21, 3))
                for i, landmark_ in enumerate(hand_landmarks.landmark):
                    hand_joints[i, :] = landmark_.x, landmark_.y, landmark_.z

                cls = str(hand_cls.classification._values[0].label)
                if cls == 'Right':
                    log_xr.append(np.mean(hand_joints[:, 0]))
                    log_yr.append(np.mean(hand_joints[:, 1]))
                    log_zr.append(np.mean(hand_joints[:, 2]) * -5)
                    log_zr_wrist.append(hand_joints[0, 2] * -5)
                    log_xr_wrist.append(hand_joints[0, 0])
                    log_yr_wrist.append(hand_joints[0, 1])
                    log_z_root.append(np.mean(hand_joints[[1, 5, 9, 13, 17], 2]) * -5)
                    log_z_fingers.append(
                        np.mean(hand_joints[[2, 3, 4, 6, 7, 8, 10, 11, 12, 14, 15, 16, 18, 19, 20], 2]) * -5)
                else:
                    log_zl_wrist.append(hand_joints[0, 2] * -5)
                    log_xl_wrist.append(hand_joints[0, 0])
                    log_yl_wrist.append(hand_joints[0, 1])

                    log_xl.append(np.mean(hand_joints[:, 0]))
                    log_yl.append(np.mean(hand_joints[:, 1]))
                    log_zl.append(np.mean(hand_joints[:, 2]) * -5)
                joints_string = ''
                for i in range(len(hand_joints)):
                    for val in hand_joints[i]:
                        joints_string += str(val)[:7] + ','
                string_packet += joints_string + '/'
                string_packet += cls + '/'

            # print(string_packet)
            # print(string_packet.encode('utf-8'))

        # TODO : (2) gesture recognition ?
        # TODO : visualize above process
        # Flip the image horizontally for a selfie-view display.

        cv2.imshow('MediaPipe Hands', cv2.flip(image, 1))
        if cv2.waitKey(5) & 0xFF == 27:
            break
        frames += 1

cap.release()

import matplotlib.pyplot as plt

theta = []
for i in range(len(log_xr)):
    line = (log_yl[i] - log_yr[i]) / (log_xl[i] - log_xr[i])
    line = np.pi / 180 * np.arctan(line)
    theta.append(line)

plt.plot(log_xr)
plt.plot(log_yr)
plt.plot(log_zr)
plt.plot(log_xl)
plt.plot(log_yl)
plt.plot(log_zl)
# plt.plot(['Right z', 'Left z'])
plt.legend(['xr', 'yr', 'zr', 'xl', 'yl', 'zl'])
plt.show()

plt.plot(theta)
plt.show()

plt.plot(log_zr_wrist)
plt.plot(log_zl_wrist)
# plt.plot(log_z_fingers)
# plt.plot(log_z_root)
# plt.legend(['Wrist', 'Fingers', 'Root'])
plt.legend(['Right', 'Left'])
plt.show()


plt.plot(log_zr_wrist)
plt.plot(log_xr_wrist)
plt.plot(log_yr_wrist)
plt.plot(log_xl_wrist)
plt.plot(log_yl_wrist)
plt.legend(['z', 'xr', 'yr', 'xl', 'yl'])
plt.show()

#
# plt.plot(log_xr)
# plt.plot(log_yr)
# plt.plot(log_zr)
# plt.legend(['X', 'Y', 'Z'])
# plt.show()

# plt.plot(log_xr)
# plt.plot(log_xl)
# plt.legend(['R', 'L'])
# plt.show()
#
# plt.plot(log_yr)
# plt.plot(log_yl)
# plt.legend(['R', 'L'])
# plt.show()

# for x, y, z in zip(log_x, log_y, log_z):
#     plt.plot(x)
#     plt.plot(y)
#     plt.plot(z)
#     plt.legend()
#     plt.show()
# print(dir(results))
# print(results.multi_handedness)     # Left랑 Right랑 지금 반대임. 웹캠이 날 보는 입장에서는 내 오른손이 웹캠의 왼손 (그래서 visualize할 때 flip 시켜줌)
# print(results.multi_handedness[0])

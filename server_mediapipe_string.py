'''


pip install errno
pip install mediapipe
'''

import os
import socket
import cv2
import numpy as np
import base64
import glob
import sys
import time
import threading
from datetime import datetime
import errno

import mediapipe as mp
from numpy.core.fromnumeric import resize


class ServerSocket:
    def __init__(self, ip, port):
        self.TCP_IP = ip
        self.TCP_PORT = port

    def socketOpen(self):  # socket open
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((self.TCP_IP, self.TCP_PORT))
        self.sock.listen(1)
        # self.sock.settimeout(5) # 2초 타임 아웃.

        print(u'Server socket [ TCP_IP: ' + self.TCP_IP + ', TCP_PORT: ' + str(self.TCP_PORT) + ' ] is open')
        self.conn, self.addr = self.sock.accept()
        print(u'Server socket [ TCP_IP: ' + self.TCP_IP + ', TCP_PORT: ' + str(
            self.TCP_PORT) + ' ] is connected with client')

    def socketClose(self):  # socket close
        self.sock.close()
        print(u'Server socket [ TCP_IP: ' + self.TCP_IP + ', TCP_PORT: ' + str(self.TCP_PORT) + ' ] is close')

    def recvall(self, sock, count):
        buf = b''
        while count:
            newbuf = sock.recv(count)
            if not newbuf: return None
            buf += newbuf
            count -= len(newbuf)
        return buf

    def getDate(self, now):
        year = str(now.tm_year)
        month = str(now.tm_mon)
        day = str(now.tm_mday)

        if len(month) == 1:
            month = '0' + month
        if len(day) == 1:
            day = '0' + day
        return (year + '-' + month + '-' + day)

    def getTime(self, now):
        file_time = (str(now.tm_hour) + '_' + str(now.tm_min) + '_' + str(now.tm_sec))
        return file_time


class CameraServerSocket(ServerSocket):
    def __init__(self, ip, port):
        super().__init__(ip, port)
        print("CameraServerSocket class init function")

        self.dataReady = False

        self.createImageDir()
        self.folder_num = 0

        self.ct = 0

        super().socketOpen()

        self.receiveThread = threading.Thread(target=self.receiveImages)
        self.receiveThread.start()
        self.queue = []     # 11 / 13

    def receiveImages(self):
        cnt_str = ''
        cnt = 0

        try:
            # mp drawing variable
            mp_drawing = mp.solutions.drawing_utils
            mp_drawing_styles = mp.solutions.drawing_styles
            mp_hands = mp.solutions.hands

            while True:
                # file name numbering
                if (cnt < 10):
                    cnt_str = '000' + str(cnt)
                elif (cnt < 100):
                    cnt_str = '00' + str(cnt)
                elif (cnt < 1000):
                    cnt_str = '0' + str(cnt)
                else:
                    cnt_str = str(cnt)
                if cnt == 0: startTime = time.localtime()
                cnt += 1

                # recv data : data length, data, send time
                length = super().recvall(self.conn, 64)

                length1 = length.decode('utf-8')
                stringData = super().recvall(self.conn, int(length1))

                stime = super().recvall(self.conn, 64)

                # print('send time: ' + stime.decode('utf-8'))
                now = time.localtime()
                # print('receive time: ' + datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f'))
                data = np.frombuffer(base64.b64decode(stringData), np.uint8)
                decimg = cv2.imdecode(data, 1)

                rimage = decimg

                with mp_hands.Hands(
                        model_complexity=0,
                        min_detection_confidence=0.5,
                        min_tracking_confidence=0.5) as hands:

                    rimage.flags.writeable = False
                    rimage = cv2.cvtColor(rimage, cv2.COLOR_BGR2RGB)
                    results = hands.process(rimage)

                    rimage.flags.writeable = True
                    rimage = cv2.cvtColor(rimage, cv2.COLOR_RGB2BGR)

                    if results.multi_hand_landmarks:
                        for hand_landmarks in results.multi_hand_landmarks:
                            mp_drawing.draw_landmarks(
                                rimage,
                                hand_landmarks,
                                mp_hands.HAND_CONNECTIONS,
                                mp_drawing_styles.get_default_hand_landmarks_style(),
                                mp_drawing_styles.get_default_hand_connections_style())

                        # data type list of class -> (results.multi_hand_landmarks)[0] type : mediapipe coord class
                        self.saveData(results.multi_hand_landmarks, results.multi_handedness)  # save point data
                        self.dataReady = True
                    else:
                        self.dataReady = False
                    # cv2.imshow('MediaPipe Hands', cv2.flip(rimage, 1))  # Image show -> hide
                    decimg = rimage

                # cv2.imshow("image", decimg)
                # cv2.imwrite('./' + str(self.TCP_PORT) + '_images' + str(self.folder_num) + '/img' + cnt_str + '.jpg',
                #             decimg)
                cv2.waitKey(1)
                if (cnt == 60 * 10):
                    cnt = 0
                    convertThread = threading.Thread(target=self.convertImage(str(self.folder_num), 600, startTime))
                    convertThread.start()
                    self.folder_num = (self.folder_num + 1) % 2

        except Exception as e:
            print(e)
            self.convertImage(str(self.folder_num), cnt, startTime)
            super().socketClose()
            cv2.destroyAllWindows()
            super().socketOpen()
            self.receiveThread = threading.Thread(target=self.receiveImages)
            self.receiveThread.start()

    def createImageDir(self):

        folder_name = str(self.TCP_PORT) + "_images0"
        try:
            if not os.path.exists(folder_name):
                os.makedirs(os.path.join(folder_name))
        except OSError as e:
            if e.errno != errno.EEXIST:
                print("Failed to create " + folder_name + " directory")
                raise

        folder_name = str(self.TCP_PORT) + "_images1"
        try:
            if not os.path.exists(folder_name):
                os.makedirs(os.path.join(folder_name))
        except OSError as e:
            if e.errno != errno.EEXIST:
                print("Failed to create " + folder_name + " directory")
                raise

        folder_name = "videos"
        try:
            if not os.path.exists(folder_name):
                os.makedirs(os.path.join(folder_name))
        except OSError as e:
            if e.errno != errno.EEXIST:
                print("Failed to create " + folder_name + " directory")
                raise

    def convertImage(self, fnum, count, now):
        img_array = []
        cnt = 0
        for filename in glob.glob('./' + str(self.TCP_PORT) + '_images' + fnum + '/*.jpg'):
            if (cnt == count):
                break
            cnt = cnt + 1
            img = cv2.imread(filename)
            height, width, layers = img.shape
            size = (width, height)
            img_array.append(img)

        file_date = super().getDate(now)
        file_time = super().getTime(now)
        name = 'video(' + file_date + ' ' + file_time + ').mp4'
        file_path = './videos/' + name
        out = cv2.VideoWriter(file_path, cv2.VideoWriter_fourcc(*'.mp4'), 20, size)

        for i in range(len(img_array)):
            out.write(img_array[i])
        out.release()
        print(u'complete')

    # todo : data store function
    # todo : data prepare variable

    def saveData(self, handData, handedness):
        self.multi_hand_landmarks = handData
        self.multi_handedness = handedness

        self.dataReady = True

    def getdataReady(self):
        return self.dataReady

    def changeDataReady(self):
        self.dataReady = False

    def getData(self):
        if not self.dataReady:
            return None

        ## 민수 추가 ####
        # [1]
        # string_packets_joint = []
        # string_packets_cls = []
        #
        # for hand_landmarks, hand_cls in zip(self.multi_hand_landmarks, self.multi_handedness):
        #     hand_joints = np.zeros((21, 3))
        #     for i, landmark_ in enumerate(hand_landmarks.landmark):
        #         hand_joints[i, :] = landmark_.x, landmark_.y, landmark_.z
        #     cls = str(hand_cls.classification._values[0].label)
        #     # array to bytes.
        #     # option (1)
        #     array_packet = hand_joints.tobytes()
        #
        #     # option (2)
        #     joints_string = ''
        #     for i in range(len(hand_joints)):
        #         for val in hand_joints[i]:
        #             joints_string += str(val) + ','
        #     string_packet_joints = bytes(joints_string, 'utf-

        #     # string_packet_cls = bytes(cls, 'utf-8')
        #
        #     # 더 짧게 가능할듯
        #     if cls == 'Right':
        #         cls = 'R'
        #     else:
        #         cls = 'L'
        #     string_packet_cls = bytes(str(cls), 'utf-8')
        #     string_packets_joint.append(string_packet_joints)
        #     string_packets_cls.append(string_packet_cls)
        # return string_packets_joint, string_packets_cls


        # [2]
        string_packet = ''

        for hand_landmarks, hand_cls in zip(self.multi_hand_landmarks, self.multi_handedness):
            hand_joints = np.zeros((21, 3))
            for i, landmark_ in enumerate(hand_landmarks.landmark):
                hand_joints[i, :] = landmark_.x, landmark_.y, landmark_.z
            cls = str(hand_cls.classification._values[0].label)
            if cls == 'Right':
                cls = 'R'
            else:
                cls = 'L'

            joints_string = ''
            for i in range(len(hand_joints)):
                for val in hand_joints[i]:
                    joints_string += str(val)[:6] + ','
            string_packet += joints_string + '/'
            string_packet += cls + '/'
        self.queue.append(string_packet)
        return string_packet



        # ## 재학 작성 #
        # self.cls = str(self.ct)
        # self.ct += 1
        # if self.ct > 100:
        #     self.ct = 0
        # #######
        # print("self.ct" + str(self.ct))
        # return self.cls


class UnityServerSocket(ServerSocket):
    def __init__(self, ip, port, cameraClass):
        super().__init__(ip, port)
        print("UnityServerSocket")

        self.cameraClass = cameraClass

        super().socketOpen()
        print("UnityServerSocket class init function")
        # todo : setting thread

        self.receiveThread = threading.Thread(target=self.sendPoint)
        self.receiveThread.start()

    def sendPoint(self):
        cnt = 0

        # todo : get hand pose point data

        try:
            while True:
                '''
                # recv data : data length, data, send time
                length = super().recvall(self.conn, 64)

                length1 = length.decode('utf-8')
                stringData = super().recvall(self.conn, int(length1))

                stime = super().recvall(self.conn, 64)

                print('send time: ' + stime.decode('utf-8'))
                #now = time.localtime()
                print('receive time: ' + datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f'))
                rdata = np.frombuffer(base64.b64decode(stringData), np.uint8)
                '''

                if self.cameraClass.getdataReady():
                    # now = time.localtime()
                    # try:
                    print("Python ---> Unity :: Succeed at {} frame".format(cnt))
                    stime = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')
                    ### 민수 작성 ######
                    send_string = self.cameraClass.getData()
                    # for i in range(len(pointdata)):
                    #     send_packet = pointdata[i].encode('utf-8').ljust(64)
                    #     print(send_packet)      # for debugging
                    #     self.conn.sendall(pointdata[i].encode('utf-8').ljust(64))
                    send_packet = send_string.encode('utf-8').ljust(64)
                    self.conn.sendall(send_packet)
                    # except socket.timeout:
                    #     print('Time out')
                    #     self.cameraClass.queue = [self.cameraClass.queue[-1]]
                    #     send_packet = self.cameraClass.queue[0].encode('utf-8').ljust(64)
                    #     self.conn.sendall(send_packet)
                    self.cameraClass.changeDataReady()
                    cnt += 1
                    # ### 재학 작성 ######
                    # pointdata = self.cameraClass.getData()  # todo : get point data
                    # # sdata = np.array(pointdata)
                    # # stringsData = base64.b64encode(sdata)
                    # # length = str(len(stringsData))
                    # # self.conn.sendall(length.encode('utf-8').ljust(64))
                    # self.conn.sendall(pointdata.encode('utf-8').ljust(64))
                    # # self.conn.send(stringsData)
                    # # self.conn.send(stime.encode('utf-8').ljust(64))
                    # # cnt += 1
                    # self.cameraClass.changeDataReady()
                else:
                    # print("Python ---> Unity :: Fail / Pass at {} frame".format(cnt))
                    pass
                    stime = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')

                    # pointdata = str(0)  # todo : get point data
                    # sdata = np.array(pointdata)
                    # stringsData = base64.b64encode(sdata)
                    # length = str(len(stringsData))
                    # self.conn.sendall(length.encode('utf-8').ljust(64))
                    # self.conn.sendall(pointdata.encode('utf-8').ljust(64))
                    # self.conn.send(stringsData)
                    # self.conn.send(stime.encode('utf-8').ljust(64))


        except Exception as e:
            print(e)

            self.sock.close()
            time.sleep(1)
            super().socketOpen()
            self.sendPoint()
            self.receiveThread = threading.Thread(target=self.sendPoint)
            self.receiveThread.start()


if __name__ == "__main__":
    CameraServer = CameraServerSocket('localhost', 8080)
    UnityServer = UnityServerSocket('localhost', 8081, CameraServer)

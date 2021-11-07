'''
cv2를 사용해서 camera 촬영
image를 encoding 하여 socket으로 전송

localhost 8000

pip install opencv-python
'''

import socket
import cv2
import numpy
import time
import base64
import sys
from datetime import datetime


class ClientSocket:
    def __init__(self, ip, port):
        self.TCP_SERVER_IP = ip
        self.TCP_SERVER_PORT = port
        self.connectCount = 0
        self.connectServer()

    def connectServer(self):
        try:
            self.sock = socket.socket()
            self.sock.connect((self.TCP_SERVER_IP, self.TCP_SERVER_PORT))
            print(u'Client socket is connected with Server socket [ TCP_SERVER_IP: ' + self.TCP_SERVER_IP + ', TCP_SERVER_PORT: ' + str(self.TCP_SERVER_PORT) + ' ]')
            self.connectCount = 0
            self.sendImages()
        except Exception as e:
            print(e)
            self.connectCount += 1
            if self.connectCount == 10:
                print(u'Connect fail %d times. exit program'%(self.connectCount))
                sys.exit()
            print(u'%d times try to connect with server'%(self.connectCount))
            self.connectServer()

    def sendImages(self):
        cnt = 0
        cap = cv2.VideoCapture(0)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 480)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 315)

        try:
            while cap.isOpened():
                success, image = cap.read()
                if not success:
                    print("Ignoring empty camera frame.")
                    continue

                resize_image = cv2.resize(image, dsize=(480, 315), interpolation=cv2.INTER_AREA)
                
                # time setting
                now = time.localtime()
                stime = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')

                # image encode to jpg
                encode_param=[int(cv2.IMWRITE_JPEG_QUALITY),90]
                result, imgencode = cv2.imencode('.jpg', resize_image, encode_param)

                # binary data to text data
                data = numpy.array(imgencode)
                stringData = base64.b64encode(data) # Base64 Encoding은 Binary Data를 Text로 변경하는 Encoding
                length = str(len(stringData))       # length
                
                # socket send
                self.sock.sendall(length.encode('utf-8').ljust(64))  # data 길이 전송: ljust: 64보다 길이가 부족할 때, 공백으로 채운다.
                self.sock.send(stringData)                           # data image 전송
                self.sock.send(stime.encode('utf-8').ljust(64))      # 시간 전송
                
                print(u'send images %d'%(cnt))
                cnt+=1
                time.sleep(0.1)

        except Exception as e:
            print(e)
            self.sock.close()
            time.sleep(1)
            self.connectServer()
            self.sendImages()


if __name__ == "__main__":
    TCP_IP = 'localhost' 
    TCP_PORT = 8080 
    client = ClientSocket(TCP_IP, TCP_PORT)

'''
ljust () : http://www.w3big.com/ko/python/att-string-ljust.html

'''

import os
import sys
import errno

import socket
import numpy as np
import base64
import glob

import threading

import time
from datetime import datetime

import cv2

import mediapipe as mp
from numpy.core.fromnumeric import resize

class ServerSocket:
    def __init__(self, ip, port):
        self.TCP_IP = ip
        self.TCP_PORT = port

    def socketOpen(self):   # socket open
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((self.TCP_IP, self.TCP_PORT))
        self.sock.listen(1)

        print(u'Server socket [ TCP_IP: ' + self.TCP_IP + ', TCP_PORT: ' + str(self.TCP_PORT) + ' ] is open')
        self.conn, self.addr = self.sock.accept()
        print(u'Server socket [ TCP_IP: ' + self.TCP_IP + ', TCP_PORT: ' + str(self.TCP_PORT) + ' ] is connected with client')

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


class UnityServerSocket(ServerSocket):
    def __init__(self, ip, port):
        super().__init__(ip, port)
        print("UnityServerSocket")


        #self.cameraClass = cameraClass
        
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

                stime = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')

                nstime = " "*(64-len(stime))+stime
                
                self.conn.sendall(nstime.encode())
                print(nstime.encode())
                print(len(nstime.encode()))

                '''
                if True: # todo : data enable
                    
                    #now = time.localtime()
                    stime = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')
                    
                    pointdata = self.cameraClass.getData()   # todo : get point data
                    sdata = np.array(pointdata)
                    stringsData = base64.b64encode(sdata)
                    length = str(len(stringsData))
                    self.sock.sendall(length.encode('utf-8').ljust(64))
                    self.sock.send(stringsData)
                    self.sock.send(stime.encode('utf-8').ljust(64))
                    #cnt += 1
                    self.cameraClass.changeDataReady()
                else:
                    stime = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')
                    
                    pointdata = 0   # todo : get point data
                    sdata = np.array(pointdata)
                    stringsData = base64.b64encode(sdata)
                    length = str(len(stringsData))
                    self.sock.sendall(length.encode('utf-8').ljust(64))
                    self.sock.send(stringsData)
                    self.sock.send(stime.encode('utf-8').ljust(64))
                '''

        except Exception as e:
            print(e)
            
            self.sock.close()
            time.sleep(1)
            super().socketOpen()
            self.sendPoint()
            self.receiveThread = threading.Thread(target=self.sendPoint)
            self.receiveThread.start()




if __name__ == "__main__":
    UnityServer = UnityServerSocket('localhost', 8081)

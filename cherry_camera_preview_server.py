# https://elsammit-beginnerblg.hatenablog.com/entry/2020/12/20/181957

import socketserver  
import cv2
import numpy  
import socket  
import sys  

from datetime import datetime

#hostとportを設定
HOST = '192.168.143.94'
PORT = 10001
  
class TCPHandler(socketserver.BaseRequestHandler):  
    def handle(self):

        capture=cv2.VideoCapture(0)
        if not capture:  
            print("Could not open camera")  
            sys.exit()

        self.data = self.request.recv(1024).strip()
        ret, frame=capture.read()
        jpegstring=cv2.imencode('.jpg', frame)[1].tobytes()  
        self.request.send(jpegstring)
        print('[{}] send frame'.format(datetime.now().strftime('%Y-%m-%d %H:%M:%S')))

        capture.release()

#カメラの設定

socketserver.TCPServer.allow_reuse_address = True
server = socketserver.TCPServer((HOST, PORT), TCPHandler)  
# server.capture=capture

try:
    print('[{}] run server'.format(datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
    server.serve_forever()
except KeyboardInterrupt:
    pass
server.shutdown()
sys.exit()
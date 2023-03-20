# https://www.raspberrypirulo.net/entry/socket-server
# https://syachiku-python.com/python%E3%81%A7%E3%81%99%E3%81%90%E5%87%BA%E6%9D%A5%E3%82%8B%EF%BC%81-%E3%83%95%E3%82%A1%E3%82%A4%E3%83%AB%E3%82%92%E8%BB%A2%E9%80%81%E3%81%99%E3%82%8B%E6%96%B9%E6%B3%95%E3%80%90tcp%E9%80%9A%E4%BF%A1/

# 画像送信テスト

import socket
import threading
from datetime import datetime

from time import sleep
import subprocess
import os
import RPi.GPIO as GPIO

import servo
import cherry_slider

HOST_IP = "192.168.143.94" # サーバーのIPアドレス
PORT = 10002 # 使用するポート
CLIENTNUM = 3 # クライアントの接続上限数
DATESIZE = 1024 # 受信データバイト数

LED_PIN = 21
servo_PIN = 26

class SocketServer():
    def __init__(self, host, port):
        self.host = host
        self.port = port

        self.servo_hatch = servo.servo()
        self.servo_hatch.init(servo_PIN, angle_min=-90.0, angle_max=90.0)
        self.servo_hatch.set_angle(0)

    # サーバー起動 
    def run_server(self):

        self.slider = cherry_slider.cherry_slider()

        # server_socketインスタンスを生成
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server_socket.bind((self.host, self.port))
            server_socket.listen(CLIENTNUM)
            print('[{}] run server'.format(datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
            
            while True:
                # クライアントからの接続要求受け入れ
                client_socket, address = server_socket.accept()
                print('[{0}] connect client -> address : {1}'.format(datetime.now().strftime('%Y-%m-%d %H:%M:%S'), address) )
                client_socket.settimeout(60)
                # クライアントごとにThread起動 send/recvのやり取りをする
                t = threading.Thread(target = self.conn_client, args = (client_socket,address))
                t.setDaemon(True)
                t.start()

    # クライアントごとにThread起動する関数
    def conn_client(self, client_socket, address):

        with client_socket:
            rcv_data = client_socket.recv(DATESIZE)
            rcv_text = rcv_data.decode('utf-8')

            print('[{0}] recv date : {1}'.format(datetime.now().strftime('%Y-%m-%d %H:%M:%S'), rcv_text))

            rcv_texts = rcv_text.split()
            if len(rcv_texts) >= 2:
                command = rcv_texts[0]
                text = rcv_texts[1]
            else:
                command = rcv_text
            del rcv_texts[0]


            if command == 'move_abs':
                distance = float(text)

                if distance == 0:
                    self.slider.origin()
                    print('[{}] move origin'.format(datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
                elif distance == 300:
                    self.slider.max()
                    print('[{}] move max'.format(datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
                else:
                    self.slider.move_abs(distance)
                    print('[{}] move abs {}mm'.format(datetime.now().strftime('%Y-%m-%d %H:%M:%S'), str(distance)))

                if self.slider.smotor.emergency == True:
                    status_message = 'emerghency stop'
                else:
                    status_message = 'move done'

                print('[{}] {}'.format(datetime.now().strftime('%Y-%m-%d %H:%M:%S'), status_message))
                client_socket.sendall(status_message.encode('utf-8'))

            if command == 'status':
                if self.slider.smotor.emergency == True:
                    status = "emergency stop"
                else:
                    status = str(self.slider.now_abs_distance)
                client_socket.sendall(status.encode('utf-8'))

            if command == 'servo':
                self.servo_hatch.set_angle(int(text))
                print('[{}] servo set angle {}'.format(datetime.now().strftime('%Y-%m-%d %H:%M:%S'), text))
                status_message = 'servo angle ' + text
                client_socket.sendall(status_message.encode('utf-8'))

if __name__ == "__main__":
    
    server = SocketServer(HOST_IP, PORT)
    server.run_server()
    try:
        while True:
            pass
    except:
        server.slider.end()
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

HOST_IP = "192.168.143.94" # サーバーのIPアドレス
PORT = 10000 # 使用するポート
CLIENTNUM = 3 # クライアントの接続上限数
DATESIZE = 1024 # 受信データバイト数

LED_PIN = 14

class SocketServer():
    def __init__(self, host, port):
        self.host = host
        self.port = port

    # サーバー起動 
    def run_server(self):

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

            # 受信データを命令と内容に分割
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

            # ディレクトリ取得
            path = os.path.dirname(os.path.abspath(__file__))
            directory = path + '/picture/'
            
            # 撮影処理
            if command == 'shoot':
                file_name = text
                
                # 撮影
                GPIO.setmode(GPIO.BCM)
                GPIO.setup(LED_PIN, GPIO.OUT)
                GPIO.output(LED_PIN, GPIO.HIGH)
                subprocess.run(['raspistill', '-o', directory + file_name, '-t', '1'])
                GPIO.output(LED_PIN, GPIO.LOW)
                GPIO.cleanup()

                status_message = 'shoot done  ' + directory + file_name
                print('[{}] {}'.format(datetime.now().strftime('%Y-%m-%d %H:%M:%S'), status_message))
                client_socket.sendall(status_message.encode('utf-8'))

            # 画像送信処理
            if command == 'send':
                file_name = text
                with open(directory +  file_name, mode='rb') as f:
                    for line in f:
                        client_socket.sendall(line)
                        data = client_socket.recv(DATESIZE)
                print('[{}] send done {}'.format(datetime.now().strftime('%Y-%m-%d %H:%M:%S'), file_name))
            
            if command == 'LED':
                if text == 'ON':
                    GPIO.setmode(GPIO.BCM)
                    GPIO.setup(LED_PIN, GPIO.OUT)
                    GPIO.output(LED_PIN, GPIO.HIGH)
                elif text == 'OFF':
                    GPIO.output(LED_PIN, GPIO.LOW)
                    GPIO.cleanup()
                print('[{}] LED {}'.format(datetime.now().strftime('%Y-%m-%d %H:%M:%S'), text))

            if command == 'hello':
                message = 'hello'
                client_socket.sendall(message.encode('utf-8'))

            if command == 'shutdown':
                subprocess.run(['sudo', 'shutdown', '-h', 'now'])

            if command == 'reboot':
                subprocess.run(['sudo', 'reboot'])

            if command == 'command':
                subprocess.run(rcv_texts.split)

if __name__ == "__main__":
    
    SocketServer(HOST_IP, PORT).run_server()
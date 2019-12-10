#!/usr/bin/env python3

import socket
import time
import cv2

from socket_base import SocketBase
import camera

debug = True
header_size = 10
encoding = 'ISO-8859-1'
connection = ('192.168.1.163', 3005)
reconnect_time = 5

socket_base = SocketBase(header_size, encoding)
cam = camera.Vision()

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    while True:
        try:
            sock.connect(connection)
        except Exception as e:
            print(e, '\n', 'Waiting for connection...')
            time.sleep(reconnect_time)
            continue
        while True:
            img_bytes = cv2.imencode('.jpg', cam.get_gray_image())[1].tostring()

            if debug:
                print('Sending', len(img_bytes), 'bytes')

            socket_base.send_message(sock, img_bytes.decode(encoding))

            # server_msg --- data from the server
            server_msg = socket_base.receive_message(sock)[header_size:]
            if debug:
                print('Received:', server_msg)


            # YOUR CODE


except Exception as e:
    print(e)
    sock.close()
    print("Connection ended")
